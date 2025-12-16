"""
Job Service - Manages job lifecycle for process mining tasks.

Centralizes job creation, status tracking, and Celery task dispatch.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import Job, JobResponse, Mapping, Upload
from ..core import get_logger

logger = get_logger(__name__)


class JobServiceError(Exception):
    """Base exception for job service errors."""

    def __init__(self, message: str, job_id: Optional[str] = None):
        self.message = message
        self.job_id = job_id
        super().__init__(message)


class JobNotFoundError(JobServiceError):
    """Raised when a job is not found."""
    pass


class MappingNotFoundError(JobServiceError):
    """Raised when a mapping is not found."""
    pass


class JobService:
    """
    Service for managing process mining jobs.

    Handles:
    - Job creation and validation
    - Celery task dispatch
    - Job status retrieval
    - Job lifecycle management
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_processing_job(self, mapping_id: str) -> tuple[Job, str]:
        """
        Create a new processing job and dispatch it to Celery.

        Args:
            mapping_id: The mapping configuration ID

        Returns:
            Tuple of (Job, celery_task_id)

        Raises:
            MappingNotFoundError: If mapping doesn't exist
        """
        # Verify mapping exists and get upload
        result = await self.db.execute(
            select(Mapping).where(Mapping.id == mapping_id)
        )
        mapping = result.scalar_one_or_none()

        if not mapping:
            raise MappingNotFoundError(f"Mapping {mapping_id} not found")

        # Verify upload exists
        result = await self.db.execute(
            select(Upload).where(Upload.id == mapping.upload_id)
        )
        upload = result.scalar_one_or_none()

        if not upload:
            raise MappingNotFoundError(f"Upload for mapping {mapping_id} not found")

        # Create job record
        new_job = Job(
            mapping_id=mapping_id,
            status="queued",
            progress=0,
            progress_message="Queued for processing...",
            created_at=datetime.utcnow(),
        )
        self.db.add(new_job)
        await self.db.commit()
        await self.db.refresh(new_job)

        # Dispatch Celery task (import here to avoid circular import)
        from ..tasks.mining_tasks import run_mining_task
        from ..celery_app import celery_app
        
        # DEBUG: Log broker URL being used
        logger.info(
            "celery_dispatch_starting",
            job_id=new_job.id,
            mapping_id=mapping_id,
            broker_url=celery_app.conf.broker_url,
        )
        
        try:
            task = run_mining_task.delay(new_job.id, mapping_id)
            logger.info(
                "celery_dispatch_success",
                job_id=new_job.id,
                celery_task_id=task.id,
            )
        except Exception as e:
            logger.error(
                "celery_dispatch_failed",
                job_id=new_job.id,
                error=str(e),
                broker_url=celery_app.conf.broker_url,
            )
            # Update job status to failed
            new_job.status = "failed"
            new_job.error = f"Failed to queue task: {str(e)}"
            await self.db.commit()
            raise

        logger.info(
            "job_created",
            job_id=new_job.id,
            mapping_id=mapping_id,
            celery_task_id=task.id,
        )

        return new_job, task.id

    async def get_job(self, job_id: str) -> Job:
        """
        Get a job by ID.

        Args:
            job_id: The job ID

        Returns:
            Job instance

        Raises:
            JobNotFoundError: If job doesn't exist
        """
        result = await self.db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()

        if not job:
            raise JobNotFoundError(f"Job {job_id} not found", job_id=job_id)

        return job

    async def get_job_status(self, job_id: str) -> JobResponse:
        """
        Get job status as API response.

        Args:
            job_id: The job ID

        Returns:
            JobResponse for API

        Raises:
            JobNotFoundError: If job doesn't exist
        """
        job = await self.get_job(job_id)

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

    async def get_jobs_by_mapping(self, mapping_id: str) -> list[Job]:
        """
        Get all jobs for a mapping.

        Args:
            mapping_id: The mapping ID

        Returns:
            List of Job instances
        """
        result = await self.db.execute(
            select(Job)
            .where(Job.mapping_id == mapping_id)
            .order_by(Job.created_at.desc())
        )
        return list(result.scalars().all())

    async def cancel_job(self, job_id: str) -> Job:
        """
        Cancel a queued or processing job.

        Args:
            job_id: The job ID

        Returns:
            Updated Job instance

        Raises:
            JobNotFoundError: If job doesn't exist
            JobServiceError: If job cannot be cancelled
        """
        job = await self.get_job(job_id)

        if job.status not in ("queued", "processing"):
            raise JobServiceError(
                f"Cannot cancel job in '{job.status}' status",
                job_id=job_id
            )

        job.status = "failed"
        job.error = "Cancelled by user"
        job.completed_at = datetime.utcnow()
        await self.db.commit()

        logger.info("job_cancelled", job_id=job_id)
        return job

    def to_response(self, job: Job) -> JobResponse:
        """Convert Job model to API response."""
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


async def get_job_service(db: AsyncSession) -> JobService:
    """Dependency injection helper for JobService."""
    return JobService(db)
