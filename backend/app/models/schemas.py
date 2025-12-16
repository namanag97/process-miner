"""
Pydantic models for API request/response schemas.

These models define the contract between frontend and backend.
"""

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Column Detection & Upload
# ============================================================================

class ColumnMetadata(BaseModel):
    """Metadata about a detected column in uploaded file."""
    
    name: str
    detected_type: Literal["string", "number", "datetime", "boolean"]
    sample_values: list[str] = Field(default_factory=list, max_length=5)
    null_percentage: float = 0.0
    unique_count: int = 0
    detected_format: str | None = None  # For datetime columns


class UploadResponse(BaseModel):
    """Response after file upload with detected columns."""
    
    upload_id: str
    filename: str
    file_size_bytes: int
    row_count: int
    columns: list[ColumnMetadata]
    created_at: datetime


class UploadInfo(BaseModel):
    """Brief upload info for listings."""
    
    upload_id: str
    filename: str
    row_count: int
    column_count: int
    created_at: datetime


# ============================================================================
# Column Mapping
# ============================================================================

class MappingCreate(BaseModel):
    """Request to create a column mapping."""
    
    case_id_column: str
    activity_column: str
    timestamp_column: str
    timestamp_format: str | None = None  # Auto-detect if not provided
    resource_column: str | None = None
    cost_column: str | None = None


class MappingResponse(BaseModel):
    """Response after creating a mapping."""
    
    mapping_id: str
    upload_id: str
    case_id_column: str
    activity_column: str
    timestamp_column: str
    timestamp_format: str | None = None
    resource_column: str | None = None
    cost_column: str | None = None
    created_at: datetime


class ValidationError(BaseModel):
    """A validation error for a specific field."""
    
    field: str
    message: str
    sample_bad_values: list[str] = Field(default_factory=list)


class ValidationWarning(BaseModel):
    """A validation warning (non-blocking)."""
    
    field: str
    message: str
    suggestion: str | None = None


class ValidationStats(BaseModel):
    """Statistics from validation."""
    
    total_rows: int
    valid_rows: int
    case_count: int
    activity_count: int
    date_range_start: datetime | None = None
    date_range_end: datetime | None = None


class ValidationResult(BaseModel):
    """Result of mapping validation."""
    
    is_valid: bool
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[ValidationWarning] = Field(default_factory=list)
    stats: ValidationStats | None = None


# ============================================================================
# Processing & Jobs
# ============================================================================

class ProcessingRequest(BaseModel):
    """Request to start processing."""
    pass  # No additional params needed for MVP


class JobResponse(BaseModel):
    """Response with job status."""
    
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    progress: int = 0  # 0-100
    progress_message: str | None = None
    dataset_id: str | None = None  # Set when completed
    error: str | None = None  # Set when failed
    created_at: datetime
    completed_at: datetime | None = None


# ============================================================================
# Analysis Results
# ============================================================================

class NodePosition(BaseModel):
    """Position for React Flow node."""
    
    x: float
    y: float


class ActivityNodeData(BaseModel):
    """Data for activity node in process graph."""
    
    label: str
    frequency: int
    isStart: bool = False
    isEnd: bool = False
    avgDuration: float = 0  # milliseconds
    maxFrequency: int = 0  # For scaling


class DFGNode(BaseModel):
    """Node in DFG for React Flow."""
    
    id: str
    type: str = "activityNode"
    position: NodePosition
    data: ActivityNodeData


class EdgeData(BaseModel):
    """Data for edge in process graph."""
    
    frequency: int
    avgDuration: float = 0  # milliseconds


class DFGEdge(BaseModel):
    """Edge in DFG for React Flow."""
    
    id: str
    source: str
    target: str
    type: str = "processEdge"
    data: EdgeData


class DFGSummary(BaseModel):
    """Summary statistics for DFG."""
    
    totalCases: int
    totalEvents: int
    totalActivities: int
    totalVariants: int


class DFGResponse(BaseModel):
    """Complete DFG response in React Flow format."""
    
    nodes: list[DFGNode]
    edges: list[DFGEdge]
    summary: DFGSummary


class VariantItem(BaseModel):
    """A single process variant."""
    
    id: str
    sequence: list[str]
    trace_display: str  # "A → B → C"
    case_count: int
    percentage: float
    avg_duration_ms: float
    is_happy_path: bool = False
    case_ids: list[str] = Field(default_factory=list)


class VariantsResponse(BaseModel):
    """Response with variant list."""
    
    total: int
    variants: list[VariantItem]


class ActivityStat(BaseModel):
    """Statistics for a single activity."""
    
    name: str
    frequency: int
    frequency_pct: float
    is_start: bool
    is_end: bool
    avg_duration_ms: float


class Deviation(BaseModel):
    """A detected process deviation."""
    
    type: Literal["rework", "skip", "unusual_path"]
    description: str
    affected_cases: list[str]
    frequency: int


class ProcessStats(BaseModel):
    """Overall process statistics."""
    
    total_cases: int
    total_events: int
    total_activities: int
    total_variants: int
    avg_case_duration_ms: float
    median_case_duration_ms: float
    start_activities: list[str]
    end_activities: list[str]


class DatasetSummary(BaseModel):
    """Summary response for a dataset."""
    
    dataset_id: str
    stats: ProcessStats
    created_at: datetime


# ============================================================================
# Error Responses
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str
    detail: str | None = None
