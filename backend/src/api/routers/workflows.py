"""Workflows API Router - Pipeline Automation."""

import json
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_session
from src.core.enums import WorkflowStatus
from src.core.logging_config import get_logger
from src.models.orm import Dataset, Workflow, WorkflowRun
from src.models.schemas import (
    WorkflowCreateRequest,
    WorkflowResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowTemplate,
)
from src.services.workflow import workflow_service

logger = get_logger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("/templates", response_model=list[WorkflowTemplate])
async def list_templates():
    """List predefined workflow templates."""
    templates = workflow_service.get_templates()
    return [
        WorkflowTemplate(
            id=t["id"],
            name=t["name"],
            description=t["description"],
            steps=t["steps"],
        )
        for t in templates
    ]


@router.post("", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Create a new workflow."""
    # Validate
    is_valid, msg = workflow_service.validate_workflow([s.model_dump() for s in request.steps])
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    workflow = Workflow(
        name=request.name,
        steps_json=json.dumps([s.model_dump() for s in request.steps]),
        schedule=request.schedule,
        is_active=True,
    )
    session.add(workflow)
    await session.commit()
    await session.refresh(workflow)

    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        steps=request.steps,
        schedule=workflow.schedule,
        is_active=workflow.is_active,
        created_at=workflow.created_at,
    )


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(
    session: AsyncSession = Depends(get_session),
):
    """List all workflows."""
    result = await session.execute(select(Workflow).order_by(Workflow.created_at.desc()))
    workflows = result.scalars().all()

    return [WorkflowResponse.model_validate(w) for w in workflows]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get workflow by ID."""
    result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Delete a workflow."""
    result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    await session.delete(workflow)
    await session.commit()
    return {"status": "deleted", "workflow_id": workflow_id}


@router.post("/{workflow_id}/run", response_model=WorkflowRunResponse)
async def run_workflow(
    workflow_id: str,
    request: WorkflowRunRequest,
    session: AsyncSession = Depends(get_session),
):
    """Execute a workflow."""
    logger.info(
        "workflow_run_started",
        workflow_id=workflow_id,
        dataset_id=request.dataset_id,
    )
    start_time = time.perf_counter()

    result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        logger.warning("workflow_not_found", workflow_id=workflow_id)
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Validate log exists if provided
    if request.dataset_id:
        log_result = await session.execute(select(Dataset).where(Dataset.id == request.dataset_id))
        if not log_result.scalar_one_or_none():
            logger.warning("dataset_not_found", dataset_id=request.dataset_id)
            raise HTTPException(status_code=404, detail="Event log not found")

    # Create run record
    run = WorkflowRun(
        workflow_id=workflow_id,
        dataset_id=request.dataset_id,
        status=WorkflowStatus.RUNNING.value,
        started_at=datetime.utcnow(),
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)

    # Execute steps (simplified - in production would be async)
    try:
        steps = json.loads(workflow.steps_json)
        results = {}
        context = {"dataset_id": request.dataset_id, **request.params}

        for step in steps:
            step_result = await workflow_service.execute_step(
                step["type"], step.get("params", {}), context
            )
            results[step["name"]] = step_result

        run.status = WorkflowStatus.COMPLETED.value
        run.result_json = json.dumps(results)
        run.completed_at = datetime.utcnow()

    except Exception as e:
        run.status = WorkflowStatus.FAILED.value
        run.error = str(e)
        run.completed_at = datetime.utcnow()
        logger.error(
            "workflow_run_failed",
            run_id=run.id,
            workflow_id=workflow_id,
            error=str(e),
            exc_info=True,
        )

    await session.commit()
    await session.refresh(run)

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "workflow_run_completed",
        run_id=run.id,
        workflow_id=workflow_id,
        status=run.status,
        duration_ms=round(duration_ms, 2),
    )

    return WorkflowRunResponse(
        id=run.id,
        workflow_id=run.workflow_id,
        dataset_id=run.dataset_id,
        status=run.status,
        started_at=run.started_at,
        completed_at=run.completed_at,
        error=run.error,
    )


@router.get("/{workflow_id}/runs", response_model=list[WorkflowRunResponse])
async def list_workflow_runs(
    workflow_id: str,
    session: AsyncSession = Depends(get_session),
):
    """List runs for a workflow."""
    result = await session.execute(
        select(WorkflowRun)
        .where(WorkflowRun.workflow_id == workflow_id)
        .order_by(WorkflowRun.started_at.desc())
    )
    runs = result.scalars().all()

    return [
        WorkflowRunResponse(
            id=r.id,
            workflow_id=r.workflow_id,
            dataset_id=r.dataset_id,
            status=r.status,
            started_at=r.started_at,
            completed_at=r.completed_at,
            error=r.error,
        )
        for r in runs
    ]


@router.get("/runs/{run_id}", response_model=WorkflowRunResponse)
async def get_workflow_run(
    run_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get a specific workflow run."""
    result = await session.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")

    return WorkflowRunResponse(
        id=run.id,
        workflow_id=run.workflow_id,
        dataset_id=run.dataset_id,
        status=run.status,
        started_at=run.started_at,
        completed_at=run.completed_at,
        error=run.error,
    )
