"""Event Logs API Router."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
import io

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.application.support.ingestion_service import ingestion_service
from src.presentation.api.routers.auth import require_auth, User


router = APIRouter(prefix="/logs")


class EventLogResponse(BaseModel):
    id: str
    name: str
    source_file: Optional[str]
    total_cases: int
    total_events: int
    created_at: str


class EventLogDetailResponse(EventLogResponse):
    unique_activities: int
    unique_resources: int
    variant_count: int
    date_range: Optional[Dict[str, str]]


class UploadResponse(BaseModel):
    id: str
    name: str
    total_cases: int
    total_events: int
    validation: Dict[str, Any]


class VariantResponse(BaseModel):
    key: str
    activities: List[str]
    case_count: int
    length: int


class ColumnDetectionResponse(BaseModel):
    columns: List[str]
    suggestions: Dict[str, Optional[str]]
    sample_rows: List[Dict[str, Any]]


class FilePreviewResponse(BaseModel):
    """Response for file preview before full ingestion."""
    filename: str
    file_format: str  # csv, xes, xlsx
    columns: List[str]
    column_types: Dict[str, str]  # column -> detected type
    suggestions: Dict[str, Optional[str]]  # case_id, activity, timestamp, resource
    sample_rows: List[Dict[str, Any]]
    row_count: int
    estimated_case_count: int
    estimated_event_count: int


class LogStatisticsResponse(BaseModel):
    """Detailed log statistics response."""
    log_id: str
    event_count: int
    case_count: int
    activity_count: int
    variant_count: int
    resource_count: int
    date_range_start: Optional[str]
    date_range_end: Optional[str]
    avg_case_duration_seconds: Optional[float]
    median_case_duration_seconds: Optional[float]
    min_case_duration_seconds: Optional[float]
    max_case_duration_seconds: Optional[float]
    activities: List[str]
    start_activities: Dict[str, int]
    end_activities: Dict[str, int]


class QualityIssueResponse(BaseModel):
    """A single quality issue."""
    issue_type: str
    message: str
    severity: str
    affected_rows: int
    column: Optional[str]


class QualityReportResponse(BaseModel):
    """Quality assessment report for an event log."""
    log_id: str
    completeness_score: float
    validity_score: float
    overall_score: float
    is_valid: bool
    issues: List[QualityIssueResponse]


class EnhancedVariantResponse(BaseModel):
    """Enhanced variant with performance metrics."""
    variant_hash: str
    activity_trace: str
    activities: List[str]
    length: int
    case_count: int
    frequency_percent: float
    avg_duration_seconds: Optional[float]
    median_duration_seconds: Optional[float]
    is_happy_path: bool
    is_compliant: bool
    rank: int


class LogUpdateRequest(BaseModel):
    """Request body for updating event log metadata."""
    name: Optional[str] = None
    description: Optional[str] = None


class PaginatedLogsResponse(BaseModel):
    """Paginated list of event logs with metadata."""
    items: List[EventLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.post("/upload", response_model=UploadResponse)
async def upload_log(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    case_id_column: Optional[str] = Form(None),
    activity_column: Optional[str] = Form(None),
    timestamp_column: Optional[str] = Form(None),
    resource_column: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Upload an event log file (CSV or XES).
    """
    content = await file.read()
    
    # Build column mapping if provided
    column_mapping = None
    if any([case_id_column, activity_column, timestamp_column]):
        column_mapping = {
            "case_id": case_id_column or "case:concept:name",
            "activity": activity_column or "concept:name",
            "timestamp": timestamp_column or "time:timestamp",
            "resource": resource_column,
        }
    
    try:
        aggregate = await ingestion_service.ingest_file(
            file_content=content,
            filename=file.filename,
            name=name,
            column_mapping=column_mapping,
        )
        
        # Validate log
        validation = ingestion_service.validate_log(aggregate)
        
        # Save to database
        repo = EventLogRepository(session)
        await repo.save(aggregate.log)
        
        return UploadResponse(
            id=str(aggregate.log.id),
            name=aggregate.log.name,
            total_cases=aggregate.log.total_cases,
            total_events=aggregate.log.total_events,
            validation=validation,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/detect-columns", response_model=ColumnDetectionResponse)
async def detect_columns(
    file: UploadFile = File(...),
):
    """
    Detect column types from a CSV file preview.
    """
    content = await file.read()
    
    try:
        result = ingestion_service.detect_columns(content)
        return ColumnDetectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PaginatedLogsResponse)
async def list_logs(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    state: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    List all event logs with pagination, search, and sorting.
    
    - **search**: Filter logs by name (case-insensitive partial match)
    - **sort_by**: Field to sort by (created_at, name, total_cases, total_events)
    - **sort_order**: Sort direction (asc, desc)
    - **state**: Filter by log state (draft, ready, processing, archived)
    """
    repo = EventLogRepository(session)
    
    # Calculate offset from page
    offset = (page - 1) * page_size
    
    # Get logs with filters (repo method to be enhanced)
    logs = await repo.list_all(limit=page_size, offset=offset)
    
    # Apply search filter in-memory (can be moved to repo for large datasets)
    if search:
        search_lower = search.lower()
        logs = [log for log in logs if search_lower in log.name.lower()]
    
    # Apply state filter
    if state:
        logs = [log for log in logs if log.state.value == state]
    
    # Get total count (simplified - should be from repo)
    all_logs = await repo.list_all(limit=10000, offset=0)
    total = len(all_logs)
    if search:
        total = len([log for log in all_logs if search.lower() in log.name.lower()])
    if state:
        total = len([log for log in all_logs if log.state.value == state])
    
    total_pages = (total + page_size - 1) // page_size
    
    items = [
        EventLogResponse(
            id=str(log.id),
            name=log.name,
            source_file=log.source_file,
            total_cases=log.metadata.get("total_cases", 0),
            total_events=log.metadata.get("total_events", 0),
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]
    
    return PaginatedLogsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{log_id}", response_model=EventLogDetailResponse)
async def get_log(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get event log details.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    start, end = log.date_range
    
    return EventLogDetailResponse(
        id=str(log.id),
        name=log.name,
        source_file=log.source_file,
        total_cases=log.total_cases,
        total_events=log.total_events,
        unique_activities=len(log.activities),
        unique_resources=len(log.resources),
        variant_count=len(log.variants),
        date_range={
            "start": start.isoformat() if start else None,
            "end": end.isoformat() if end else None,
        },
        created_at=log.created_at.isoformat(),
    )


@router.get("/{log_id}/variants", response_model=List[VariantResponse])
async def get_variants(
    log_id: UUID,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get variants for an event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    variants = log.variants[:limit]
    
    return [
        VariantResponse(
            key=v.key[:200],  # Truncate long variants
            activities=list(v.activities),
            case_count=v.case_count,
            length=v.length,
        )
        for v in variants
    ]


@router.get("/{log_id}/activities")
async def get_activities(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get all activities in an event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    return {"activities": list(log.activities)}


@router.delete("/{log_id}")
async def delete_log(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Delete an event log.
    """
    repo = EventLogRepository(session)
    deleted = await repo.delete(log_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    return {"message": "Event log deleted successfully"}


@router.patch("/{log_id}", response_model=EventLogDetailResponse)
async def update_log(
    log_id: UUID,
    update: LogUpdateRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Update event log metadata.
    
    - **name**: New name for the event log
    - **description**: New description for the event log
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    # Update fields
    if update.name is not None:
        log.name = update.name
    if update.description is not None:
        log.metadata["description"] = update.description
    
    # Save changes
    await repo.save(log)
    
    start, end = log.date_range
    
    return EventLogDetailResponse(
        id=str(log.id),
        name=log.name,
        source_file=log.source_file,
        total_cases=log.total_cases,
        total_events=log.total_events,
        unique_activities=len(log.activities),
        unique_resources=len(log.resources),
        variant_count=len(log.variants),
        date_range={
            "start": start.isoformat() if start else None,
            "end": end.isoformat() if end else None,
        },
        created_at=log.created_at.isoformat(),
    )


# =============================================================================
# FLOW 1 ENHANCED ENDPOINTS - File Preview, Statistics, Quality
# =============================================================================

@router.post("/preview", response_model=FilePreviewResponse)
async def preview_file(
    file: UploadFile = File(...),
):
    """
    Preview a file before full ingestion.
    Returns sample data, column detection, and estimates without persisting.
    """
    content = await file.read()
    filename = file.filename or "unknown"
    
    try:
        # Detect file format
        if filename.lower().endswith('.xes'):
            file_format = "xes"
        elif filename.lower().endswith('.xlsx'):
            file_format = "xlsx"
        else:
            file_format = "csv"
        
        # Use existing detect_columns for CSV
        if file_format == "csv":
            detection = ingestion_service.detect_columns(content)
            columns = detection["columns"]
            suggestions = detection["suggestions"]
            sample_rows = detection["sample_rows"]
            
            # Detect column types
            column_types = {}
            for col in columns:
                # Simple type detection based on column name patterns
                col_lower = col.lower()
                if "time" in col_lower or "date" in col_lower or "timestamp" in col_lower:
                    column_types[col] = "datetime"
                elif "id" in col_lower or "case" in col_lower:
                    column_types[col] = "string"
                elif "cost" in col_lower or "amount" in col_lower or "price" in col_lower:
                    column_types[col] = "numeric"
                else:
                    column_types[col] = "string"
            
            # Estimate counts
            row_count = len(sample_rows) if len(sample_rows) < 10 else "10+ (preview)"
            case_col = suggestions.get("case_id")
            if case_col and sample_rows:
                unique_cases = len(set(str(row.get(case_col, "")) for row in sample_rows))
                estimated_case_count = unique_cases
            else:
                estimated_case_count = 0
            estimated_event_count = len(sample_rows)
            
            return FilePreviewResponse(
                filename=filename,
                file_format=file_format,
                columns=columns,
                column_types=column_types,
                suggestions=suggestions,
                sample_rows=sample_rows[:10],
                row_count=len(sample_rows),
                estimated_case_count=estimated_case_count,
                estimated_event_count=estimated_event_count,
            )
        else:
            # XES/XLSX - basic preview
            return FilePreviewResponse(
                filename=filename,
                file_format=file_format,
                columns=[],
                column_types={},
                suggestions={"case_id": "case:concept:name", "activity": "concept:name", "timestamp": "time:timestamp", "resource": "org:resource"},
                sample_rows=[],
                row_count=0,
                estimated_case_count=0,
                estimated_event_count=0,
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Preview failed: {str(e)}")


@router.get("/{log_id}/statistics", response_model=LogStatisticsResponse)
async def get_log_statistics(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get detailed statistics for an event log.
    Includes activity frequencies, duration stats, and start/end activities.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        # Get basic statistics
        stats = log.get_statistics()
        
        # Calculate additional metrics
        durations = []
        for case in log.cases:
            if case.duration:
                durations.append(case.duration.total_seconds)
        
        median_duration = None
        min_duration = None
        max_duration = None
        if durations:
            durations.sort()
            median_duration = durations[len(durations) // 2]
            min_duration = durations[0]
            max_duration = durations[-1]
        
        # Get start and end activities
        start_activities: Dict[str, int] = {}
        end_activities: Dict[str, int] = {}
        for case in log.cases:
            if case.events:
                sorted_events = sorted(case.events, key=lambda e: e.timestamp.value)
                start_act = str(sorted_events[0].activity)
                end_act = str(sorted_events[-1].activity)
                start_activities[start_act] = start_activities.get(start_act, 0) + 1
                end_activities[end_act] = end_activities.get(end_act, 0) + 1
        
        return LogStatisticsResponse(
            log_id=str(log_id),
            event_count=stats.event_count,
            case_count=stats.case_count,
            activity_count=stats.activity_count,
            variant_count=stats.variant_count,
            resource_count=stats.resource_count,
            date_range_start=stats.date_range_start.isoformat() if stats.date_range_start else None,
            date_range_end=stats.date_range_end.isoformat() if stats.date_range_end else None,
            avg_case_duration_seconds=stats.avg_case_duration_seconds,
            median_case_duration_seconds=median_duration,
            min_case_duration_seconds=min_duration,
            max_case_duration_seconds=max_duration,
            activities=list(log.activities),
            start_activities=start_activities,
            end_activities=end_activities,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics calculation failed: {str(e)}")


@router.get("/{log_id}/quality", response_model=QualityReportResponse)
async def get_log_quality(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get quality assessment report for an event log.
    Checks for data completeness, validity, and potential issues.
    """
    from src.domain.aggregates import EventLogAggregate
    
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        # Create aggregate for validation
        aggregate = EventLogAggregate(log)
        validation = ingestion_service.validate_log(aggregate)
        
        # Build quality issues
        issues = []
        
        # Check for missing resources
        events_without_resource = sum(
            1 for case in log.cases for event in case.events if not event.resource
        )
        if events_without_resource > 0:
            issues.append(QualityIssueResponse(
                issue_type="missing_resource",
                message=f"{events_without_resource} events have no resource assigned",
                severity="low" if events_without_resource < log.total_events * 0.1 else "medium",
                affected_rows=events_without_resource,
                column="resource",
            ))
        
        # Check for single-event cases
        single_event_cases = sum(1 for case in log.cases if len(case.events) == 1)
        if single_event_cases > 0:
            issues.append(QualityIssueResponse(
                issue_type="single_event_case",
                message=f"{single_event_cases} cases have only one event",
                severity="low",
                affected_rows=single_event_cases,
                column=None,
            ))
        
        # Check for duplicate events (same case, activity, timestamp)
        duplicate_count = 0
        for case in log.cases:
            seen = set()
            for event in case.events:
                key = (str(event.activity), event.timestamp.to_iso())
                if key in seen:
                    duplicate_count += 1
                seen.add(key)
        
        if duplicate_count > 0:
            issues.append(QualityIssueResponse(
                issue_type="duplicate_events",
                message=f"{duplicate_count} potential duplicate events detected",
                severity="medium",
                affected_rows=duplicate_count,
                column=None,
            ))
        
        # Calculate scores
        completeness_score = 1.0 - (events_without_resource / max(log.total_events, 1))
        validity_score = 1.0 if duplicate_count == 0 else max(0.5, 1.0 - (duplicate_count / max(log.total_events, 1)))
        overall_score = (completeness_score + validity_score) / 2
        is_valid = overall_score >= 0.7
        
        return QualityReportResponse(
            log_id=str(log_id),
            completeness_score=round(completeness_score, 3),
            validity_score=round(validity_score, 3),
            overall_score=round(overall_score, 3),
            is_valid=is_valid,
            issues=issues,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality check failed: {str(e)}")


@router.get("/{log_id}/variants/enhanced", response_model=List[EnhancedVariantResponse])
async def get_enhanced_variants(
    log_id: UUID,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get enhanced variants with performance metrics.
    Includes duration statistics, frequency, and ranking.
    """
    import hashlib
    
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        # Group cases by variant
        variant_cases: Dict[str, list] = {}
        for case in log.cases:
            key = case.variant_key
            if key not in variant_cases:
                variant_cases[key] = []
            variant_cases[key].append(case)
        
        # Build enhanced variants
        total_cases = len(log.cases)
        variants = []
        
        for rank, (key, cases) in enumerate(sorted(variant_cases.items(), key=lambda x: len(x[1]), reverse=True)):
            activities = key.split(",") if key else []
            activity_trace = " -> ".join(activities)
            variant_hash = hashlib.md5(activity_trace.encode()).hexdigest()[:16]
            
            # Calculate durations
            durations = [c.duration.total_seconds for c in cases if c.duration]
            avg_duration = sum(durations) / len(durations) if durations else None
            durations.sort()
            median_duration = durations[len(durations) // 2] if durations else None
            
            variants.append(EnhancedVariantResponse(
                variant_hash=variant_hash,
                activity_trace=activity_trace,
                activities=activities,
                length=len(activities),
                case_count=len(cases),
                frequency_percent=round(len(cases) / total_cases * 100, 2),
                avg_duration_seconds=round(avg_duration, 2) if avg_duration else None,
                median_duration_seconds=round(median_duration, 2) if median_duration else None,
                is_happy_path=rank == 0,  # Most frequent variant
                is_compliant=True,  # To be enhanced with conformance checking
                rank=rank + 1,
            ))
            
            if len(variants) >= limit:
                break
        
        return variants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variant analysis failed: {str(e)}")
