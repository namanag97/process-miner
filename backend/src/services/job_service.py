"""Job Service for unified async job tracking.

Provides business logic layer for:
- Creating and managing async jobs
- Progress tracking with stage updates
- Publishing events to Redis for SSE
- Job lifecycle management
"""

import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import EntityType, JobStatus, JobType
from src.core.logging_config import get_logger
from src.models.orm import AsyncJob
from src.models.repositories import SQLAlchemyAsyncJobRepository

logger = get_logger(__name__)


class JobService:
    """Service for managing async jobs with unified tracking."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repo = SQLAlchemyAsyncJobRepository(session)

    # =========================================================================
    # Create Jobs
    # =========================================================================

    async def create(
        self,
        job_type: JobType,
        user_id: str,
        entity_type: EntityType | None = None,
        entity_id: str | None = None,
        parameters: dict | None = None,
        parent_job_id: str | None = None,
    ) -> AsyncJob:
        """Create a new job and return it.

        Args:
            job_type: Type of job (INGESTION, DISCOVERY, etc.)
            user_id: ID of user who initiated the job
            entity_type: Type of entity this job creates/affects
            entity_id: ID of existing entity (if applicable)
            parameters: Job parameters as dict
            parent_job_id: Parent job ID for chained jobs

        Returns:
            Created AsyncJob instance
        """
        job = AsyncJob(
            id=str(uuid4()),
            job_type=job_type.value,
            user_id=user_id,
            status=JobStatus.QUEUED.value,
            progress=0,
            entity_type=entity_type.value if entity_type else None,
            entity_id=entity_id,
            parent_job_id=parent_job_id,
            parameters_json=json.dumps(parameters) if parameters else None,
            created_at=datetime.utcnow(),
        )

        await self._repo.save(job)
        logger.info(f"Created job {job.id} of type {job_type.value} for user {user_id}")

        # TODO: Publish JOB_CREATED event to Redis for SSE

        return job

    async def set_task_id(self, job_id: str, task_id: str) -> bool:
        """Set the Celery task ID for a job.

        Called after queuing a Celery task.
        """
        job = await self._repo.get_by_id(job_id)
        if not job:
            return False

        job.task_id = task_id
        await self._session.flush()
        return True

    # =========================================================================
    # Progress Tracking
    # =========================================================================

    async def start(self, job_id: str) -> bool:
        """Mark job as started (RUNNING state).

        Called at the beginning of a Celery task.
        """
        job = await self._repo.get_by_id(job_id)
        if not job:
            return False

        job.status = JobStatus.RUNNING.value
        job.started_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        await self._session.flush()

        logger.info(f"Job {job_id} started")

        # TODO: Publish JOB_STARTED event to Redis for SSE

        return True

    async def update_progress(
        self,
        job_id: str,
        progress: int,
        stage: str | None = None,
    ) -> bool:
        """Update job progress and stage.

        Args:
            job_id: Job ID
            progress: Progress percentage (0-100)
            stage: Current stage name (e.g., "parsing", "computing_variants")

        Returns:
            True if updated successfully
        """
        success = await self._repo.update_progress(job_id, progress, stage)

        if success:
            logger.debug(f"Job {job_id} progress: {progress}% ({stage})")
            # TODO: Publish JOB_PROGRESS event to Redis for SSE

        return success

    # =========================================================================
    # Completion
    # =========================================================================

    async def complete(
        self,
        job_id: str,
        result: dict | None = None,
        entity_id: str | None = None,
    ) -> bool:
        """Mark job as completed.

        Args:
            job_id: Job ID
            result: Result payload
            entity_id: ID of created entity (if applicable)

        Returns:
            True if updated successfully
        """
        success = await self._repo.complete(job_id, result, entity_id)

        if success:
            logger.info(f"Job {job_id} completed successfully")
            # TODO: Publish JOB_COMPLETED event to Redis for SSE

        return success

    async def fail(
        self,
        job_id: str,
        error: str,
        error_details: dict | None = None,
    ) -> bool:
        """Mark job as failed.

        Args:
            job_id: Job ID
            error: Error message
            error_details: Additional error details

        Returns:
            True if updated successfully
        """
        error_json = json.dumps({"message": error, "details": error_details or {}})

        success = await self._repo.fail(job_id, error_json)

        if success:
            logger.error(f"Job {job_id} failed: {error}")
            # TODO: Publish JOB_FAILED event to Redis for SSE

        return success

    async def cancel(self, job_id: str) -> bool:
        """Cancel a job if it's cancellable (QUEUED or RUNNING).

        Returns:
            True if cancelled, False if not cancellable
        """
        job = await self._repo.get_by_id(job_id)
        if not job:
            return False

        if job.status not in [JobStatus.QUEUED.value, JobStatus.RUNNING.value]:
            return False

        job.status = JobStatus.CANCELLED.value
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        await self._session.flush()

        logger.info(f"Job {job_id} cancelled")

        # TODO: Cancel Celery task if running
        # TODO: Publish JOB_CANCELLED event to Redis for SSE

        return True

    # =========================================================================
    # Queries
    # =========================================================================

    async def get(self, job_id: str) -> AsyncJob | None:
        """Get a job by ID."""
        return await self._repo.get_by_id(job_id)

    async def get_by_task_id(self, task_id: str) -> AsyncJob | None:
        """Get a job by Celery task ID."""
        return await self._repo.get_by_task_id(task_id)

    async def list_for_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        job_type: str | None = None,
        status: str | None = None,
        entity_id: str | None = None,
    ) -> tuple[list[AsyncJob], int]:
        """List jobs for a user with optional filtering."""
        return await self._repo.list_by_user(
            user_id=user_id,
            page=page,
            page_size=page_size,
            job_type=job_type,
            status=status,
            entity_id=entity_id,
        )

    async def list_for_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> list[AsyncJob]:
        """List all jobs for a specific entity."""
        return await self._repo.list_by_entity(entity_type, entity_id)
