"""ORM models - SQLAlchemy declarative models.

Only 8 essential tables vs the original 84.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


# =============================================================================
# State Machine Enums
# =============================================================================


class DatasetStatus(str, Enum):
    """Dataset lifecycle states."""

    UPLOADING = "uploading"
    VALIDATING = "validating"
    READY = "ready"
    ERROR = "error"
    ARCHIVED = "archived"


class JobStatus(str, Enum):
    """AsyncJob lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Enterprise Hierarchy: Organization → Workspace → Project
# =============================================================================


class Organization(Base):
    """Organization - root of multi-tenancy hierarchy."""

    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    workspaces: Mapped[list["Workspace"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="organization",
        lazy="selectin",
    )


class Workspace(Base):
    """Workspace - work context within an organization containing projects."""

    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="workspaces")
    projects: Mapped[list["Project"]] = relationship(
        back_populates="workspace",
        lazy="selectin",
    )
    members: Mapped[list["WorkspaceMember"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class User(Base):
    """User entity with organization and workspace associations."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    org_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(50), default="local", nullable=False)
    auth_provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="users")
    workspace_memberships: Mapped[list["WorkspaceMember"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class WorkspaceMember(Base):
    """User membership in a workspace with role."""

    __tablename__ = "workspace_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)  # owner, admin, member, viewer

    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="workspace_memberships")


# =============================================================================
# Projects (within Workspace)
# =============================================================================


class Project(Base):
    """Project container for organizing event logs and analyses."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of tags

    # Statistics
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    total_analyses: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    workspace: Mapped[Optional["Workspace"]] = relationship(back_populates="projects")
    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="project",
        lazy="selectin",
    )


# =============================================================================
# Datasets (formerly Event Logs)
# =============================================================================


class Dataset(Base):
    """Uploaded dataset metadata."""

    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_format: Mapped[str] = mapped_column(String(20), default="csv")

    # Project association (optional for backward compatibility)
    project_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )

    # Computed statistics (stored for quick access)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)

    # JSON columns for flexibility
    activities_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    statistics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Lifecycle state machine
    status: Mapped[str] = mapped_column(String(20), default=DatasetStatus.READY.value)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Filtering support
    source_dataset_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=True
    )
    filter_config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_filtered: Mapped[bool] = mapped_column(Boolean, default=False)
    filter_stats_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    cases: Mapped[list["ProcessCase"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    models: Mapped[list["ProcessModel"]] = relationship(
        back_populates="source_dataset",
        lazy="selectin",
    )
    source_dataset: Mapped[Optional["Dataset"]] = relationship(
        "Dataset",
        remote_side="Dataset.id",
        foreign_keys=[source_dataset_id],
        lazy="selectin",
    )
    filtered_datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset",
        back_populates="source_dataset",
        foreign_keys=[source_dataset_id],
        lazy="selectin",
    )
    project: Mapped[Optional["Project"]] = relationship(back_populates="datasets")
    uploaded_file: Mapped[Optional["UploadedFile"]] = relationship(
        back_populates="dataset",
        uselist=False,
        lazy="selectin",
    )
    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class UploadedFile(Base):
    """Raw uploaded file metadata."""

    __tablename__ = "uploaded_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # File info
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # SHA256

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="uploaded_file")


class AnalysisType(str, Enum):
    """Types of process analyses."""

    DISCOVERY = "discovery"
    CONFORMANCE = "conformance"
    ENHANCEMENT = "enhancement"
    VARIANTS = "variants"
    BOTTLENECK = "bottleneck"


class AnalysisStatus(str, Enum):
    """Analysis job lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Analysis(Base):
    """Saved process analysis with configuration and results."""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Configuration
    config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default=AnalysisStatus.PENDING.value)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Cached results
    result_summary_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Link to ProcessModel for discovery analyses
    model_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("process_models.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="analyses")
    process_model: Mapped[Optional["ProcessModel"]] = relationship(lazy="selectin")


class ProcessCase(Base):
    """Individual case/trace in a dataset."""

    __tablename__ = "process_cases"


    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Variant (activity sequence hash for grouping)
    variant_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Case-level timestamps
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="cases")
    events: Mapped[list["ProcessEvent"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ProcessEvent.timestamp",
    )


class ProcessEvent(Base):
    """Single event in a case."""

    __tablename__ = "process_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    case_ref_id: Mapped[str] = mapped_column(
        ForeignKey("process_cases.id", ondelete="CASCADE"), nullable=False
    )
    activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resource: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Additional attributes as JSON
    attributes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    case: Mapped["ProcessCase"] = relationship(back_populates="events")


class ProcessModel(Base):
    """Discovered process model."""

    __tablename__ = "process_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True
    )

    # Mining info
    miner_type: Mapped[str] = mapped_column(String(50), nullable=False)
    model_format: Mapped[str] = mapped_column(String(50), nullable=False)

    # Serialized PM4Py model (pickled)
    serialized_model: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)

    # Quality metrics
    fitness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    source_dataset: Mapped[Optional["Dataset"]] = relationship(back_populates="models")


class ConformanceResult(Base):
    """Conformance checking result."""

    __tablename__ = "conformance_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    model_id: Mapped[str] = mapped_column(
        ForeignKey("process_models.id", ondelete="CASCADE"), nullable=False
    )

    # Results - Core metrics
    fitness: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    method: Mapped[str] = mapped_column(String(50), default="token_replay")

    # Extended quality metrics (PM4py full output)
    generalization: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    simplicity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Harmonic mean of fitness & precision

    # Alignment statistics
    non_fitting_traces: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    average_alignment_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Detailed diagnostics as JSON
    diagnostics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Workflow(Base):
    """Workflow/pipeline definition."""

    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Pipeline definition as JSON
    steps_json: Mapped[str] = mapped_column(Text, nullable=False)

    # Scheduling
    schedule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    runs: Mapped[list["WorkflowRun"]] = relationship(
        back_populates="workflow",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class WorkflowRun(Base):
    """Workflow execution record."""

    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workflow_id: Mapped[str] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False
    )
    dataset_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True
    )

    # Execution state
    status: Mapped[str] = mapped_column(String(50), default="pending")
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    workflow: Mapped["Workflow"] = relationship(back_populates="runs")


# =============================================================================
# OCEL (Object-Centric Event Logs)
# =============================================================================


class OCELLog(Base):
    """Object-Centric Event Log metadata."""

    __tablename__ = "ocel_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_format: Mapped[str] = mapped_column(String(20), default="jsonocel")

    # Statistics
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_objects: Mapped[int] = mapped_column(Integer, default=0)
    total_object_types: Mapped[int] = mapped_column(Integer, default=0)

    # JSON metadata (activities, objects_per_type)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Raw OCEL data for re-parsing (enables OC-DFG and other analyses)
    ocel_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    object_types: Mapped[list["OCELObjectType"]] = relationship(
        back_populates="ocel_log",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    petri_nets: Mapped[list["OCPetriNet"]] = relationship(
        back_populates="ocel_log",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class OCELObjectType(Base):
    """Object type in an OCEL log."""

    __tablename__ = "ocel_object_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    log_id: Mapped[str] = mapped_column(
        ForeignKey("ocel_logs.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    object_count: Mapped[int] = mapped_column(Integer, default=0)

    # Attributes schema as JSON
    attributes_schema_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    ocel_log: Mapped["OCELLog"] = relationship(back_populates="object_types")


class OCPetriNet(Base):
    """Object-Centric Petri Net discovered from OCEL."""

    __tablename__ = "oc_petri_nets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    log_id: Mapped[str] = mapped_column(
        ForeignKey("ocel_logs.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Object types this model covers
    object_types_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Serialized OC-PN (pickled)
    serialized_model: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    ocel_log: Mapped["OCELLog"] = relationship(back_populates="petri_nets")


# =============================================================================
# Analytics & Caching
# =============================================================================


class AnalyticsCache(Base):
    """Cached analytics results for datasets."""

    __tablename__ = "analytics_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ttl_seconds: Mapped[int] = mapped_column(Integer, default=3600)


# =============================================================================
# Social Networks (Organizational Mining)
# =============================================================================


class SocialNetwork(Base):
    """Social network discovered from dataset."""

    __tablename__ = "social_networks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    network_type: Mapped[str] = mapped_column(String(50), nullable=False)
    graph_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metrics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# =============================================================================
# Prediction Models
# =============================================================================


class PredictionModel(Base):
    """ML prediction model for process outcomes."""

    __tablename__ = "prediction_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False)
    model_binary: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    metrics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    """Individual prediction record."""

    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    model_id: Mapped[str] = mapped_column(
        ForeignKey("prediction_models.id", ondelete="CASCADE"), nullable=False
    )
    case_prefix_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prediction_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    """Prescriptive recommendation for a process case."""

    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False)  # Logical ID, not FK to avoid tight coupling

    # The Signal (Why we are recommending this)
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "predicted_delay"
    signal_data_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # The Prescription (What to do)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "reassign_resource"
    action_params_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    state: Mapped[str] = mapped_column(String(20), default="pending")  # pending, accepted, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# =============================================================================
# Async Jobs
# =============================================================================


class AsyncJob(Base):
    """Async job tracking for long-running operations with proper state machine."""

    __tablename__ = "async_jobs"

    # Identity
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # External reference (Celery task ID) - CRITICAL for job status lookups
    task_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)

    # Type & State
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=JobStatus.PENDING.value)
    progress: Mapped[int] = mapped_column(Integer, default=0)

    # Input/Output
    parameters_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps for state transitions
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
