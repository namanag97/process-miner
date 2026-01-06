"""Workflows API Router - Pipeline Automation.

Reusable multi-step analysis pipelines.
"""

import json
import time
from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from src.api.dependencies import DBSession
from src.features.process_mining.models import Dataset, Workflow, WorkflowRun
from src.features.process_mining.schemas import (
    WorkflowCreateRequest,
    WorkflowResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowTemplate,
)
from src.features.process_mining.workflows.service import workflow_service
from src.platform.core.enums import WorkflowStatus
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("/templates", response_model=list[WorkflowTemplate])
async def list_templates():
    """List predefined workflow templates."""
    templates = workflow_service.get_templates()
    return [WorkflowTemplate(id=t["id"], name=t["name"], description=t["description"], steps=t["steps"]) for t in templates]


@router.post("", response_model=WorkflowResponse)
async def create_workflow(request: WorkflowCreateRequest, db: DBSession):
    """Create a new workflow."""
    is_valid, msg = workflow_service.validate_workflow([s.model_dump() for s in request.steps])
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    workflow = Workflow(
        name=request.name,
        steps_json=json.dumps([s.model_dump() for s in request.steps]),
        schedule=request.schedule,
        is_active=True,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        steps=request.steps,
        schedule=workflow.schedule,
        is_active=workflow.is_active,
        created_at=workflow.created_at,
    )


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(db: DBSession):
    """List all workflows."""
    result = await db.execute(select(Workflow).order_by(Workflow.created_at.desc()))
    return [WorkflowResponse.model_validate(w) for w in result.scalars().all()]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, db: DBSession):
    """Get workflow by ID."""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str, db: DBSession):
    """Delete a workflow."""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    await db.delete(workflow)
    await db.commit()
    return {"status": "deleted", "workflow_id": workflow_id}


@router.post("/{workflow_id}/run", response_model=WorkflowRunResponse)
async def run_workflow(workflow_id: str, request: WorkflowRunRequest, db: DBSession):
    """Execute a workflow."""
    start_time = time.perf_counter()

    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if request.dataset_id:
        log_result = await db.execute(select(Dataset).where(Dataset.id == request.dataset_id))
        if not log_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Event log not found")

    run = WorkflowRun(
        workflow_id=workflow_id,
        dataset_id=request.dataset_id,
        status=WorkflowStatus.RUNNING.value,
        started_at=datetime.utcnow(),
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    try:
        steps = json.loads(workflow.steps_json)
        results = {}
        context = {"dataset_id": request.dataset_id, **request.params}

        for step in steps:
            step_result = await workflow_service.execute_step(step["type"], step.get("params", {}), context)
            results[step["name"]] = step_result

        run.status = WorkflowStatus.COMPLETED.value
        run.result_json = json.dumps(results)
        run.completed_at = datetime.utcnow()
    except Exception as e:
        run.status = WorkflowStatus.FAILED.value
        run.error = str(e)
        run.completed_at = datetime.utcnow()
        logger.error("workflow_run_failed", run_id=run.id, error=str(e), exc_info=True)

    await db.commit()
    await db.refresh(run)

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info("workflow_run_completed", run_id=run.id, status=run.status, duration_ms=round(duration_ms, 2))

    return WorkflowRunResponse(
        id=run.id, workflow_id=run.workflow_id, dataset_id=run.dataset_id,
        status=run.status, started_at=run.started_at, completed_at=run.completed_at, error=run.error)


@router.get("/{workflow_id}/runs", response_model=list[WorkflowRunResponse])
async def list_workflow_runs(workflow_id: str, db: DBSession):
    """List runs for a workflow."""
    result = await db.execute(
        select(WorkflowRun).where(WorkflowRun.workflow_id == workflow_id).order_by(WorkflowRun.started_at.desc())
    )
    runs = result.scalars().all()
    return [WorkflowRunResponse(id=r.id, workflow_id=r.workflow_id, dataset_id=r.dataset_id,
            status=r.status, started_at=r.started_at, completed_at=r.completed_at, error=r.error) for r in runs]


@router.get("/runs/{run_id}", response_model=WorkflowRunResponse)
async def get_workflow_run(run_id: str, db: DBSession):
    """Get a specific workflow run."""
    result = await db.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return WorkflowRunResponse(id=run.id, workflow_id=run.workflow_id, dataset_id=run.dataset_id,
        status=run.status, started_at=run.started_at, completed_at=run.completed_at, error=run.error)
