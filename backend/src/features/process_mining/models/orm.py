"""Process Mining Feature ORM Models.

Domain-specific models for process mining functionality.
These models reference Platform models via foreign keys.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, deferred, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from src.platform.models import Project


# =============================================================================
# Enums
# =============================================================================


class DatasetStatus(str, Enum):
    """Dataset lifecycle states.
    
    4-Phase Flow:
    1. PENDING → File upload initiated (presigned URL generated)
    2. UPLOADED → File stored in S3, awaiting validation
    3. VALIDATING → Background job validating file
    4. AWAITING_MAPPING → Validation passed, needs column mapping
    5. MAPPED → Column mapping confirmed, ready for ingestion
    6. INGESTING → Background job parsing and storing events
    7. READY → Dataset ready for analysis
    
    Error/Archive states:
    - ERROR → Any phase failed
    - ARCHIVED → Dataset archived by user
    - UNSTRUCTURED → Legacy: file stored without parsing
    - ANALYZING → Legacy: analysis in progress
    """

    PENDING = "pending"
    UPLOADED = "uploaded"  # NEW: File in S3, awaiting validation job
    VALIDATING = "validating"
    AWAITING_MAPPING = "awaiting_mapping"
    MAPPED = "mapped"  # NEW: Mapping confirmed, ready for ingestion
    INGESTING = "ingesting"
    READY = "ready"
    ERROR = "error"
    ARCHIVED = "archived"
    UNSTRUCTURED = "unstructured"
    ANALYZING = "analyzing"


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


# =============================================================================
# Core Feature Models
# =============================================================================


class Dataset(Base):
    """Uploaded dataset metadata."""

    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_format: Mapped[str] = mapped_column(String(20), default="csv")

    # Project association - references Platform layer
    project_id: Mapped[str | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )

    # Statistics
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)

    # JSON columns
    activities_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    statistics_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Lifecycle
    status: Mapped[str] = mapped_column(String(20), default=DatasetStatus.PENDING.value, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    mapping_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    column_suggestions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_columns_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # File metadata
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Job tracking
    validation_job_id: Mapped[str | None] = mapped_column(
        ForeignKey("async_jobs.id", ondelete="SET NULL"), nullable=True
    )
    ingestion_job_id: Mapped[str | None] = mapped_column(
        ForeignKey("async_jobs.id", ondelete="SET NULL"), nullable=True
    )

    # Filtering
    source_dataset_id: Mapped[str | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=True
    )
    filter_config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_filtered: Mapped[bool] = mapped_column(Boolean, default=False)
    filter_stats_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    cases: Mapped[list["ProcessCase"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan", lazy="raise"
    )
    models: Mapped[list["ProcessModel"]] = relationship(
        back_populates="source_dataset", lazy="select"
    )
    source_dataset: Mapped[Optional["Dataset"]] = relationship(
        "Dataset", remote_side="Dataset.id", foreign_keys=[source_dataset_id], lazy="selectin"
    )
    filtered_datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset", back_populates="source_dataset", foreign_keys=[source_dataset_id], lazy="select"
    )
    # One-way relationship to Project (Platform layer doesn't back-reference for proper layering)
    project: Mapped[Optional["Project"]] = relationship()
    uploaded_file: Mapped[Optional["UploadedFile"]] = relationship(
        back_populates="dataset", uselist=False, lazy="selectin"
    )
    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan", lazy="select"
    )
    activity_mappings: Mapped[list["ActivityMapping"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan", lazy="select"
    )
    
    # NEW: 4-Phase Upload Architecture relationships
    columns: Mapped[list["DatasetColumn"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan", lazy="select"
    )
    column_mapping: Mapped[Optional["DatasetColumnMapping"]] = relationship(
        back_populates="dataset", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )
    metadata_record: Mapped[Optional["DatasetMetadata"]] = relationship(
        back_populates="dataset", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )


class UploadedFile(Base):
    """Raw uploaded file metadata."""

    __tablename__ = "uploaded_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    dataset: Mapped["Dataset"] = relationship(back_populates="uploaded_file")


# =============================================================================
# NEW: 4-Phase Upload Architecture Models
# =============================================================================


class DatasetColumn(Base):
    """Detected column metadata from validation phase.
    
    Stores information about each column in the uploaded file,
    including type detection and sample values for mapping UI.
    """

    __tablename__ = "dataset_columns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Column info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dtype: Mapped[str] = mapped_column(String(50), nullable=False)  # STRING, INTEGER, DATETIME, FLOAT
    position: Mapped[int] = mapped_column(Integer, nullable=False)  # Column index in file
    
    # Statistics for mapping UI
    sample_values_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # First 5 unique values
    null_count: Mapped[int] = mapped_column(Integer, default=0)
    null_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    unique_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Process mining column suggestion
    suggested_role: Mapped[str | None] = mapped_column(String(50), nullable=True)  # case_id, activity, timestamp, resource
    suggestion_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0.0-1.0
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="columns")
    
    # Composite unique constraint: one entry per column per dataset
    __table_args__ = (
        Index("ix_dataset_columns_dataset_position", "dataset_id", "position", unique=True),
    )


class DatasetColumnMapping(Base):
    """Column mapping configuration for ingestion.
    
    Stores the mapping from file columns to process mining concepts.
    Can be auto-generated (high confidence) or user-provided.
    """

    __tablename__ = "dataset_column_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    
    # Required mappings
    case_id_column: Mapped[str] = mapped_column(String(255), nullable=False)
    activity_column: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp_column: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Optional mappings
    timestamp_format: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g., "%Y-%m-%d %H:%M:%S"
    resource_column: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Additional columns to preserve as event attributes
    additional_columns_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # ["cost", "department"]
    
    # Confidence scores for each mapping (used for display)
    confidence_scores_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # {"case_id": 0.95, ...}
    
    # Whether this was auto-mapped or user-provided
    auto_mapped: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="column_mapping")


class DatasetMetadata(Base):
    """Computed metadata after ingestion.
    
    Stores aggregate statistics computed after successful ingestion.
    Used for quick display without recomputing from events.
    """

    __tablename__ = "dataset_metadata"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    
    # Core counts
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)
    total_variants: Mapped[int] = mapped_column(Integer, default=0)
    
    # Time range
    first_event_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_event_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Duration stats (seconds)
    avg_case_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_case_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_case_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Resource stats
    total_resources: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Computation tracking
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    computation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)


    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="metadata_record")


class Analysis(Base):
    """Saved process analysis."""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=AnalysisStatus.PENDING.value)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = deferred(mapped_column(Text, nullable=True))
    model_id: Mapped[str | None] = mapped_column(
        ForeignKey("process_models.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

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
    variant_key: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    dataset: Mapped["Dataset"] = relationship(back_populates="cases")
    events: Mapped[list["ProcessEvent"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        lazy="raise",
        order_by="ProcessEvent.timestamp",
    )


class ProcessEvent(Base):
    """Single event in a case.
    
    Scalability Note: This table can grow to millions of rows.
    Activity and resource are normalized via lookup tables for efficiency.
    """

    __tablename__ = "process_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    case_ref_id: Mapped[str] = mapped_column(
        ForeignKey("process_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Normalized FK references (preferred - use these for new code)
    activity_id: Mapped[int | None] = mapped_column(
        ForeignKey("lookup_activities.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    resource_id: Mapped[int | None] = mapped_column(
        ForeignKey("lookup_resources.id", ondelete="SET NULL"), nullable=True
    )
    
    # Legacy string columns (kept for backward compatibility during migration)
    # TODO: Remove after data migration is complete
    activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    resource: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    attributes_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    case: Mapped["ProcessCase"] = relationship(back_populates="events")
    
    # Composite indexes for common query patterns
    __table_args__ = (
        # Query: all events for a case, ordered by time
        Index("ix_events_case_timestamp", "case_ref_id", "timestamp"),
        # Query: activity frequency analysis by time
        Index("ix_events_activity_timestamp", "activity_id", "timestamp"),
        # Query: time-series analytics
        Index("ix_events_timestamp_activity", "timestamp", "activity_id"),
    )


class ProcessModel(Base):
    """Discovered process model."""

    __tablename__ = "process_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_id: Mapped[str | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True
    )
    miner_type: Mapped[str] = mapped_column(String(50), nullable=False)
    model_format: Mapped[str] = mapped_column(String(50), nullable=False)
    serialized_model: Mapped[bytes | None] = deferred(mapped_column(LargeBinary, nullable=True))
    standard_content_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    graph_structure_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    fitness: Mapped[float | None] = mapped_column(Float, nullable=True)
    precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    source_dataset: Mapped[Optional["Dataset"]] = relationship(back_populates="models")
    metrics: Mapped[Optional["ProcessModelMetrics"]] = relationship(
        back_populates="model", uselist=False, cascade="all, delete-orphan"
    )
    graph_caches: Mapped[list["GraphCache"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )


class ProcessModelMetrics(Base):
    """Precomputed metrics for process models."""

    __tablename__ = "process_model_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    model_id: Mapped[str] = mapped_column(
        ForeignKey("process_models.id", ondelete="CASCADE"), nullable=False
    )
    total_activities: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_transitions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    complexity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    fitness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    precision_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    model: Mapped["ProcessModel"] = relationship(back_populates="metrics")


class GraphCache(Base):
    """Cached graph layouts."""

    __tablename__ = "graph_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    model_id: Mapped[str] = mapped_column(
        ForeignKey("process_models.id", ondelete="CASCADE"), nullable=False
    )
    abstraction_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    layout_algorithm: Mapped[str] = mapped_column(String(50), default="dagre", nullable=False)
    cached_layout_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    model: Mapped["ProcessModel"] = relationship(back_populates="graph_caches")


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
    fitness: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    method: Mapped[str] = mapped_column(String(50), default="token_replay")
    generalization: Mapped[float | None] = mapped_column(Float, nullable=True)
    simplicity: Mapped[float | None] = mapped_column(Float, nullable=True)
    f_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    non_fitting_traces: Mapped[int | None] = mapped_column(Integer, nullable=True)
    average_alignment_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    diagnostics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ActivityMapping(Base):
    """Activity mapping for hierarchical abstraction."""

    __tablename__ = "activity_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mapping_rules: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    dataset: Mapped["Dataset"] = relationship(back_populates="activity_mappings")
    hierarchical_models: Mapped[list["HierarchicalProcessModel"]] = relationship(
        back_populates="mapping", cascade="all, delete-orphan"
    )


class AnalyticsCache(Base):
    """Cached analytics results."""

    __tablename__ = "analytics_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ttl_seconds: Mapped[int] = mapped_column(Integer, default=3600)


class SocialNetwork(Base):
    """Social network from organizational mining."""

    __tablename__ = "social_networks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    network_type: Mapped[str] = mapped_column(String(50), nullable=False)
    graph_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PredictionModel(Base):
    """ML prediction model."""

    __tablename__ = "prediction_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False)
    model_binary: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    trained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    """Individual prediction record."""

    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    model_id: Mapped[str] = mapped_column(
        ForeignKey("prediction_models.id", ondelete="CASCADE"), nullable=False
    )
    case_prefix_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    prediction_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    """Prescriptive recommendation for a process case."""

    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    signal_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action_params_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    state: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# =============================================================================
# Workflows
# =============================================================================


class Workflow(Base):
    """Workflow/pipeline definition."""

    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    steps_json: Mapped[str] = mapped_column(Text, nullable=False)
    schedule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    runs: Mapped[list["WorkflowRun"]] = relationship(
        back_populates="workflow", cascade="all, delete-orphan", lazy="selectin"
    )


class WorkflowRun(Base):
    """Workflow execution record."""

    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workflow_id: Mapped[str] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False
    )
    dataset_id: Mapped[str | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default="pending")
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    workflow: Mapped["Workflow"] = relationship(back_populates="runs")


# =============================================================================
# OCEL (Object-Centric Event Logs)
# =============================================================================


class OCELLog(Base):
    """Object-Centric Event Log metadata."""

    __tablename__ = "ocel_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_format: Mapped[str] = mapped_column(String(20), default="jsonocel")
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_objects: Mapped[int] = mapped_column(Integer, default=0)
    total_object_types: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocel_data: Mapped[bytes | None] = deferred(mapped_column(LargeBinary, nullable=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    object_types: Mapped[list["OCELObjectType"]] = relationship(
        back_populates="ocel_log", cascade="all, delete-orphan", lazy="selectin"
    )
    petri_nets: Mapped[list["OCPetriNet"]] = relationship(
        back_populates="ocel_log", cascade="all, delete-orphan", lazy="selectin"
    )


class OCELObjectType(Base):
    """Object type in an OCEL log."""

    __tablename__ = "ocel_object_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("ocel_logs.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    object_count: Mapped[int] = mapped_column(Integer, default=0)
    attributes_schema_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    ocel_log: Mapped["OCELLog"] = relationship(back_populates="object_types")


class OCPetriNet(Base):
    """Object-Centric Petri Net discovered from OCEL."""

    __tablename__ = "oc_petri_nets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("ocel_logs.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    object_types_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    serialized_model: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ocel_log: Mapped["OCELLog"] = relationship(back_populates="petri_nets")


# =============================================================================
# Hierarchical Mining
# =============================================================================


class HierarchicalProcessModel(Base):
    """Process model at a specific abstraction level."""

    __tablename__ = "hierarchical_process_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    mapping_id: Mapped[str] = mapped_column(
        ForeignKey("activity_mappings.id", ondelete="CASCADE"), nullable=False
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    graph_structure_json: Mapped[str] = mapped_column(Text, nullable=False)
    pnml_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    activity_count: Mapped[int] = mapped_column(Integer, nullable=False)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    mapping: Mapped["ActivityMapping"] = relationship(back_populates="hierarchical_models")
