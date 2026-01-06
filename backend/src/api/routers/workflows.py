"""Workflow Status Router.

Provides endpoints for querying Temporal workflow status.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status."""

    workflow_id: str
    status: str
    current_activity: str | None = None
    progress: int | None = None
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str) -> WorkflowStatusResponse:
    """Get the status of a Temporal workflow.

    Args:
        workflow_id: The workflow ID (e.g., "dataset_ingestion-abc123")

    Returns:
        Workflow status including current activity and progress
    """
    from src.platform.temporal.compat import get_workflow_status as query_status

    try:
        status = await query_status(workflow_id)
        return WorkflowStatusResponse(
            workflow_id=workflow_id,
            status=status.get("status", "UNKNOWN"),
            current_activity=status.get("current_activity"),
            progress=status.get("progress"),
            started_at=status.get("started_at"),
            completed_at=status.get("completed_at"),
            error_message=status.get("error_message"),
        )
    except Exception as e:
        logger.error("workflow_status_error", workflow_id=workflow_id, error=str(e))
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")


@router.post("/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str) -> dict:
    """Cancel a running Temporal workflow.

    Args:
        workflow_id: The workflow ID to cancel

    Returns:
        Confirmation of cancellation request
    """
    from src.platform.temporal.compat import cancel_workflow as do_cancel

    try:
        await do_cancel(workflow_id)
        logger.info("workflow_cancelled", workflow_id=workflow_id)
        return {"workflow_id": workflow_id, "status": "cancel_requested"}
    except Exception as e:
        logger.error("workflow_cancel_error", workflow_id=workflow_id, error=str(e))
        raise HTTPException(status_code=400, detail=f"Failed to cancel workflow: {e}")
