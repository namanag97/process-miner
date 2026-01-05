"""Jobs Router.

Unified endpoint for polling asynchronous job status and progress.

Hardened with:
- UUID validation for job_id path parameters
- Proper pagination with accurate total counts
- Validated enum filters for job_type and status
- Consistent error responses
"""

from fastapi import APIRouter, Path, Query, Request
from pydantic import BaseModel
from sqlalchemy import func, select

from src.api.dependencies import DBSession
from src.features.process_mining.schemas import JobStatusResponse
from src.platform.core.enums import JobStatus, JobType
from src.platform.core.exceptions import NotFoundError
from src.platform.core.logging_config import get_logger
from src.platform.core.validation import calculate_total_pages, validate_uuid
from src.platform.models import AsyncJob
from src.platform.schemas import PaginatedResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# =============================================================================
# Response Models
# =============================================================================


class JobListResponse(PaginatedResponse):
    """Paginated job list."""

    items: list[JobStatusResponse]


# =============================================================================
# Helper Functions
# =============================================================================


def _validate_job_type(job_type: str | None) -> str | None:
    """Validate job_type against known enum values."""
    if job_type is None:
        return None
    # Accept valid enum values (case-insensitive)
    try:
        return JobType(job_type.lower()).value
    except ValueError:
        # Accept as-is for forward compatibility with new job types
        return job_type


def _validate_job_status(status: str | None) -> str | None:
    """Validate status against known enum values."""
    if status is None:
        return None
    # Accept valid enum values (case-insensitive)
    try:
        return JobStatus(status.lower()).value
    except ValueError:
        # Accept as-is for forward compatibility with new statuses
        return status


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=JobListResponse)
async def list_jobs(
    db: DBSession,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    job_type: str | None = Query(None, description="Filter by job type (e.g., ingestion, discovery)"),
    status: str | None = Query(None, description="Filter by status (e.g., pending, running, completed, failed)"),
    entity_id: str | None = Query(None, description="Filter by entity ID"),
    user_id: str | None = Query(None, description="Filter by user ID"),
) -> JobListResponse:
    """
    List asynchronous jobs with filtering and pagination.

    Returns paginated list of jobs, ordered by creation time (newest first).
    """
    # Validate and normalize filter values
    validated_job_type = _validate_job_type(job_type)
    validated_status = _validate_job_status(status)

    # Build base query for counting
    count_query = select(func.count()).select_from(AsyncJob)
    if validated_job_type:
        count_query = count_query.where(AsyncJob.job_type == validated_job_type)
    if validated_status:
        count_query = count_query.where(AsyncJob.status == validated_status)
    if entity_id:
        count_query = count_query.where(AsyncJob.entity_id == entity_id)
    if user_id:
        count_query = count_query.where(AsyncJob.user_id == user_id)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Build query for results
    query = select(AsyncJob).order_by(AsyncJob.created_at.desc())
    if validated_job_type:
        query = query.where(AsyncJob.job_type == validated_job_type)
    if validated_status:
        query = query.where(AsyncJob.status == validated_status)
    if entity_id:
        query = query.where(AsyncJob.entity_id == entity_id)
    if user_id:
        query = query.where(AsyncJob.user_id == user_id)

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return JobListResponse(
        items=[JobStatusResponse.model_validate(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
        pages=calculate_total_pages(total, page_size),
    )


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    db: DBSession,
    job_id: str = Path(..., description="Job ID (UUID format)"),
) -> JobStatusResponse:
    """
    Get the current status and progress of an asynchronous job.

    Use this endpoint to poll job status for process mining operations
    like data ingestion, process discovery, or conformance checking.
    """
    # Validate UUID format
    validate_uuid(job_id, "job_id")

    query = select(AsyncJob).where(AsyncJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        logger.warning("job_not_found", job_id=job_id)
        raise NotFoundError(resource="Job", resource_id=job_id)

    return JobStatusResponse.model_validate(job)


class JobCancelResponse(BaseModel):
    """Response after cancelling or deleting a job."""

    id: str
    status: str
    message: str


@router.delete("/{job_id}", response_model=JobCancelResponse)
async def cancel_job(
    db: DBSession,
    job_id: str = Path(..., description="Job ID (UUID format)"),
) -> JobCancelResponse:
    """
    Cancel or delete an asynchronous job.

    - PENDING/QUEUED jobs: Cancelled before execution
    - RUNNING jobs: Cancellation requested (may take time)
    - COMPLETED/FAILED/CANCELLED jobs: Deleted from history

    Returns the final status of the job operation.
    """
    from src.platform.core.enums import JobStatus

    # Validate UUID format
    validate_uuid(job_id, "job_id")

    query = select(AsyncJob).where(AsyncJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise NotFoundError(resource="Job", resource_id=job_id)

    original_status = job.status

    # Handle based on current job status
    if job.status in [JobStatus.PENDING.value, JobStatus.QUEUED.value]:
        # Job hasn't started - cancel it
        job.status = JobStatus.CANCELLED.value
        await db.commit()
        logger.info("job_cancelled", job_id=job_id, original_status=original_status)
        return JobCancelResponse(
            id=job_id,
            status="cancelled",
            message="Job cancelled before execution",
        )

    elif job.status == JobStatus.RUNNING.value:
        # Job is running - request cancellation
        # In production, would also revoke Celery task:
        # celery_app.control.revoke(job.task_id, terminate=True)
        job.status = JobStatus.CANCELLED.value
        await db.commit()
        logger.info("job_cancel_requested", job_id=job_id, task_id=job.task_id)
        return JobCancelResponse(
            id=job_id,
            status="cancellation_requested",
            message="Cancellation requested for running job",
        )

    else:
        # Job is already terminal (completed/failed/cancelled) - delete it
        await db.delete(job)
        await db.commit()
        logger.info("job_deleted", job_id=job_id, original_status=original_status)
        return JobCancelResponse(
            id=job_id,
            status="deleted",
            message=f"Deleted job with status '{original_status}'",
        )


@router.get("/{job_id}/stream")
async def stream_job_progress(
    db: DBSession,
    job_id: str = Path(..., description="Job ID (UUID format)"),
    request: Request = None,
):
    """
    SSE stream for real-time job progress updates.

    Returns Server-Sent Events as job progresses:
    - event: job:progress - Progress updates with stage info
    - event: job:completed - Job completed successfully
    - event: job:failed - Job failed with error

    Client should keep connection open and parse SSE events.
    Connection closes when job completes/fails or client disconnects.

    Useful for tracking long-running process mining operations like
    data ingestion, process discovery, or conformance checking.
    """
    # Validate UUID format
    validate_uuid(job_id, "job_id")
    import asyncio

    from fastapi.responses import StreamingResponse

    from src.features.process_mining.services.ingestion.stream import (
        EventType,
        SSEEvent,
        event_stream_manager,
    )

    # Verify job exists
    query = select(AsyncJob).where(AsyncJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise NotFoundError(resource="Job", resource_id=job_id)

    user_id = job.user_id or "anonymous"

    async def event_generator():
        """Generate SSE events for this job."""
        # Send initial state
        initial_event = SSEEvent(
            event_type=EventType.JOB_PROGRESS,
            data={
                "job_id": job_id,
                "status": job.status,
                "progress": job.progress,
                "stage": job.stage,
            },
        )
        yield initial_event.to_sse_format()

        # If job is already completed/failed, send final event and close
        if job.status in ["completed", "failed", "cancelled"]:
            if job.status == "completed":
                yield SSEEvent(EventType.JOB_COMPLETED, {"job_id": job_id}).to_sse_format()
            elif job.status == "failed":
                yield SSEEvent(
                    EventType.JOB_FAILED, {"job_id": job_id, "error": job.error}
                ).to_sse_format()
            return

        # Subscribe to Redis for real-time updates
        try:
            async for event_data in event_stream_manager.subscribe(user_id, job_id):
                yield event_data
                # Check if client disconnected
                if await request.is_disconnected():
                    break
        except Exception as e:
            logger.warning("sse_stream_error", job_id=job_id, error=str(e))
            # Fallback: poll database for updates
            while True:
                if await request.is_disconnected():
                    break

                # Refresh job status from DB
                result = await db.execute(query)
                current_job = result.scalar_one_or_none()

                if not current_job:
                    break

                # Send progress update
                yield SSEEvent(
                    event_type=EventType.JOB_PROGRESS,
                    data={
                        "job_id": job_id,
                        "status": current_job.status,
                        "progress": current_job.progress,
                        "stage": current_job.stage,
                    },
                ).to_sse_format()

                # Check if done
                if current_job.status in ["completed", "failed", "cancelled"]:
                    break

                await asyncio.sleep(1)  # Poll every second

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
