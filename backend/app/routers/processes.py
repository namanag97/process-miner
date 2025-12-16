"""
Processes router - Manage business processes.

Processes group uploads by business function (e.g., Order-to-Cash).
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models import (
    Process,
    ProcessCreate,
    ProcessUpdate,
    ProcessResponse,
    ProcessWithStats,
    Upload,
    Dataset,
    Mapping,
    InsightSummary,
)
from ..database import get_db
from ..services import audit_service, insight_service
from ..core import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/processes", tags=["processes"])


@router.post("", response_model=ProcessResponse)
async def create_process(
    process_data: ProcessCreate,
    org_id: str = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
):
    """Create a new process within an organization."""
    process = Process(
        org_id=org_id,
        name=process_data.name,
        description=process_data.description,
        icon=process_data.icon,
        color=process_data.color,
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    db.add(process)
    await db.commit()
    await db.refresh(process)
    
    # Log action
    await audit_service.log_action(
        db=db,
        entity_type="process",
        entity_id=process.id,
        action="create",
        details={"name": process.name, "org_id": org_id},
    )
    
    log.info("process_created", process_id=process.id, name=process.name)
    
    return ProcessResponse(
        id=process.id,
        org_id=process.org_id,
        name=process.name,
        description=process.description,
        status=process.status,
        icon=process.icon,
        color=process.color,
        created_at=process.created_at,
        updated_at=process.updated_at,
        upload_count=0,
        dataset_count=0,
    )


@router.get("", response_model=list[ProcessResponse])
async def list_processes(
    org_id: Optional[str] = Query(None, description="Filter by organization"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
):
    """List processes with optional filtering."""
    query = select(Process).order_by(Process.created_at.desc())
    
    if org_id:
        query = query.where(Process.org_id == org_id)
    if status:
        query = query.where(Process.status == status)
    
    result = await db.execute(query)
    processes = result.scalars().all()
    
    responses = []
    for process in processes:
        # Count uploads
        upload_count_result = await db.execute(
            select(func.count()).select_from(Upload).where(Upload.process_id == process.id)
        )
        upload_count = upload_count_result.scalar() or 0
        
        # Count datasets (through uploads -> mappings -> datasets)
        dataset_count = 0  # Simplified for now
        
        responses.append(ProcessResponse(
            id=process.id,
            org_id=process.org_id,
            name=process.name,
            description=process.description,
            status=process.status,
            icon=process.icon,
            color=process.color,
            created_at=process.created_at,
            updated_at=process.updated_at,
            upload_count=upload_count,
            dataset_count=dataset_count,
        ))
    
    return responses


@router.get("/{process_id}", response_model=ProcessWithStats)
async def get_process(
    process_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get process with aggregated statistics."""
    result = await db.execute(
        select(Process).where(Process.id == process_id)
    )
    process = result.scalar_one_or_none()
    
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    
    # Count uploads
    upload_count_result = await db.execute(
        select(func.count()).select_from(Upload).where(Upload.process_id == process.id)
    )
    upload_count = upload_count_result.scalar() or 0
    
    # Get aggregated stats from datasets
    total_cases = 0
    total_events = 0
    avg_duration = 0.0
    last_analysis_at = None
    
    # Find datasets through uploads -> mappings
    uploads_result = await db.execute(
        select(Upload).where(Upload.process_id == process.id)
    )
    uploads = uploads_result.scalars().all()
    
    for upload in uploads:
        mappings_result = await db.execute(
            select(Mapping).where(Mapping.upload_id == upload.id)
        )
        for mapping in mappings_result.scalars():
            datasets_result = await db.execute(
                select(Dataset).where(Dataset.mapping_id == mapping.id)
            )
            for dataset in datasets_result.scalars():
                if dataset.stats_json:
                    import json
                    stats = json.loads(dataset.stats_json)
                    total_cases += stats.get("total_cases", 0)
                    total_events += stats.get("total_events", 0)
                    if not last_analysis_at or dataset.created_at > last_analysis_at:
                        last_analysis_at = dataset.created_at
    
    return ProcessWithStats(
        id=process.id,
        org_id=process.org_id,
        name=process.name,
        description=process.description,
        status=process.status,
        icon=process.icon,
        color=process.color,
        created_at=process.created_at,
        updated_at=process.updated_at,
        upload_count=upload_count,
        dataset_count=0,
        total_cases=total_cases,
        total_events=total_events,
        avg_case_duration_ms=avg_duration,
        last_analysis_at=last_analysis_at,
    )


@router.patch("/{process_id}", response_model=ProcessResponse)
async def update_process(
    process_id: str,
    update_data: ProcessUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a process."""
    result = await db.execute(
        select(Process).where(Process.id == process_id)
    )
    process = result.scalar_one_or_none()
    
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    
    # Apply updates
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(process, key, value)
    process.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(process)
    
    # Log action
    await audit_service.log_action(
        db=db,
        entity_type="process",
        entity_id=process.id,
        action="update",
        details=update_dict,
    )
    
    return ProcessResponse(
        id=process.id,
        org_id=process.org_id,
        name=process.name,
        description=process.description,
        status=process.status,
        icon=process.icon,
        color=process.color,
        created_at=process.created_at,
        updated_at=process.updated_at,
        upload_count=0,
        dataset_count=0,
    )


@router.delete("/{process_id}")
async def delete_process(
    process_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a process and all its uploads."""
    result = await db.execute(
        select(Process).where(Process.id == process_id)
    )
    process = result.scalar_one_or_none()
    
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    
    # Log before delete
    await audit_service.log_action(
        db=db,
        entity_type="process",
        entity_id=process.id,
        action="delete",
        details={"name": process.name},
    )
    
    await db.delete(process)
    await db.commit()
    
    log.info("process_deleted", process_id=process_id)
    
    return {"message": "Process deleted", "process_id": process_id}


@router.get("/{process_id}/insights", response_model=InsightSummary)
async def get_process_insights(
    process_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated insights for a process."""
    # First verify process exists
    result = await db.execute(
        select(Process).where(Process.id == process_id)
    )
    process = result.scalar_one_or_none()
    
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    
    # Aggregate insights across all datasets in this process
    total_summary = InsightSummary(
        total_insights=0,
        by_type={},
        by_severity={},
        critical_count=0,
        unacknowledged_count=0,
    )
    
    # Get all datasets for this process
    uploads_result = await db.execute(
        select(Upload).where(Upload.process_id == process_id)
    )
    
    for upload in uploads_result.scalars():
        mappings_result = await db.execute(
            select(Mapping).where(Mapping.upload_id == upload.id)
        )
        for mapping in mappings_result.scalars():
            datasets_result = await db.execute(
                select(Dataset).where(Dataset.mapping_id == mapping.id)
            )
            for dataset in datasets_result.scalars():
                summary = await insight_service.get_insight_summary(db, dataset.id)
                total_summary.total_insights += summary.total_insights
                total_summary.critical_count += summary.critical_count
                total_summary.unacknowledged_count += summary.unacknowledged_count
                
                for t, c in summary.by_type.items():
                    total_summary.by_type[t] = total_summary.by_type.get(t, 0) + c
                for s, c in summary.by_severity.items():
                    total_summary.by_severity[s] = total_summary.by_severity.get(s, 0) + c
    
    return total_summary
