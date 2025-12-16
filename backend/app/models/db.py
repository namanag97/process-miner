"""
Database Models - Consolidated SQLModel tables.

Domain Hierarchy:
Organization (1) → Process (n) → Upload (n) → Mapping (n) → Job (n) → Dataset (n)

All database tables are defined here. Pydantic-only schemas are in schemas.py.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship


# =============================================================================
# Utility Functions
# =============================================================================

def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid4())


# =============================================================================
# Enums
# =============================================================================

class UploadStatus(str, Enum):
    """Status of an uploaded file."""
    PENDING = "pending"
    VALIDATED = "validated"
    FAILED = "failed"


class JobStatus(str, Enum):
    """Status of a processing job."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Database Models (in domain hierarchy order)
# =============================================================================


class Organization(SQLModel, table=True):
    """Organization table - top-level container for multi-tenancy."""
    __tablename__ = "organizations"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    name: str = Field(index=True)
    slug: str = Field(index=True, unique=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    users: list["User"] = Relationship(back_populates="organization")
    processes: list["Process"] = Relationship(back_populates="organization", cascade_delete=True)


class User(SQLModel, table=True):
    """User table - for session management."""
    __tablename__ = "users"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    org_id: Optional[str] = Field(default=None, foreign_key="organizations.id", index=True)
    display_name: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_active_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="users")
    uploads: list["Upload"] = Relationship(back_populates="user", cascade_delete=True)
    audit_logs: list["AuditLog"] = Relationship(back_populates="user")


class Process(SQLModel, table=True):
    """Process table - groups uploads by business process."""
    __tablename__ = "processes"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    org_id: str = Field(foreign_key="organizations.id", index=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    status: str = "active"  # active, archived, draft
    icon: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="processes")
    uploads: list["Upload"] = Relationship(back_populates="process", cascade_delete=True)


class Upload(SQLModel, table=True):
    """Upload table - tracks uploaded files."""
    __tablename__ = "uploads"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    process_id: Optional[str] = Field(default=None, foreign_key="processes.id", index=True)
    filename: str
    file_path: str
    file_size_bytes: int = 0
    row_count: int = 0
    status: str = UploadStatus.PENDING.value
    error_message: Optional[str] = None
    columns_json: Optional[str] = None  # Cached column metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="uploads")
    process: Optional["Process"] = Relationship(back_populates="uploads")
    mappings: list["Mapping"] = Relationship(back_populates="upload", cascade_delete=True)


class Mapping(SQLModel, table=True):
    """Mapping table - stores column mapping configurations."""
    __tablename__ = "mappings"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    upload_id: str = Field(foreign_key="uploads.id", index=True)
    case_id_column: str
    activity_column: str
    timestamp_column: str
    timestamp_format: Optional[str] = None
    resource_column: Optional[str] = None
    cost_column: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    upload: Optional["Upload"] = Relationship(back_populates="mappings")
    jobs: list["Job"] = Relationship(back_populates="mapping", cascade_delete=True)
    datasets: list["Dataset"] = Relationship(back_populates="mapping", cascade_delete=True)


class Job(SQLModel, table=True):
    """Job table - tracks background processing status."""
    __tablename__ = "jobs"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    mapping_id: str = Field(foreign_key="mappings.id", index=True)
    status: str = JobStatus.QUEUED.value
    progress: int = 0
    progress_message: Optional[str] = None
    error: Optional[str] = None
    dataset_id: Optional[str] = Field(default=None, foreign_key="datasets.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Relationships
    mapping: Optional["Mapping"] = Relationship(back_populates="jobs")
    dataset: Optional["Dataset"] = Relationship(back_populates="job")


class Dataset(SQLModel, table=True):
    """Dataset table - stores analysis results as JSON."""
    __tablename__ = "datasets"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    mapping_id: str = Field(foreign_key="mappings.id", index=True)
    process_id: Optional[str] = Field(default=None, foreign_key="processes.id", index=True)  # Denormalized
    
    # Analysis results stored as JSON strings
    dfg_json: Optional[str] = None
    variants_json: Optional[str] = None
    stats_json: Optional[str] = None
    activity_stats_json: Optional[str] = None
    deviations_json: str = "[]"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    mapping: Optional["Mapping"] = Relationship(back_populates="datasets")
    insights: list["Insight"] = Relationship(back_populates="dataset", cascade_delete=True)
    job: Optional["Job"] = Relationship(back_populates="dataset")


class AuditLog(SQLModel, table=True):
    """Audit log table - tracks all significant user actions."""
    __tablename__ = "audit_logs"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    user_id: Optional[str] = Field(default=None, foreign_key="users.id", index=True)
    entity_type: str = Field(index=True)
    entity_id: Optional[str] = Field(default=None, index=True)
    action: str = Field(index=True)
    details_json: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = None
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="audit_logs")
    
    @property
    def details(self) -> dict:
        """Parse details JSON."""
        if not self.details_json:
            return {}
        import json
        return json.loads(self.details_json)
    
    @details.setter
    def details(self, value: dict):
        """Serialize details to JSON."""
        import json
        self.details_json = json.dumps(value) if value else None


class Insight(SQLModel, table=True):
    """Insight table - queryable extracted findings from analysis."""
    __tablename__ = "insights"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    dataset_id: str = Field(foreign_key="datasets.id", index=True)
    insight_type: str = Field(index=True)  # bottleneck, rework, deviation, kpi_alert
    severity: str = Field(default="medium", index=True)  # low, medium, high, critical
    severity_score: float = Field(default=0.5)
    title: str
    description: str
    affected_activity: Optional[str] = None
    affected_case_count: int = 0
    affected_case_ids_json: Optional[str] = None
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    metric_threshold: Optional[float] = None
    data_json: Optional[str] = None
    is_acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = None
    
    # Relationships
    dataset: Optional["Dataset"] = Relationship(back_populates="insights")
    
    @property
    def affected_case_ids(self) -> list[str]:
        """Parse case IDs JSON."""
        if not self.affected_case_ids_json:
            return []
        import json
        return json.loads(self.affected_case_ids_json)
    
    @property
    def data(self) -> dict:
        """Parse data JSON."""
        if not self.data_json:
            return {}
        import json
        return json.loads(self.data_json)
