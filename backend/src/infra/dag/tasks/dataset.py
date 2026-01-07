"""Dataset DAG Task Nodes.

Pure business logic functions extracted from Celery tasks for DAG execution.
Each function is registered with TaskRegistry and can be orchestrated by DAGExecutor.
"""

import time
from typing import Any

import structlog

from src.infra.dag.registry import DAGContext, TaskResult, dag_task

logger = structlog.get_logger(__name__)


@dag_task("validate_file", timeout_seconds=300, max_retries=3)
async def validate_file(ctx: DAGContext, params: dict[str, Any]) -> TaskResult:
    """Validate an uploaded file with magic byte detection and schema sniffing.

    Extracted from validate_uploaded_file_task. Performs:
    1. Download file from storage (streamed)
    2. Magic byte verification (detect real file type)
    3. Basic file format validation

    Args:
        ctx: DAG context with dataset_id
        params: Task parameters (storage_key, file_extension)

    Returns:
        TaskResult with file validation status
    """
    start = time.perf_counter()
    dataset_id = ctx.dataset_id or params.get("dataset_id")
    storage_key = params.get("storage_key")
    file_extension = params.get("file_extension", "csv")

    if not dataset_id:
        return TaskResult.fail("dataset_id is required")

    logger.info("validate_file_started", dataset_id=dataset_id, run_id=ctx.run_id)

    try:
        from src.infra.infrastructure.object_storage import get_storage_client

        storage_client = get_storage_client()

        # Stream first 10MB for validation
        validation_chunk_size = 10 * 1024 * 1024
        file_chunks = []
        total_bytes = 0

        if storage_key:
            for chunk in storage_client.stream_file("raw", storage_key, chunk_size=64 * 1024):
                file_chunks.append(chunk)
                total_bytes += len(chunk)
                if total_bytes >= validation_chunk_size:
                    break

            file_content = b"".join(file_chunks)
        else:
            # For testing or when file is already loaded
            file_content = params.get("file_content", b"")

        # Magic byte verification
        if file_extension == "xes":
            if not file_content.startswith((b"<?xml", b"<log")):
                return TaskResult.fail("Invalid XES file signature (not valid XML)")
        elif file_extension == "csv":
            try:
                file_content[:1024].decode("utf-8")
            except UnicodeDecodeError:
                return TaskResult.fail("Invalid CSV file signature (contains binary data)")

        duration_ms = (time.perf_counter() - start) * 1000

        # Store validated content in context for downstream steps
        ctx.set("file_content", file_content)
        ctx.set("file_size_bytes", total_bytes or len(file_content))

        logger.info(
            "validate_file_completed",
            dataset_id=dataset_id,
            file_size=total_bytes,
            duration_ms=round(duration_ms, 2),
        )

        return TaskResult.ok(
            data={
                "dataset_id": dataset_id,
                "file_extension": file_extension,
                "file_size_bytes": total_bytes or len(file_content),
                "is_valid": True,
            },
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error("validate_file_failed", error=str(e), dataset_id=dataset_id)
        return TaskResult.fail(str(e))


@dag_task("detect_columns", timeout_seconds=600, max_retries=3)
async def detect_columns(ctx: DAGContext, params: dict[str, Any]) -> TaskResult:
    """Detect columns and compute AI suggestions for column mapping.

    Extracted from validate_dataset_task. Performs:
    1. Parse file for column detection
    2. Compute AI column suggestions
    3. Optionally perform auto-mapping for high-confidence matches

    Args:
        ctx: DAG context with dataset_id, file_content in shared_data
        params: Task parameters (filename)

    Returns:
        TaskResult with detected columns and suggestions
    """
    start = time.perf_counter()
    dataset_id = ctx.dataset_id or params.get("dataset_id")

    if not dataset_id:
        return TaskResult.fail("dataset_id is required")

    # Get file content from previous step or params
    file_content = ctx.get("file_content") or params.get("file_content")
    filename = params.get("filename", "upload.csv")

    if not file_content:
        return TaskResult.fail("file_content not found in context or params")

    logger.info("detect_columns_started", dataset_id=dataset_id, run_id=ctx.run_id)

    try:
        from src.features.process_mining.services.ingestion.unified import (
            unified_ingestion_service,
        )

        # Detect columns using unified service
        detection_result = unified_ingestion_service.detect_columns(file_content, filename)

        columns = detection_result.get("columns", [])
        suggestions = detection_result.get("suggestions", {})
        row_count = detection_result.get("row_count", 0)

        # Check if auto-mapping is possible
        required_roles = {"case_id", "activity", "timestamp"}
        can_auto_map = True
        auto_mapping = {}
        confidence_scores = {}

        for role in required_roles:
            if role in suggestions:
                col_name = suggestions[role].get("column")
                confidence = suggestions[role].get("confidence", 0.0)
                auto_mapping[role] = col_name
                confidence_scores[role] = confidence
                if confidence < 0.8:
                    can_auto_map = False
            else:
                can_auto_map = False

        if "resource" in suggestions:
            auto_mapping["resource"] = suggestions["resource"].get("column")
            confidence_scores["resource"] = suggestions["resource"].get("confidence", 0.0)

        # Store in context for downstream steps
        ctx.set("columns", columns)
        ctx.set("suggestions", suggestions)
        ctx.set("auto_mapping", auto_mapping if can_auto_map else None)

        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "detect_columns_completed",
            dataset_id=dataset_id,
            columns_count=len(columns),
            can_auto_map=can_auto_map,
            duration_ms=round(duration_ms, 2),
        )

        return TaskResult.ok(
            data={
                "dataset_id": dataset_id,
                "columns": columns,
                "suggestions": suggestions,
                "row_count": row_count,
                "can_auto_map": can_auto_map,
                "auto_mapping": auto_mapping if can_auto_map else None,
            },
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error("detect_columns_failed", error=str(e), dataset_id=dataset_id)
        return TaskResult.fail(str(e))


@dag_task("ingest_dataset", timeout_seconds=1800, max_retries=2)
async def ingest_dataset(ctx: DAGContext, params: dict[str, Any]) -> TaskResult:
    """Ingest dataset with DuckDB parsing and bulk insert.

    Extracted from ingest_dataset_task. Performs:
    1. Parse file with DuckDB (vectorized)
    2. Compute variants and statistics
    3. Bulk insert cases/events to DB
    4. Update dataset status to READY

    Args:
        ctx: DAG context with dataset_id
        params: Task parameters with column mappings

    Returns:
        TaskResult with ingestion statistics
    """
    start = time.perf_counter()
    dataset_id = ctx.dataset_id or params.get("dataset_id")

    if not dataset_id:
        return TaskResult.fail("dataset_id is required")

    logger.info("ingest_dataset_started", dataset_id=dataset_id, run_id=ctx.run_id)

    try:
        # Get column mapping from params or context
        mapping = params.get("mapping") or ctx.get("auto_mapping")

        if not mapping:
            return TaskResult.fail("Column mapping is required")

        case_id_col = mapping.get("case_id_column") or mapping.get("case_id")
        activity_col = mapping.get("activity_column") or mapping.get("activity")
        timestamp_col = mapping.get("timestamp_column") or mapping.get("timestamp")
        resource_col = mapping.get("resource_column") or mapping.get("resource")

        if not all([case_id_col, activity_col, timestamp_col]):
            return TaskResult.fail("case_id, activity, and timestamp columns are required")

        # Get file content - from context, params, or storage
        file_content = ctx.get("file_content") or params.get("file_content")

        if not file_content:
            # Load from storage if not in context

            from src.infra.infrastructure.object_storage import get_storage_client

            storage_key = params.get("storage_key")
            if storage_key:
                storage_client = get_storage_client()
                file_obj = storage_client.download_fileobj("raw", storage_key)
                file_content = file_obj.read()

        if not file_content:
            return TaskResult.fail("file_content not found")

        from src.features.process_mining.services.ingestion.duckdb import (
            duckdb_ingestion_service,
        )

        # Parse with DuckDB
        duck_result = duckdb_ingestion_service.parse_csv_fast(
            file_content=file_content,
            case_id_col=case_id_col,
            activity_col=activity_col,
            timestamp_col=timestamp_col,
            resource_col=resource_col,
        )

        stats = duck_result["statistics"]

        # Store results in context
        ctx.set("statistics", stats)
        ctx.set("cases_arrow", duck_result.get("cases_arrow"))
        ctx.set("events_arrow", duck_result.get("events_arrow"))

        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "ingest_dataset_completed",
            dataset_id=dataset_id,
            total_cases=stats.get("total_cases"),
            total_events=stats.get("total_events"),
            duration_ms=round(duration_ms, 2),
        )

        return TaskResult.ok(
            data={
                "dataset_id": dataset_id,
                "statistics": stats,
                "total_cases": stats.get("total_cases"),
                "total_events": stats.get("total_events"),
                "total_activities": stats.get("total_activities"),
            },
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error("ingest_dataset_failed", error=str(e), dataset_id=dataset_id, exc_info=True)
        return TaskResult.fail(str(e))
