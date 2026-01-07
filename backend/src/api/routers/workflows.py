"""Workflow Status Router.

Provides endpoints for querying Temporal workflow status and database-backed workflow records.
"""

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.api.dependencies import CurrentUser, DBSession
from src.platform.core.logging_config import get_logger
from src.platform.workflows import (
    Workflow,
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowTaskResponse,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


# =============================================================================
# Database-backed Workflow Endpoints
# =============================================================================


@router.get("", response_model=WorkflowListResponse)
async def list_workflows(
    db: DBSession,
    user: CurrentUser,
    status: str | None = Query(None, description="Filter by status"),
    workflow_type: str | None = Query(None, description="Filter by type"),
    entity_type: str | None = Query(None, description="Filter by entity type"),
    entity_id: str | None = Query(None, description="Filter by entity ID"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
) -> WorkflowListResponse:
    """List workflows for the current user/organization.
    
    Use entity_type + entity_id to get workflows for a specific dataset/model.
    """
    query = select(Workflow).options(selectinload(Workflow.tasks))
    
    # Filter by user's org
    query = query.where(Workflow.org_id == user.org_id)
    
    # Apply filters
    if status:
        query = query.where(Workflow.status == status)
    if workflow_type:
        query = query.where(Workflow.workflow_type == workflow_type)
    if entity_type:
        query = query.where(Workflow.entity_type == entity_type)
    if entity_id:
        query = query.where(Workflow.entity_id == entity_id)
    
    # Order by created_at desc
    query = query.order_by(Workflow.created_at.desc())
    
    # Count total
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    workflows = result.scalars().all()
    
    return WorkflowListResponse(
        items=[WorkflowResponse.model_validate(w) for w in workflows],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    db: DBSession,
    workflow_id: str,
    user: CurrentUser,
) -> WorkflowResponse:
    """Get workflow details with task-level progress."""
    query = (
        select(Workflow)
        .options(selectinload(Workflow.tasks))
        .where(Workflow.id == workflow_id)
        .where(Workflow.org_id == user.org_id)
    )
    
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    
    return WorkflowResponse.model_validate(workflow)


@router.get("/{workflow_id}/tasks", response_model=list[WorkflowTaskResponse])
async def get_workflow_tasks(
    db: DBSession,
    workflow_id: str,
    user: CurrentUser,
) -> list[WorkflowTaskResponse]:
    """Get granular task progress for a workflow.
    
    Returns ordered list of tasks with their individual status and progress.
    """
    query = (
        select(Workflow)
        .options(selectinload(Workflow.tasks))
        .where(Workflow.id == workflow_id)
        .where(Workflow.org_id == user.org_id)
    )
    
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    
    # Tasks are already ordered by task_order via relationship
    return [WorkflowTaskResponse.model_validate(t) for t in workflow.tasks]


# =============================================================================
# Temporal Integration Endpoints
# =============================================================================


@router.get("/{workflow_id}/status")
async def get_workflow_temporal_status(workflow_id: str) -> dict:
    """Get real-time status from Temporal for a workflow.

    Args:
        workflow_id: The Temporal workflow ID (e.g., "dataset_ingestion-abc123")

    Returns:
        Workflow status including current activity and progress from Temporal
    """
    from src.platform.temporal.compat import get_workflow_status as query_status

    try:
        status = await query_status(workflow_id)
        return {
            "workflow_id": workflow_id,
            "status": status.get("status", "UNKNOWN"),
            "current_activity": status.get("current_activity"),
            "progress": status.get("progress"),
            "started_at": status.get("started_at"),
            "completed_at": status.get("completed_at"),
            "error_message": status.get("error_message"),
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    except ConnectionError as e:
        logger.error("temporal_connection_failed", workflow_id=workflow_id, error=str(e))
        raise HTTPException(status_code=503, detail="Workflow service temporarily unavailable")
    except Exception as e:
        logger.error("workflow_status_error", workflow_id=workflow_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")


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
