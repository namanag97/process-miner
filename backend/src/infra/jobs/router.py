"""Jobs Router.

Unified endpoint for tracking asynchronous job status and progress.

## Business Context
Many process mining operations run asynchronously:
- Dataset ingestion (CSV/XES parsing into events and cases)
- Process discovery (mining algorithms like Alpha, Inductive, Heuristic)
- Conformance checking (token replay, alignments)
- Predictions training (ML model training)

Jobs have a lifecycle: `pending → queued → running → completed/failed/cancelled`

## Testing Instructions

### Workflow
1. Trigger an async operation (e.g., `POST /api/v1/datasets/{id}/ingest`)
2. Get job_id from the response
3. Poll `GET /api/v1/jobs/{job_id}` until status is `completed` or `failed`
4. Or use SSE streaming: `GET /api/v1/jobs/{job_id}/stream`

### Endpoints
- **List Jobs**: `GET /api/v1/jobs` - Paginated, filterable by job_type/status
- **Get Job**: `GET /api/v1/jobs/{job_id}` - Current status and progress
- **Cancel Job**: `DELETE /api/v1/jobs/{job_id}` - Cancel running or delete completed
- **Stream Progress**: `GET /api/v1/jobs/{job_id}/stream` - SSE real-time updates
- **Get Logs**: `GET /api/v1/jobs/{job_id}/logs` - Execution history

### Job Types
`ingestion`, `discovery`, `conformance`, `training`, `export`, `validation`

### Common Errors
- **404**: Job not found (may have expired or been deleted)
- **422**: Invalid UUID format for job_id
"""

from fastapi import APIRouter, Path, Query, Request
from sqlalchemy import func, select

from src.api.dependencies import ReadDBSession
from src.features.process_mining.schemas import JobStatusResponse
from src.infra.core.enums import JobStatus, JobType
from src.infra.core.exceptions import NotFoundError
from src.infra.core.logging_config import get_logger
from src.infra.core.validation import calculate_total_pages, validate_uuid
from src.infra.jobs.schemas import (
    JobCancelResponse,
    JobListResponse,
    JobLogEntry,
    JobLogsResponse,
)
from src.infra.models import AsyncJob

logger = get_logger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# =============================================================================
# Helper Functions
# =============================================================================


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
    db: ReadDBSession,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    job_type: str | None = Query(
        None, description="Filter by job type (e.g., ingestion, discovery)"
    ),
    status: str | None = Query(
        None, description="Filter by status (e.g., pending, running, completed, failed)"
    ),
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
    db: ReadDBSession,
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


@router.delete("/{job_id}", response_model=JobCancelResponse)
async def cancel_job(
    db: ReadDBSession,
    job_id: str = Path(..., description="Job ID (UUID format)"),
) -> JobCancelResponse:
    """
    Cancel or delete an asynchronous job.

    - PENDING/QUEUED jobs: Cancelled before execution
    - RUNNING jobs: Cancellation requested (may take time)
    - COMPLETED/FAILED/CANCELLED jobs: Deleted from history

    Returns the final status of the job operation.
    """
    from src.infra.core.enums import JobStatus

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

    if job.status == JobStatus.RUNNING.value:
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
    db: ReadDBSession,
    request: Request,
    job_id: str = Path(..., description="Job ID (UUID format)"),
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

    from src.infra.jobs.stream import (
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


# =============================================================================
# Job Logs Endpoint (per API spec)
# =============================================================================


@router.get("/{job_id}/logs", response_model=JobLogsResponse)
async def get_job_logs(
    db: ReadDBSession,
    job_id: str = Path(..., description="Job ID (UUID format)"),
    limit: int = Query(100, ge=1, le=1000, description="Max log entries to return"),
    level: str | None = Query(None, description="Filter by log level (info, warn, error)"),
) -> JobLogsResponse:
    """
    Get execution logs for a job.

    Returns structured log entries for the job's execution.
    Useful for debugging failed jobs or understanding execution flow.
    """
    # Validate UUID format
    validate_uuid(job_id, "job_id")

    # Verify job exists
    query = select(AsyncJob).where(AsyncJob.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise NotFoundError(resource="Job", resource_id=job_id)

    # Note: In production, logs would be stored in a dedicated table or log service
    # For now, return synthetic logs based on job state
    logs = []

    # Add job creation log
    logs.append(
        JobLogEntry(
            timestamp=job.created_at.isoformat() if job.created_at else "",
            level="info",
            message=f"Job {job.job_type} created",
            details={"entity_type": job.entity_type, "entity_id": job.entity_id},
        )
    )

    # Add started log if running or completed
    if job.started_at:
        logs.append(
            JobLogEntry(
                timestamp=job.started_at.isoformat(),
                level="info",
                message="Job execution started",
            )
        )

    # Add stage info if available
    if job.stage:
        logs.append(
            JobLogEntry(
                timestamp=job.updated_at.isoformat() if job.updated_at else "",
                level="info",
                message=f"Processing stage: {job.stage}",
                details={"progress": job.progress},
            )
        )

    # Add completion/error logs
    if job.status == "completed":
        logs.append(
            JobLogEntry(
                timestamp=job.completed_at.isoformat() if job.completed_at else "",
                level="info",
                message="Job completed successfully",
                details={"result": job.result_json if hasattr(job, "result_json") else None},
            )
        )
    elif job.status == "failed":
        logs.append(
            JobLogEntry(
                timestamp=job.completed_at.isoformat() if job.completed_at else "",
                level="error",
                message=f"Job failed: {job.error_message or 'Unknown error'}",
                details={"error": job.error_message},
            )
        )
    elif job.status == "cancelled":
        logs.append(
            JobLogEntry(
                timestamp=job.updated_at.isoformat() if job.updated_at else "",
                level="warn",
                message="Job was cancelled",
            )
        )

    # Apply level filter
    if level:
        logs = [log for log in logs if log.level == level.lower()]

    # Apply limit
    logs = logs[:limit]

    return JobLogsResponse(
        job_id=job_id,
        logs=logs,
        total=len(logs),
    )
