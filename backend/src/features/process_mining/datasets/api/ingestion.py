"""Ingest Router - Background ingestion trigger endpoint.

Handles triggering the ingestion job after mapping is confirmed.
Part of 4-Phase Upload Architecture: Upload → Validate → Map → Ingest
"""

import json

from fastapi import APIRouter
from sqlalchemy import select

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import DatasetStatus, DatasetColumnMapping
from src.features.process_mining.schemas.analyses import JobStatusResponse
from src.platform.core.exceptions import ValidationError
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.models import AsyncJob
from src.platform.users.services import require_dataset_permission

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
    from src.platform.temporal.compat import dispatch_workflow

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
    mapping_result = await db.execute(
        select(DatasetColumnMapping).where(DatasetColumnMapping.dataset_id == dataset_id)
    )
    mapping = mapping_result.scalar_one_or_none()
    
    if not mapping and not dataset.mapping_json:
        raise ValidationError("No column mapping found. Submit mapping first.")

    # Get column mapping
    mapping_data = mapping.__dict__ if mapping else json.loads(dataset.mapping_json or "{}")
    case_id_col = mapping_data.get("case_id_column", "case_id")
    activity_col = mapping_data.get("activity_column", "activity")
    timestamp_col = mapping_data.get("timestamp_column", "timestamp")
    resource_col = mapping_data.get("resource_column")

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

    # Dispatch via Temporal/Celery compat layer
    result = await dispatch_workflow(
        workflow_type="dataset_ingestion",
        args={
            "dataset_id": dataset_id,
            "storage_key": dataset.storage_key,
            "case_id_column": case_id_col,
            "activity_column": activity_col,
            "timestamp_column": timestamp_col,
            "resource_column": resource_col,
        },
        entity_type="dataset",
        entity_id=dataset_id,
    )

    # Update job with workflow/task_id
    job.task_id = result.get("workflow_id") or result.get("task_id")
    await db.commit()

    logger.info(
        "ingestion_triggered",
        dataset_id=dataset_id,
        job_id=job.id,
        workflow_id=result.get("workflow_id"),
    )

    return JobStatusResponse(
        id=job.id,
        job_type="ingest_dataset",
        status=JobStatus.PENDING.value,
        progress=0,
        stage="queued",
        created_at=job.created_at,
        result={"workflow_id": result.get("workflow_id"), "message": "Ingestion job queued"},
    )


@router.post(
    "/{dataset_id}/reingest",
    response_model=JobStatusResponse,
    summary="Re-ingest Dataset",
    description="""
Re-ingest a dataset with updated mapping.

Use this when you've updated the column mapping and want to
re-process the data without re-uploading the file.

Clears existing events and reprocesses from the original file.
    """,
    responses={
        202: {"description": "Re-ingestion job queued"},
        400: {"description": "Dataset not in READY or ERROR state"},
        404: {"description": "Dataset not found"},
    },
)
async def trigger_reingest(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
) -> JobStatusResponse:
    """Trigger re-ingestion with updated mapping."""
    from datetime import datetime
    from uuid import uuid4

    from src.platform.core.enums import JobStatus
    from src.platform.temporal.compat import dispatch_workflow

    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_UPDATE
    )

    # Check status - allow from READY or ERROR
    valid_statuses = [
        DatasetStatus.READY.value,
        DatasetStatus.ERROR.value,
        DatasetStatus.MAPPED.value,
    ]
    if dataset.status not in valid_statuses:
        raise ValidationError(
            f"Dataset must be in READY, MAPPED or ERROR state for re-ingestion. Current: {dataset.status}"
        )

    # Check mapping exists
    mapping_result = await db.execute(
        select(DatasetColumnMapping).where(DatasetColumnMapping.dataset_id == dataset_id)
    )
    mapping = mapping_result.scalar_one_or_none()

    if not mapping and not dataset.mapping_json:
        raise ValidationError("No column mapping found. Submit mapping first.")

    # Get column mapping
    mapping_data = mapping.__dict__ if mapping else json.loads(dataset.mapping_json or "{}")
    case_id_col = mapping_data.get("case_id_column", "case_id")
    activity_col = mapping_data.get("activity_column", "activity")
    timestamp_col = mapping_data.get("timestamp_column", "timestamp")
    resource_col = mapping_data.get("resource_column")

    # Create async job record
    job = AsyncJob(
        id=str(uuid4()),
        job_type="reingest_dataset",
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

    # Dispatch via Temporal/Celery compat layer
    result = await dispatch_workflow(
        workflow_type="dataset_ingestion",
        args={
            "dataset_id": dataset_id,
            "storage_key": dataset.storage_key,
            "case_id_column": case_id_col,
            "activity_column": activity_col,
            "timestamp_column": timestamp_col,
            "resource_column": resource_col,
        },
        entity_type="dataset",
        entity_id=dataset_id,
    )

    # Update job with workflow/task_id
    job.task_id = result.get("workflow_id") or result.get("task_id")
    await db.commit()

    logger.info(
        "reingest_triggered",
        dataset_id=dataset_id,
        job_id=job.id,
        workflow_id=result.get("workflow_id"),
    )

    return JobStatusResponse(
        id=job.id,
        job_type="reingest_dataset",
        status=JobStatus.PENDING.value,
        progress=0,
        stage="queued",
        created_at=job.created_at,
        result={"workflow_id": result.get("workflow_id"), "message": "Re-ingestion job queued"},
    )
