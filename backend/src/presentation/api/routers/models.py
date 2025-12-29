"""Process Models API Router."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.core.discovery_service import discovery_service
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import ProcessModelRepository
from src.presentation.api.routers.auth import User, require_auth
from src.domain.constants import HttpStatus, DisplayLimits, PaginationDefaults

router = APIRouter(prefix="/models")


class ProcessModelResponse(BaseModel):
    id: str
    name: str
    format: str
    miner_type: Optional[str]
    source_log_id: Optional[str]
    created_at: str


class ModelUpdateRequest(BaseModel):
    """Request body for updating process model metadata."""

    name: Optional[str] = None
    description: Optional[str] = None


@router.get("/", response_model=List[ProcessModelResponse])
async def list_models(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    List all process models.
    """
    repo = ProcessModelRepository(session)
    models = await repo.list_all(limit=limit, offset=offset)

    return [
        ProcessModelResponse(
            id=str(m.id),
            name=m.name,
            format=m.format.value,
            miner_type=m.miner_type.value if m.miner_type else None,
            source_log_id=str(m.source_log_id) if m.source_log_id else None,
            created_at=m.created_at.isoformat(),
        )
        for m in models
    ]


@router.get("/{model_id}", response_model=ProcessModelResponse)
async def get_model(
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get process model details.
    """
    repo = ProcessModelRepository(session)
    model = await repo.get_by_id(model_id)

    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    return ProcessModelResponse(
        id=str(model.id),
        name=model.name,
        format=model.format.value,
        miner_type=model.miner_type.value if model.miner_type else None,
        source_log_id=str(model.source_log_id) if model.source_log_id else None,
        created_at=model.created_at.isoformat(),
    )


@router.patch("/{model_id}", response_model=ProcessModelResponse)
async def update_model(
    model_id: UUID,
    update: ModelUpdateRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Update process model metadata.

    - **name**: New name for the process model
    - **description**: New description for the process model
    """
    repo = ProcessModelRepository(session)
    model = await repo.get_by_id(model_id)

    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    # Update fields
    if update.name is not None:
        model.name = update.name
    if update.description is not None:
        model.metadata["description"] = update.description

    # Save changes
    await repo.save(model)

    return ProcessModelResponse(
        id=str(model.id),
        name=model.name,
        format=model.format.value,
        miner_type=model.miner_type.value if model.miner_type else None,
        source_log_id=str(model.source_log_id) if model.source_log_id else None,
        created_at=model.created_at.isoformat(),
    )


@router.get("/{model_id}/visualize")
async def visualize_model(
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get visualization of a process model as SVG.
    """
    repo = ProcessModelRepository(session)
    model = await repo.get_by_id(model_id)

    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        svg_bytes = discovery_service.visualize_model(model)

        return Response(
            content=svg_bytes,
            media_type="image/svg+xml",
            headers={"Content-Disposition": f"inline; filename=model_{model_id}.svg"},
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Visualization failed: {str(e)}")


@router.delete("/{model_id}")
async def delete_model(
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Delete a process model.
    """
    repo = ProcessModelRepository(session)
    deleted = await repo.delete(model_id)

    if not deleted:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    return {"message": "Process model deleted successfully"}
