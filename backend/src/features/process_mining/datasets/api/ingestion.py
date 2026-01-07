"""Ingest Router - Background ingestion trigger endpoint.

Handles triggering the ingestion job after mapping is confirmed.
Part of 4-Phase Upload Architecture: Upload → Validate → Map → Ingest

Uses Temporal v2 workflows for durable execution.
"""

import json

from fastapi import APIRouter
from sqlalchemy import select

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import DatasetColumnMapping, DatasetStatus
from src.features.process_mining.schemas.analyses import JobStatusResponse
from src.platform.core.enums import JobStatus, JobType
from src.platform.core.exceptions import ValidationError
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
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

Use `GET /operations/{workflow_id}` to track progress.
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
    """Trigger background ingestion job using Temporal v2 workflow."""
    from datetime import datetime

    from temporalio.client import WorkflowExecutionStatus
    from temporalio.common import WorkflowIDReusePolicy
    from temporalio.exceptions import WorkflowAlreadyStartedError

    from src.platform.core.enums import JobStatus
    from src.platform.temporal.client import get_temporal_client
    from src.platform.temporal.config import get_temporal_config
    from src.platform.temporal.workflows_v2.ingestion import DatasetIngestionWorkflowV2

    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_UPDATE)

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
    mapping_dict = {
        "case_id": mapping_data.get("case_id_column", "case_id"),
        "activity": mapping_data.get("activity_column", "activity"),
        "timestamp": mapping_data.get("timestamp_column", "timestamp"),
        "resource": mapping_data.get("resource_column"),
    }

    config = get_temporal_config()

    # Deterministic workflow ID - enables idempotent starts
    workflow_id = f"ingest-dataset-{dataset_id}"

    client = await get_temporal_client()

    try:
        handle = await client.start_workflow(
            DatasetIngestionWorkflowV2.run,
            args=[dataset_id, dataset.storage_key, mapping_dict],
            id=workflow_id,
            task_queue=config.QUEUE_INGESTION,
            id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
        )
        workflow_run_id = handle.result_run_id
    except WorkflowAlreadyStartedError:
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()
        workflow_run_id = desc.run_id

        if desc.status in (WorkflowExecutionStatus.COMPLETED, WorkflowExecutionStatus.FAILED):
            handle = await client.start_workflow(
                DatasetIngestionWorkflowV2.run,
                args=[dataset_id, dataset.storage_key, mapping_dict],
                id=workflow_id,
                task_queue=config.QUEUE_INGESTION,
                id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
            )
            workflow_run_id = handle.result_run_id

    dataset.status = DatasetStatus.INGESTING.value
    dataset.error_message = None
    await db.commit()

    logger.info("ingestion_triggered", dataset_id=dataset_id, workflow_id=workflow_id)

    from datetime import timezone
    now = datetime.now(timezone.utc)
    
    return JobStatusResponse(
        id=workflow_id,
        job_type=JobType.INGESTION,
        status=JobStatus.QUEUED,
        progress=0,
        stage="queued",
        created_at=now,
        result={
            "workflow_id": workflow_id,
            "workflow_run_id": workflow_run_id,
            "message": "Ingestion job queued",
            "poll_endpoint": f"/api/v1/operations/{workflow_id}",
        },
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
    """Trigger re-ingestion with updated mapping using Temporal v2 workflow."""
    from datetime import datetime

    from temporalio.common import WorkflowIDReusePolicy

    from src.platform.core.enums import JobStatus
    from src.platform.temporal.client import get_temporal_client
    from src.platform.temporal.config import get_temporal_config
    from src.platform.temporal.workflows_v2.ingestion import DatasetIngestionWorkflowV2

    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_UPDATE)

    # Check status
    valid_statuses = [
        DatasetStatus.READY.value,
        DatasetStatus.ERROR.value,
        DatasetStatus.MAPPED.value,
    ]
    if dataset.status not in valid_statuses:
        raise ValidationError(
            f"Dataset must be in READY, MAPPED or ERROR state. Current: {dataset.status}"
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
    mapping_dict = {
        "case_id": mapping_data.get("case_id_column", "case_id"),
        "activity": mapping_data.get("activity_column", "activity"),
        "timestamp": mapping_data.get("timestamp_column", "timestamp"),
        "resource": mapping_data.get("resource_column"),
    }

    config = get_temporal_config()
    workflow_id = f"reingest-dataset-{dataset_id}"

    client = await get_temporal_client()

    handle = await client.start_workflow(
        DatasetIngestionWorkflowV2.run,
        args=[dataset_id, dataset.storage_key, mapping_dict],
        id=workflow_id,
        task_queue=config.QUEUE_INGESTION,
        id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
    )

    dataset.status = DatasetStatus.INGESTING.value
    dataset.error_message = None
    await db.commit()

    logger.info("reingest_triggered", dataset_id=dataset_id, workflow_id=workflow_id)

    from datetime import timezone
    now = datetime.now(timezone.utc)

    return JobStatusResponse(
        id=workflow_id,
        job_type=JobType.INGESTION,
        status=JobStatus.QUEUED,
        progress=0,
        stage="queued",
        created_at=now,
        result={
            "workflow_id": workflow_id,
            "workflow_run_id": handle.result_run_id,
            "message": "Re-ingestion job queued",
            "poll_endpoint": f"/api/v1/operations/{workflow_id}",
        },
    )
