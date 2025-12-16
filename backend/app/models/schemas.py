"""
Pydantic Schemas - API request/response models.

These are Pydantic-only models (not database tables).
Database tables are in db.py.
"""

from datetime import datetime
from typing import Optional, Literal
from sqlmodel import SQLModel, Field


# =============================================================================
# Organization Schemas
# =============================================================================

class OrganizationBase(SQLModel):
    """Base organization fields."""
    name: str
    slug: str = ""
    description: Optional[str] = None


class OrganizationCreate(SQLModel):
    """Organization creation request."""
    name: str
    description: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    """Organization API response."""
    id: str
    created_at: datetime
    user_count: int = 0
    process_count: int = 0


# =============================================================================
# User Schemas
# =============================================================================

class UserBase(SQLModel):
    """Base user fields."""
    display_name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(SQLModel):
    """User API response."""
    id: str
    org_id: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    last_active_at: datetime


# =============================================================================
# Process Schemas
# =============================================================================

class ProcessBase(SQLModel):
    """Base process fields."""
    name: str
    description: Optional[str] = None
    status: str = "active"


class ProcessCreate(SQLModel):
    """Process creation request."""
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class ProcessUpdate(SQLModel):
    """Process update request."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class ProcessResponse(ProcessBase):
    """Process API response."""
    id: str
    org_id: str
    icon: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    upload_count: int = 0
    dataset_count: int = 0


class ProcessWithStats(ProcessResponse):
    """Process with aggregated statistics."""
    total_cases: int = 0
    total_events: int = 0
    avg_case_duration_ms: float = 0
    last_analysis_at: Optional[datetime] = None


# =============================================================================
# Upload Schemas
# =============================================================================

class UploadBase(SQLModel):
    """Shared upload fields."""
    filename: str
    file_size_bytes: int = 0
    row_count: int = 0


class ColumnMetadata(SQLModel):
    """Metadata about a detected column in uploaded file."""
    name: str
    detected_type: Literal["string", "number", "datetime", "boolean"]
    sample_values: list[str] = Field(default_factory=list)
    null_percentage: float = 0.0
    unique_count: int = 0
    detected_format: Optional[str] = None


class UploadResponse(UploadBase):
    """Upload API response with detected columns."""
    upload_id: str
    columns: list[ColumnMetadata] = []
    created_at: datetime


# =============================================================================
# Mapping Schemas
# =============================================================================

class MappingBase(SQLModel):
    """Shared mapping fields."""
    case_id_column: str
    activity_column: str
    timestamp_column: str
    timestamp_format: Optional[str] = None
    resource_column: Optional[str] = None
    cost_column: Optional[str] = None


class MappingCreate(MappingBase):
    """Mapping creation request."""
    pass


class MappingResponse(MappingBase):
    """Mapping API response."""
    mapping_id: str
    upload_id: str
    created_at: datetime


# =============================================================================
# Job Schemas
# =============================================================================

class JobResponse(SQLModel):
    """Job status API response."""
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    progress: int = 0
    progress_message: Optional[str] = None
    dataset_id: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class ProcessingRequest(SQLModel):
    """Request to start processing."""
    pass


# =============================================================================
# Dataset Schemas
# =============================================================================

class DatasetSummary(SQLModel):
    """Summary response for a dataset."""
    id: str
    created_at: datetime


# =============================================================================
# Analysis Schemas (React Flow format)
# =============================================================================

class NodePosition(SQLModel):
    """Position for React Flow node."""
    x: float
    y: float


class ActivityNodeData(SQLModel):
    """Data for activity node in process graph."""
    label: str
    frequency: int
    isStart: bool = False
    isEnd: bool = False
    avgDuration: float = 0
    maxFrequency: int = 0


class DFGNode(SQLModel):
    """Node in DFG for React Flow."""
    id: str
    type: str = "activityNode"
    position: NodePosition
    data: ActivityNodeData


class EdgeData(SQLModel):
    """Data for edge in process graph."""
    frequency: int
    avgDuration: float = 0


class DFGEdge(SQLModel):
    """Edge in DFG for React Flow."""
    id: str
    source: str
    target: str
    type: str = "processEdge"
    data: EdgeData


class DFGSummary(SQLModel):
    """Summary statistics for DFG."""
    totalCases: int
    totalEvents: int
    totalActivities: int
    totalVariants: int


class DFGResponse(SQLModel):
    """Complete DFG response in React Flow format."""
    nodes: list[DFGNode]
    edges: list[DFGEdge]
    summary: DFGSummary


class VariantItem(SQLModel):
    """A single process variant."""
    id: str
    sequence: list[str]
    trace_display: str
    case_count: int
    percentage: float
    avg_duration_ms: float
    is_happy_path: bool = False
    case_ids: list[str] = Field(default_factory=list)


class VariantsResponse(SQLModel):
    """Response with variant list."""
    total: int
    variants: list[VariantItem]


class ActivityStat(SQLModel):
    """Statistics for a single activity."""
    name: str
    frequency: int
    frequency_pct: float
    is_start: bool
    is_end: bool
    avg_duration_ms: float


class Deviation(SQLModel):
    """A detected process deviation."""
    type: Literal["rework", "skip", "unusual_path"]
    description: str
    affected_cases: list[str]
    frequency: int


class ProcessStats(SQLModel):
    """Overall process statistics."""
    total_cases: int
    total_events: int
    total_activities: int
    total_variants: int
    avg_case_duration_ms: float
    median_case_duration_ms: float
    start_activities: list[str]
    end_activities: list[str]


# =============================================================================
# Validation Schemas
# =============================================================================

class ValidationError(SQLModel):
    """Validation error detail."""
    field: str
    message: str
    row: Optional[int] = None


class ValidationWarning(SQLModel):
    """Validation warning detail."""
    field: str
    message: str
    count: int = 1


class ValidationStats(SQLModel):
    """Validation statistics."""
    total_rows: int
    valid_rows: int
    error_rows: int
    null_counts: dict[str, int] = {}


class ValidationResult(SQLModel):
    """Complete validation result."""
    is_valid: bool
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []
    stats: ValidationStats


# =============================================================================
# Audit Log Schemas
# =============================================================================

class AuditLogCreate(SQLModel):
    """Audit log creation (internal use only)."""
    user_id: Optional[str] = None
    entity_type: str
    entity_id: Optional[str] = None
    action: str
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None


class AuditLogResponse(SQLModel):
    """Audit log API response."""
    id: str
    user_id: Optional[str]
    entity_type: str
    entity_id: Optional[str]
    action: str
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    request_path: Optional[str] = None
    created_at: datetime


class AuditLogFilter(SQLModel):
    """Audit log query filters."""
    user_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


# =============================================================================
# Insight Schemas
# =============================================================================

class InsightCreate(SQLModel):
    """Insight creation (internal use during analysis)."""
    dataset_id: str
    insight_type: str
    severity: str = "medium"
    severity_score: float = 0.5
    title: str
    description: str
    affected_activity: Optional[str] = None
    affected_case_count: int = 0
    affected_case_ids: Optional[list[str]] = None
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    metric_threshold: Optional[float] = None
    data: Optional[dict] = None


class InsightResponse(SQLModel):
    """Insight API response."""
    id: str
    dataset_id: str
    insight_type: str
    severity: str
    severity_score: float
    title: str
    description: str
    affected_activity: Optional[str]
    affected_case_count: int
    metric_name: Optional[str]
    metric_value: Optional[float]
    is_acknowledged: bool
    created_at: datetime


class InsightSummary(SQLModel):
    """Aggregated insight summary for a process/dataset."""
    total_insights: int = 0
    by_type: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    critical_count: int = 0
    unacknowledged_count: int = 0


# =============================================================================
# Error Schemas
# =============================================================================

class ErrorResponse(SQLModel):
    """Standard error response."""
    detail: str
    code: Optional[str] = None
