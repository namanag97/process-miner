"""Dataset Processing Tasks.

Celery tasks for dataset validation, file processing, and ingestion.
"""

import json
import time
from datetime import datetime
from typing import Any

import structlog
from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .base import AsyncSessionLocal, AsyncTask, celery_app
from src.platform.models import Project

logger = structlog.get_logger(__name__)


# =============================================================================
# Validate Dataset Task
# =============================================================================


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="validate_dataset",
    autoretry_for=(SQLAlchemyError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
async def validate_dataset_task(
    self,
    dataset_id: str,
    job_id: str,
) -> dict[str, Any]:
    """Job-Centric Architecture: Async task for CSV validation and column detection.

    Phase 1 of deferred ingestion:
    1. Load raw file from storage
    2. Detect columns using unified ingestion service
    3. Compute AI column suggestions
    4. Update dataset with detected columns and status=AWAITING_MAPPING

    Args:
        dataset_id: Dataset ID to validate
        job_id: Job ID for progress tracking

    Returns:
        dict with detected columns and suggestions
    """
    logger.info(
        "validate_dataset_task_started",
        dataset_id=dataset_id,
        job_id=job_id,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Loading file", "progress": 10, "stage": "loading"},
        )

        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import (
                Dataset,
                DatasetStatus,
                UploadedFile,
            )
            from src.features.process_mining.services.ingestion.unified import (
                unified_ingestion_service,
            )
            from src.platform.core.enums import JobStatus
            from src.platform.models import AsyncJob
            from src.platform.storage.storage import storage_service

            # Load dataset
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")

            # Load uploaded file
            result = await db.execute(
                select(UploadedFile).where(UploadedFile.dataset_id == dataset_id)
            )
            uploaded_file = result.scalar_one_or_none()
            if not uploaded_file:
                raise ValueError(f"No uploaded file for dataset: {dataset_id}")

            # Update job progress
            job = await db.get(AsyncJob, job_id)
            if job:
                job.status = JobStatus.RUNNING.value
                job.started_at = datetime.utcnow()
                job.stage = "loading"
                job.progress = 10
                await db.flush()

            self.update_state(
                state="PROGRESS",
                meta={"status": "Reading file from storage", "progress": 20, "stage": "reading"},
            )

            # Read file content
            file_content = await storage_service.backend.retrieve(
                f"{dataset_id}/{uploaded_file.filename}"
            )

            # Update job
            if job:
                job.stage = "detecting_columns"
                job.progress = 40
                await db.flush()

            self.update_state(
                state="PROGRESS",
                meta={"status": "Detecting columns", "progress": 40, "stage": "detecting_columns"},
            )

            # Detect columns using unified service
            detection_result = unified_ingestion_service.detect_columns(
                file_content, uploaded_file.filename
            )

            columns = detection_result.get("columns", [])
            suggestions = detection_result.get("suggestions", {})
            row_count = detection_result.get("row_count", 0)

            # Update job
            if job:
                job.stage = "computing_suggestions"
                job.progress = 70
                await db.flush()

            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Computing suggestions",
                    "progress": 70,
                    "stage": "computing_suggestions",
                },
            )

            # Update dataset with detection results
            dataset.detected_columns_json = json.dumps(columns)
            dataset.column_suggestions_json = json.dumps(suggestions)
            dataset.file_size_bytes = len(file_content)
            dataset.status = DatasetStatus.AWAITING_MAPPING.value
            dataset.validation_job_id = job_id
            dataset.error_message = None
            dataset.updated_at = datetime.utcnow()

            # Complete job
            if job:
                job.status = JobStatus.COMPLETED.value
                job.progress = 100
                job.stage = "completed"
                job.entity_id = dataset_id
                job.result_json = json.dumps(
                    {
                        "dataset_id": dataset_id,
                        "columns": columns,
                        "suggestions": suggestions,
                        "row_count": row_count,
                    }
                )
                job.completed_at = datetime.utcnow()

            await db.commit()

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "validate_dataset_task_completed",
                dataset_id=dataset_id,
                columns_found=len(columns),
                row_count=row_count,
                duration_ms=round(duration, 2),
                task_id=self.request.id,
            )

            return {
                "dataset_id": dataset_id,
                "columns": columns,
                "suggestions": suggestions,
                "row_count": row_count,
                "duration_ms": round(duration, 2),
            }

    except SoftTimeLimitExceeded:
        logger.warning(
            "validate_dataset_soft_timeout",
            dataset_id=dataset_id,
            task_id=self.request.id,
        )
        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, DatasetStatus
            from src.platform.core.enums import JobStatus
            from src.platform.models import AsyncJob

            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if dataset:
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = "Validation timed out (soft limit)"

            job = await db.get(AsyncJob, job_id)
            if job:
                job.status = JobStatus.FAILED.value
                job.error = "Task exceeded soft time limit"
                job.completed_at = datetime.utcnow()

            await db.commit()
        raise

    except Exception as e:
        logger.error(
            "validate_dataset_task_failed",
            error=str(e),
            dataset_id=dataset_id,
            task_id=self.request.id,
        )

        # Update dataset and job status
        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, DatasetStatus
            from src.platform.core.enums import JobStatus
            from src.platform.models import AsyncJob

            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if dataset:
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = str(e)

            job = await db.get(AsyncJob, job_id)
            if job:
                job.status = JobStatus.FAILED.value
                job.error = str(e)
                job.completed_at = datetime.utcnow()

            await db.commit()

        raise


# =============================================================================
# Validate Uploaded File Task
# =============================================================================


@celery_app.task(bind=True, base=AsyncTask, name="validate_uploaded_file", max_retries=3)
async def validate_uploaded_file_task(
    self,
    dataset_id: str,
    storage_key: str,
) -> dict[str, Any]:
    """Phase 4: Stream-based file validation for presigned uploads.

    Steps:
    1. Download file from S3 (streamed, memory-efficient)
    2. Magic byte verification (detect real file type)
    3. Schema sniffing (parse first 10MB for columns)
    4. Update dataset status (PENDING → VALIDATING → AWAITING_MAPPING)

    Args:
        dataset_id: Dataset ID to validate
        storage_key: S3 object key

    Returns:
        dict with validation results and detected columns

    Raises:
        Exception: If validation fails (retries up to 3 times)
    """
    logger.info(
        "validate_uploaded_file_started",
        dataset_id=dataset_id,
        storage_key=storage_key,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Downloading file from storage", "progress": 10},
        )

        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, DatasetStatus
            from src.features.process_mining.services.ingestion.unified import (
                unified_ingestion_service,
            )
            from src.platform.infrastructure.object_storage import get_storage_client
            from src.features.process_mining.services.ingestion.unified import (
                unified_ingestion_service,
            )
            from src.platform.infrastructure.object_storage import get_storage_client

            # Load dataset
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")

            # Update status to VALIDATING
            dataset.status = DatasetStatus.VALIDATING.value
            await db.flush()

            self.update_state(
                state="PROGRESS",
                meta={"status": "Downloading file", "progress": 20},
            )

            # Download file from S3 (streaming to avoid memory exhaustion)
            storage_client = get_storage_client()

            # Stream first 10MB for validation (don't load entire file)
            validation_chunk_size = 10 * 1024 * 1024  # 10 MB
            file_chunks = []
            total_bytes = 0

            try:
                for chunk in storage_client.stream_file("raw", storage_key, chunk_size=64 * 1024):
                    file_chunks.append(chunk)
                    total_bytes += len(chunk)
                    if total_bytes >= validation_chunk_size:
                        break  # Stop after 10MB for validation
            except Exception as e:
                logger.error(
                    "file_download_failed",
                    error=str(e),
                    dataset_id=dataset_id,
                    storage_key=storage_key,
                )
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = f"Failed to download file: {e}"
                await db.commit()
                raise

            file_content = b"".join(file_chunks)

            self.update_state(
                state="PROGRESS",
                meta={"status": "Verifying file signature", "progress": 40},
            )

            # Step 1: Magic byte verification
            file_extension = dataset.source_format.lower()

            if file_extension == "xes":
                if not file_content.startswith((b"<?xml", b"<log")):
                    logger.warning(
                        "file_signature_mismatch",
                        dataset_id=dataset_id,
                        expected="XES/XML",
                        actual="binary",
                    )
                    dataset.status = DatasetStatus.ERROR.value
                    dataset.error_message = "File appears to be invalid XES format (not valid XML)"
                    await db.commit()
                    raise ValueError("Invalid XES file signature")
            elif file_extension == "csv":
                try:
                    file_content[:1024].decode("utf-8")
                except UnicodeDecodeError:
                    logger.warning(
                        "file_signature_mismatch",
                        dataset_id=dataset_id,
                        expected="CSV/text",
                        actual="binary",
                    )
                    dataset.status = DatasetStatus.ERROR.value
                    dataset.error_message = (
                        "File appears to be invalid CSV format (contains binary data)"
                    )
                    await db.commit()
                    raise ValueError("Invalid CSV file signature")

            self.update_state(
                state="PROGRESS",
                meta={"status": "Detecting columns", "progress": 60},
            )

            # Step 2: Schema sniffing
            try:
                detection_result = unified_ingestion_service.detect_columns(
                    file_content,
                    dataset.source_file or f"upload.{file_extension}",
                )

                columns = detection_result.get("columns", [])
                suggestions = detection_result.get("suggestions", {})
                row_count_sample = detection_result.get("row_count", 0)

                logger.info(
                    "columns_detected",
                    dataset_id=dataset_id,
                    columns_count=len(columns),
                    sample_rows=row_count_sample,
                )

            except Exception as e:
                logger.error(
                    "column_detection_failed",
                    error=str(e),
                    dataset_id=dataset_id,
                )
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = f"Failed to detect columns: {e}"
                await db.commit()
                raise

            self.update_state(
                state="PROGRESS",
                meta={"status": "Updating dataset metadata", "progress": 90},
            )

            # Step 3: Update dataset with detection results
            dataset.detected_columns_json = json.dumps(columns)
            dataset.column_suggestions_json = json.dumps(suggestions)
            dataset.error_message = None

            # Step 3a: Store detected columns in database
            from src.features.process_mining.models import DatasetColumn, DatasetColumnMapping

            for idx, col_info in enumerate(columns):
                col_name = col_info.get('name', f'column_{idx}')
                col_dtype = col_info.get('dtype', 'STRING')
                samples = col_info.get('sample_values', [])
                null_pct = col_info.get('null_percentage', 0.0)
                unique_cnt = col_info.get('unique_count', 0)

                suggested_role = None
                confidence = None
                for role, suggestion in suggestions.items():
                    if suggestion.get('column') == col_name:
                        suggested_role = role
                        confidence = suggestion.get('confidence', 0.0)
                        break

                dataset_column = DatasetColumn(
                    dataset_id=dataset_id,
                    name=col_name,
                    dtype=col_dtype,
                    position=idx,
                    sample_values_json=json.dumps(samples) if samples else None,
                    null_count=int(row_count_sample * null_pct / 100) if row_count_sample else 0,
                    null_percentage=null_pct,
                    unique_count=unique_cnt,
                    suggested_role=suggested_role,
                    suggestion_confidence=confidence,
                )
                db.add(dataset_column)

            # Step 3b: Auto-mapping if high confidence
            required_roles = {'case_id', 'activity', 'timestamp'}
            can_auto_map = True
            auto_mapping = {}
            confidence_scores = {}

            for role in required_roles:
                if role in suggestions:
                    col_name = suggestions[role].get('column')
                    confidence = suggestions[role].get('confidence', 0.0)
                    auto_mapping[role] = col_name
                    confidence_scores[role] = confidence
                    if confidence < 0.8:
                        can_auto_map = False
                else:
                    can_auto_map = False

            if 'resource' in suggestions:
                auto_mapping['resource'] = suggestions['resource'].get('column')
                confidence_scores['resource'] = suggestions['resource'].get('confidence', 0.0)

            if can_auto_map and len(auto_mapping) >= 3:
                mapping = DatasetColumnMapping(
                    dataset_id=dataset_id,
                    case_id_column=auto_mapping['case_id'],
                    activity_column=auto_mapping['activity'],
                    timestamp_column=auto_mapping['timestamp'],
                    resource_column=auto_mapping.get('resource'),
                    auto_mapped=True,
                    confidence_scores_json=json.dumps(confidence_scores),
                )
                db.add(mapping)

                dataset.mapping_json = json.dumps({
                    'case_id_column': auto_mapping['case_id'],
                    'activity_column': auto_mapping['activity'],
                    'timestamp_column': auto_mapping['timestamp'],
                    'resource_column': auto_mapping.get('resource'),
                })

                dataset.status = DatasetStatus.MAPPED.value
                logger.info(
                    "auto_mapping_applied",
                    dataset_id=dataset_id,
                    case_id=auto_mapping['case_id'],
                    activity=auto_mapping['activity'],
                    timestamp=auto_mapping['timestamp'],
                )
            else:
                dataset.status = DatasetStatus.AWAITING_MAPPING.value

            # Get actual file size from S3
            try:
                actual_size = storage_client.get_file_size("raw", storage_key)
                dataset.file_size_bytes = actual_size
            except Exception:
                pass

            await db.commit()

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "validate_uploaded_file_completed",
                dataset_id=dataset_id,
                columns_detected=len(columns),
                duration_ms=round(duration, 2),
                task_id=self.request.id,
            )

            return {
                "dataset_id": dataset_id,
                "storage_key": storage_key,
                "columns": columns,
                "suggestions": suggestions,
                "status": "awaiting_mapping",
                "duration_ms": round(duration, 2),
            }

    except Exception as e:
        logger.error(
            "validate_uploaded_file_failed",
            error=str(e),
            dataset_id=dataset_id,
            storage_key=storage_key,
            task_id=self.request.id,
            exc_info=True,
        )

        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, DatasetStatus

            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if dataset:
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = str(e)
                await db.commit()

        raise self.retry(exc=e, countdown=2**self.request.retries)


# =============================================================================
# Ingest Dataset Task
# =============================================================================


@celery_app.task(
    bind=True,
    base=AsyncTask,
    name="ingest_dataset",
    autoretry_for=(SQLAlchemyError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
async def ingest_dataset_task(
    self,
    dataset_id: str,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Async task for background dataset ingestion.

    Phase 2 of deferred ingestion:
    1. Load raw file from storage
    2. Parse with DuckDB (vectorized)
    3. Compute variants and statistics
    4. Bulk insert cases/events to DB
    5. Update dataset status to READY

    Args:
        dataset_id: Dataset ID to ingest
        job_id: Optional job ID for tracking (if provided)

    Returns:
        dict with dataset_id, stats, and duration info
    """
    logger.info(
        "ingest_dataset_task_started",
        dataset_id=dataset_id,
        job_id=job_id,
        task_id=self.request.id,
    )
    start = time.perf_counter()

    try:
        self.update_state(
            state="PROGRESS",
            meta={"status": "Loading file", "progress": 5},
        )

        async with AsyncSessionLocal() as db:
            import pyarrow as pa

            from src.features.process_mining.models import (
                Dataset,
                DatasetColumnMapping,
                DatasetMetadata,
                DatasetStatus,
                ProcessCase,
                ProcessEvent,
                UploadedFile,
            )
            from src.features.process_mining.services.ingestion.duckdb import (
                duckdb_ingestion_service,
            )
            from src.platform.models import AsyncJob
            from src.platform.infrastructure.object_storage import get_storage_client

            # Load dataset and file
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {dataset_id}")

            # Load mapping from database
            mapping_result = await db.execute(
                select(DatasetColumnMapping).where(DatasetColumnMapping.dataset_id == dataset_id)
            )
            column_mapping = mapping_result.scalar_one_or_none()

            if column_mapping:
                mapping = {
                    'case_id_column': column_mapping.case_id_column,
                    'activity_column': column_mapping.activity_column,
                    'timestamp_column': column_mapping.timestamp_column,
                    'resource_column': column_mapping.resource_column,
                    'timestamp_format': column_mapping.timestamp_format,
                }
                logger.info("loaded_mapping_from_table", dataset_id=dataset_id)
            elif dataset.mapping_json:
                mapping = json.loads(dataset.mapping_json)
                logger.info("loaded_mapping_from_json", dataset_id=dataset_id)
            else:
                raise ValueError(f"No column mapping found for dataset: {dataset_id}")

            result = await db.execute(
                select(UploadedFile).where(UploadedFile.dataset_id == dataset_id)
            )
            uploaded_file = result.scalar_one_or_none()
            if not uploaded_file:
                raise ValueError(f"No uploaded file for dataset: {dataset_id}")

            self.update_state(
                state="PROGRESS",
                meta={"status": "Reading file from storage", "progress": 10},
            )

            # Retrieve file using the object storage client (matches upload/validation)
            storage_client = get_storage_client()
            file_obj = storage_client.download_fileobj("raw", uploaded_file.storage_path)
            file_content = file_obj.read()

            self.update_state(
                state="PROGRESS",
                meta={"status": "Parsing with DuckDB", "progress": 20, "stage": "parsing"},
            )

            # Update job with stage
            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "running"
                job.started_at = datetime.utcnow() if not job.started_at else job.started_at
                job.stage = "parsing"
                job.progress = 20
                job.entity_type = "dataset"
                job.entity_id = dataset_id
                await db.flush()

            # Parse with DuckDB
            duck_result = duckdb_ingestion_service.parse_csv_fast(
                file_content=file_content,
                case_id_col=mapping.get("case_id_column", "case_id"),
                activity_col=mapping.get("activity_column", "activity"),
                timestamp_col=mapping.get("timestamp_column", "timestamp"),
                resource_col=mapping.get("resource_column"),
            )

            stats = duck_result["statistics"]
            cases_arrow = duck_result["cases_arrow"]

            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Creating cases and events",
                    "progress": 50,
                    "stage": "creating_entities",
                },
            )
            if job:
                job.stage = "creating_entities"
                job.progress = 50
                await db.flush()

            # Convert Arrow to batches
            cases_arrow = duck_result["cases_arrow"]
            if isinstance(cases_arrow, pa.RecordBatchReader):
                cases_arrow = cases_arrow.read_all()

            events_arrow = duck_result["events_arrow"]
            if isinstance(events_arrow, pa.RecordBatchReader):
                events_arrow = events_arrow.read_all()

            # Process cases in chunks
            case_id_map = {}
            for batch in cases_arrow.to_batches(max_chunksize=5000):
                batch_dict = {col: batch.column(col).to_pylist() for col in batch.schema.names}
                batch_cases = []
                for i in range(batch.num_rows):
                    case = ProcessCase(
                        dataset_id=dataset_id,
                        case_id=str(batch_dict["case_id"][i]),
                        variant_key=batch_dict["variant"][i],
                        start_time=batch_dict["start_time"][i],
                        end_time=batch_dict["end_time"][i],
                    )
                    batch_cases.append(case)

                db.add_all(batch_cases)
                await db.flush()

                for c in batch_cases:
                    case_id_map[c.case_id] = c.id

                db.expunge_all()

            self.update_state(
                state="PROGRESS",
                meta={"status": "Creating events", "progress": 70, "stage": "creating_events"},
            )
            if job:
                job.stage = "creating_events"
                job.progress = 70
                await db.flush()

            # Process events in chunks
            for batch in events_arrow.to_batches(max_chunksize=10000):
                batch_dict = {col: batch.column(col).to_pylist() for col in batch.schema.names}
                batch_events = []
                for i in range(batch.num_rows):
                    case_ref_id = case_id_map.get(str(batch_dict["case_id"][i]))
                    if case_ref_id:
                        resource = batch_dict.get("resource", [None] * batch.num_rows)[i]
                        event = ProcessEvent(
                            case_ref_id=case_ref_id,
                            activity=str(batch_dict["activity"][i]),
                            timestamp=batch_dict["timestamp"][i],
                            resource=str(resource) if resource else None,
                        )
                        batch_events.append(event)

                if batch_events:
                    db.add_all(batch_events)
                    await db.flush()
                    db.expunge_all()

            self.update_state(
                state="PROGRESS",
                meta={"status": "Computing statistics", "progress": 90, "stage": "computing_stats"},
            )
            if job:
                job.stage = "computing_stats"
                job.progress = 90
                await db.flush()

            # Re-fetch dataset after session clear
            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()

            dataset.total_cases = stats["total_cases"]
            dataset.total_events = stats["total_events"]
            dataset.total_activities = stats["total_activities"]
            dataset.activities_json = json.dumps(stats.get("activities", []))
            dataset.statistics_json = json.dumps(stats)
            dataset.status = DatasetStatus.READY.value
            dataset.error_message = None

            # Create DatasetMetadata record
            metadata = DatasetMetadata(
                dataset_id=dataset_id,
                total_events=stats["total_events"],
                total_cases=stats["total_cases"],
                total_activities=stats["total_activities"],
                total_variants=stats.get("total_variants", 0),
                first_event_at=stats.get("first_event_at"),
                last_event_at=stats.get("last_event_at"),
                avg_case_duration=stats.get("avg_case_duration"),
                min_case_duration=stats.get("min_case_duration"),
                max_case_duration=stats.get("max_case_duration"),
                total_resources=stats.get("total_resources"),
                computed_at=datetime.utcnow(),
                computation_time_ms=int((time.perf_counter() - start) * 1000),
            )
            db.add(metadata)
            logger.info("dataset_metadata_created", dataset_id=dataset_id)

            # Update AsyncJob
            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "completed"
                job.progress = 100
                job.result_json = json.dumps(
                    {
                        "dataset_id": dataset_id,
                        "total_cases": stats["total_cases"],
                        "total_events": stats["total_events"],
                    }
                )
                job.completed_at = datetime.utcnow()

            await db.commit()

            duration = (time.perf_counter() - start) * 1000
            logger.info(
                "ingest_dataset_task_completed",
                dataset_id=dataset_id,
                total_cases=stats["total_cases"],
                total_events=stats["total_events"],
                duration_ms=round(duration, 2),
                task_id=self.request.id,
            )

            return {
                "dataset_id": dataset_id,
                "total_cases": stats["total_cases"],
                "total_events": stats["total_events"],
                "total_activities": stats["total_activities"],
                "duration_ms": round(duration, 2),
            }

    except SoftTimeLimitExceeded:
        logger.warning(
            "ingest_dataset_soft_timeout",
            dataset_id=dataset_id,
            task_id=self.request.id,
        )
        
        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, DatasetStatus
            from src.platform.models import AsyncJob

            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if dataset:
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = "Ingestion timed out (soft limit)"

            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error = "Task exceeded soft time limit"
                job.completed_at = datetime.utcnow()

            await db.commit()
            
        raise

    except Exception as e:
        logger.error(
            "ingest_dataset_task_failed",
            error=str(e),
            dataset_id=dataset_id,
            task_id=self.request.id,
        )

        async with AsyncSessionLocal() as db:
            from src.features.process_mining.models import Dataset, DatasetStatus
            from src.platform.models import AsyncJob

            result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
            dataset = result.scalar_one_or_none()
            if dataset:
                dataset.status = DatasetStatus.ERROR.value
                dataset.error_message = str(e)

            job_result = await db.execute(
                select(AsyncJob).where(AsyncJob.task_id == self.request.id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error = str(e)
                job.completed_at = datetime.utcnow()

            await db.commit()

        raise
