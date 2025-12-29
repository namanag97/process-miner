"""Processes (Event Logs) Router.

Endpoints for uploading, listing, and managing event logs.
"""

import json
import time
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.api.dependencies import DBSession
from src.core.exceptions import NotFoundError, ValidationError
from src.core.logging_config import get_logger
from src.models.orm import EventLog, ProcessCase
from src.models.schemas import (
    CaseListResponse,
    CaseResponse,
    ColumnDetectionResponse,
    ProcessDetailResponse,
    ProcessListResponse,
    ProcessResponse,
    StatisticsResponse,
    VariantResponse,
)
from src.services.ingestion import ingestion_service
from src.services.mining import mining_service

logger = get_logger(__name__)

router = APIRouter(prefix="/processes", tags=["Processes"])


# =============================================================================
# Upload & Ingest
# =============================================================================


@router.post("/upload", response_model=ProcessResponse)
async def upload_process(
    db: DBSession,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
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
    if not file.filename:
        logger.warning("upload_rejected", reason="no_filename")
        raise HTTPException(status_code=400, detail="No file provided")

    logger.info("upload_started", filename=file.filename, name=name)
    start_time = time.perf_counter()

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    logger.info("file_read", size_mb=round(file_size_mb, 2))

    try:
        event_log = await ingestion_service.ingest_file(
            session=db,
            file_content=content,
            filename=file.filename,
            name=name,
            case_id_col=case_id_column,
            activity_col=activity_column,
            timestamp_col=timestamp_column,
            resource_col=resource_column,
        )

        activities = json.loads(event_log.activities_json) if event_log.activities_json else []
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "upload_completed",
            log_id=event_log.id,
            total_events=event_log.total_events,
            total_cases=event_log.total_cases,
            total_activities=event_log.total_activities,
            duration_ms=round(duration_ms, 2),
        )

        return ProcessResponse(
            id=event_log.id,
            name=event_log.name,
            source_format=event_log.source_format,
            total_events=event_log.total_events,
            total_cases=event_log.total_cases,
            total_activities=event_log.total_activities,
            activities=activities,
            created_at=event_log.created_at,
        )
    except ValidationError as e:
        logger.warning("upload_validation_error", error=e.message, filename=file.filename)
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.error("upload_error", error=str(e), filename=file.filename, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-columns", response_model=ColumnDetectionResponse)
async def detect_columns(
    file: UploadFile = File(...),
):
    """
    Detect column mappings from a CSV file.

    Returns suggested mappings for case_id, activity, timestamp, and resource columns.
    """
    if not file.filename:
        logger.warning("detect_columns_rejected", reason="no_filename")
        raise HTTPException(status_code=400, detail="No file provided")

    logger.info("detect_columns_started", filename=file.filename)
    content = await file.read()
    result = ingestion_service.detect_columns(content)
    logger.info(
        "detect_columns_completed",
        columns_found=len(result.get("columns", [])),
        row_count=result.get("row_count", 0),
    )

    return ColumnDetectionResponse(**result)


# =============================================================================
# List & Get
# =============================================================================


@router.get("", response_model=ProcessListResponse)
async def list_processes(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_format: Optional[str] = Query(None),
):
    """
    List all uploaded event logs.

    Supports pagination and filtering by source format.
    """
    logger.debug("list_processes", page=page, page_size=page_size, source_format=source_format)

    # Build query
    query = select(EventLog).order_by(EventLog.created_at.desc())

    if source_format:
        query = query.where(EventLog.source_format == source_format)

    # Count total
    count_query = select(func.count()).select_from(EventLog)
    if source_format:
        count_query = count_query.where(EventLog.source_format == source_format)

    total = await db.scalar(count_query) or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    items = []
    for log in logs:
        activities = json.loads(log.activities_json) if log.activities_json else []
        items.append(ProcessResponse(
            id=log.id,
            name=log.name,
            source_format=log.source_format,
            total_events=log.total_events,
            total_cases=log.total_cases,
            total_activities=log.total_activities,
            activities=activities,
            created_at=log.created_at,
        ))

    return ProcessListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{process_id}", response_model=ProcessDetailResponse)
async def get_process(
    db: DBSession,
    process_id: str,
):
    """
    Get detailed information about an event log.
    """
    logger.debug("get_process", process_id=process_id)
    query = select(EventLog).where(EventLog.id == process_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("process_not_found", process_id=process_id)
        raise HTTPException(status_code=404, detail=f"Process not found: {process_id}")

    activities = json.loads(event_log.activities_json) if event_log.activities_json else []
    statistics = json.loads(event_log.statistics_json) if event_log.statistics_json else None

    return ProcessDetailResponse(
        id=event_log.id,
        name=event_log.name,
        source_format=event_log.source_format,
        source_file=event_log.source_file,
        total_events=event_log.total_events,
        total_cases=event_log.total_cases,
        total_activities=event_log.total_activities,
        activities=activities,
        statistics=statistics,
        created_at=event_log.created_at,
        updated_at=event_log.updated_at,
    )


@router.delete("/{process_id}")
async def delete_process(
    db: DBSession,
    process_id: str,
):
    """
    Delete an event log and all associated data.
    """
    logger.info("delete_process_started", process_id=process_id)
    query = select(EventLog).where(EventLog.id == process_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("process_not_found", process_id=process_id)
        raise HTTPException(status_code=404, detail=f"Process not found: {process_id}")

    await db.delete(event_log)
    await db.flush()
    logger.info("delete_process_completed", process_id=process_id)

    return {"status": "deleted", "id": process_id}


# =============================================================================
# Statistics & Analysis
# =============================================================================


@router.get("/{process_id}/statistics", response_model=StatisticsResponse)
async def get_statistics(
    db: DBSession,
    process_id: str,
):
    """
    Get comprehensive statistics for an event log.

    Includes activities, variants, case durations, and more.
    """
    logger.info("get_statistics_started", process_id=process_id)
    start_time = time.perf_counter()

    # Load with cases and events
    query = (
        select(EventLog)
        .options(selectinload(EventLog.cases).selectinload(ProcessCase.events))
        .where(EventLog.id == process_id)
    )
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("process_not_found", process_id=process_id)
        raise HTTPException(status_code=404, detail=f"Process not found: {process_id}")

    activities = json.loads(event_log.activities_json) if event_log.activities_json else []

    # Get start/end activities from mining service
    start_activities = mining_service.get_start_activities(event_log)
    end_activities = mining_service.get_end_activities(event_log)

    # Get variants
    variants_data = mining_service.get_variants(event_log)

    # Get case statistics
    case_stats = mining_service.get_case_statistics(event_log)

    # Calculate date range
    date_range = None
    if event_log.cases:
        all_times = []
        for case in event_log.cases:
            if case.start_time:
                all_times.append(case.start_time)
            if case.end_time:
                all_times.append(case.end_time)
        if all_times:
            date_range = {
                "start": min(all_times),
                "end": max(all_times),
            }

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "get_statistics_completed",
        process_id=process_id,
        total_variants=variants_data.get("total_variants", 0),
        duration_ms=round(duration_ms, 2),
    )

    return StatisticsResponse(
        total_events=event_log.total_events,
        total_cases=event_log.total_cases,
        total_activities=event_log.total_activities,
        total_variants=variants_data.get("total_variants", 0),
        activities=activities,
        start_activities=start_activities,
        end_activities=end_activities,
        avg_case_duration_seconds=case_stats.get("avg_duration_seconds"),
        min_case_duration_seconds=case_stats.get("min_duration_seconds"),
        max_case_duration_seconds=case_stats.get("max_duration_seconds"),
        date_range=date_range,
    )


@router.get("/{process_id}/cases", response_model=CaseListResponse)
async def list_cases(
    db: DBSession,
    process_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    List cases in an event log with pagination.
    """
    logger.debug("list_cases", process_id=process_id, page=page, page_size=page_size)

    # Verify log exists
    log_query = select(EventLog).where(EventLog.id == process_id)
    log_result = await db.execute(log_query)
    if not log_result.scalar_one_or_none():
        logger.warning("process_not_found", process_id=process_id)
        raise HTTPException(status_code=404, detail=f"Process not found: {process_id}")

    # Count total cases
    count_query = select(func.count()).select_from(ProcessCase).where(ProcessCase.log_id == process_id)
    total = await db.scalar(count_query) or 0

    # Paginate cases
    offset = (page - 1) * page_size
    cases_query = (
        select(ProcessCase)
        .options(selectinload(ProcessCase.events))
        .where(ProcessCase.log_id == process_id)
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

        items.append(CaseResponse(
            case_id=case.case_id,
            event_count=len(case.events),
            variant=case.variant_key,
            start_time=case.start_time,
            end_time=case.end_time,
            duration_seconds=duration,
        ))

    return CaseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{process_id}/variants", response_model=list[VariantResponse])
async def get_variants(
    db: DBSession,
    process_id: str,
    top_n: int = Query(20, ge=1, le=100),
):
    """
    Get process variants (unique activity sequences) with frequencies.
    """
    logger.info("get_variants_started", process_id=process_id, top_n=top_n)

    # Load with cases
    query = (
        select(EventLog)
        .options(selectinload(EventLog.cases).selectinload(ProcessCase.events))
        .where(EventLog.id == process_id)
    )
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("process_not_found", process_id=process_id)
        raise HTTPException(status_code=404, detail=f"Process not found: {process_id}")

    # Group cases by variant
    variant_cases: dict[str, list[ProcessCase]] = {}
    for case in event_log.cases:
        key = case.variant_key or "unknown"
        if key not in variant_cases:
            variant_cases[key] = []
        variant_cases[key].append(case)

    total_cases = len(event_log.cases)

    # Build response
    variants = []
    for variant_key, cases in sorted(variant_cases.items(), key=lambda x: -len(x[1]))[:top_n]:
        # Calculate average duration
        durations = []
        for case in cases:
            if case.start_time and case.end_time:
                durations.append((case.end_time - case.start_time).total_seconds())

        avg_duration = sum(durations) / len(durations) if durations else None

        variants.append(VariantResponse(
            variant_key=variant_key,
            activity_trace=variant_key,  # Already in "A -> B -> C" format
            case_count=len(cases),
            frequency_percent=round(len(cases) / total_cases * 100, 2) if total_cases > 0 else 0,
            avg_duration_seconds=avg_duration,
        ))

    logger.info("get_variants_completed", process_id=process_id, variants_count=len(variants))
    return variants
