"""Processes API Router - Unified Process Mining Resource.

This router provides a unified interface for both:
- Traditional single-case event logs (CSV, XES)
- Object-Centric event logs (OCEL 2.0: JSON, SQLite, XML)

OCPM is the default/primary approach. Traditional PM is treated as a 
special case where there is one implicit object type ("case").

URL Pattern: /processes/{id}/...
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from uuid import UUID
from enum import Enum
import io
import json
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.infrastructure.persistence.models import (
    OCELLogModel,
    OCELObjectTypeModel,
)
from src.application.support.ingestion_service import ingestion_service
from src.application.core.ocpm_service import ocpm_service
from src.presentation.api.routers.auth import require_auth, User


router = APIRouter(prefix="/processes", tags=["Processes"])


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class ProcessType(str, Enum):
    """Type of process data."""
    TRADITIONAL = "traditional"  # Single-case event log
    OBJECT_CENTRIC = "object_centric"  # OCEL 2.0


class SourceFormat(str, Enum):
    """Supported source file formats."""
    CSV = "csv"
    XES = "xes"
    XLSX = "xlsx"
    JSONOCEL = "jsonocel"
    SQLITE = "sqlite"
    XMLOCEL = "xmlocel"


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class ProcessResponse(BaseModel):
    """Unified response for process data (both traditional and OCPM)."""
    id: str
    name: str
    source_file: Optional[str]
    source_format: str
    process_type: str  # "traditional" or "object_centric"
    
    # Common stats
    total_events: int
    total_cases: int = Field(description="Number of cases (traditional) or objects (OCPM)")
    
    # OCPM-specific (empty for traditional)
    object_types: List[str] = []
    objects_per_type: Dict[str, int] = {}
    
    # Common
    activities: List[str] = []
    created_at: str
    
    # Hypermedia links
    _links: Dict[str, Dict[str, str]] = {}


class ProcessListResponse(BaseModel):
    """Paginated list of processes."""
    items: List[ProcessResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProcessDetailResponse(ProcessResponse):
    """Detailed process information."""
    unique_activities: int
    unique_resources: int
    variant_count: int
    date_range: Optional[Dict[str, str]]
    
    # Quality scores
    completeness_score: Optional[float]
    validity_score: Optional[float]


class UploadResponse(BaseModel):
    """Response for process upload."""
    id: str
    name: str
    process_type: str
    total_events: int
    total_cases: int
    object_types: List[str] = []
    validation: Dict[str, Any] = {}
    _links: Dict[str, Dict[str, str]] = {}


class ObjectTypeResponse(BaseModel):
    """Object type information (OCPM)."""
    name: str
    object_count: int
    attributes: List[str] = []


class VariantResponse(BaseModel):
    """Process variant response."""
    variant_hash: str
    activity_trace: str
    activities: List[str]
    length: int
    case_count: int
    frequency_percent: float
    avg_duration_seconds: Optional[float] = None
    median_duration_seconds: Optional[float] = None
    is_happy_path: bool = False
    rank: int


class StatisticsResponse(BaseModel):
    """Unified statistics response."""
    process_id: str
    process_type: str
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
    # OCPM-specific
    object_types: List[str] = []
    objects_per_type: Dict[str, int] = {}


class ColumnDetectionResponse(BaseModel):
    """Column detection for CSV upload."""
    columns: List[str]
    suggestions: Dict[str, Optional[str]]
    sample_rows: List[Dict[str, Any]]


class FilePreviewResponse(BaseModel):
    """File preview before ingestion."""
    filename: str
    file_format: str
    process_type: str  # Detected: traditional or object_centric
    columns: List[str]
    column_types: Dict[str, str]
    suggestions: Dict[str, Optional[str]]
    sample_rows: List[Dict[str, Any]]
    row_count: int
    estimated_case_count: int
    estimated_event_count: int
    # OCPM-specific preview
    detected_object_types: List[str] = []


class QualityIssueResponse(BaseModel):
    """Single quality issue."""
    issue_type: str
    message: str
    severity: str
    affected_rows: int
    column: Optional[str]


class QualityReportResponse(BaseModel):
    """Quality assessment report."""
    process_id: str
    completeness_score: float
    validity_score: float
    overall_score: float
    is_valid: bool
    issues: List[QualityIssueResponse]


class UpdateRequest(BaseModel):
    """Request for updating process metadata."""
    name: Optional[str] = None
    description: Optional[str] = None


class CaseResponse(BaseModel):
    """Single case/trace information."""
    case_id: str
    event_count: int
    variant: str
    duration_seconds: Optional[float]
    start_time: Optional[str]
    end_time: Optional[str]


class CasesResponse(BaseModel):
    """Paginated cases response."""
    items: List[CaseResponse]
    total: int
    page: int
    page_size: int


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def detect_file_format(filename: str) -> tuple[SourceFormat, ProcessType]:
    """Detect file format and process type from filename."""
    filename_lower = filename.lower()
    
    # OCEL formats (Object-Centric)
    if filename_lower.endswith('.jsonocel') or filename_lower.endswith('.json'):
        return SourceFormat.JSONOCEL, ProcessType.OBJECT_CENTRIC
    elif filename_lower.endswith('.sqlite'):
        return SourceFormat.SQLITE, ProcessType.OBJECT_CENTRIC
    elif filename_lower.endswith('.xmlocel'):
        return SourceFormat.XMLOCEL, ProcessType.OBJECT_CENTRIC
    
    # Traditional formats
    elif filename_lower.endswith('.xes'):
        return SourceFormat.XES, ProcessType.TRADITIONAL
    elif filename_lower.endswith('.xlsx'):
        return SourceFormat.XLSX, ProcessType.TRADITIONAL
    else:
        return SourceFormat.CSV, ProcessType.TRADITIONAL


def build_links(process_id: str, base_url: str = "/api/v1/processes") -> Dict[str, Dict[str, str]]:
    """Build hypermedia links for a process."""
    return {
        "self": {"href": f"{base_url}/{process_id}"},
        "statistics": {"href": f"{base_url}/{process_id}/statistics"},
        "quality": {"href": f"{base_url}/{process_id}/quality"},
        "variants": {"href": f"{base_url}/{process_id}/variants"},
        "activities": {"href": f"{base_url}/{process_id}/activities"},
        "cases": {"href": f"{base_url}/{process_id}/cases"},
        "discovery": {"href": f"{base_url}/{process_id}/discovery", "method": "POST"},
        "dfg": {"href": f"{base_url}/{process_id}/dfg"},
        "object_types": {"href": f"{base_url}/{process_id}/object-types"},
    }


# =============================================================================
# CORE ENDPOINTS
# =============================================================================

@router.post("/upload", response_model=UploadResponse)
async def upload_process(
    file: UploadFile = File(..., description="Event log file (CSV, XES, OCEL)"),
    name: Optional[str] = Form(None, description="Custom name for the process"),
    case_id_column: Optional[str] = Form(None, description="Case ID column (CSV only)"),
    activity_column: Optional[str] = Form(None, description="Activity column (CSV only)"),
    timestamp_column: Optional[str] = Form(None, description="Timestamp column (CSV only)"),
    resource_column: Optional[str] = Form(None, description="Resource column (CSV only)"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Upload a process data file.
    
    **Supported Formats:**
    - Traditional: CSV, XES, XLSX
    - Object-Centric (OCEL 2.0): JSONOCEL, SQLite, XMLOCEL
    
    The system auto-detects the format and process type from the file extension.
    For OCEL files, the data is parsed as object-centric. For CSV/XES, it's 
    treated as traditional single-case process mining.
    
    **OCPM Note:** Traditional logs are internally represented as OCPM with 
    one implicit object type ("case").
    """
    filename = file.filename or "unknown"
    source_format, process_type = detect_file_format(filename)
    content = await file.read()
    
    try:
        if process_type == ProcessType.OBJECT_CENTRIC:
            # Parse as OCEL
            ocel = ocpm_service.read_ocel_from_bytes(content, source_format.value)
            stats = ocpm_service.get_ocel_statistics(ocel)
            
            log_name = name or filename.rsplit(".", 1)[0]
            log_model = OCELLogModel(
                name=log_name,
                source_file=filename,
                source_format=source_format.value,
                total_events=stats["total_events"],
                total_objects=stats["total_objects"],
                total_object_types=stats["total_object_types"],
                metadata_json=json.dumps({
                    "activities": stats["activities"],
                    "objects_per_type": stats["objects_per_type"],
                }),
            )
            session.add(log_model)
            
            for ot_name in stats["object_types"]:
                ot_model = OCELObjectTypeModel(
                    log_id=log_model.id,
                    name=ot_name,
                    object_count=stats["objects_per_type"].get(ot_name, 0),
                )
                session.add(ot_model)
            
            await session.commit()
            await session.refresh(log_model)
            
            return UploadResponse(
                id=log_model.id,
                name=log_model.name,
                process_type=ProcessType.OBJECT_CENTRIC.value,
                total_events=log_model.total_events,
                total_cases=log_model.total_objects,
                object_types=stats["object_types"],
                validation={"status": "valid", "issues": []},
                _links=build_links(log_model.id),
            )
        else:
            # Parse as traditional event log
            column_mapping = None
            if any([case_id_column, activity_column, timestamp_column]):
                column_mapping = {
                    "case_id": case_id_column or "case:concept:name",
                    "activity": activity_column or "concept:name",
                    "timestamp": timestamp_column or "time:timestamp",
                    "resource": resource_column,
                }
            
            aggregate = await ingestion_service.ingest_file(
                file_content=content,
                filename=filename,
                name=name,
                column_mapping=column_mapping,
            )
            
            validation = ingestion_service.validate_log(aggregate)
            
            repo = EventLogRepository(session)
            await repo.save(aggregate.log)
            
            return UploadResponse(
                id=str(aggregate.log.id),
                name=aggregate.log.name,
                process_type=ProcessType.TRADITIONAL.value,
                total_events=aggregate.log.total_events,
                total_cases=aggregate.log.total_cases,
                object_types=["case"],  # Implicit single object type
                validation=validation,
                _links=build_links(str(aggregate.log.id)),
            )
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/detect-columns", response_model=ColumnDetectionResponse)
async def detect_columns(
    file: UploadFile = File(...),
):
    """
    Detect column types from a CSV file preview.
    
    Returns column names and suggested mappings for case_id, activity, 
    timestamp, and resource columns.
    """
    content = await file.read()
    
    try:
        result = ingestion_service.detect_columns(content)
        return ColumnDetectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/preview", response_model=FilePreviewResponse)
async def preview_file(
    file: UploadFile = File(...),
):
    """
    Preview a file before full ingestion.
    
    Returns sample data, column detection, format detection, and estimates 
    without persisting anything. Useful for UI preview before upload.
    """
    content = await file.read()
    filename = file.filename or "unknown"
    source_format, process_type = detect_file_format(filename)
    
    try:
        if process_type == ProcessType.TRADITIONAL and source_format == SourceFormat.CSV:
            detection = ingestion_service.detect_columns(content)
            columns = detection["columns"]
            suggestions = detection["suggestions"]
            sample_rows = detection["sample_rows"]
            
            column_types = {}
            for col in columns:
                col_lower = col.lower()
                if "time" in col_lower or "date" in col_lower or "timestamp" in col_lower:
                    column_types[col] = "datetime"
                elif "id" in col_lower or "case" in col_lower:
                    column_types[col] = "string"
                elif "cost" in col_lower or "amount" in col_lower or "price" in col_lower:
                    column_types[col] = "numeric"
                else:
                    column_types[col] = "string"
            
            case_col = suggestions.get("case_id")
            estimated_case_count = len(set(str(row.get(case_col, "")) for row in sample_rows)) if case_col else 0
            
            return FilePreviewResponse(
                filename=filename,
                file_format=source_format.value,
                process_type=process_type.value,
                columns=columns,
                column_types=column_types,
                suggestions=suggestions,
                sample_rows=sample_rows[:10],
                row_count=len(sample_rows),
                estimated_case_count=estimated_case_count,
                estimated_event_count=len(sample_rows),
                detected_object_types=[],
            )
        elif process_type == ProcessType.OBJECT_CENTRIC:
            # OCEL preview
            try:
                ocel = ocpm_service.read_ocel_from_bytes(content, source_format.value)
                stats = ocpm_service.get_ocel_statistics(ocel)
                
                return FilePreviewResponse(
                    filename=filename,
                    file_format=source_format.value,
                    process_type=process_type.value,
                    columns=["events", "objects", "object_types"],
                    column_types={},
                    suggestions={"auto_detected": "ocel"},
                    sample_rows=[],
                    row_count=stats["total_events"],
                    estimated_case_count=stats["total_objects"],
                    estimated_event_count=stats["total_events"],
                    detected_object_types=stats["object_types"],
                )
            except Exception:
                return FilePreviewResponse(
                    filename=filename,
                    file_format=source_format.value,
                    process_type=process_type.value,
                    columns=[],
                    column_types={},
                    suggestions={},
                    sample_rows=[],
                    row_count=0,
                    estimated_case_count=0,
                    estimated_event_count=0,
                    detected_object_types=[],
                )
        else:
            # XES/XLSX preview
            return FilePreviewResponse(
                filename=filename,
                file_format=source_format.value,
                process_type=process_type.value,
                columns=[],
                column_types={},
                suggestions={
                    "case_id": "case:concept:name",
                    "activity": "concept:name",
                    "timestamp": "time:timestamp",
                    "resource": "org:resource",
                },
                sample_rows=[],
                row_count=0,
                estimated_case_count=0,
                estimated_event_count=0,
                detected_object_types=[],
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Preview failed: {str(e)}")


@router.get("/", response_model=ProcessListResponse)
async def list_processes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|name|total_cases|total_events)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    process_type: Optional[str] = Query(None, pattern="^(traditional|object_centric)$"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    List all processes (both traditional and object-centric).
    
    **Query Parameters:**
    - **search**: Filter by name
    - **sort_by**: Sort field
    - **sort_order**: asc or desc
    - **process_type**: Filter by type (traditional, object_centric)
    """
    # Fetch traditional logs
    repo = EventLogRepository(session)
    offset = (page - 1) * page_size
    traditional_logs = await repo.list_all(limit=page_size, offset=offset)
    
    # Fetch OCPM logs
    from sqlalchemy import select
    ocel_result = await session.execute(
        select(OCELLogModel).order_by(OCELLogModel.created_at.desc())
    )
    ocel_logs = ocel_result.scalars().all()
    
    items = []
    
    # Add traditional logs
    if process_type != "object_centric":
        for log in traditional_logs:
            if search and search.lower() not in log.name.lower():
                continue
            items.append(ProcessResponse(
                id=str(log.id),
                name=log.name,
                source_file=log.source_file,
                source_format="csv",  # Most common
                process_type=ProcessType.TRADITIONAL.value,
                total_events=log.metadata.get("total_events", log.total_events),
                total_cases=log.metadata.get("total_cases", log.total_cases),
                object_types=["case"],
                objects_per_type={"case": log.total_cases},
                activities=list(log.activities),
                created_at=log.created_at.isoformat(),
                _links=build_links(str(log.id)),
            ))
    
    # Add OCPM logs
    if process_type != "traditional":
        for log in ocel_logs:
            if search and search.lower() not in log.name.lower():
                continue
            metadata = json.loads(log.metadata_json) if log.metadata_json else {}
            items.append(ProcessResponse(
                id=log.id,
                name=log.name,
                source_file=log.source_file,
                source_format=log.source_format,
                process_type=ProcessType.OBJECT_CENTRIC.value,
                total_events=log.total_events,
                total_cases=log.total_objects,
                object_types=list(metadata.get("objects_per_type", {}).keys()),
                objects_per_type=metadata.get("objects_per_type", {}),
                activities=metadata.get("activities", []),
                created_at=log.created_at.isoformat(),
                _links=build_links(log.id),
            ))
    
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    
    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    items = items[start:end]
    
    return ProcessListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{process_id}", response_model=ProcessDetailResponse)
async def get_process(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get process details.
    
    Returns detailed information about a process, including statistics,
    quality scores, and hypermedia links for available operations.
    """
    # Try traditional log first
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if log:
        start, end = log.date_range
        return ProcessDetailResponse(
            id=str(log.id),
            name=log.name,
            source_file=log.source_file,
            source_format="csv",
            process_type=ProcessType.TRADITIONAL.value,
            total_events=log.total_events,
            total_cases=log.total_cases,
            object_types=["case"],
            objects_per_type={"case": log.total_cases},
            activities=list(log.activities),
            created_at=log.created_at.isoformat(),
            unique_activities=len(log.activities),
            unique_resources=len(log.resources),
            variant_count=len(log.variants),
            date_range={
                "start": start.isoformat() if start else None,
                "end": end.isoformat() if end else None,
            },
            completeness_score=None,
            validity_score=None,
            _links=build_links(str(log.id)),
        )
    
    # Try OCPM log
    from sqlalchemy import select
    result = await session.execute(
        select(OCELLogModel).where(OCELLogModel.id == str(process_id))
    )
    ocel_log = result.scalar_one_or_none()
    
    if ocel_log:
        metadata = json.loads(ocel_log.metadata_json) if ocel_log.metadata_json else {}
        return ProcessDetailResponse(
            id=ocel_log.id,
            name=ocel_log.name,
            source_file=ocel_log.source_file,
            source_format=ocel_log.source_format,
            process_type=ProcessType.OBJECT_CENTRIC.value,
            total_events=ocel_log.total_events,
            total_cases=ocel_log.total_objects,
            object_types=list(metadata.get("objects_per_type", {}).keys()),
            objects_per_type=metadata.get("objects_per_type", {}),
            activities=metadata.get("activities", []),
            created_at=ocel_log.created_at.isoformat(),
            unique_activities=len(metadata.get("activities", [])),
            unique_resources=0,
            variant_count=0,
            date_range=None,
            completeness_score=None,
            validity_score=None,
            _links=build_links(ocel_log.id),
        )
    
    raise HTTPException(status_code=404, detail="Process not found")


@router.patch("/{process_id}", response_model=ProcessResponse)
async def update_process(
    process_id: UUID,
    update: UpdateRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Update process metadata.
    
    Allows updating the name and description of a process.
    """
    # Try traditional log
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if log:
        if update.name is not None:
            log.name = update.name
        if update.description is not None:
            log.metadata["description"] = update.description
        await repo.save(log)
        
        return ProcessResponse(
            id=str(log.id),
            name=log.name,
            source_file=log.source_file,
            source_format="csv",
            process_type=ProcessType.TRADITIONAL.value,
            total_events=log.total_events,
            total_cases=log.total_cases,
            object_types=["case"],
            objects_per_type={"case": log.total_cases},
            activities=list(log.activities),
            created_at=log.created_at.isoformat(),
            _links=build_links(str(log.id)),
        )
    
    # Try OCPM log
    from sqlalchemy import select
    result = await session.execute(
        select(OCELLogModel).where(OCELLogModel.id == str(process_id))
    )
    ocel_log = result.scalar_one_or_none()
    
    if ocel_log:
        if update.name is not None:
            ocel_log.name = update.name
        await session.commit()
        await session.refresh(ocel_log)
        
        metadata = json.loads(ocel_log.metadata_json) if ocel_log.metadata_json else {}
        return ProcessResponse(
            id=ocel_log.id,
            name=ocel_log.name,
            source_file=ocel_log.source_file,
            source_format=ocel_log.source_format,
            process_type=ProcessType.OBJECT_CENTRIC.value,
            total_events=ocel_log.total_events,
            total_cases=ocel_log.total_objects,
            object_types=list(metadata.get("objects_per_type", {}).keys()),
            objects_per_type=metadata.get("objects_per_type", {}),
            activities=metadata.get("activities", []),
            created_at=ocel_log.created_at.isoformat(),
            _links=build_links(ocel_log.id),
        )
    
    raise HTTPException(status_code=404, detail="Process not found")


@router.delete("/{process_id}")
async def delete_process(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Delete a process and all associated data.
    """
    # Try traditional log
    repo = EventLogRepository(session)
    deleted = await repo.delete(process_id)
    
    if deleted:
        return {"status": "deleted", "process_id": str(process_id)}
    
    # Try OCPM log
    from sqlalchemy import select
    result = await session.execute(
        select(OCELLogModel).where(OCELLogModel.id == str(process_id))
    )
    ocel_log = result.scalar_one_or_none()
    
    if ocel_log:
        await session.delete(ocel_log)
        await session.commit()
        return {"status": "deleted", "process_id": str(process_id)}
    
    raise HTTPException(status_code=404, detail="Process not found")


# =============================================================================
# STATISTICS & QUALITY ENDPOINTS
# =============================================================================

@router.get("/{process_id}/statistics", response_model=StatisticsResponse)
async def get_statistics(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get detailed statistics for a process.
    
    Returns comprehensive statistics including activity counts, 
    duration metrics, and start/end activities.
    """
    # Try traditional log
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if log:
        try:
            stats = log.get_statistics()
            
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
            
            start_activities: Dict[str, int] = {}
            end_activities: Dict[str, int] = {}
            for case in log.cases:
                if case.events:
                    sorted_events = sorted(case.events, key=lambda e: e.timestamp.value)
                    start_act = str(sorted_events[0].activity)
                    end_act = str(sorted_events[-1].activity)
                    start_activities[start_act] = start_activities.get(start_act, 0) + 1
                    end_activities[end_act] = end_activities.get(end_act, 0) + 1
            
            return StatisticsResponse(
                process_id=str(process_id),
                process_type=ProcessType.TRADITIONAL.value,
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
                object_types=["case"],
                objects_per_type={"case": stats.case_count},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Statistics calculation failed: {str(e)}")
    
    # Try OCPM log
    from sqlalchemy import select
    result = await session.execute(
        select(OCELLogModel).where(OCELLogModel.id == str(process_id))
    )
    ocel_log = result.scalar_one_or_none()
    
    if ocel_log:
        metadata = json.loads(ocel_log.metadata_json) if ocel_log.metadata_json else {}
        return StatisticsResponse(
            process_id=ocel_log.id,
            process_type=ProcessType.OBJECT_CENTRIC.value,
            event_count=ocel_log.total_events,
            case_count=ocel_log.total_objects,
            activity_count=len(metadata.get("activities", [])),
            variant_count=0,
            resource_count=0,
            date_range_start=None,
            date_range_end=None,
            avg_case_duration_seconds=None,
            median_case_duration_seconds=None,
            min_case_duration_seconds=None,
            max_case_duration_seconds=None,
            activities=metadata.get("activities", []),
            start_activities={},
            end_activities={},
            object_types=list(metadata.get("objects_per_type", {}).keys()),
            objects_per_type=metadata.get("objects_per_type", {}),
        )
    
    raise HTTPException(status_code=404, detail="Process not found")


@router.get("/{process_id}/quality", response_model=QualityReportResponse)
async def get_quality(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get quality assessment for a process.
    
    Returns completeness and validity scores along with identified issues.
    """
    from src.domain.aggregates import EventLogAggregate
    
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        # Check OCPM
        from sqlalchemy import select
        result = await session.execute(
            select(OCELLogModel).where(OCELLogModel.id == str(process_id))
        )
        ocel_log = result.scalar_one_or_none()
        
        if ocel_log:
            # OCPM quality check (simplified)
            return QualityReportResponse(
                process_id=ocel_log.id,
                completeness_score=1.0,
                validity_score=1.0,
                overall_score=1.0,
                is_valid=True,
                issues=[],
            )
        
        raise HTTPException(status_code=404, detail="Process not found")
    
    try:
        aggregate = EventLogAggregate(log)
        validation = ingestion_service.validate_log(aggregate)
        
        issues = []
        
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
        
        single_event_cases = sum(1 for case in log.cases if len(case.events) == 1)
        if single_event_cases > 0:
            issues.append(QualityIssueResponse(
                issue_type="single_event_case",
                message=f"{single_event_cases} cases have only one event",
                severity="low",
                affected_rows=single_event_cases,
                column=None,
            ))
        
        completeness_score = 1.0 - (events_without_resource / max(log.total_events, 1))
        validity_score = 1.0
        overall_score = (completeness_score + validity_score) / 2
        
        return QualityReportResponse(
            process_id=str(process_id),
            completeness_score=round(completeness_score, 3),
            validity_score=round(validity_score, 3),
            overall_score=round(overall_score, 3),
            is_valid=overall_score >= 0.7,
            issues=issues,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality check failed: {str(e)}")


# =============================================================================
# VARIANTS, ACTIVITIES, CASES
# =============================================================================

@router.get("/{process_id}/variants", response_model=List[VariantResponse])
async def get_variants(
    process_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    view: str = Query("enhanced", pattern="^(basic|enhanced)$"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get process variants.
    
    **Views:**
    - basic: Activity trace and counts only
    - enhanced: Includes performance metrics and ranking
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    try:
        variant_cases: Dict[str, list] = {}
        for case in log.cases:
            key = case.variant_key
            if key not in variant_cases:
                variant_cases[key] = []
            variant_cases[key].append(case)
        
        total_cases = len(log.cases)
        variants = []
        
        for rank, (key, cases) in enumerate(sorted(variant_cases.items(), key=lambda x: len(x[1]), reverse=True)):
            activities = key.split(",") if key else []
            activity_trace = " -> ".join(activities)
            variant_hash = hashlib.md5(activity_trace.encode()).hexdigest()[:16]
            
            if view == "enhanced":
                durations = [c.duration.total_seconds for c in cases if c.duration]
                avg_duration = sum(durations) / len(durations) if durations else None
                durations.sort()
                median_duration = durations[len(durations) // 2] if durations else None
            else:
                avg_duration = None
                median_duration = None
            
            variants.append(VariantResponse(
                variant_hash=variant_hash,
                activity_trace=activity_trace,
                activities=activities,
                length=len(activities),
                case_count=len(cases),
                frequency_percent=round(len(cases) / total_cases * 100, 2),
                avg_duration_seconds=round(avg_duration, 2) if avg_duration else None,
                median_duration_seconds=round(median_duration, 2) if median_duration else None,
                is_happy_path=rank == 0,
                rank=rank + 1,
            ))
            
            if len(variants) >= limit:
                break
        
        return variants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variant analysis failed: {str(e)}")


@router.get("/{process_id}/activities")
async def get_activities(
    process_id: UUID,
    filter: Optional[str] = Query(None, pattern="^(start|end|all)$"),
    view: str = Query("basic", pattern="^(basic|performance)$"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get activities in a process.
    
    **Filters:**
    - all: All activities (default)
    - start: Only start activities
    - end: Only end activities
    
    **Views:**
    - basic: Activity names and frequencies
    - performance: Includes duration metrics
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        # Check OCPM
        from sqlalchemy import select
        result = await session.execute(
            select(OCELLogModel).where(OCELLogModel.id == str(process_id))
        )
        ocel_log = result.scalar_one_or_none()
        
        if ocel_log:
            metadata = json.loads(ocel_log.metadata_json) if ocel_log.metadata_json else {}
            return {"activities": metadata.get("activities", []), "filter": filter or "all"}
        
        raise HTTPException(status_code=404, detail="Process not found")
    
    if filter == "start":
        start_activities: Dict[str, int] = {}
        for case in log.cases:
            if case.events:
                sorted_events = sorted(case.events, key=lambda e: e.timestamp.value)
                act = str(sorted_events[0].activity)
                start_activities[act] = start_activities.get(act, 0) + 1
        return {"activities": start_activities, "filter": "start"}
    
    elif filter == "end":
        end_activities: Dict[str, int] = {}
        for case in log.cases:
            if case.events:
                sorted_events = sorted(case.events, key=lambda e: e.timestamp.value)
                act = str(sorted_events[-1].activity)
                end_activities[act] = end_activities.get(act, 0) + 1
        return {"activities": end_activities, "filter": "end"}
    
    else:
        return {"activities": list(log.activities), "filter": "all", "count": len(log.activities)}


@router.get("/{process_id}/cases", response_model=CasesResponse)
async def get_cases(
    process_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get cases/traces in a process.
    
    Returns paginated list of cases with their event counts and durations.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    total = len(log.cases)
    start = (page - 1) * page_size
    end = start + page_size
    
    items = []
    for case in log.cases[start:end]:
        sorted_events = sorted(case.events, key=lambda e: e.timestamp.value) if case.events else []
        items.append(CaseResponse(
            case_id=str(case.case_id),
            event_count=len(case.events),
            variant=case.variant_key[:100] if case.variant_key else "",
            duration_seconds=case.duration.total_seconds if case.duration else None,
            start_time=sorted_events[0].timestamp.to_iso() if sorted_events else None,
            end_time=sorted_events[-1].timestamp.to_iso() if sorted_events else None,
        ))
    
    return CasesResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


# =============================================================================
# OBJECT-CENTRIC SPECIFIC ENDPOINTS
# =============================================================================

@router.get("/{process_id}/object-types", response_model=List[ObjectTypeResponse])
async def get_object_types(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get object types in a process.
    
    For traditional logs, returns ["case"] as the single implicit object type.
    For OCPM logs, returns all detected object types (e.g., Order, Item, Package).
    """
    # Check traditional log first
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if log:
        return [ObjectTypeResponse(
            name="case",
            object_count=log.total_cases,
            attributes=["case_id"],
        )]
    
    # Check OCPM log
    from sqlalchemy import select
    result = await session.execute(
        select(OCELObjectTypeModel).where(OCELObjectTypeModel.log_id == str(process_id))
    )
    object_types = result.scalars().all()
    
    if object_types:
        return [
            ObjectTypeResponse(
                name=ot.name,
                object_count=ot.object_count,
                attributes=list(json.loads(ot.attributes_schema_json).keys()) if ot.attributes_schema_json else [],
            )
            for ot in object_types
        ]
    
    # Check if OCPM log exists but has no object types stored
    ocel_result = await session.execute(
        select(OCELLogModel).where(OCELLogModel.id == str(process_id))
    )
    if ocel_result.scalar_one_or_none():
        return []
    
    raise HTTPException(status_code=404, detail="Process not found")


# =============================================================================
# EXPORT ENDPOINT
# =============================================================================

@router.get("/{process_id}/export")
async def export_process(
    process_id: UUID,
    format: str = Query("csv", pattern="^(csv|xes)$"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Export process data.
    
    **Formats:**
    - csv: Comma-separated values
    - xes: IEEE XES format
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    if format == "csv":
        # Generate CSV
        lines = ["case_id,activity,timestamp,resource"]
        for case in log.cases:
            for event in sorted(case.events, key=lambda e: e.timestamp.value):
                resource = str(event.resource) if event.resource else ""
                lines.append(f"{case.case_id},{event.activity},{event.timestamp.to_iso()},{resource}")
        
        content = "\n".join(lines)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={log.name}.csv"}
        )
    else:
        # XES export (simplified)
        return Response(
            content="<log></log>",  # Placeholder
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={log.name}.xes"}
        )


# =============================================================================
# COMPARE ENDPOINT
# =============================================================================

@router.post("/compare")
async def compare_processes(
    process_ids: List[str],
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Compare multiple processes.
    
    Returns comparative statistics for the specified processes.
    """
    if len(process_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 process IDs required")
    
    results = []
    repo = EventLogRepository(session)
    
    for pid in process_ids:
        try:
            log = await repo.get_by_id(UUID(pid))
            if log:
                results.append({
                    "id": str(log.id),
                    "name": log.name,
                    "total_cases": log.total_cases,
                    "total_events": log.total_events,
                    "unique_activities": len(log.activities),
                    "process_type": "traditional",
                })
        except Exception:
            pass
    
    return {
        "processes": results,
        "comparison": {
            "count": len(results),
        }
    }


# =============================================================================
# SUB-ROUTER INCLUDES
# =============================================================================
# These sub-routers provide nested endpoints under /processes/{process_id}/

from src.presentation.api.routers import (
    processes_discovery,
    processes_conformance,
    processes_performance,
    processes_analytics,
    processes_organization,
)

# Include sub-routers with process_id path parameter
router.include_router(
    processes_discovery.router,
    prefix="/{process_id}/discovery",
    tags=["Processes - Discovery"],
)

router.include_router(
    processes_conformance.router,
    prefix="/{process_id}/conformance",
    tags=["Processes - Conformance"],
)

router.include_router(
    processes_performance.router,
    prefix="/{process_id}/performance",
    tags=["Processes - Performance"],
)

router.include_router(
    processes_analytics.router,
    prefix="/{process_id}/analytics",
    tags=["Processes - Analytics"],
)

router.include_router(
    processes_organization.router,
    prefix="/{process_id}/organization",
    tags=["Processes - Organization"],
)

