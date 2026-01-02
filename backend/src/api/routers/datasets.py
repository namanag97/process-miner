"""Datasets Router.

Endpoints for uploading, listing, and managing datasets.
"""

import json
import os
import time
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.api.dependencies import DBSession
from src.core.exceptions import (
    InsufficientDataError,
    InvalidFileError,
    ProcessNotFoundError,
    ProcessingError,
    ValidationError,
)
from src.core.logging_config import get_logger
from src.models.orm import Dataset, ProcessCase, Project
from src.models.schemas import (
    ActivityDetailResponse,
    CaseListResponse,
    CaseResponse,
    ColumnDetectionResponse,
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetResponse,
    StatisticsResponse,
    VariantResponse,
)
from src.services.ingestion import ingestion_service
from src.services.mining import mining_service
from src.services.duckdb_ingestion import duckdb_ingestion_service
# Domain model imports for new architecture
from src.domain.repositories import SQLAlchemyDatasetRepository

logger = get_logger(__name__)

# =============================================================================
# Constants
# =============================================================================

MAX_FILE_SIZE_MB = 100  # Maximum file upload size
MIN_EVENTS_FOR_ANALYSIS = 1  # Minimum events required for analysis
MIN_CASES_FOR_VARIANTS = 1  # Minimum cases required for variant analysis

router = APIRouter(prefix="/datasets", tags=["Datasets"])



# =============================================================================
# File Validation Helpers
# =============================================================================


def validate_file_upload(file: UploadFile) -> None:
    """Validate file extension and content type for security.

    Args:
        file: The uploaded file to validate

    Raises:
        InvalidFileError: If file validation fails
    """
    if not file.filename:
        raise InvalidFileError("No filename provided")

    # Validate file extension
    allowed_extensions = {".csv", ".xes"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        logger.warning("upload_rejected_extension", filename=file.filename, extension=ext)
        raise InvalidFileError(
            f"Invalid file type '{ext}'. Allowed extensions: {', '.join(allowed_extensions)}",
            filename=file.filename,
            expected_types=list(allowed_extensions),
        )

    # Validate content type (allow common browser defaults)
    allowed_mimetypes = {
        "text/csv", "application/csv", "application/xml", "text/xml",
        "application/octet-stream", "text/plain",  # Common browser defaults
    }
    if file.content_type and file.content_type not in allowed_mimetypes:
        logger.warning(
            "upload_rejected_mimetype",
            filename=file.filename,
            content_type=file.content_type,
        )
        raise InvalidFileError(
            f"Invalid content type: {file.content_type}. Expected CSV or XML.",
            filename=file.filename,
        )


def validate_file_size(content: bytes, filename: str) -> None:
    """Validate file size is within limits.
    
    Args:
        content: File content as bytes
        filename: Original filename
        
    Raises:
        InvalidFileError: If file is too large
    """
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        logger.warning(
            "upload_rejected_size",
            filename=filename,
            size_mb=round(file_size_mb, 2),
            max_size_mb=MAX_FILE_SIZE_MB,
        )
        raise InvalidFileError(
            f"File too large ({file_size_mb:.1f}MB). Maximum size: {MAX_FILE_SIZE_MB}MB",
            filename=filename,
        )


async def validate_file_signature(content: bytes, filename: str) -> None:
    """Validate file content signature to prevent file type spoofing.

    Args:
        content: First bytes of the file
        filename: The filename with extension

    Raises:
        InvalidFileError: If file signature doesn't match extension
    """
    ext = os.path.splitext(filename)[1].lower()

    # Read first 512 bytes for signature check
    signature = content[:512]

    if ext == ".xes":
        # XES files should start with XML declaration
        if not (signature.startswith(b"<?xml") or signature.startswith(b"<log")):
            logger.warning("file_signature_mismatch", filename=filename, extension=ext)
            raise InvalidFileError(
                "File appears to be invalid XES format (not valid XML)",
                filename=filename,
            )
    elif ext == ".csv":
        # CSV should be readable ASCII/UTF-8 text, check for binary content
        try:
            signature.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning("file_signature_mismatch", filename=filename, extension=ext)
            raise InvalidFileError(
                "File appears to be invalid CSV format (contains binary data)",
                filename=filename,
            )


# =============================================================================
# Upload & Ingest
# =============================================================================


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    db: DBSession,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None, description="Project ID to assign dataset to"),
    case_id_column: Optional[str] = Form(None),
    activity_column: Optional[str] = Form(None),
    timestamp_column: Optional[str] = Form(None),
    resource_column: Optional[str] = Form(None),
):
    """
    Upload and ingest an event log file.

    Supports CSV and XES formats. For CSV files, column mappings
    will be auto-detected if not provided.
    """
    # Validate file type and extension
    validate_file_upload(file)

    # Ensure filename is present (FastAPI UploadFile can have None filename)
    filename = file.filename
    if not filename:
        raise InvalidFileError("Filename is required")

    logger.info("upload_started", filename=filename, name=name, project_id=project_id)
    start_time = time.perf_counter()

    # Validate project exists if project_id is provided
    if project_id:
        project_query = select(Project).where(Project.id == project_id)
        project_result = await db.execute(project_query)
        if not project_result.scalar_one_or_none():
            raise ProcessNotFoundError(project_id, resource_name="Project")

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    logger.info("file_read", size_mb=round(file_size_mb, 2))

    # Validate file size
    validate_file_size(content, filename)

    # Validate file signature to prevent spoofing
    await validate_file_signature(content, filename)

    try:
        # Use DuckDB for high-performance CSV ingestion if it's a CSV file
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".csv":
            # DuckDB vectorized parse
            logger.info("using_duckdb_ingestion", filename=filename)
            duck_result = duckdb_ingestion_service.parse_csv_fast(
                file_content=content,
                case_id_col=case_id_column or "case_id",
                activity_col=activity_column or "activity",
                timestamp_col=timestamp_column or "timestamp",
                resource_col=resource_column,
            )

            # For now, we still save to SQLite through ingestion_service's logic
            # but we use the pre-parsed statistics and Arrow conversion
            dataset = await ingestion_service.ingest_file(
                session=db,
                file_content=content,
                filename=filename,
                name=name,
                case_id_col=case_id_column,
                activity_col=activity_column,
                timestamp_col=timestamp_column,
                resource_col=resource_column,
                precomputed_stats=duck_result["statistics"],
            )
        else:
            dataset = await ingestion_service.ingest_file(
                session=db,
                file_content=content,
                filename=filename,
                name=name,
                case_id_col=case_id_column,
                activity_col=activity_column,
                timestamp_col=timestamp_column,
                resource_col=resource_column,
            )

        activities = json.loads(dataset.activities_json) if dataset.activities_json else []
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Assign to project if project_id provided
        if project_id:
            dataset.project_id = project_id
            await db.flush()
            logger.info("dataset_assigned_to_project", dataset_id=dataset.id, project_id=project_id)

        logger.info(
            "upload_completed",
            dataset_id=dataset.id,
            total_events=dataset.total_events,
            total_cases=dataset.total_cases,
            total_activities=dataset.total_activities,
            duration_ms=round(duration_ms, 2),
        )

        return DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            source_format=dataset.source_format,
            total_events=dataset.total_events,
            total_cases=dataset.total_cases,
            total_activities=dataset.total_activities,
            activities=activities,
            created_at=dataset.created_at,
        )
    except ValidationError as e:
        logger.warning("upload_validation_error", error=e.message, filename=filename)
        raise  # Let the AppException handler deal with it
    except InvalidFileError:
        raise  # Let the AppException handler deal with it
    except Exception as e:
        logger.error("upload_error", error=str(e), filename=filename, exc_info=True)
        raise ProcessingError(f"Failed to process file: {str(e)}")


@router.post("/detect-columns", response_model=ColumnDetectionResponse)
async def detect_columns(
    file: UploadFile = File(...),
):
    """
    Detect column mappings from a CSV file.

    Returns suggested mappings for case_id, activity, timestamp, and resource columns.
    """
    # Validate file type and extension
    validate_file_upload(file)

    # Ensure filename is present
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    logger.info("detect_columns_started", filename=filename)
    start_time = time.perf_counter()

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    read_time_ms = (time.perf_counter() - start_time) * 1000
    logger.debug("file_read_for_detection", size_mb=round(file_size_mb, 2), duration_ms=round(read_time_ms, 2))

    # Validate file signature to prevent spoofing
    await validate_file_signature(content, filename)

    detection_start = time.perf_counter()

    ext = os.path.splitext(filename)[1].lower()
    if ext == ".csv":
        # Use DuckDB's native schema inference for 10x speedup
        result = duckdb_ingestion_service.detect_columns_fast(content)
        # Adapt keys for frontend response
        response_data = {
            "columns": [c["name"] for c in result["columns"]],
            "suggestions": result["suggestions"],
            "sample_rows": [], # DuckDB doesn't return sample rows in this call yet
            "row_count": result["row_count"],
        }
    else:
        result = ingestion_service.detect_columns(content)
        response_data = result

    detection_time_ms = (time.perf_counter() - detection_start) * 1000
    
    total_time_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "detect_columns_completed",
        columns_found=len(response_data.get("columns", [])),
        row_count=response_data.get("row_count", 0),
        file_size_mb=round(file_size_mb, 2),
        detection_ms=round(detection_time_ms, 2),
        total_ms=round(total_time_ms, 2),
    )

    return ColumnDetectionResponse(**response_data)


# =============================================================================
# List & Get
# =============================================================================


@router.get("", response_model=DatasetListResponse)
async def list_datasets(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_format: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
):
    """
    List all uploaded datasets.

    Supports pagination and filtering by source format.
    """
    logger.debug("list_datasets", page=page, page_size=page_size, source_format=source_format, project_id=project_id)

    # Build query
    query = select(Dataset).order_by(Dataset.created_at.desc())

    if source_format:
        query = query.where(Dataset.source_format == source_format)
    
    if project_id:
        query = query.where(Dataset.project_id == project_id)

    # Count total
    count_query = select(func.count()).select_from(Dataset)
    if source_format:
        count_query = count_query.where(Dataset.source_format == source_format)
    if project_id:
        count_query = count_query.where(Dataset.project_id == project_id)

    total = await db.scalar(count_query) or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    items = []
    for log in logs:
        activities = json.loads(log.activities_json) if log.activities_json else []
        items.append(
            DatasetResponse(
                id=log.id,
                name=log.name,
                source_format=log.source_format,
                total_events=log.total_events,
                total_cases=log.total_cases,
                total_activities=log.total_activities,
                activities=activities,
                created_at=log.created_at,
            )
        )

    return DatasetListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
async def get_dataset(
    db: DBSession,
    dataset_id: str,
):
    """
    Get detailed information about an event log.
    """
    logger.debug("get_dataset", dataset_id=dataset_id)
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    dataset = result.scalar_one_or_none()

    if not dataset:
        logger.warning("process_not_found", dataset_id=dataset_id)
        raise ProcessNotFoundError(dataset_id)

    activities = json.loads(dataset.activities_json) if dataset.activities_json else []
    statistics = json.loads(dataset.statistics_json) if dataset.statistics_json else None

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        source_format=dataset.source_format,
        source_file=dataset.source_file,
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        activities=activities,
        statistics=statistics,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
    )


@router.delete("/{dataset_id}")
async def delete_dataset(
    db: DBSession,
    dataset_id: str,
):
    """
    Delete an event log and all associated data.
    """
    logger.info("delete_dataset_started", dataset_id=dataset_id)
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    dataset = result.scalar_one_or_none()

    if not dataset:
        logger.warning("process_not_found", dataset_id=dataset_id)
        raise ProcessNotFoundError(dataset_id)

    await db.delete(dataset)
    await db.flush()
    logger.info("delete_dataset_completed", dataset_id=dataset_id)

    return {"status": "deleted", "id": dataset_id}


# =============================================================================
# Statistics & Analysis
# =============================================================================


@router.get("/{dataset_id}/statistics", response_model=StatisticsResponse)
async def get_statistics(
    db: DBSession,
    dataset_id: str,
):
    """
    Get comprehensive statistics for an event log.

    Includes activities, variants, case durations, and more.
    
    PERFORMANCE: Uses SQL aggregations instead of ORM eager loading
    to prevent OOM on large datasets (1M+ events).
    """
    logger.info("get_statistics_started", dataset_id=dataset_id)
    start_time = time.perf_counter()

    # Load ONLY the dataset metadata (no eager loading of cases/events!)
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    dataset = result.scalar_one_or_none()

    if not dataset:
        logger.warning("process_not_found", dataset_id=dataset_id)
        raise ProcessNotFoundError(dataset_id)

    activities = json.loads(dataset.activities_json) if dataset.activities_json else []

    # Get start/end activities from mining service (uses fast DuckDB path)
    start_activities = mining_service.get_start_activities(dataset)
    end_activities = mining_service.get_end_activities(dataset)

    # Get variants using mining service (uses fast DuckDB path)
    variants_data = mining_service.get_variants(dataset)

    # Get case duration stats via SQL aggregation (NO ORM object instantiation!)
    from sqlalchemy import func as sql_func
    duration_stats = await db.execute(
        select(
            sql_func.avg(
                sql_func.extract('epoch', ProcessCase.end_time) - 
                sql_func.extract('epoch', ProcessCase.start_time)
            ).label("avg_duration"),
            sql_func.min(
                sql_func.extract('epoch', ProcessCase.end_time) - 
                sql_func.extract('epoch', ProcessCase.start_time)
            ).label("min_duration"),
            sql_func.max(
                sql_func.extract('epoch', ProcessCase.end_time) - 
                sql_func.extract('epoch', ProcessCase.start_time)
            ).label("max_duration"),
            sql_func.min(ProcessCase.start_time).label("date_start"),
            sql_func.max(ProcessCase.end_time).label("date_end"),
        )
        .where(ProcessCase.dataset_id == dataset_id)
        .where(ProcessCase.start_time.isnot(None))
        .where(ProcessCase.end_time.isnot(None))
    )
    stats_row = duration_stats.one_or_none()
    
    # Extract values from SQL result (handles None cases)
    avg_duration = float(stats_row.avg_duration) if stats_row and stats_row.avg_duration else None
    min_duration = float(stats_row.min_duration) if stats_row and stats_row.min_duration else None
    max_duration = float(stats_row.max_duration) if stats_row and stats_row.max_duration else None
    
    date_range = None
    if stats_row and stats_row.date_start and stats_row.date_end:
        date_range = {
            "start": stats_row.date_start,
            "end": stats_row.date_end,
        }

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "get_statistics_completed",
        dataset_id=dataset_id,
        total_variants=variants_data.get("total_variants", 0),
        duration_ms=round(duration_ms, 2),
    )

    return StatisticsResponse(
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        total_variants=variants_data.get("total_variants", 0),
        activities=activities,
        start_activities=start_activities,
        end_activities=end_activities,
        avg_case_duration_seconds=avg_duration,
        min_case_duration_seconds=min_duration,
        max_case_duration_seconds=max_duration,
        date_range=date_range,
    )


@router.get("/{dataset_id}/cases", response_model=CaseListResponse)
async def list_cases(
    db: DBSession,
    dataset_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    List cases in an event log with pagination.
    """
    logger.debug("list_cases", dataset_id=dataset_id, page=page, page_size=page_size)

    # Verify log exists
    log_query = select(Dataset).where(Dataset.id == dataset_id)
    log_result = await db.execute(log_query)
    if not log_result.scalar_one_or_none():
        logger.warning("process_not_found", dataset_id=dataset_id)
        raise ProcessNotFoundError(dataset_id)

    # Count total cases
    count_query = (
        select(func.count()).select_from(ProcessCase).where(ProcessCase.dataset_id == dataset_id)
    )
    total = await db.scalar(count_query) or 0

    # Paginate cases
    offset = (page - 1) * page_size
    cases_query = (
        select(ProcessCase)
        .options(selectinload(ProcessCase.events))
        .where(ProcessCase.dataset_id == dataset_id)
        .order_by(ProcessCase.case_id)
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(cases_query)
    cases = result.scalars().all()

    items = []
    for case in cases:
        duration = None
        if case.start_time and case.end_time:
            duration = (case.end_time - case.start_time).total_seconds()

        items.append(
            CaseResponse(
                case_id=case.case_id,
                event_count=len(case.events),
                variant=case.variant_key,
                start_time=case.start_time,
                end_time=case.end_time,
                duration_seconds=duration,
            )
        )

    return CaseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{dataset_id}/variants", response_model=list[VariantResponse])
async def get_variants(
    db: DBSession,
    dataset_id: str,
    top_n: int = Query(20, ge=1, le=100),
    top_k_percent: Optional[float] = Query(
        None, ge=0, le=100, description="Return variants covering top K% of cases"
    ),
    include_complexity: bool = Query(
        False, description="Include complexity metrics (score, rework count, unique activities)"
    ),
    sort_by: Optional[str] = Query(
        None,
        description="Sort variants by: 'frequency', 'complexity', 'duration'. Default: frequency",
    ),
):
    """
    Get process variants (unique activity sequences) with frequencies.

    Supports filtering by:
    - top_n: Return top N variants by case count
    - top_k_percent: Return variants covering top K% of cases

    When include_complexity=true, each variant includes:
    - complexity_score: 0-1 score based on length, rework, and repetition
    - rework_count: Number of repeated activities
    - unique_activity_count: Number of distinct activities
    """
    logger.info(
        "get_variants_started",
        dataset_id=dataset_id,
        top_n=top_n,
        top_k_percent=top_k_percent,
        include_complexity=include_complexity,
    )

    # Load with cases
    query = (
        select(Dataset)
        .options(selectinload(Dataset.cases).selectinload(ProcessCase.events))
        .where(Dataset.id == dataset_id)
    )
    result = await db.execute(query)
    dataset = result.scalar_one_or_none()

    if not dataset:
        logger.warning("process_not_found", dataset_id=dataset_id)
        raise ProcessNotFoundError(dataset_id)

    # Group cases by variant
    variant_cases: dict[str, list[ProcessCase]] = {}
    for case in dataset.cases:
        key = case.variant_key or "unknown"
        if key not in variant_cases:
            variant_cases[key] = []
        variant_cases[key].append(case)

    total_cases = len(dataset.cases)

    # Sort by case count initially (will re-sort if sort_by is specified)
    sorted_variants = sorted(variant_cases.items(), key=lambda x: -len(x[1]))

    # Apply top_k_percent filtering if specified
    if top_k_percent is not None:
        target_cases = int(total_cases * top_k_percent / 100)
        cumulative = 0
        filtered_variants = []
        for variant_key, cases in sorted_variants:
            filtered_variants.append((variant_key, cases))
            cumulative += len(cases)
            if cumulative >= target_cases:
                break
        sorted_variants = filtered_variants
    else:
        sorted_variants = sorted_variants[:top_n]

    # Build response with optional complexity
    variants = []
    for variant_key, cases in sorted_variants:
        # Calculate average duration
        durations = []
        for case in cases:
            if case.start_time and case.end_time:
                durations.append((case.end_time - case.start_time).total_seconds())

        avg_duration = sum(durations) / len(durations) if durations else None

        # Build response with optional complexity
        complexity_score: Optional[float] = None
        rework_count: Optional[int] = None
        unique_activity_count: Optional[int] = None

        if include_complexity:
            complexity = mining_service.calculate_variant_complexity(variant_key)
            complexity_score = complexity.get("complexity_score")
            rework_count = complexity.get("rework_count")
            unique_activity_count = complexity.get("unique_activity_count")

        # Parse activities from variant_key using standard separator
        # Variant key format: "A → B → C" or "A -> B -> C"
        if " → " in variant_key:
            activities = [a.strip() for a in variant_key.split(" → ")]
        elif " -> " in variant_key:
            activities = [a.strip() for a in variant_key.split(" -> ")]
        else:
            activities = [variant_key.strip()] if variant_key.strip() else []

        variants.append(VariantResponse(
            variant_key=variant_key,
            activity_trace=variant_key,
            activities=activities,
            case_count=len(cases),
            frequency_percent=round(len(cases) / total_cases * 100, 2) if total_cases > 0 else 0.0,
            avg_duration_seconds=avg_duration,
            complexity_score=complexity_score,
            rework_count=rework_count,
            unique_activity_count=unique_activity_count,
        ))

    # Apply sorting if specified
    if sort_by == "complexity" and include_complexity:
        variants.sort(key=lambda v: v.complexity_score or 0, reverse=True)
    elif sort_by == "duration":
        variants.sort(key=lambda v: v.avg_duration_seconds or 0, reverse=True)
    # Default (frequency) is already sorted

    logger.info("get_variants_completed", dataset_id=dataset_id, variants_count=len(variants))
    return variants


@router.get("/{dataset_id}/activities", response_model=list[ActivityDetailResponse])
async def get_activities(
    db: DBSession,
    dataset_id: str,
    sort_by: Optional[str] = Query(
        None,
        description="Sort activities by: 'frequency', 'duration', 'position'. Default: frequency",
    ),
):
    """
    Get detailed activity statistics for a process.

    Returns each activity with:
    - frequency: Total occurrences
    - frequency_percent: Percentage of total events
    - avg/min/max_duration_seconds: Time to next activity
    - is_start_activity/is_end_activity: Position flags
    - position_avg: Average normalized position (0=start, 1=end)
    """
    logger.info("get_activities_started", dataset_id=dataset_id, sort_by=sort_by)
    start_time = time.perf_counter()

    # Load with cases and events
    query = (
        select(Dataset)
        .options(selectinload(Dataset.cases).selectinload(ProcessCase.events))
        .where(Dataset.id == dataset_id)
    )
    result = await db.execute(query)
    dataset = result.scalar_one_or_none()

    if not dataset:
        logger.warning("process_not_found", dataset_id=dataset_id)
        raise ProcessNotFoundError(dataset_id)

    # Get activity statistics
    activities_data = mining_service.get_activity_statistics(dataset)

    # Convert to response objects
    activities = [ActivityDetailResponse(**a) for a in activities_data]

    # Apply sorting if specified
    if sort_by == "duration":
        activities.sort(key=lambda a: a.avg_duration_seconds or 0, reverse=True)
    elif sort_by == "position":
        activities.sort(key=lambda a: a.position_avg or 0.5)
    # Default (frequency) is already sorted

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "get_activities_completed",
        dataset_id=dataset_id,
        activities_count=len(activities),
        duration_ms=round(duration_ms, 2),
    )
    return activities


# =============================================================================
# Domain Model Integration (New Architecture Demo)
# =============================================================================


@router.get("/{dataset_id}/domain/analysis")
async def get_domain_analysis(
    db: DBSession,
    dataset_id: str,
):
    """
    Get process analysis using the new rich domain model.
    
    This endpoint demonstrates the improved architecture:
    1. Repository pattern for data access
    2. DatasetAggregate for domain logic
    3. PM4Py log caching (single conversion)
    4. Computed properties on domain entities
    
    Returns aggregate statistics, variant analysis, and PM4Py cache status.
    """
    import pm4py
    
    logger.info("domain_analysis_started", dataset_id=dataset_id)
    start_time = time.perf_counter()
    
    # 1. Load via repository (eager loading)
    repo = SQLAlchemyDatasetRepository(db)
    aggregate = await repo.get(dataset_id)
    
    if not aggregate:
        logger.warning("process_not_found", dataset_id=dataset_id)
        raise ProcessNotFoundError(dataset_id)
    
    repo_load_ms = (time.perf_counter() - start_time) * 1000
    
    # 2. First PM4Py conversion (builds cache)
    pm4py_start = time.perf_counter()
    pm4py_log = aggregate.to_pm4py_log()
    first_conversion_ms = (time.perf_counter() - pm4py_start) * 1000
    
    # 3. Second PM4Py access (cache hit)
    cache_start = time.perf_counter()
    pm4py_log_cached = aggregate.to_pm4py_log()  # Should be instant
    cache_hit_ms = (time.perf_counter() - cache_start) * 1000
    
    # 4. Use PM4Py for analysis (uses cached log)
    pm4py_analysis_start = time.perf_counter()
    dfg, start_acts, end_acts = pm4py.discover_dfg(pm4py_log_cached)
    pm4py_analysis_ms = (time.perf_counter() - pm4py_analysis_start) * 1000
    
    # 5. Get domain computed properties
    stats = aggregate.statistics
    variant_stats = aggregate.get_variant_stats(top_n=5)
    
    total_ms = (time.perf_counter() - start_time) * 1000
    
    logger.info(
        "domain_analysis_completed",
        dataset_id=dataset_id,
        repo_load_ms=round(repo_load_ms, 2),
        first_conversion_ms=round(first_conversion_ms, 2),
        cache_hit_ms=round(cache_hit_ms, 2),
        pm4py_analysis_ms=round(pm4py_analysis_ms, 2),
        total_ms=round(total_ms, 2),
    )
    
    return {
        "dataset_id": aggregate.id,
        "name": aggregate.name,
        
        # Statistics from domain aggregate
        "statistics": {
            "total_events": stats.total_events,
            "total_cases": stats.total_cases,
            "total_activities": stats.total_activities,
            "total_variants": stats.total_variants,
            "avg_events_per_case": round(stats.avg_events_per_case, 2),
            "avg_case_duration_seconds": stats.avg_case_duration_seconds,
        },
        
        # Top variants from domain model
        "top_variants": [
            {
                "variant": v.sequence.to_trace_string(),
                "case_count": v.case_count,
                "frequency_percent": round(v.frequency_percent, 2),
                "complexity_score": round(v.complexity_score, 4),
                "has_rework": v.sequence.has_rework,
            }
            for v in variant_stats
        ],
        
        # DFG summary from PM4Py (using cached log)
        "dfg_summary": {
            "edges_count": len(dfg),
            "start_activities": list(start_acts.keys())[:5],
            "end_activities": list(end_acts.keys())[:5],
        },
        
        # Performance metrics (demonstrates caching benefit)
        "performance": {
            "repository_load_ms": round(repo_load_ms, 2),
            "first_pm4py_conversion_ms": round(first_conversion_ms, 2),
            "cached_pm4py_access_ms": round(cache_hit_ms, 2),
            "pm4py_dfg_analysis_ms": round(pm4py_analysis_ms, 2),
            "total_ms": round(total_ms, 2),
            "cache_speedup": f"{round(first_conversion_ms / max(cache_hit_ms, 0.001), 1)}x",
        },
    }
