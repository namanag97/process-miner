"""Ingest Router - Background ingestion trigger endpoint.

Handles triggering the ingestion job after mapping is confirmed.
Part of 4-Phase Upload Architecture: Upload → Validate → Map → Ingest

Now uses Temporal workflows for durable execution (with Celery fallback).
"""

from fastapi import APIRouter
from sqlalchemy import select

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import DatasetStatus, DatasetColumnMapping
from src.features.process_mining.schemas.analysis import JobStatusResponse
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

Use `GET /operations/{workflow_id}` (v2) or `GET /jobs/{job_id}` to track progress.
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
    """Trigger background ingestion job.
    
    Uses Temporal v2 (native) or v1 (compat) based on feature flag.
    """
    from datetime import datetime
    from uuid import uuid4

    from src.platform.core.enums import JobStatus
    from src.platform.temporal.config import get_temporal_config

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

    # Build mapping dict
    if mapping:
        mapping_dict = {
            "case_id": mapping.case_id_column,
            "activity": mapping.activity_column,
            "timestamp": mapping.timestamp_column,
            "resource": mapping.resource_column,
        }
    elif dataset.mapping_json:
        import json
        mapping_dict = json.loads(dataset.mapping_json) if isinstance(dataset.mapping_json, str) else dataset.mapping_json
    else:
        mapping_dict = {}

    config = get_temporal_config()

    # =========================================================================
    # V2: Temporal-native architecture
    # =========================================================================
    if config.use_temporal_v2:
        from temporalio.client import WorkflowExecutionStatus
        from temporalio.common import WorkflowIDReusePolicy
        from temporalio.exceptions import WorkflowAlreadyStartedError

        from src.platform.temporal.client import get_temporal_client
        from src.platform.temporal.workflows_v2.ingestion import DatasetIngestionWorkflowV2

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
            # Idempotent - workflow already running, that's fine
            handle = client.get_workflow_handle(workflow_id)
            desc = await handle.describe()
            workflow_run_id = desc.run_id
            
            # If already completed/failed, allow restart
            if desc.status in (WorkflowExecutionStatus.COMPLETED, WorkflowExecutionStatus.FAILED):
                handle = await client.start_workflow(
                    DatasetIngestionWorkflowV2.run,
                    args=[dataset_id, dataset.storage_key, mapping_dict],
                    id=workflow_id,
                    task_queue=config.QUEUE_INGESTION,
                    id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
                )
                workflow_run_id = handle.result_run_id

        # Update dataset status (minimal DB write - just status)
        dataset.status = DatasetStatus.INGESTING.value
        dataset.error_message = None
        await db.commit()

        logger.info(
            "ingestion_triggered_v2",
            dataset_id=dataset_id,
            workflow_id=workflow_id,
            temporal_v2=True,
        )

        # Return v2 response (no job_id, use workflow_id)
        return JobStatusResponse(
            id=workflow_id,  # Use workflow_id as the ID
            job_type="ingest_dataset",
            status=JobStatus.PENDING.value,
            progress=0,
            stage="queued",
            created_at=datetime.utcnow(),
            result={
                "workflow_id": workflow_id,
                "workflow_run_id": workflow_run_id,
                "message": "Ingestion job queued (v2)",
                "poll_endpoint": f"/api/v1/operations/{workflow_id}",
            },
        )

    # =========================================================================
    # V1: Legacy AsyncJob + Temporal compat layer
    # =========================================================================
    from src.platform.temporal.compat import dispatch_workflow, is_temporal_enabled

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

    # Dispatch workflow (Temporal or Celery based on feature flag)
    result = await dispatch_workflow(
        workflow_type="dataset_ingestion",
        args={
            "dataset_id": dataset_id,
            "job_id": job.id,
            "storage_key": dataset.storage_key,
        },
        entity_type="dataset",
        entity_id=dataset_id,
    )

    # Update job with task/workflow ID
    job.task_id = result.get("task_id") or result.get("workflow_id")
    await db.commit()

    logger.info(
        "ingestion_triggered",
        dataset_id=dataset_id,
        job_id=job.id,
        workflow_id=result.get("workflow_id"),
        temporal_enabled=is_temporal_enabled(),
    )

    return JobStatusResponse(
        id=job.id,
        job_type="ingest_dataset",
        status=JobStatus.PENDING.value,
        progress=0,
        stage="queued",
        created_at=job.created_at,
        result={
            "workflow_id": result.get("workflow_id"),
            "message": "Ingestion job queued",
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
    """Trigger re-ingestion with updated mapping.
    
    Uses Temporal v2 (native) or v1 (compat) based on feature flag.
    """
    from datetime import datetime
    from uuid import uuid4

    from src.platform.core.enums import JobStatus
    from src.platform.temporal.config import get_temporal_config

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

    # Build mapping dict
    if mapping:
        mapping_dict = {
            "case_id": mapping.case_id_column,
            "activity": mapping.activity_column,
            "timestamp": mapping.timestamp_column,
            "resource": mapping.resource_column,
        }
    elif dataset.mapping_json:
        import json
        mapping_dict = json.loads(dataset.mapping_json) if isinstance(dataset.mapping_json, str) else dataset.mapping_json
    else:
        mapping_dict = {}

    config = get_temporal_config()

    # =========================================================================
    # V2: Temporal-native architecture
    # =========================================================================
    if config.use_temporal_v2:
        from temporalio.common import WorkflowIDReusePolicy

        from src.platform.temporal.client import get_temporal_client
        from src.platform.temporal.workflows_v2.ingestion import DatasetIngestionWorkflowV2

        # For reingest, use timestamp suffix to allow re-runs
        workflow_id = f"reingest-dataset-{dataset_id}"

        client = await get_temporal_client()

        # For reingest, always allow if previous completed/failed
        handle = await client.start_workflow(
            DatasetIngestionWorkflowV2.run,
            args=[dataset_id, dataset.storage_key, mapping_dict],
            id=workflow_id,
            task_queue=config.QUEUE_INGESTION,
            id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
        )

        # Update dataset status
        dataset.status = DatasetStatus.INGESTING.value
        dataset.error_message = None
        await db.commit()

        logger.info(
            "reingest_triggered_v2",
            dataset_id=dataset_id,
            workflow_id=workflow_id,
            temporal_v2=True,
        )

        return JobStatusResponse(
            id=workflow_id,
            job_type="reingest_dataset",
            status=JobStatus.PENDING.value,
            progress=0,
            stage="queued",
            created_at=datetime.utcnow(),
            result={
                "workflow_id": workflow_id,
                "workflow_run_id": handle.result_run_id,
                "message": "Re-ingestion job queued (v2)",
                "poll_endpoint": f"/api/v1/operations/{workflow_id}",
            },
        )

    # =========================================================================
    # V1: Legacy AsyncJob + Temporal compat layer
    # =========================================================================
    from src.platform.temporal.compat import dispatch_workflow, is_temporal_enabled

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

    # Dispatch workflow (Temporal or Celery based on feature flag)
    result = await dispatch_workflow(
        workflow_type="dataset_ingestion",
        args={
            "dataset_id": dataset_id,
            "job_id": job.id,
            "storage_key": dataset.storage_key,
            "reingest": True,
        },
        entity_type="dataset",
        entity_id=dataset_id,
    )

    # Update job with task/workflow ID
    job.task_id = result.get("task_id") or result.get("workflow_id")
    await db.commit()

    logger.info(
        "reingest_triggered",
        dataset_id=dataset_id,
        job_id=job.id,
        workflow_id=result.get("workflow_id"),
        temporal_enabled=is_temporal_enabled(),
    )

    return JobStatusResponse(
        id=job.id,
        job_type="reingest_dataset",
        status=JobStatus.PENDING.value,
        progress=0,
        stage="queued",
        created_at=job.created_at,
        result={
            "workflow_id": result.get("workflow_id"),
            "message": "Re-ingestion job queued",
        },
    )

