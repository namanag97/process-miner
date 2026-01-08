"""Ingest Router - Background ingestion trigger endpoint.

Handles triggering the ingestion job after mapping is confirmed.
Part of 4-Phase Upload Architecture: Upload → Validate → Map → Ingest

Uses Temporal v2 workflows for durable execution.
"""

import json

from fastapi import APIRouter
from sqlalchemy import select

from src.api.dependencies import CurrentUser, ReadDBSession
from src.features.process_mining.models import DatasetColumnMapping, DatasetStatus
from src.features.process_mining.schemas.analyses import JobStatusResponse
from src.infra.core.enums import JobType
from src.infra.core.exceptions import ValidationError
from src.infra.core.logging_config import get_logger
from src.infra.core.permissions import Permission
from src.infra.users.services import require_dataset_permission

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
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
) -> JobStatusResponse:
    """Trigger background ingestion job using Temporal v2 workflow."""
    from datetime import datetime

    from temporalio.client import WorkflowExecutionStatus
    from temporalio.common import WorkflowIDReusePolicy
    from temporalio.exceptions import WorkflowAlreadyStartedError

    from src.infra.core.enums import JobStatus
    from src.infra.temporal.client import get_temporal_client
    from src.infra.temporal.config import get_temporal_config
    from src.infra.temporal.workflows_v2.ingestion import DatasetIngestionWorkflowV2

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

    try:
        client = await get_temporal_client()
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
    except Exception as e:
        # Temporal unavailable - fall back to synchronous processing
        logger.warning(
            "temporal_unavailable_falling_back_to_sync",
            dataset_id=dataset_id,
            workflow_id=workflow_id,
            error=str(e),
        )

        # Perform synchronous ingestion instead
        from datetime import datetime, timezone

        from starlette.concurrency import run_in_threadpool

        from src.features.process_mining.ingestion import duckdb_parser
        from src.features.process_mining.models import DatasetMetadata
        from src.infra.infrastructure.object_storage import get_storage_client

        dataset.status = DatasetStatus.INGESTING.value
        dataset.error_message = None
        await db.commit()

        try:
            storage_client = get_storage_client()
            file_obj = await run_in_threadpool(
                storage_client.download_fileobj, bucket_type="raw", key=dataset.storage_key
            )
            file_content = file_obj.read()

            result = await run_in_threadpool(
                duckdb_parser.parse_csv,
                file_content=file_content,
                case_id_col=mapping_dict["case_id"],
                activity_col=mapping_dict["activity"],
                timestamp_col=mapping_dict["timestamp"],
                resource_col=mapping_dict.get("resource"),
            )

            stats = result["statistics"]
            events_arrow = result.get("events_arrow")

            # Save events to Parquet file for analytics/visualization
            parquet_key = None
            if events_arrow is not None and len(events_arrow) > 0:
                import io

                import pyarrow.parquet as pq

                # Rename columns to PM4Py standard names for analytics compatibility
                column_mapping = {
                    "case_id": "case:concept:name",
                    "activity": "concept:name",
                    "timestamp": "time:timestamp",
                }
                new_names = [column_mapping.get(c, c) for c in events_arrow.column_names]
                events_arrow = events_arrow.rename_columns(new_names)

                # Write Arrow table to Parquet bytes
                parquet_buffer = io.BytesIO()
                pq.write_table(events_arrow, parquet_buffer)
                parquet_buffer.seek(0)

                # Save to storage
                parquet_key = f"{dataset_id}/events.parquet"
                await run_in_threadpool(
                    storage_client.upload_fileobj,
                    file_obj=parquet_buffer,
                    bucket_type="cache",
                    key=parquet_key,
                )
                logger.info("parquet_saved", dataset_id=dataset_id, key=parquet_key)

            dataset.total_cases = stats.get("total_cases", 0)
            dataset.total_events = stats.get("total_events", 0)
            dataset.total_activities = stats.get("total_activities", 0)
            dataset.variant_count = stats.get("total_variants", 0)
            dataset.activities_json = json.dumps(stats.get("activities", []))
            dataset.parquet_s3_key = parquet_key
            dataset.status = DatasetStatus.READY.value
            dataset.updated_at = datetime.now(timezone.utc)

            # Create or update DatasetMetadata
            from sqlalchemy import delete
            await db.execute(delete(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id))

            metadata = DatasetMetadata(
                dataset_id=dataset_id,
                total_cases=stats.get("total_cases", 0),
                total_events=stats.get("total_events", 0),
                total_activities=stats.get("total_activities", 0),
                total_variants=stats.get("total_variants", 0),
                total_resources=stats.get("total_resources", 0),
                first_event_at=stats.get("first_event_at"),
                last_event_at=stats.get("last_event_at"),
                avg_case_duration=stats.get("avg_case_duration"),
                min_case_duration=stats.get("min_case_duration"),
                max_case_duration=stats.get("max_case_duration"),
                computed_at=datetime.now(timezone.utc),
            )
            db.add(metadata)
            await db.commit()

            logger.info("sync_fallback_ingest_completed", dataset_id=dataset_id, stats=stats)

            now = datetime.now(timezone.utc)
            return JobStatusResponse(
                id=f"sync-ingest-{dataset_id}",
                job_type=JobType.INGESTION,
                status=JobStatus.COMPLETED,
                progress=100,
                stage="completed",
                created_at=now,
                result={
                    "message": "Ingestion completed (sync fallback)",
                    "statistics": stats,
                },
            )
        except Exception as sync_error:
            logger.error("sync_fallback_ingest_failed", dataset_id=dataset_id, error=str(sync_error))
            dataset.status = DatasetStatus.ERROR.value
            dataset.error_message = f"Ingestion failed: {sync_error!s}"
            await db.commit()
            from src.infra.core.exceptions import ProcessingError
            raise ProcessingError(f"Ingestion failed: {sync_error!s}")

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
    "/{dataset_id}/ingest-sync",
    summary="Synchronous Ingestion (Dev Mode)",
    description="""
Process dataset ingestion synchronously without Temporal.

**Development mode only** - use this when Temporal is unavailable.
For production, use `POST /datasets/{id}/ingest` with Temporal workflows.

Prerequisites:
- Dataset must be in MAPPED or ERROR status
- Column mapping must be saved
    """,
    responses={
        200: {"description": "Ingestion completed successfully"},
        400: {"description": "Dataset not in valid state"},
        404: {"description": "Dataset not found"},
        500: {"description": "Ingestion failed"},
    },
)
async def sync_ingest(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
) -> dict:
    """Process dataset ingestion synchronously (dev mode fallback)."""
    from datetime import datetime

    from starlette.concurrency import run_in_threadpool

    from src.features.process_mining.ingestion import duckdb_parser
    from src.features.process_mining.models import DatasetMetadata
    from src.infra.core.exceptions import ProcessingError
    from src.infra.infrastructure.object_storage import get_storage_client

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
    case_id_col = mapping_data.get("case_id_column", "case_id")
    activity_col = mapping_data.get("activity_column", "activity")
    timestamp_col = mapping_data.get("timestamp_column", "timestamp")
    resource_col = mapping_data.get("resource_column")

    logger.info(
        "sync_ingest_started",
        dataset_id=dataset_id,
        case_id_col=case_id_col,
        activity_col=activity_col,
        timestamp_col=timestamp_col,
    )

    # Update status to INGESTING
    dataset.status = DatasetStatus.INGESTING.value
    dataset.error_message = None
    await db.commit()

    try:
        # Download file from storage
        storage_client = get_storage_client()
        file_obj = await run_in_threadpool(
            storage_client.download_fileobj, bucket_type="raw", key=dataset.storage_key
        )
        file_content = file_obj.read()

        # Parse with DuckDB
        result = await run_in_threadpool(
            duckdb_parser.parse_csv,
            file_content=file_content,
            case_id_col=case_id_col,
            activity_col=activity_col,
            timestamp_col=timestamp_col,
            resource_col=resource_col,
        )

        stats = result["statistics"]

        # Update dataset with statistics
        dataset.total_cases = stats.get("total_cases", 0)
        dataset.total_events = stats.get("total_events", 0)
        dataset.total_activities = stats.get("total_activities", 0)
        dataset.variant_count = stats.get("total_variants", 0)
        dataset.activities_json = json.dumps(stats.get("activities", []))
        dataset.status = DatasetStatus.READY.value
        dataset.updated_at = datetime.utcnow()

        # Create or update DatasetMetadata
        from sqlalchemy import delete

        await db.execute(delete(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id))

        metadata = DatasetMetadata(
            dataset_id=dataset_id,
            total_cases=stats.get("total_cases", 0),
            total_events=stats.get("total_events", 0),
            total_activities=stats.get("total_activities", 0),
            total_variants=stats.get("total_variants", 0),
            total_resources=stats.get("total_resources", 0),
            first_event_at=stats.get("first_event_at"),
            last_event_at=stats.get("last_event_at"),
            avg_case_duration=stats.get("avg_case_duration"),
            min_case_duration=stats.get("min_case_duration"),
            max_case_duration=stats.get("max_case_duration"),
            computed_at=datetime.utcnow(),
        )
        db.add(metadata)

        await db.commit()

        logger.info(
            "sync_ingest_completed",
            dataset_id=dataset_id,
            total_cases=stats.get("total_cases"),
            total_events=stats.get("total_events"),
            total_activities=stats.get("total_activities"),
            total_variants=stats.get("total_variants"),
        )

        return {
            "status": "completed",
            "dataset_id": dataset_id,
            "statistics": stats,
            "message": "Dataset ingested successfully (sync mode)",
        }

    except Exception as e:
        logger.error("sync_ingest_failed", dataset_id=dataset_id, error=str(e), exc_info=True)
        dataset.status = DatasetStatus.ERROR.value
        dataset.error_message = f"Ingestion failed: {e!s}"
        await db.commit()
        raise ProcessingError(f"Ingestion failed: {e!s}")


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
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
) -> JobStatusResponse:
    """Trigger re-ingestion with updated mapping using Temporal v2 workflow."""
    from datetime import datetime

    from temporalio.common import WorkflowIDReusePolicy

    from src.infra.core.enums import JobStatus
    from src.infra.temporal.client import get_temporal_client
    from src.infra.temporal.config import get_temporal_config
    from src.infra.temporal.workflows_v2.ingestion import DatasetIngestionWorkflowV2

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

    try:
        handle = await client.start_workflow(
            DatasetIngestionWorkflowV2.run,
            args=[dataset_id, dataset.storage_key, mapping_dict],
            id=workflow_id,
            task_queue=config.QUEUE_INGESTION,
            id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
        )
    except Exception as e:
        # Handle Temporal client errors - update dataset to ERROR state
        from src.infra.core.exceptions import ServiceUnavailableError

        logger.error(
            "temporal_reingest_start_failed",
            dataset_id=dataset_id,
            workflow_id=workflow_id,
            error=str(e),
        )
        dataset.status = DatasetStatus.ERROR.value
        dataset.error_message = f"Failed to start re-ingestion workflow: {e!s}"
        await db.commit()
        raise ServiceUnavailableError(
            service="Temporal",
            message="Failed to start re-ingestion workflow. Please try again later.",
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
