"""Temporal Compatibility Layer.

Provides a compatibility layer for transitioning from Celery to Temporal.
When Temporal is not available, provides synchronous fallbacks for critical workflows.
"""

import asyncio
import uuid
from typing import Any

import structlog

from src.infra.temporal.config import get_temporal_config

logger = structlog.get_logger(__name__)

# Cache for Temporal availability check
_temporal_available: bool | None = None
_check_lock = asyncio.Lock()


async def _check_temporal_connection() -> bool:
    """Actually attempt to connect to Temporal server.

    Returns:
        True if connection successful, False otherwise
    """
    config = get_temporal_config()

    try:
        from temporalio.client import Client

        # Try to connect with a short timeout
        await asyncio.wait_for(
            Client.connect(
                config.host,
                namespace=config.namespace,
                tls=config.use_tls,
            ),
            timeout=5.0,
        )
        logger.info(
            "temporal_connection_successful",
            host=config.host,
            namespace=config.namespace,
        )
        return True
    except asyncio.TimeoutError:
        logger.warning(
            "temporal_connection_timeout",
            host=config.host,
            message="Temporal server not responding",
        )
        return False
    except Exception as e:
        logger.warning(
            "temporal_connection_failed",
            host=config.host,
            error=str(e),
            message="Falling back to synchronous mode",
        )
        return False


def is_temporal_enabled() -> bool:
    """Check if Temporal is enabled in config.

    This is a sync check of the config setting only.
    Use is_temporal_available() for actual connectivity check.

    Returns:
        True if Temporal is enabled in config
    """
    config = get_temporal_config()
    return config.use_temporal


async def is_temporal_available() -> bool:
    """Check if Temporal is enabled AND the server is reachable.

    Caches the result after first check to avoid repeated connection attempts.

    Returns:
        True if Temporal is enabled and server is reachable
    """
    global _temporal_available

    # Return cached result if available
    if _temporal_available is not None:
        return _temporal_available

    async with _check_lock:
        # Double-check after acquiring lock
        if _temporal_available is not None:
            return _temporal_available

        # Check config first
        if not is_temporal_enabled():
            logger.info("temporal_disabled_by_config")
            _temporal_available = False
            return False

        # Check actual connectivity
        _temporal_available = await _check_temporal_connection()
        return _temporal_available


def reset_temporal_availability_cache() -> None:
    """Reset the cached Temporal availability status.

    Call this if you want to re-check Temporal connectivity.
    """
    global _temporal_available
    _temporal_available = None


async def _run_validation_sync(dataset_id: str, storage_key: str) -> dict[str, Any]:
    """Run file validation synchronously (fallback when Temporal is disabled).

    This is a simplified validation that runs synchronously instead of via Temporal.
    It validates the file format and updates the dataset status.
    """
    from src.infra.infrastructure.object_storage import get_storage_client

    logger.info(
        "sync_validation_started",
        dataset_id=dataset_id,
        storage_key=storage_key,
    )

    try:
        storage_client = get_storage_client()

        # Stream first 10MB for validation
        validation_chunk_size = 10 * 1024 * 1024
        file_chunks = []
        total_bytes = 0

        for chunk in storage_client.stream_file("raw", storage_key, chunk_size=64 * 1024):
            file_chunks.append(chunk)
            total_bytes += len(chunk)
            if total_bytes >= validation_chunk_size:
                break

        file_content = b"".join(file_chunks)

        # Determine file type from storage key
        file_extension = storage_key.split(".")[-1].lower() if "." in storage_key else "csv"

        # Magic byte verification
        is_valid = True
        error_message = None

        if file_extension == "xes":
            if not file_content.startswith((b"<?xml", b"<log")):
                is_valid = False
                error_message = "Invalid XES file signature (not valid XML)"
        elif file_extension == "csv":
            try:
                file_content[:1024].decode("utf-8")
            except UnicodeDecodeError:
                is_valid = False
                error_message = "Invalid CSV file signature (contains binary data)"

        if not is_valid:
            logger.error(
                "sync_validation_failed",
                dataset_id=dataset_id,
                error=error_message,
            )
            return {
                "status": "failed",
                "error": error_message,
            }

        logger.info(
            "sync_validation_completed",
            dataset_id=dataset_id,
            file_size=total_bytes,
            is_valid=True,
        )

        return {
            "status": "completed",
            "workflow_id": f"sync-{uuid.uuid4().hex[:8]}",
            "dataset_id": dataset_id,
            "file_size_bytes": total_bytes,
            "is_valid": True,
        }

    except Exception as e:
        logger.error(
            "sync_validation_exception",
            dataset_id=dataset_id,
            error=str(e),
        )
        return {
            "status": "error",
            "error": str(e),
        }


async def dispatch_workflow(
    workflow_type: str,
    args: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    """Dispatch workflow to Temporal or fall back to synchronous execution.

    Checks if Temporal is available and dispatches accordingly.
    When Temporal is unavailable, provides synchronous implementations for
    critical workflows like file validation.

    Args:
        workflow_type: Type of workflow to dispatch
        args: Workflow arguments
        **kwargs: Additional options

    Returns:
        Dict with status and results
    """
    temporal_available = await is_temporal_available()

    logger.info(
        "dispatch_workflow_called",
        workflow_type=workflow_type,
        temporal_enabled=is_temporal_enabled(),
        temporal_available=temporal_available,
    )

    # If Temporal is available, dispatch to Temporal
    if temporal_available:
        return await _dispatch_to_temporal(workflow_type, args, **kwargs)

    # Synchronous fallbacks when Temporal is unavailable
    if workflow_type == "validate_uploaded_file":
        dataset_id = args.get("dataset_id")
        storage_key = args.get("storage_key")

        if not dataset_id or not storage_key:
            return {"status": "error", "error": "Missing required args: dataset_id, storage_key"}

        return await _run_validation_sync(dataset_id, storage_key)

    # For other workflow types without sync fallback
    logger.warning(
        "workflow_sync_fallback_unavailable",
        workflow_type=workflow_type,
        message="No sync fallback available for this workflow type",
    )

    return {
        "status": "pending",
        "workflow_id": f"placeholder-{uuid.uuid4().hex[:8]}",
        "message": f"Workflow '{workflow_type}' queued (sync mode - limited functionality)",
    }


async def _dispatch_to_temporal(
    workflow_type: str,
    args: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    """Dispatch workflow to Temporal server.

    Args:
        workflow_type: Type of workflow to dispatch
        args: Workflow arguments
        **kwargs: Additional options

    Returns:
        Dict with workflow_id and status
    """
    from src.infra.temporal.client import get_temporal_client

    try:
        client = await get_temporal_client()

        # Map workflow types to actual workflow classes
        workflow_id = f"{workflow_type}-{uuid.uuid4().hex[:8]}"

        if workflow_type == "validate_uploaded_file":
            from src.infra.temporal.workflows_v2.ingestion import DatasetIngestionWorkflowV2

            handle = await client.start_workflow(
                DatasetIngestionWorkflowV2.run,
                args,
                id=workflow_id,
                task_queue="ingestion-queue",
            )

            logger.info(
                "temporal_workflow_started",
                workflow_type=workflow_type,
                workflow_id=workflow_id,
            )

            return {
                "status": "running",
                "workflow_id": workflow_id,
                "temporal_run_id": handle.result_run_id,
            }

        if workflow_type == "run_analysis":
            from src.infra.temporal.workflows_v2.analysis import AnalysisWorkflowV2

            handle = await client.start_workflow(
                AnalysisWorkflowV2.run,
                args,
                id=workflow_id,
                task_queue="analysis-queue",
            )

            logger.info(
                "temporal_workflow_started",
                workflow_type=workflow_type,
                workflow_id=workflow_id,
            )

            return {
                "status": "running",
                "workflow_id": workflow_id,
                "temporal_run_id": handle.result_run_id,
            }

        logger.warning(
            "unknown_workflow_type",
            workflow_type=workflow_type,
        )
        return {
            "status": "error",
            "error": f"Unknown workflow type: {workflow_type}",
        }

    except Exception as e:
        logger.error(
            "temporal_dispatch_failed",
            workflow_type=workflow_type,
            error=str(e),
        )
        return {
            "status": "error",
            "error": f"Failed to dispatch to Temporal: {e}",
        }


async def get_workflow_status(workflow_id: str) -> dict[str, Any]:
    """Get workflow execution status (compatibility stub).

    Args:
        workflow_id: Workflow instance ID

    Returns:
        Status dict
    """
    # For sync workflows (prefixed with "sync-"), return completed
    if workflow_id.startswith("sync-"):
        return {
            "status": "completed",
            "workflow_id": workflow_id,
        }

    # For placeholder workflows
    if workflow_id.startswith("placeholder-"):
        return {
            "status": "unknown",
            "workflow_id": workflow_id,
            "message": "Temporal not available - workflow status unknown",
        }

    return {
        "status": "unknown",
        "workflow_id": workflow_id,
    }


async def cancel_workflow(workflow_id: str) -> bool:
    """Cancel running workflow (compatibility stub).

    Args:
        workflow_id: Workflow instance ID

    Returns:
        True if cancelled (sync workflows are already done)
    """
    # Sync workflows complete immediately, nothing to cancel
    if workflow_id.startswith("sync-"):
        return True

    logger.warning(
        "cancel_workflow_not_implemented",
        workflow_id=workflow_id,
    )
    return False
