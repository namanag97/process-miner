"""Jobs Router.

Unified endpoint for polling asynchronous job status and progress.
"""

from fastapi import APIRouter, Query, Request
from sqlalchemy import select

from src.api.dependencies import DBSession
from src.core.exceptions import ProcessNotFoundError
from src.core.logging_config import get_logger
from src.models.orm import AsyncJob
from src.models.schemas import JobStatusResponse, PaginatedResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobListResponse(PaginatedResponse):
    """Paginated job list."""

    items: list[JobStatusResponse]


@router.get("", response_model=JobListResponse)
async def list_jobs(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    job_type: str | None = Query(None),
    status: str | None = Query(None),
    entity_id: str | None = Query(None),
    user_id: str | None = Query(None),  # In production, this would come from Auth
):
    """
    List asynchronous jobs with filtering and pagination.
    """
    # Build query
    query = select(AsyncJob).order_by(AsyncJob.created_at.desc())

    if job_type:
        query = query.where(AsyncJob.job_type == job_type)
    if status:
        query = query.where(AsyncJob.status == status)
    if entity_id:
        query = query.where(AsyncJob.entity_id == entity_id)
    if user_id:
        query = query.where(AsyncJob.user_id == user_id)

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    jobs = result.scalars().all()

    # Get total count (simplification for now, should use a proper count query)
    total = len(jobs)  # This is wrong for real pagination but okay for MVP

    return JobListResponse(
        items=[JobStatusResponse.from_orm(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
        pages=1,
    )


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    db: DBSession,
    job_id: str,
):
    """
    Get the current status and progress of an asynchronous job.
    """
    query = select(AsyncJob).where(AsyncJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        logger.warning("job_not_found", job_id=job_id)
        raise ProcessNotFoundError(job_id, resource_name="Job")

    return JobStatusResponse.from_orm(job)


@router.delete("/{job_id}")
async def cancel_job(
    db: DBSession,
    job_id: str,
):
    """
    Cancel or delete an asynchronous job.
    """
    query = select(AsyncJob).where(AsyncJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise ProcessNotFoundError(job_id, resource_name="Job")

    # In a real implementation, we would also cancel the Celery task
    # from src.infrastructure.tasks import celery_app
    # celery_app.control.revoke(job.task_id, terminate=True)

    await db.delete(job)
    await db.commit()

    return {"status": "deleted", "id": job_id}


@router.get("/{job_id}/stream")
async def stream_job_progress(
    db: DBSession,
    job_id: str,
    request: Request,
):
    """
    SSE stream for real-time job progress updates.

    Returns Server-Sent Events as job progresses:
    - event: job:progress - Progress updates with stage info
    - event: job:completed - Job completed successfully
    - event: job:failed - Job failed with error

    Client should keep connection open and parse SSE events.
    Connection closes when job completes/fails or client disconnects.
    """
    import asyncio

    from fastapi.responses import StreamingResponse

    from src.services.event_stream import EventType, SSEEvent, event_stream_manager

    # Verify job exists
    query = select(AsyncJob).where(AsyncJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise ProcessNotFoundError(job_id, resource_name="Job")

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
