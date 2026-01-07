"""Operations Router - Unified Workflow Status API.

Single source of truth: Temporal.
This replaces dual-polling of /jobs/{id} and /workflows/{id}/status.

All status queries go through Temporal. The database is updated BY activities,
not queried for status.

Real-Time Streaming:
    GET /api/v1/operations/{workflow_id}/stream - SSE stream for real-time progress
    - Combines Temporal query with Redis pub/sub for real-time updates
    - Frontend should use EventSource to connect

Example Frontend Usage:
    ```javascript
    const eventSource = new EventSource('/api/v1/operations/ingest-dataset-123/stream');
    eventSource.addEventListener('step:progress', (event) => {
        const data = JSON.parse(event.data);
        console.log(`Step ${data.step}: ${data.progress}%`);
    });
    eventSource.addEventListener('workflow:completed', (event) => {
        console.log('Workflow completed!');
        eventSource.close();
    });
    ```
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.api.dependencies import CurrentUser
from src.infra.core.exceptions import BadRequestError, NotFoundError, ProcessingError
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/operations", tags=["Operations"])


# =============================================================================
# Response Models
# =============================================================================


class OperationStatus(BaseModel):
    """Operation status response from Temporal."""

    workflow_id: str = Field(..., description="Temporal workflow ID")
    status: str = Field(
        ..., description="PENDING, RUNNING, COMPLETED, FAILED, CANCELLED, TIMED_OUT"
    )
    progress: int = Field(0, ge=0, le=100, description="Progress percentage 0-100")
    current_step: str | None = Field(None, description="Current activity/step name")
    started_at: str | None = Field(None, description="ISO timestamp when started")
    completed_at: str | None = Field(None, description="ISO timestamp when completed")
    error_message: str | None = Field(None, description="Error message if failed")
    entity_type: str | None = Field(None, description="Entity type (dataset, model, etc)")
    entity_id: str | None = Field(None, description="Entity ID")
    operation_type: str | None = Field(None, description="Operation type (ingest, discover, etc)")


class OperationListResponse(BaseModel):
    """List of operations."""

    items: list[OperationStatus]
    total: int


class CancelResponse(BaseModel):
    """Response for cancel operation."""

    workflow_id: str
    status: str


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/{workflow_id}", response_model=OperationStatus)
async def get_operation_status(workflow_id: str, user: CurrentUser) -> OperationStatus:
    """Get operation status from Temporal.

    This is the ONLY place to get job/workflow status.
    Queries Temporal directly - no database status polling.

    Workflow ID Patterns:
    - Ingestion: ingest-dataset-{dataset_id}
    - Validation: validate-dataset-{dataset_id}
    - Discovery: discover-{dataset_id}-{miner_type}
    - Conformance: conformance-{dataset_id}-{model_id}

    Args:
        workflow_id: The Temporal workflow ID

    Returns:
        OperationStatus with current status and progress
    """
    from src.infra.temporal.client import get_temporal_client

    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)

        # Get workflow description
        try:
            desc = await handle.describe()
            status = desc.status.name if desc.status else "UNKNOWN"
            started_at = desc.start_time.isoformat() if desc.start_time else None
            completed_at = desc.close_time.isoformat() if desc.close_time else None
        except Exception as e:
            logger.warning("workflow_describe_failed", workflow_id=workflow_id, error=str(e))
            raise NotFoundError(resource='Resource', resource_id='unknown')

        # Query workflow for progress (Temporal-native, survives replays)
        progress = 0
        current_step = None
        error_message = None

        try:
            progress_info = await handle.query("get_progress")
            progress = progress_info.get("progress", 0)
            current_step = progress_info.get("current_step")
            error_message = progress_info.get("error")
        except Exception as e:
            # Query may fail if workflow is not running or doesn't have query handler
            logger.debug("workflow_query_failed", workflow_id=workflow_id, error=str(e))

        # Parse entity info from workflow_id
        # Format: {operation}-{entity_type}-{entity_id} or {operation}-{entity_id}-{extra}
        entity_type, entity_id, operation_type = _parse_workflow_id(workflow_id)

        return OperationStatus(
            workflow_id=workflow_id,
            status=status,
            progress=progress,
            current_step=current_step,
            started_at=started_at,
            completed_at=completed_at,
            error_message=error_message,
            entity_type=entity_type,
            entity_id=entity_id,
            operation_type=operation_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_operation_status_failed", workflow_id=workflow_id, error=str(e))
        raise ProcessingError(message=f"Failed to get operation status: {e}")


@router.get("", response_model=OperationListResponse)
async def list_operations(
    user: CurrentUser,
    entity_type: str | None = Query(None, description="Filter by entity type (dataset, model)"),
    entity_id: str | None = Query(None, description="Filter by entity ID"),
    status: str | None = Query(None, description="Filter by status (RUNNING, COMPLETED, FAILED)"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
) -> OperationListResponse:
    """List operations from Temporal.

    Note: Temporal list queries may be slower than database queries.
    For high-frequency list access, consider using the Workflow read-model.

    Args:
        entity_type: Filter by entity type
        entity_id: Filter by entity ID
        status: Filter by status
        limit: Maximum results
        offset: Pagination offset

    Returns:
        List of operations matching filters
    """
    from src.infra.temporal.client import get_temporal_client

    try:
        client = await get_temporal_client()

        # Build Temporal list filter query
        # Note: This requires Temporal's advanced visibility (Elasticsearch)
        query_parts = []

        if status:
            query_parts.append(f'ExecutionStatus = "{status}"')

        # For entity filtering, we rely on workflow ID patterns
        if entity_id:
            query_parts.append(f'WorkflowId LIKE "%{entity_id}%"')

        query = " AND ".join(query_parts) if query_parts else None

        try:
            # List workflows from Temporal
            workflows: list[OperationStatus] = []
            async for workflow in client.list_workflows(query=query):
                if len(workflows) >= offset + limit:
                    break

                if len(workflows) >= offset:
                    entity_type_parsed, entity_id_parsed, op_type = _parse_workflow_id(workflow.id)

                    # Apply entity_type filter if specified
                    if entity_type and entity_type_parsed != entity_type:
                        continue

                    workflows.append(
                        OperationStatus(
                            workflow_id=workflow.id,
                            status=workflow.status.name if workflow.status else "UNKNOWN",
                            progress=0,  # Would need query for each
                            current_step=None,
                            started_at=workflow.start_time.isoformat()
                            if workflow.start_time
                            else None,
                            completed_at=workflow.close_time.isoformat()
                            if workflow.close_time
                            else None,
                            error_message=None,
                            entity_type=entity_type_parsed,
                            entity_id=entity_id_parsed,
                            operation_type=op_type,
                        )
                    )
                else:
                    # Skip for offset
                    pass

            return OperationListResponse(
                items=workflows[offset : offset + limit],
                total=len(workflows),  # Approximate
            )

        except Exception as e:
            logger.warning("temporal_list_failed", error=str(e))
            # Fall back to empty list
            return OperationListResponse(items=[], total=0)

    except Exception as e:
        logger.error("list_operations_failed", error=str(e))
        raise ProcessingError(message=f"Failed to list operations: {e}")


@router.post("/{workflow_id}/cancel", response_model=CancelResponse)
async def cancel_operation(workflow_id: str, user: CurrentUser) -> CancelResponse:
    """Cancel a running operation.

    Sends cancel request to Temporal. The workflow will receive a
    CancelledError and should perform cleanup.

    Args:
        workflow_id: The operation to cancel

    Returns:
        Confirmation of cancel request
    """
    from src.infra.temporal.client import get_temporal_client

    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)

        await handle.cancel()

        logger.info("operation_cancelled", workflow_id=workflow_id, user_id=user.id)

        return CancelResponse(workflow_id=workflow_id, status="cancel_requested")

    except Exception as e:
        logger.error("cancel_operation_failed", workflow_id=workflow_id, error=str(e))
        raise BadRequestError(message=f"Cannot cancel operation: {e}")


@router.get("/{workflow_id}/result")
async def get_operation_result(workflow_id: str, user: CurrentUser):
    """Get the final result of a completed operation.

    Only available for COMPLETED workflows.

    Args:
        workflow_id: The operation ID

    Returns:
        The workflow's return value
    """
    from src.infra.temporal.client import get_temporal_client

    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)

        # Get workflow status first
        desc = await handle.describe()
        if (desc.status.name if desc.status else "UNKNOWN") != "COMPLETED":
            raise BadRequestError(message=f"Operation not completed. Status: {desc.status.name if desc.status else 'UNKNOWN'}")

        # Get result
        result = await handle.result()

        return {"workflow_id": workflow_id, "status": "COMPLETED", "result": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_operation_result_failed", workflow_id=workflow_id, error=str(e))
        raise ProcessingError(message=f"Failed to get result: {e}")


# =============================================================================
# Real-Time SSE Streaming
# =============================================================================


@router.get("/{workflow_id}/stream")
async def stream_operation_progress(
    request: Request,
    workflow_id: str,
    user: CurrentUser,
):
    """Stream real-time workflow progress via Server-Sent Events.

    This endpoint provides real-time updates for long-running operations like:
    - Dataset ingestion (ingest-dataset-{uuid})
    - Process discovery (discover-{uuid}-{miner})
    - Conformance checking (conformance-{uuid}-{uuid})

    ## Event Types

    The stream emits the following SSE event types:

    - `step:started` - Activity step has started
    - `step:progress` - Progress update within a step (0-100%)
    - `step:completed` - Activity step completed successfully
    - `step:failed` - Activity step failed
    - `workflow:completed` - Entire workflow completed
    - `workflow:failed` - Entire workflow failed

    ## Event Data Format

    ```json
    {
        "workflow_id": "ingest-dataset-abc123",
        "event": "step:progress",
        "step": "parse_to_parquet",
        "progress": 45,
        "timestamp": "2024-01-15T10:30:00Z",
        "details": {
            "phase": "converting_events",
            "total_events": 10000
        }
    }
    ```

    ## Frontend Usage

    ```javascript
    const eventSource = new EventSource('/api/v1/operations/ingest-dataset-123/stream');

    eventSource.addEventListener('step:progress', (event) => {
        const data = JSON.parse(event.data);
        updateProgressBar(data.progress);
        showStatus(`${data.step}: ${data.details.phase}`);
    });

    eventSource.addEventListener('workflow:completed', (event) => {
        showSuccess('Operation completed!');
        eventSource.close();
    });

    eventSource.addEventListener('workflow:failed', (event) => {
        const data = JSON.parse(event.data);
        showError(data.details.error);
        eventSource.close();
    });

    eventSource.onerror = () => {
        // Reconnect logic
    };
    ```

    ## Connection Behavior

    - Sends initial state from Temporal query on connect
    - Subscribes to Redis pub/sub for real-time updates
    - Sends heartbeat every 15 seconds to keep connection alive
    - Automatically closes when workflow completes or fails
    - Client should handle reconnection for network issues

    Args:
        workflow_id: The Temporal workflow ID (e.g., "ingest-dataset-{uuid}")

    Returns:
        SSE stream with progress events
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for the workflow."""
        from src.infra.core.config import get_settings
        from src.infra.temporal.client import get_temporal_client

        settings = get_settings()

        # 1. Send initial state from Temporal query
        try:
            client = await get_temporal_client()
            handle = client.get_workflow_handle(workflow_id)

            # Get workflow description
            desc = await handle.describe()
            status = desc.status.name if desc.status else "UNKNOWN"
            started_at = desc.start_time.isoformat() if desc.start_time else None

            # Query progress from workflow
            progress_info = {"progress": 0, "current_step": "unknown"}
            try:
                progress_info = await handle.query("get_progress")
            except Exception:
                pass  # Query may fail for various reasons

            # Send initial state
            initial_data = {
                "workflow_id": workflow_id,
                "event": "workflow:progress",
                "step": progress_info.get("current_step", "unknown"),
                "progress": progress_info.get("progress", 0),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": {
                    "status": status,
                    "started_at": started_at,
                    **{k: v for k, v in progress_info.items() if k not in ("progress", "current_step")},
                },
            }
            yield f"event: workflow:progress\ndata: {json.dumps(initial_data)}\n\n"

            # If already completed or failed, send final event and close
            if status == "COMPLETED":
                yield f"event: workflow:completed\ndata: {json.dumps({'workflow_id': workflow_id, 'status': 'completed'})}\n\n"
                return
            elif status in ("FAILED", "CANCELLED", "TERMINATED", "TIMED_OUT"):
                error = progress_info.get("error", f"Workflow {status.lower()}")
                yield f"event: workflow:failed\ndata: {json.dumps({'workflow_id': workflow_id, 'error': error})}\n\n"
                return

        except Exception as e:
            logger.warning("stream_initial_state_failed", workflow_id=workflow_id, error=str(e))
            # Send error but continue to try Redis subscription
            yield f"event: error\ndata: {json.dumps({'error': f'Failed to get initial state: {e}'})}\n\n"

        # 2. Subscribe to Redis for real-time updates
        redis_client = None
        pubsub = None

        try:
            import redis.asyncio as redis

            redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

            channel = f"workflow:progress:{workflow_id}"
            pubsub = redis_client.pubsub()
            await pubsub.subscribe(channel)

            logger.info("sse_stream_subscribed", workflow_id=workflow_id, channel=channel)

            # Track last heartbeat
            last_heartbeat = asyncio.get_event_loop().time()

            async for message in pubsub.listen():
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info("sse_client_disconnected", workflow_id=workflow_id)
                    break

                # Send heartbeat every 15 seconds
                now = asyncio.get_event_loop().time()
                if now - last_heartbeat >= 15:
                    yield ": heartbeat\n\n"
                    last_heartbeat = now

                if message["type"] == "message":
                    # Forward the SSE message from Redis
                    yield message["data"]

                    # Check if workflow completed or failed
                    if "workflow:completed" in message["data"] or "workflow:failed" in message["data"]:
                        break

        except Exception as e:
            logger.warning("sse_redis_failed", workflow_id=workflow_id, error=str(e))
            # Fallback to polling Temporal
            yield ": redis_unavailable, falling back to polling\n\n"

            poll_count = 0
            max_polls = 600  # 10 minutes max

            while poll_count < max_polls:
                if await request.is_disconnected():
                    break

                try:
                    client = await get_temporal_client()
                    handle = client.get_workflow_handle(workflow_id)
                    desc = await handle.describe()
                    status = desc.status.name if desc.status else "UNKNOWN"

                    progress_info = {"progress": 0, "current_step": "unknown"}
                    try:
                        progress_info = await handle.query("get_progress")
                    except Exception:
                        pass

                    poll_data = {
                        "workflow_id": workflow_id,
                        "event": "workflow:progress",
                        "step": progress_info.get("current_step", "unknown"),
                        "progress": progress_info.get("progress", 0),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "details": {"status": status, "poll_mode": True},
                    }
                    yield f"event: workflow:progress\ndata: {json.dumps(poll_data)}\n\n"

                    if status == "COMPLETED":
                        yield f"event: workflow:completed\ndata: {json.dumps({'workflow_id': workflow_id})}\n\n"
                        break
                    elif status in ("FAILED", "CANCELLED", "TERMINATED", "TIMED_OUT"):
                        yield f"event: workflow:failed\ndata: {json.dumps({'workflow_id': workflow_id, 'error': status})}\n\n"
                        break

                except Exception as poll_error:
                    logger.warning("sse_poll_failed", error=str(poll_error))

                await asyncio.sleep(1)
                poll_count += 1

        finally:
            # Cleanup Redis connection
            if pubsub:
                try:
                    await pubsub.unsubscribe()
                    await pubsub.close()
                except Exception:
                    pass
            if redis_client:
                try:
                    await redis_client.close()
                except Exception:
                    pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*",
        },
    )


# =============================================================================
# Helpers
# =============================================================================


def _parse_workflow_id(workflow_id: str) -> tuple[str | None, str | None, str | None]:
    """Parse entity info from workflow ID.

    Workflow ID Patterns:
    - ingest-dataset-{dataset_id}
    - validate-dataset-{dataset_id}
    - discover-{dataset_id}-{miner_type}
    - conformance-{dataset_id}-{model_id}

    Returns:
        (entity_type, entity_id, operation_type)
    """
    parts = workflow_id.split("-")

    if len(parts) < 2:
        return None, None, None

    operation = parts[0]

    if operation in ("ingest", "validate"):
        # Format: {operation}-dataset-{uuid}
        if len(parts) >= 3 and parts[1] == "dataset":
            return "dataset", "-".join(parts[2:]), operation
        if len(parts) >= 2:
            return "dataset", "-".join(parts[1:]), operation

    elif operation == "discover":
        # Format: discover-{dataset_id}-{miner_type}
        if len(parts) >= 3:
            # Try to find where miner_type starts (it's the last part)
            miner_types = ["alpha", "inductive", "heuristic", "ilp"]
            for i, part in enumerate(parts[1:], start=1):
                if part in miner_types:
                    dataset_id = "-".join(parts[1:i])
                    return "dataset", dataset_id, operation
            # Default: last part is miner, rest is dataset_id
            return "dataset", "-".join(parts[1:-1]), operation

    elif operation == "conformance":
        # Format: conformance-{dataset_id}-{model_id}
        if len(parts) >= 3:
            # Assume UUIDs are 36 chars with dashes
            # This is a simplification - in practice, parse more carefully
            return "dataset", parts[1] if len(parts[1]) == 36 else "-".join(parts[1:]), operation

    # Generic fallback
    return None, "-".join(parts[1:]) if len(parts) > 1 else None, operation
