"""
Unified models using SQLModel.

SQLModel combines SQLAlchemy ORM and Pydantic into single model definitions,
eliminating the need for separate db.py and schemas.py files.
"""

import uuid
import json
from datetime import datetime
from typing import Optional, Literal, Any

from sqlmodel import SQLModel, Field, Relationship


# =============================================================================
# Utility Functions
# =============================================================================

def generate_uuid() -> str:
    return str(uuid.uuid4())


# =============================================================================
# User Models
# =============================================================================

class UserBase(SQLModel):
    """Base user fields."""
    pass


class User(UserBase, table=True):
    """User table - for no-auth session management."""
    __tablename__ = "users"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    uploads: list["Upload"] = Relationship(back_populates="user", cascade_delete=True)


class UserResponse(SQLModel):
    """User API response."""
    id: str
    created_at: datetime


# =============================================================================
# Upload Models
# =============================================================================

class UploadBase(SQLModel):
    """Shared upload fields."""
    filename: str
    file_size_bytes: int = 0
    row_count: int = 0


class Upload(UploadBase, table=True):
    """Upload table - tracks uploaded files."""
    __tablename__ = "uploads"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    user_id: str = Field(foreign_key="users.id")
    file_path: str
    status: str = "uploaded"  # uploaded, processing, completed, error
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # NEW: Cache column metadata to avoid re-parsing files
    columns_json: Optional[str] = None
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="uploads")
    mappings: list["Mapping"] = Relationship(back_populates="upload", cascade_delete=True)


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
# Mapping Models
# =============================================================================

class MappingBase(SQLModel):
    """Shared mapping fields (used for create and response)."""
    case_id_column: str
    activity_column: str
    timestamp_column: str
    timestamp_format: Optional[str] = None
    resource_column: Optional[str] = None
    cost_column: Optional[str] = None


class MappingCreate(MappingBase):
    """Mapping creation request."""
    pass


class Mapping(MappingBase, table=True):
    """Mapping table - stores column mapping configurations."""
    __tablename__ = "mappings"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    upload_id: str = Field(foreign_key="uploads.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    upload: Optional[Upload] = Relationship(back_populates="mappings")
    jobs: list["Job"] = Relationship(back_populates="mapping", cascade_delete=True)
    datasets: list["Dataset"] = Relationship(back_populates="mapping", cascade_delete=True)


class MappingResponse(MappingBase):
    """Mapping API response."""
    mapping_id: str
    upload_id: str
    created_at: datetime


# =============================================================================
# Job Models (Background Processing)
# =============================================================================

class Job(SQLModel, table=True):
    """Job table - tracks background processing status."""
    __tablename__ = "jobs"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    mapping_id: str = Field(foreign_key="mappings.id")
    status: str = "queued"  # queued, processing, completed, failed
    progress: int = 0
    progress_message: Optional[str] = None
    error: Optional[str] = None
    dataset_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Relationships
    mapping: Optional[Mapping] = Relationship(back_populates="jobs")


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
    """Request to start processing - no additional params needed for MVP."""
    pass


# =============================================================================
# Dataset Models (Analysis Results)
# =============================================================================

class Dataset(SQLModel, table=True):
    """Dataset table - stores analysis results as JSON."""
    __tablename__ = "datasets"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    mapping_id: str = Field(foreign_key="mappings.id")
    
    # Analysis results stored as JSON strings
    dfg_json: Optional[str] = None
    variants_json: Optional[str] = None
    stats_json: Optional[str] = None
    activity_stats_json: Optional[str] = None
    deviations_json: str = "[]"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    mapping: Optional[Mapping] = Relationship(back_populates="datasets")


# =============================================================================
# Analysis Response Models (React Flow format)
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


class DatasetSummary(SQLModel):
    """Summary response for a dataset."""
    dataset_id: str
    stats: ProcessStats
    created_at: datetime


# =============================================================================
# Validation Models
# =============================================================================

class ValidationError(SQLModel):
    """A validation error for a specific field."""
    field: str
    message: str
    sample_bad_values: list[str] = Field(default_factory=list)


class ValidationWarning(SQLModel):
    """A validation warning (non-blocking)."""
    field: str
    message: str
    suggestion: Optional[str] = None


class ValidationStats(SQLModel):
    """Statistics from validation."""
    total_rows: int
    valid_rows: int
    case_count: int
    activity_count: int
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None


class ValidationResult(SQLModel):
    """Result of mapping validation."""
    is_valid: bool
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[ValidationWarning] = Field(default_factory=list)
    stats: Optional[ValidationStats] = None


# =============================================================================
# Error Response
# =============================================================================

class ErrorResponse(SQLModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
