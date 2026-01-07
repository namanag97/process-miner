"""Operations Router - Unified Workflow Status API.

Single source of truth: Temporal.
This replaces dual-polling of /jobs/{id} and /workflows/{id}/status.

All status queries go through Temporal. The database is updated BY activities,
not queried for status.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.dependencies import CurrentUser
from src.platform.core.logging_config import get_logger
from src.platform.core.exceptions import BadRequestError, NotFoundError, ProcessingError

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
    from src.platform.temporal.client import get_temporal_client

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
    from src.platform.temporal.client import get_temporal_client

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
            workflows: list[dict] = []
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
    from src.platform.temporal.client import get_temporal_client

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
    from src.platform.temporal.client import get_temporal_client

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
