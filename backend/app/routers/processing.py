"""
Processing router - Handles process mining job execution.

This router:
1. Takes a mapping ID
2. Creates a job record
3. Dispatches a Celery task for background processing
4. Returns job ID for status polling
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Mapping, Upload, Job, JobResponse, ProcessingRequest
from ..database import get_db
from ..services.repository import BaseRepository
from ..tasks.mining_tasks import run_mining_task
from ..core import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/processing", tags=["processing"])


async def get_mapping_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[Mapping]:
    return BaseRepository(Mapping, db)


async def get_upload_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[Upload]:
    return BaseRepository(Upload, db)


async def get_job_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[Job]:
    return BaseRepository(Job, db)


@router.post("/mappings/{mapping_id}/process", response_model=JobResponse)
async def start_processing(
    mapping_id: str, 
    request: ProcessingRequest | None = None,
    db: AsyncSession = Depends(get_db),
    mapping_repo: BaseRepository[Mapping] = Depends(get_mapping_repo),
    upload_repo: BaseRepository[Upload] = Depends(get_upload_repo),
):
    """
    Start processing a mapped file asynchronously.
    
    Creates a job record and dispatches a Celery task.
    Returns immediately with job ID for status polling.
    """
    # Verify resources exist
    mapping = await mapping_repo.get_or_404(mapping_id)
    await upload_repo.get_or_404(mapping.upload_id)
    
    # Create job record
    new_job = Job(
        mapping_id=mapping_id,
        status="queued",
        progress=0,
        progress_message="Queued for processing...",
        created_at=datetime.utcnow(),
    )
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)
    
    # Dispatch Celery task
    task = run_mining_task.delay(new_job.id, mapping_id)
    
    log.info(
        "job_queued",
        job_id=new_job.id,
        mapping_id=mapping_id,
        celery_task_id=task.id,
    )
    
    return JobResponse(
        job_id=new_job.id,
        status="queued",
        progress=0,
        progress_message="Queued for processing...",
        dataset_id=None,
        error=None,
        created_at=new_job.created_at,
        completed_at=None,
    )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    job_repo: BaseRepository[Job] = Depends(get_job_repo),
):
    """Get job status by ID."""
    job = await job_repo.get_or_404(job_id)
    
    return JobResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        progress_message=job.progress_message,
        dataset_id=job.dataset_id,
        error=job.error,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )

