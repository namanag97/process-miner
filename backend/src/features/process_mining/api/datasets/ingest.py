"""Ingest Router - Background ingestion trigger endpoint.

Handles triggering the ingestion job after mapping is confirmed.
Part of 4-Phase Upload Architecture: Upload → Validate → Map → Ingest
"""

from fastapi import APIRouter

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import Dataset, DatasetStatus
from src.features.process_mining.schemas import JobStatusResponse
from src.platform.core.exceptions import ValidationError
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.models import AsyncJob
from src.platform.workspaces.authorization import require_dataset_permission

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/{dataset_id}/ingest",
    response_model=JobStatusResponse,
    summary="Trigger Dataset Ingestion",
    description="""
Start background ingestion job for a MAPPED dataset.

Prerequisites:
- Dataset must be in MAPPED status
- Column mapping must be saved

The ingestion job will:
1. Parse the file using the column mapping
2. Insert events into process_events table
3. Aggregate into process_cases
4. Compute metadata statistics
5. Update status to READY

Use `GET /jobs/{job_id}` to track progress.
    """,
    responses={
        202: {"description": "Ingestion job queued"},
        400: {"description": "Dataset not in MAPPED state"},
        404: {"description": "Dataset not found"},
    },
)
async def trigger_ingestion(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
) -> JobStatusResponse:
    """Trigger background ingestion job."""
    from datetime import datetime
    from uuid import uuid4

    from src.platform.core.enums import JobStatus
    from src.platform.infrastructure.tasks import ingest_dataset_task

    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_UPDATE
    )

    # Check status
    valid_statuses = [DatasetStatus.MAPPED.value, DatasetStatus.ERROR.value]
    if dataset.status not in valid_statuses:
        raise ValidationError(
            f"Dataset must be in MAPPED or ERROR state. Current: {dataset.status}"
        )

    # Check mapping exists
    if not dataset.column_mapping and not dataset.mapping_json:
        raise ValidationError("No column mapping found. Submit mapping first.")

    # Create async job record
    job = AsyncJob(
        id=str(uuid4()),
        job_type="ingest_dataset",
        status=JobStatus.PENDING.value,
        entity_type="dataset",
        entity_id=dataset_id,
        user_id=user.id,
        created_at=datetime.utcnow(),
    )
    db.add(job)

    # Update dataset status
    dataset.status = DatasetStatus.INGESTING.value
    dataset.ingestion_job_id = job.id
    dataset.error_message = None

    await db.commit()

    # Queue Celery task
    task = ingest_dataset_task.delay(dataset_id, job.id)

    # Update job with task_id
    job.task_id = task.id
    await db.commit()

    logger.info(
        "ingestion_triggered",
        dataset_id=dataset_id,
        job_id=job.id,
        task_id=task.id,
    )

    return JobStatusResponse(
        job_id=job.id,
        task_id=task.id,
        status=JobStatus.PENDING.value,
        job_type="ingest_dataset",
        entity_type="dataset",
        entity_id=dataset_id,
        progress=0,
        message="Ingestion job queued",
    )
