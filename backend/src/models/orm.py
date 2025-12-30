"""ORM models - SQLAlchemy declarative models.

Only 8 essential tables vs the original 84.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class EventLog(Base):
    """Uploaded event log metadata."""

    __tablename__ = "event_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_format: Mapped[str] = mapped_column(String(20), default="csv")

    # Computed statistics (stored for quick access)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)

    # JSON columns for flexibility
    activities_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    statistics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Filtering support
    source_log_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("event_logs.id", ondelete="CASCADE"), nullable=True
    )
    filter_config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_filtered: Mapped[bool] = mapped_column(Boolean, default=False)
    filter_stats_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    cases: Mapped[list["ProcessCase"]] = relationship(
        back_populates="event_log",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    models: Mapped[list["ProcessModel"]] = relationship(
        back_populates="source_log",
        lazy="selectin",
    )
    source_log: Mapped[Optional["EventLog"]] = relationship(
        "EventLog",
        remote_side="EventLog.id",
        foreign_keys=[source_log_id],
        lazy="selectin",
    )
    filtered_logs: Mapped[list["EventLog"]] = relationship(
        "EventLog",
        back_populates="source_log",
        foreign_keys=[source_log_id],
        lazy="selectin",
    )


class ProcessCase(Base):
    """Individual case/trace in an event log."""

    __tablename__ = "process_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    log_id: Mapped[str] = mapped_column(
        ForeignKey("event_logs.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Variant (activity sequence hash for grouping)
    variant_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Case-level timestamps
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    event_log: Mapped["EventLog"] = relationship(back_populates="cases")
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
    log_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("event_logs.id", ondelete="SET NULL"), nullable=True
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
    source_log: Mapped[Optional["EventLog"]] = relationship(back_populates="models")


class ConformanceResult(Base):
    """Conformance checking result."""

    __tablename__ = "conformance_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    log_id: Mapped[str] = mapped_column(
        ForeignKey("event_logs.id", ondelete="CASCADE"), nullable=False
    )
    model_id: Mapped[str] = mapped_column(
        ForeignKey("process_models.id", ondelete="CASCADE"), nullable=False
    )

    # Results
    fitness: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    method: Mapped[str] = mapped_column(String(50), default="token_replay")

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
    log_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("event_logs.id", ondelete="SET NULL"), nullable=True
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
    """Cached analytics results for event logs."""

    __tablename__ = "analytics_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    log_id: Mapped[str] = mapped_column(
        ForeignKey("event_logs.id", ondelete="CASCADE"), nullable=False
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ttl_seconds: Mapped[int] = mapped_column(Integer, default=3600)


# =============================================================================
# Social Networks (Organizational Mining)
# =============================================================================


class SocialNetwork(Base):
    """Social network discovered from event log."""

    __tablename__ = "social_networks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    log_id: Mapped[str] = mapped_column(
        ForeignKey("event_logs.id", ondelete="CASCADE"), nullable=False
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
    log_id: Mapped[str] = mapped_column(
        ForeignKey("event_logs.id", ondelete="CASCADE"), nullable=False
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


# =============================================================================
# Async Jobs
# =============================================================================


class AsyncJob(Base):
    """Async job tracking for long-running operations."""

    __tablename__ = "async_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
