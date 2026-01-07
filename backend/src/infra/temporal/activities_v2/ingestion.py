"""Ingestion Activities v2 - Stateless and Idempotent.

Each activity:
- Has single responsibility
- Executes in <5 minutes
- Is idempotent (same input → same result)
- Updates business entities directly (no AsyncJob)
- Uses heartbeat for operations >30 seconds
"""

import time
from datetime import datetime

import structlog
from temporalio import activity

from src.infra.temporal.activities_v2.types import (
    ChunkInfo,
    ChunkProcessResult,
    ColumnDetectionResult,
    ColumnMapping,
    IngestionResult,
    ValidationResult,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Validate File Activity
# =============================================================================


@activity.defn
async def validate_file(dataset_id: str, storage_key: str) -> ValidationResult:
    """Validate file format using magic bytes.

    Fast operation (<2 min). Idempotent - returns same result for same input.

    Args:
        dataset_id: UUID of the dataset
        storage_key: S3 key where file is stored

    Returns:
        ValidationResult with is_valid, file_format, file_size
    """
    logger.info("validate_file_started", dataset_id=dataset_id, storage_key=storage_key)
    activity.heartbeat("validating")

    try:
        from src.infra.infrastructure.object_storage import get_storage_client

        storage = get_storage_client()

        # Stream first 10KB for validation (don't load entire file)
        chunks = []
        total_bytes = 0

        for chunk in storage.stream_file("raw", storage_key, chunk_size=4096):
            chunks.append(chunk)
            total_bytes += len(chunk)
            if total_bytes >= 10240:  # 10KB
                break

        header = b"".join(chunks)

        # Get actual file size
        try:
            file_size = storage.get_file_size("raw", storage_key)
        except Exception:
            file_size = 0

        # Detect format from extension
        if storage_key.lower().endswith(".xes"):
            expected_format = "xes"
            is_valid = header.startswith((b"<?xml", b"<log"))
            error = None if is_valid else "Invalid XES format (not valid XML)"
        elif storage_key.lower().endswith(".csv"):
            expected_format = "csv"
            try:
                header[:1024].decode("utf-8")
                is_valid = True
                error = None
            except UnicodeDecodeError:
                is_valid = False
                error = "Invalid CSV format (contains binary data)"
        else:
            # Default to CSV
            expected_format = "csv"
            try:
                header[:1024].decode("utf-8")
                is_valid = True
                error = None
            except UnicodeDecodeError:
                is_valid = False
                error = "Invalid format (contains binary data)"

        logger.info(
            "validate_file_completed",
            dataset_id=dataset_id,
            is_valid=is_valid,
            file_format=expected_format,
            file_size=file_size,
        )

        return ValidationResult(
            is_valid=is_valid,
            file_format=expected_format,
            file_size_bytes=file_size,
            error_message=error,
        )

    except Exception as e:
        logger.error("validate_file_failed", dataset_id=dataset_id, error=str(e))
        raise


@activity.defn
async def detect_columns(dataset_id: str, storage_key: str) -> ColumnDetectionResult:
    """Detect columns and compute AI suggestions.

    Idempotent - same file always produces same column detection.

    Args:
        dataset_id: UUID of the dataset
        storage_key: S3 key where file is stored

    Returns:
        ColumnDetectionResult with columns, suggestions, row_count
    """
    logger.info("detect_columns_started", dataset_id=dataset_id)
    activity.heartbeat("detecting_columns")

    try:
        from src.features.process_mining.ingestion import (
            unified_ingestion_service,
        )
        from src.infra.infrastructure.object_storage import get_storage_client

        storage = get_storage_client()
        # MEMORY OPTIMIZATION: Only download first 2MB for column detection
        # instead of loading entire file into memory
        file_content = storage.download_sample("raw", storage_key, max_bytes=2 * 1024 * 1024)

        activity.heartbeat("parsing_columns")

        filename = storage_key.split("/")[-1]
        detection = unified_ingestion_service.detect_columns(file_content, filename)

        columns = detection.get("columns", [])
        suggestions = detection.get("suggestions", {})
        row_count = detection.get("row_count", 0)

        # Check if we can auto-map
        required_roles = {"case_id", "activity", "timestamp"}
        can_auto_map = all(
            role in suggestions and suggestions[role].get("confidence", 0) >= 0.8
            for role in required_roles
        )

        logger.info(
            "detect_columns_completed",
            dataset_id=dataset_id,
            columns_count=len(columns),
            row_count=row_count,
            can_auto_map=can_auto_map,
        )

        return ColumnDetectionResult(
            columns=columns,
            suggestions=suggestions,
            row_count=row_count,
            can_auto_map=can_auto_map,
        )

    except Exception as e:
        logger.error("detect_columns_failed", dataset_id=dataset_id, error=str(e))
        raise


@activity.defn
async def get_chunk_list(
    dataset_id: str,
    storage_key: str,
    file_size: int,
) -> list[ChunkInfo]:
    """Split file into processable chunks.

    Idempotent - same file always produces same chunks.

    Args:
        dataset_id: UUID of the dataset
        storage_key: S3 key where file is stored
        file_size: Total file size in bytes

    Returns:
        List of ChunkInfo for parallel processing
    """
    logger.info("get_chunk_list_started", dataset_id=dataset_id, file_size=file_size)

    # Target chunk size: ~10MB for CSV, entire file for small files
    chunk_size = 10 * 1024 * 1024  # 10MB

    if file_size <= chunk_size:
        # Small file - single chunk
        chunks = [
            ChunkInfo(
                chunk_id=f"{dataset_id}-chunk-0",
                start_offset=0,
                end_offset=file_size,
                row_count=0,
            )
        ]
    else:
        # Split into chunks
        chunks = []
        offset = 0
        chunk_idx = 0

        while offset < file_size:
            end = min(offset + chunk_size, file_size)
            chunks.append(
                ChunkInfo(
                    chunk_id=f"{dataset_id}-chunk-{chunk_idx}",
                    start_offset=offset,
                    end_offset=end,
                    row_count=0,
                )
            )
            offset = end
            chunk_idx += 1

    logger.info(
        "get_chunk_list_completed",
        dataset_id=dataset_id,
        num_chunks=len(chunks),
    )

    return chunks


@activity.defn
async def process_chunk(
    dataset_id: str,
    chunk: ChunkInfo,
    mapping: ColumnMapping,
) -> ChunkProcessResult:
    """Process a single chunk of the file.

    Idempotent via upsert - can be called multiple times without duplicates.
    Uses ON CONFLICT DO NOTHING for event insertion.

    Args:
        dataset_id: UUID of the dataset
        chunk: ChunkInfo with offset boundaries
        mapping: Column mapping for parsing

    Returns:
        ChunkProcessResult with counts
    """
    logger.info(
        "process_chunk_started",
        dataset_id=dataset_id,
        chunk_id=chunk.chunk_id,
        start_offset=chunk.start_offset,
        end_offset=chunk.end_offset,
    )
    activity.heartbeat(f"processing_{chunk.chunk_id}")

    start_time = time.perf_counter()

    try:
        from src.features.process_mining.ingestion import (
            duckdb_parser as duckdb_ingestion_service,
        )
        from src.features.process_mining.models import ProcessCase, ProcessEvent
        from src.infra.infrastructure.database import async_session_maker
        from src.infra.infrastructure.object_storage import get_storage_client

        storage = get_storage_client()

        # MEMORY OPTIMIZATION: Stream to temp file instead of loading all into memory
        # This prevents OOM on large files (up to 5GB)
        temp_path = storage.stream_to_tempfile("raw", f"{dataset_id}/raw")

        activity.heartbeat(f"parsing_{chunk.chunk_id}")

        try:
            # Parse with DuckDB using file path (memory-efficient)
            result = duckdb_ingestion_service.parse_csv_from_path(
                file_path=temp_path,
                case_id_col=mapping.case_id,
                activity_col=mapping.activity,
                timestamp_col=mapping.timestamp,
                resource_col=mapping.resource,
            )

            cases_data = (
                result["cases_arrow"].to_pylist() if hasattr(result["cases_arrow"], "to_pylist") else []
            )
            events_data = (
                result["events_arrow"].to_pylist()
                if hasattr(result["events_arrow"], "to_pylist")
                else []
            )

            activity.heartbeat(f"inserting_{chunk.chunk_id}")

            # Insert with idempotency (ON CONFLICT DO NOTHING)
            async with async_session_maker() as db:
                # Insert cases
                case_id_map = {}
                for case_dict in cases_data:
                    case = ProcessCase(
                        dataset_id=dataset_id,
                        case_id=str(case_dict["case_id"]),
                        variant_key=case_dict.get("variant"),
                        start_time=case_dict.get("start_time"),
                        end_time=case_dict.get("end_time"),
                    )
                    db.add(case)
                    try:
                        await db.flush()
                        case_id_map[case.case_id] = case.id
                    except Exception:
                        # Case already exists - get existing
                        await db.rollback()
                        from sqlalchemy import select

                        existing = await db.execute(
                            select(ProcessCase).where(
                                ProcessCase.dataset_id == dataset_id,
                                ProcessCase.case_id == str(case_dict["case_id"]),
                            )
                        )
                        existing_case = existing.scalar_one_or_none()
                        if existing_case:
                            case_id_map[existing_case.case_id] = existing_case.id

                # Insert events
                events_inserted = 0
                for event_dict in events_data:
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
                        db.add(event)
                        events_inserted += 1

                await db.commit()

            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "process_chunk_completed",
                dataset_id=dataset_id,
                chunk_id=chunk.chunk_id,
                cases_processed=len(case_id_map),
                events_processed=events_inserted,
                duration_ms=round(duration_ms, 2),
            )

            return ChunkProcessResult(
                chunk_id=chunk.chunk_id,
                events_processed=events_inserted,
                cases_processed=len(case_id_map),
                success=True,
            )
        finally:
            # CRITICAL: Clean up temp file to prevent disk space leak
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.debug("temp_file_cleaned", path=temp_path)

    except Exception as e:
        logger.error(
            "process_chunk_failed",
            dataset_id=dataset_id,
            chunk_id=chunk.chunk_id,
            error=str(e),
        )
        raise


@activity.defn
async def finalize_ingestion(dataset_id: str) -> IngestionResult:
    """Finalize ingestion - compute stats and update dataset status.

    Idempotent - can be called multiple times, always sets final state.

    Args:
        dataset_id: UUID of the dataset

    Returns:
        IngestionResult with totals
    """
    logger.info("finalize_ingestion_started", dataset_id=dataset_id)
    activity.heartbeat("finalizing")

    start_time = time.perf_counter()

    try:
        from sqlalchemy import func, select

        from src.features.process_mining.models import (
            Dataset,
            DatasetMetadata,
            DatasetStatus,
            ProcessCase,
            ProcessEvent,
        )
        from src.infra.infrastructure.database import async_session_maker

        async with async_session_maker() as db:
            # Compute statistics
            case_count = (
                await db.scalar(
                    select(func.count())
                    .select_from(ProcessCase)
                    .where(ProcessCase.dataset_id == dataset_id)
                )
                or 0
            )

            event_count = (
                await db.scalar(
                    select(func.count())
                    .select_from(ProcessEvent)
                    .join(ProcessCase)
                    .where(ProcessCase.dataset_id == dataset_id)
                )
                or 0
            )

            activity_count = (
                await db.scalar(
                    select(func.count(func.distinct(ProcessEvent.activity)))
                    .select_from(ProcessEvent)
                    .join(ProcessCase)
                    .where(ProcessCase.dataset_id == dataset_id)
                )
                or 0
            )

            # Count distinct variants (unique case sequences)
            variant_count = (
                await db.scalar(
                    select(func.count(func.distinct(ProcessCase.variant_key)))
                    .select_from(ProcessCase)
                    .where(ProcessCase.dataset_id == dataset_id)
                    .where(ProcessCase.variant_key.isnot(None))
                )
                or 0
            )

            activity.heartbeat("updating_dataset")

            # Update dataset status and denormalized fields
            # Note: Dataset.total_* fields are DEPRECATED, we only update status
            dataset = await db.get(Dataset, dataset_id)
            if dataset:
                dataset.status = DatasetStatus.READY.value
                dataset.error_message = None
                # Store row count as file-level metadata (not process mining stat)
                dataset.parquet_row_count = event_count
                # Denormalized variant_count for fast listing queries (avoids JOIN)
                dataset.variant_count = variant_count

            # Create or update metadata (single source of truth for statistics)
            existing_meta = await db.execute(
                select(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id)
            )
            metadata = existing_meta.scalar_one_or_none()

            computation_time_ms = int((time.perf_counter() - start_time) * 1000)

            if metadata:
                # Update existing
                metadata.total_cases = case_count
                metadata.total_events = event_count
                metadata.total_activities = activity_count
                metadata.total_variants = variant_count
                metadata.computed_at = datetime.utcnow()
                metadata.computation_time_ms = computation_time_ms
            else:
                # Create new
                metadata = DatasetMetadata(
                    dataset_id=dataset_id,
                    total_cases=case_count,
                    total_events=event_count,
                    total_activities=activity_count,
                    total_variants=variant_count,
                    computed_at=datetime.utcnow(),
                    computation_time_ms=computation_time_ms,
                )
                db.add(metadata)

            await db.commit()

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "finalize_ingestion_completed",
            dataset_id=dataset_id,
            total_cases=case_count,
            total_events=event_count,
            total_activities=activity_count,
            duration_ms=round(duration_ms, 2),
        )

        return IngestionResult(
            total_cases=case_count,
            total_events=event_count,
            total_activities=activity_count,
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error("finalize_ingestion_failed", dataset_id=dataset_id, error=str(e))
        raise


@activity.defn
async def update_dataset_status(
    dataset_id: str,
    status: str,
    error_message: str | None = None,
) -> None:
    """Update dataset status - idempotent helper.

    Args:
        dataset_id: UUID of the dataset
        status: New status value
        error_message: Optional error message
    """
    logger.info(
        "update_dataset_status",
        dataset_id=dataset_id,
        status=status,
        has_error=error_message is not None,
    )

    try:
        from src.features.process_mining.models import Dataset
        from src.infra.infrastructure.database import async_session_maker

        async with async_session_maker() as db:
            dataset = await db.get(Dataset, dataset_id)
            if dataset:
                dataset.status = status
                dataset.error_message = error_message
                await db.commit()

    except Exception as e:
        logger.error(
            "update_dataset_status_failed",
            dataset_id=dataset_id,
            error=str(e),
        )
        raise


@activity.defn
async def precompute_dfg(dataset_id: str) -> dict:
    """Pre-compute DFG cache after ingestion.

    Per tech spec step 7: Pre-compute DFG during ingestion workflow.
    This activity:
    - Loads events from the database
    - Computes DFG using PM4Py
    - Stores in dfg_cache table for fast retrieval

    Idempotent - can be called multiple times, overwrites cache.

    Args:
        dataset_id: UUID of the dataset

    Returns:
        Dict with edge_count and computation status
    """
    logger.info("precompute_dfg_started", dataset_id=dataset_id)
    activity.heartbeat("precomputing_dfg")

    start_time = time.perf_counter()

    try:
        from src.features.process_mining.services.cache_service import CacheService
        from src.infra.infrastructure.database import async_session_maker

        async with async_session_maker() as db:
            cache_service = CacheService(db)

            activity.heartbeat("computing_dfg")

            # Pre-compute both DFG and variants
            results = await cache_service.precompute_caches(dataset_id)

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "precompute_dfg_completed",
            dataset_id=dataset_id,
            dfg_edges=results.get("dfg", {}).get("edge_count", 0),
            variant_count=results.get("variants", {}).get("variant_count", 0),
            duration_ms=round(duration_ms, 2),
        )

        return {
            "success": True,
            "dfg_edge_count": results.get("dfg", {}).get("edge_count", 0),
            "variant_count": results.get("variants", {}).get("variant_count", 0),
            "duration_ms": duration_ms,
        }

    except Exception as e:
        logger.error("precompute_dfg_failed", dataset_id=dataset_id, error=str(e))
        # Don't raise - DFG cache failure shouldn't fail ingestion
        # It can be computed on-demand later
        return {
            "success": False,
            "error": str(e),
        }
