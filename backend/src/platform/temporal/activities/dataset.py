"""Dataset Activities.

Temporal activities for dataset ingestion workflow.
Each activity is a discrete, retriable unit of work.
"""

import json
import time
from datetime import datetime

import structlog
from temporalio import activity

from src.platform.temporal.activities.types import (
    BulkCopyInput,
    BulkCopyOutput,
    ComputeStatsInput,
    ComputeStatsOutput,
    DetectColumnsInput,
    DetectColumnsOutput,
    ParseToParquetInput,
    ParseToParquetOutput,
    ValidateFileInput,
    ValidateFileOutput,
)

# CQRS: Event emission for read model sync
from src.platform.core.domain_events import DatasetIngestedEvent, event_publisher

logger = structlog.get_logger(__name__)


# =============================================================================
# Validate File Activity
# =============================================================================


@activity.defn
async def validate_file_activity(input: ValidateFileInput) -> ValidateFileOutput:
    """Validate file format using magic bytes.

    Checks file signature to verify it matches expected format (CSV/XES).
    This is a fast operation that prevents processing invalid files.

    Args:
        input: ValidateFileInput with dataset_id and storage_key

    Returns:
        ValidateFileOutput with validation results
    """
    logger.info(
        "validate_file_activity_started",
        dataset_id=input.dataset_id,
        storage_key=input.storage_key,
    )

    try:
        from src.platform.infrastructure.object_storage import get_storage_client

        storage_client = get_storage_client()

        # Stream first 10KB for validation (don't load entire file)
        validation_chunk_size = 10 * 1024  # 10 KB
        file_chunks = []
        total_bytes = 0

        for chunk in storage_client.stream_file("raw", input.storage_key, chunk_size=4096):
            file_chunks.append(chunk)
            total_bytes += len(chunk)
            if total_bytes >= validation_chunk_size:
                break

        file_content = b"".join(file_chunks)

        # Get actual file size
        try:
            file_size = storage_client.get_file_size("raw", input.storage_key)
        except Exception:
            file_size = total_bytes

        # Detect format from storage key
        storage_key_lower = input.storage_key.lower()
        if storage_key_lower.endswith(".xes"):
            expected_format = "xes"
        elif storage_key_lower.endswith(".csv"):
            expected_format = "csv"
        else:
            expected_format = "csv"  # Default to CSV

        # Validate based on format
        if expected_format == "xes":
            if not file_content.startswith((b"<?xml", b"<log")):
                return ValidateFileOutput(
                    dataset_id=input.dataset_id,
                    is_valid=False,
                    file_format=expected_format,
                    file_size_bytes=file_size,
                    error_message="File appears to be invalid XES format (not valid XML)",
                )
        else:  # CSV
            try:
                file_content[:1024].decode("utf-8")
            except UnicodeDecodeError:
                return ValidateFileOutput(
                    dataset_id=input.dataset_id,
                    is_valid=False,
                    file_format=expected_format,
                    file_size_bytes=file_size,
                    error_message="File appears to be invalid CSV format (contains binary data)",
                )

        logger.info(
            "validate_file_activity_completed",
            dataset_id=input.dataset_id,
            file_format=expected_format,
            file_size_bytes=file_size,
        )

        return ValidateFileOutput(
            dataset_id=input.dataset_id,
            is_valid=True,
            file_format=expected_format,
            file_size_bytes=file_size,
        )

    except Exception as e:
        logger.error(
            "validate_file_activity_failed",
            dataset_id=input.dataset_id,
            error=str(e),
        )
        raise


# =============================================================================
# Detect Columns Activity
# =============================================================================


@activity.defn
async def detect_columns_activity(input: DetectColumnsInput) -> DetectColumnsOutput:
    """Detect columns and compute AI suggestions.

    Parses the file to identify columns and uses heuristics/AI to suggest
    column mappings for case_id, activity, timestamp, and resource.

    Args:
        input: DetectColumnsInput with file content and filename

    Returns:
        DetectColumnsOutput with columns and suggestions
    """
    logger.info(
        "detect_columns_activity_started",
        dataset_id=input.dataset_id,
        filename=input.filename,
    )

    try:
        from src.features.process_mining.services.ingestion.unified import (
            unified_ingestion_service,
        )

        detection_result = unified_ingestion_service.detect_columns(
            input.file_content,
            input.filename,
        )

        columns = detection_result.get("columns", [])
        suggestions = detection_result.get("suggestions", {})
        row_count = detection_result.get("row_count", 0)

        # Check if we can auto-map (high confidence on required columns)
        required_roles = {"case_id", "activity", "timestamp"}
        can_auto_map = True
        for role in required_roles:
            if role not in suggestions:
                can_auto_map = False
                break
            confidence = suggestions[role].get("confidence", 0.0)
            if confidence < 0.8:
                can_auto_map = False
                break

        logger.info(
            "detect_columns_activity_completed",
            dataset_id=input.dataset_id,
            columns_count=len(columns),
            row_count=row_count,
            can_auto_map=can_auto_map,
        )

        return DetectColumnsOutput(
            dataset_id=input.dataset_id,
            columns=columns,
            suggestions=suggestions,
            row_count=row_count,
            can_auto_map=can_auto_map,
        )

    except Exception as e:
        logger.error(
            "detect_columns_activity_failed",
            dataset_id=input.dataset_id,
            error=str(e),
        )
        raise


# =============================================================================
# Parse to Parquet Activity
# =============================================================================


@activity.defn
async def parse_to_parquet_activity(input: ParseToParquetInput) -> ParseToParquetOutput:
    """Parse CSV/XES file using DuckDB for vectorized processing.

    This is a long-running activity that uses heartbeats to signal liveness.
    Converts raw file to structured cases and events data.

    Memory Management:
    - For large files (>100MB), data is processed in batches with explicit
      heartbeats to prevent Temporal timeouts.
    - Arrow tables are converted to Python lists in chunks to avoid OOM.

    Parquet-First Strategy:
    - Events are also written to S3 as Parquet for analytics queries
    - DuckDB can read directly from S3 without hitting the database

    Args:
        input: ParseToParquetInput with column mappings

    Returns:
        ParseToParquetOutput with parsed data, statistics, and parquet_s3_key
    """
    logger.info(
        "parse_to_parquet_activity_started",
        dataset_id=input.dataset_id,
        storage_key=input.storage_key,
    )

    try:
        import io

        import pyarrow as pa
        import pyarrow.parquet as pq

        from src.features.process_mining.services.ingestion.duckdb import (
            duckdb_ingestion_service,
        )
        from src.platform.infrastructure.object_storage import get_storage_client

        # Heartbeat to signal we're starting
        activity.heartbeat("downloading_file")

        # Download file
        storage_client = get_storage_client()
        file_obj = storage_client.download_fileobj("raw", input.storage_key)
        file_content = file_obj.read()

        file_size_mb = len(file_content) / (1024 * 1024)
        logger.info(
            "file_downloaded",
            dataset_id=input.dataset_id,
            file_size_mb=round(file_size_mb, 2),
        )

        # Heartbeat after download
        activity.heartbeat("parsing_with_duckdb")

        # Parse with DuckDB
        duck_result = duckdb_ingestion_service.parse_csv_fast(
            file_content=file_content,
            case_id_col=input.case_id_column,
            activity_col=input.activity_column,
            timestamp_col=input.timestamp_column,
            resource_col=input.resource_column,
        )

        stats = duck_result["statistics"]
        cases_arrow = duck_result["cases_arrow"]
        events_arrow = duck_result["events_arrow"]

        # Heartbeat during conversion
        activity.heartbeat("converting_cases_to_records")

        # Convert Arrow to Python lists with batched processing
        if isinstance(cases_arrow, pa.RecordBatchReader):
            cases_data = []
            for batch in cases_arrow:
                cases_data.extend(batch.to_pylist())
                activity.heartbeat(f"processing_cases_batch_{len(cases_data)}")
        else:
            batch_size = 10000
            cases_data = []
            for batch in cases_arrow.to_batches(max_chunksize=batch_size):
                cases_data.extend(batch.to_pylist())
            activity.heartbeat("cases_converted")

        activity.heartbeat("converting_events_to_records")

        # For events, also keep the Arrow table for Parquet writing
        if isinstance(events_arrow, pa.RecordBatchReader):
            events_batches = list(events_arrow)
            events_table = pa.Table.from_batches(events_batches)
            events_data = []
            for batch in events_batches:
                events_data.extend(batch.to_pylist())
                activity.heartbeat(f"processing_events_batch_{len(events_data)}")
        else:
            events_table = events_arrow
            batch_size = 20000
            events_data = []
            for batch in events_arrow.to_batches(max_chunksize=batch_size):
                events_data.extend(batch.to_pylist())
            activity.heartbeat("events_converted")

        # Parquet-Only Strategy: Write events to S3 as Parquet (MANDATORY)
        # This is now the authoritative storage for event data
        parquet_s3_key = None
        parquet_size_bytes = None

        activity.heartbeat("writing_parquet_to_s3")
        
        parquet_key = f"parsed/{input.dataset_id}/events.parquet"

        # Write to bytes buffer
        parquet_buffer = io.BytesIO()
        pq.write_table(events_table, parquet_buffer, compression="snappy")
        parquet_bytes = parquet_buffer.getvalue()
        parquet_size_bytes = len(parquet_bytes)

        # Upload to S3 (this MUST succeed - it's the only storage for events)
        storage_client.upload_fileobj(
            bucket_type="cache",
            key=parquet_key,
            file_obj=io.BytesIO(parquet_bytes),
            content_type="application/octet-stream",
        )

        parquet_s3_key = parquet_key
        logger.info(
            "parquet_written_to_s3",
            dataset_id=input.dataset_id,
            parquet_key=parquet_key,
            parquet_size_mb=round(parquet_size_bytes / (1024 * 1024), 2),
        )

        logger.info(
            "parse_to_parquet_activity_completed",
            dataset_id=input.dataset_id,
            total_cases=stats["total_cases"],
            total_events=stats["total_events"],
            file_size_mb=round(file_size_mb, 2),
            parquet_s3_key=parquet_s3_key,
        )

        # NOTE: cases_data and events_data are no longer returned since we don't
        # write events to PostgreSQL anymore. Parquet in S3 is the authoritative source.
        return ParseToParquetOutput(
            dataset_id=input.dataset_id,
            total_cases=stats["total_cases"],
            total_events=stats["total_events"],
            total_activities=stats["total_activities"],
            cases_data=[],  # No longer used - kept for backwards compatibility
            events_data=[],  # No longer used - kept for backwards compatibility
            statistics=stats,
            parquet_s3_key=parquet_s3_key,
            parquet_size_bytes=parquet_size_bytes,
        )

    except Exception as e:
        logger.error(
            "parse_to_parquet_activity_failed",
            dataset_id=input.dataset_id,
            error=str(e),
        )
        raise


# =============================================================================
# Bulk Copy to DB Activity
# =============================================================================


@activity.defn
async def bulk_copy_to_db_activity(input: BulkCopyInput) -> BulkCopyOutput:
    """Bulk insert cases and events to PostgreSQL.

    Processes data in batches to avoid memory exhaustion and long transactions.

    Args:
        input: BulkCopyInput with cases and events data

    Returns:
        BulkCopyOutput with insert counts
    """
    logger.info(
        "bulk_copy_to_db_activity_started",
        dataset_id=input.dataset_id,
        cases_count=len(input.cases_data),
        events_count=len(input.events_data),
    )
    start = time.perf_counter()

    try:
        from src.features.process_mining.models import ProcessCase, ProcessEvent

        async with async_session_maker() as db:
            # Insert cases in batches
            case_id_map: dict[str, str] = {}
            cases_inserted = 0

            for i in range(0, len(input.cases_data), input.batch_size):
                batch = input.cases_data[i : i + input.batch_size]
                batch_cases = []

                for case_dict in batch:
                    case = ProcessCase(
                        dataset_id=input.dataset_id,
                        case_id=str(case_dict["case_id"]),
                        variant_key=case_dict.get("variant"),
                        start_time=case_dict.get("start_time"),
                        end_time=case_dict.get("end_time"),
                    )
                    batch_cases.append(case)

                db.add_all(batch_cases)
                await db.flush()

                for c in batch_cases:
                    case_id_map[c.case_id] = c.id

                cases_inserted += len(batch_cases)
                db.expunge_all()

            # Insert events in batches
            events_inserted = 0
            event_batch_size = input.batch_size * 2  # Events are smaller

            for i in range(0, len(input.events_data), event_batch_size):
                batch = input.events_data[i : i + event_batch_size]
                batch_events = []

                for event_dict in batch:
                    case_ref_id = case_id_map.get(str(event_dict["case_id"]))
                    if case_ref_id:
                        event = ProcessEvent(
                            case_ref_id=case_ref_id,
                            activity=str(event_dict["activity"]),
                            timestamp=event_dict["timestamp"],
                            resource=str(event_dict.get("resource"))
                            if event_dict.get("resource")
                            else None,
                        )
                        batch_events.append(event)

                if batch_events:
                    db.add_all(batch_events)
                    await db.flush()
                    events_inserted += len(batch_events)
                    db.expunge_all()

            await db.commit()

        duration = (time.perf_counter() - start) * 1000

        logger.info(
            "bulk_copy_to_db_activity_completed",
            dataset_id=input.dataset_id,
            cases_inserted=cases_inserted,
            events_inserted=events_inserted,
            duration_ms=round(duration, 2),
        )

        return BulkCopyOutput(
            dataset_id=input.dataset_id,
            cases_inserted=cases_inserted,
            events_inserted=events_inserted,
            duration_ms=duration,
        )

    except Exception as e:
        logger.error(
            "bulk_copy_to_db_activity_failed",
            dataset_id=input.dataset_id,
            error=str(e),
        )
        raise


# =============================================================================
# Compute Statistics Activity
# =============================================================================


@activity.defn
async def compute_statistics_activity(input: ComputeStatsInput) -> ComputeStatsOutput:
    """Compute and store dataset metadata/statistics.

    Creates a DatasetMetadata record and updates the Dataset with statistics.

    Args:
        input: ComputeStatsInput with statistics dictionary

    Returns:
        ComputeStatsOutput with computed metadata
    """
    logger.info(
        "compute_statistics_activity_started",
        dataset_id=input.dataset_id,
    )
    start = time.perf_counter()

    try:
        from sqlalchemy import select

        from src.features.process_mining.models import (
            Dataset,
            DatasetMetadata,
            DatasetStatus,
        )

        async with async_session_maker() as db:
            # Load dataset
            result = await db.execute(select(Dataset).where(Dataset.id == input.dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {input.dataset_id}")

            stats = input.statistics

            # Update dataset
            dataset.total_cases = stats.get("total_cases", 0)
            dataset.total_events = stats.get("total_events", 0)
            dataset.total_activities = stats.get("total_activities", 0)
            dataset.activities_json = json.dumps(stats.get("activities", []))
            dataset.statistics_json = json.dumps(stats)

            # Parquet-First Strategy: Store parquet metadata for analytics
            if stats.get("parquet_s3_key"):
                dataset.parquet_s3_key = stats["parquet_s3_key"]
                dataset.parquet_size_bytes = stats.get("parquet_size_bytes")
                dataset.parquet_row_count = stats.get("total_events", 0)
            dataset.status = DatasetStatus.READY.value
            dataset.error_message = None

            # Create metadata record
            computation_time_ms = int((time.perf_counter() - start) * 1000)
            metadata = DatasetMetadata(
                dataset_id=input.dataset_id,
                total_events=stats.get("total_events", 0),
                total_cases=stats.get("total_cases", 0),
                total_activities=stats.get("total_activities", 0),
                total_variants=stats.get("total_variants", 0),
                first_event_at=stats.get("first_event_at"),
                last_event_at=stats.get("last_event_at"),
                avg_case_duration=stats.get("avg_case_duration"),
                min_case_duration=stats.get("min_case_duration"),
                max_case_duration=stats.get("max_case_duration"),
                total_resources=stats.get("total_resources"),
                computed_at=datetime.utcnow(),
                computation_time_ms=computation_time_ms,
            )
            db.add(metadata)

            await db.commit()

            # CQRS: Emit event for read model sync
            # This triggers the AnalyticsCacheProjection to pre-compute analytics
            parquet_path = stats.get("parquet_s3_key", "")
            await event_publisher.publish(
                DatasetIngestedEvent(
                    dataset_id=input.dataset_id,
                    parquet_path=parquet_path,
                    total_events=stats.get("total_events", 0),
                    total_cases=stats.get("total_cases", 0),
                    total_activities=stats.get("total_activities", 0),
                )
            )

        logger.info(
            "compute_statistics_activity_completed",
            dataset_id=input.dataset_id,
            total_cases=stats.get("total_cases"),
            total_events=stats.get("total_events"),
        )

        return ComputeStatsOutput(
            dataset_id=input.dataset_id,
            total_events=stats.get("total_events", 0),
            total_cases=stats.get("total_cases", 0),
            total_activities=stats.get("total_activities", 0),
            total_variants=stats.get("total_variants", 0),
            first_event_at=stats.get("first_event_at"),
            last_event_at=stats.get("last_event_at"),
            avg_case_duration=stats.get("avg_case_duration"),
        )

    except Exception as e:
        logger.error(
            "compute_statistics_activity_failed",
            dataset_id=input.dataset_id,
            error=str(e),
        )
        raise


__all__ = [
    "bulk_copy_to_db_activity",
    "compute_statistics_activity",
    "detect_columns_activity",
    "parse_to_parquet_activity",
    "validate_file_activity",
]
