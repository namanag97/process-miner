"""Workflow API Router."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.generic.workflow_service import PipelineStatus
from src.infrastructure.container import workflow_service
from src.presentation.api.routers.auth import User, require_auth
from src.domain.constants import HttpStatus, DisplayLimits, PaginationDefaults

router = APIRouter(prefix="/workflows")


class StartPipelineRequest(BaseModel):
    pipeline_name: str
    params: Optional[Dict[str, Any]] = None


class PipelineResponse(BaseModel):
    id: str
    pipeline_name: str
    status: str
    steps: Dict[str, str]
    started_at: Optional[str]
    completed_at: Optional[str]
    error: Optional[str]


class PipelineInfo(BaseModel):
    name: str
    steps: List[Dict[str, Any]]


@router.get("/pipelines", response_model=List[PipelineInfo])
async def list_pipelines(user: User = Depends(require_auth)):
    """List available workflow pipelines."""
    pipelines = workflow_service.get_available_pipelines()
    return [PipelineInfo(**p) for p in pipelines]


@router.post("/start", response_model=PipelineResponse)
async def start_pipeline(
    request: StartPipelineRequest,
    user: User = Depends(require_auth),
):
    """Start a workflow pipeline."""
    try:
        execution = await workflow_service.start_pipeline(
            pipeline_name=request.pipeline_name,
            params=request.params,
        )
        return PipelineResponse(**execution.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=HttpStatus.BAD_REQUEST, detail=str(e))


@router.get("/executions", response_model=List[PipelineResponse])
async def list_executions(
    status: Optional[str] = None,
    limit: int = 100,
    user: User = Depends(require_auth),
):
    """List pipeline executions."""
    pipeline_status = None
    if status:
        try:
            pipeline_status = PipelineStatus(status)
        except ValueError:
            raise HTTPException(status_code=HttpStatus.BAD_REQUEST, detail=f"Invalid status: {status}")

    executions = workflow_service.list_executions(status=pipeline_status, limit=limit)
    return [PipelineResponse(**e) for e in executions]


@router.get("/executions/{execution_id}", response_model=PipelineResponse)
async def get_execution(
    execution_id: UUID,
    user: User = Depends(require_auth),
):
    """Get execution status."""
    status = workflow_service.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Execution not found")
    return PipelineResponse(**status)


@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(
    execution_id: UUID,
    user: User = Depends(require_auth),
):
    """Cancel a running execution."""
    cancelled = workflow_service.cancel_execution(execution_id)
    if not cancelled:
        raise HTTPException(status_code=HttpStatus.BAD_REQUEST, detail="Cannot cancel execution")
    return {"message": "Execution cancelled"}
