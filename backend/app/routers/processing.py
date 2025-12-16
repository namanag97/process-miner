"""
Processing router - Handles process mining job execution.

This router:
1. Takes a mapping ID
2. Creates a job record via JobService
3. Dispatches a Celery task for background processing
4. Returns job ID for status polling
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import JobResponse, ProcessingRequest
from ..database import get_db
from ..services import JobService, JobNotFoundError, MappingNotFoundError
from ..core import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/processing", tags=["processing"])


async def get_job_service(db: AsyncSession = Depends(get_db)) -> JobService:
    """Dependency to get JobService instance."""
    return JobService(db)


@router.post("/mappings/{mapping_id}/process", response_model=JobResponse)
async def start_processing(
    mapping_id: str,
    request: ProcessingRequest | None = None,
    job_service: JobService = Depends(get_job_service),
):
    """
    Start processing a mapped file asynchronously.

    Creates a job record and dispatches a Celery task.
    Returns immediately with job ID for status polling.
    """
    try:
        job, celery_task_id = await job_service.create_processing_job(mapping_id)

        log.info(
            "job_queued",
            job_id=job.id,
            mapping_id=mapping_id,
            celery_task_id=celery_task_id,
        )

        return job_service.to_response(job)

    except MappingNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    job_service: JobService = Depends(get_job_service),
):
    """Get job status by ID."""
    try:
        return await job_service.get_job_status(job_id)
    except JobNotFoundError:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")


@router.delete("/jobs/{job_id}", response_model=JobResponse)
async def cancel_job(
    job_id: str,
    job_service: JobService = Depends(get_job_service),
):
    """Cancel a queued or processing job."""
    try:
        job = await job_service.cancel_job(job_id)
        return job_service.to_response(job)
    except JobNotFoundError:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
