"""SQLAlchemy ORM models for persistence."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.database import Base


def generate_uuid() -> str:
    """Generate a UUID string for primary keys."""
    return str(uuid4())


# =============================================================================
# REUSABLE MIXINS - Reduce code duplication across models
# =============================================================================


class IDMixin:
    """Mixin providing UUID primary key."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)


class TimestampMixin:
    """Mixin providing created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CreatedAtMixin:
    """Mixin providing only created_at timestamp (for immutable entities)."""

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WorkspaceMixin:
    """Mixin providing optional workspace_id for multi-tenancy."""

    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)


# =============================================================================
# CORE MODELS
# =============================================================================


class EventLogModel(IDMixin, TimestampMixin, Base):
    """ORM model for Event Logs."""

    __tablename__ = "event_logs"

    project_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=True, index=True
    )  # Multi-tenancy
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    state: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)  # EventLogState
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    activity_count: Mapped[int] = mapped_column(Integer, default=0)
    variant_count: Mapped[int] = mapped_column(Integer, default=0)
    statistics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # LogStatistics
    quality_report_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # QualityReport
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped[Optional["ProjectModel"]] = relationship(
        "ProjectModel", back_populates="event_logs", foreign_keys=[project_id]
    )
    cases: Mapped[list["ProcessCaseModel"]] = relationship(
        "ProcessCaseModel",
        back_populates="event_log",
        cascade="all, delete-orphan",
    )
    models: Mapped[list["ProcessModelModel"]] = relationship(
        "ProcessModelModel",
        back_populates="source_log",
        cascade="all, delete-orphan",
    )


class ProcessCaseModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for Process Cases."""

    __tablename__ = "process_cases"

    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False)
    variant_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attributes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    event_log: Mapped["EventLogModel"] = relationship("EventLogModel", back_populates="cases")
    events: Mapped[list["ProcessEventModel"]] = relationship(
        "ProcessEventModel",
        back_populates="process_case",
        cascade="all, delete-orphan",
        order_by="ProcessEventModel.timestamp",
    )


class ProcessEventModel(IDMixin, Base):
    """ORM model for Process Events."""

    __tablename__ = "process_events"

    case_db_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_cases.id"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resource: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    attributes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    process_case: Mapped["ProcessCaseModel"] = relationship(
        "ProcessCaseModel", back_populates="events"
    )


class ProcessModelModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for Process Models."""

    __tablename__ = "process_models"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    format: Mapped[str] = mapped_column(String(50), nullable=False)  # petri_net, bpmn, etc.
    miner_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    state: Mapped[str] = mapped_column(
        String(50), default="discovering", nullable=False
    )  # ProcessModelState
    source_log_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=True
    )
    repository_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("process_model_repositories.id"), nullable=True, index=True
    )
    serialized_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    filter_config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # FilterConfig
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    source_log: Mapped[Optional["EventLogModel"]] = relationship(
        "EventLogModel", back_populates="models"
    )
    repository: Mapped[Optional["ProcessModelRepositoryModel"]] = relationship(
        "ProcessModelRepositoryModel", back_populates="models", foreign_keys=[repository_id]
    )
    conformance_results: Mapped[list["ConformanceResultModel"]] = relationship(
        "ConformanceResultModel",
        back_populates="model",
        cascade="all, delete-orphan",
    )


class ConformanceResultModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for Conformance Results."""

    __tablename__ = "conformance_results"

    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False)
    model_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_models.id"), nullable=False
    )
    state: Mapped[str] = mapped_column(
        String(50), default="requested", nullable=False
    )  # ConformanceResultState
    fitness: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    generalization: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    simplicity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deviation_count: Mapped[int] = mapped_column(Integer, default=0)
    deviation_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deviations_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # List[Deviation]
    deviation_summary_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # DeviationSummary

    # Relationships
    model: Mapped["ProcessModelModel"] = relationship(
        "ProcessModelModel", back_populates="conformance_results"
    )


class DomainEventModel(IDMixin, Base):
    """ORM model for storing domain events."""

    __tablename__ = "domain_events"

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    processed: Mapped[bool] = mapped_column(
        Integer, default=False
    )  # SQLite doesn't have native bool


class BackgroundJobModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for background jobs/tasks."""

    __tablename__ = "background_jobs"

    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, running, completed, failed
    payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


# =============================================================================
# PHASE 1: CORE PROCESS MINING MODELS
# =============================================================================


class EventLogVersionModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for Event Log Versions - enables log versioning."""

    __tablename__ = "event_log_versions"

    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    version_label: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    version_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="draft", nullable=False
    )  # draft, active, superseded, archived
    observation_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    observation_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


class ActivityTypeModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for Activity Types - rich activity metadata."""

    __tablename__ = "activity_types"

    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    version_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("event_log_versions.id"), nullable=True, index=True
    )
    activity_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    activity_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activity_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activity_type: Mapped[str] = mapped_column(
        String(50), default="task", nullable=False
    )  # task, decision, start, end, intermediate, subprocess
    is_automated: Mapped[bool] = mapped_column(Integer, default=False)
    is_value_adding: Mapped[bool] = mapped_column(Integer, default=True)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class ProcessVariantModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for Process Variants - unique activity sequences."""

    __tablename__ = "process_variants"

    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    version_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("event_log_versions.id"), nullable=True, index=True
    )
    variant_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # MD5/SHA hash of activity trace
    activity_trace: Mapped[str] = mapped_column(Text, nullable=False)  # A->B->C->D format
    variant_length: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    case_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    frequency_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_happy_path: Mapped[bool] = mapped_column(Integer, default=False)
    is_compliant: Mapped[bool] = mapped_column(Integer, default=True)
    variant_rank: Mapped[int] = mapped_column(Integer, default=0)


class VariantActivityModel(IDMixin, Base):
    """ORM model for Variant Activities - activities in sequence within a variant."""

    __tablename__ = "variant_activities"

    variant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_variants.id"), nullable=False, index=True
    )
    activity_type_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence_position: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-indexed position


# =============================================================================
# TRANSITION / DFG MODELS (Process Perspective)
# =============================================================================


class TransitionModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for DFG transitions (edges between activities)."""

    __tablename__ = "transitions"

    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    source_activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    min_duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    max_duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)


# =============================================================================
# RESOURCE PERSPECTIVE MODELS
# =============================================================================


class ResourceProfileModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for resource profiles extracted from event logs."""

    __tablename__ = "resource_profiles"

    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    identifier: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    avg_activities_per_case: Mapped[float] = mapped_column(Float, default=0.0)
    frequent_activities_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class HandoffModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for resource handoffs."""

    __tablename__ = "handoffs"

    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    from_resource: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    to_resource: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    activity: Mapped[str] = mapped_column(String(255), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_handoff_time_seconds: Mapped[float] = mapped_column(Float, default=0.0)


# =============================================================================
# SLA MODELS (Time Perspective)
# =============================================================================


class SLADefinitionModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for SLA definitions."""

    __tablename__ = "sla_definitions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    warning_threshold_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    scope: Mapped[str] = mapped_column(String(50), nullable=False)  # case, activity, transition
    activity_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_activity: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_activity: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Integer, default=True)


class SLABreachModel(IDMixin, Base):
    """ORM model for SLA breach records."""

    __tablename__ = "sla_breaches"

    sla_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sla_definitions.id"), nullable=False, index=True
    )
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    actual_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    exceeded_by_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # met, warning, breached
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# =============================================================================
# PHASE 2: PROCESS DISCOVERY & MODEL MANAGEMENT
# =============================================================================


class ProcessModelRepositoryModel(IDMixin, CreatedAtMixin, WorkspaceMixin, Base):
    """ORM model for Process Model Repositories - catalogs of models."""

    __tablename__ = "process_model_repositories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    repository_type: Mapped[str] = mapped_column(
        String(50), default="discovered"
    )  # discovered, reference, imported

    # Relationships
    models: Mapped[list["ProcessModelModel"]] = relationship(
        "ProcessModelModel",
        back_populates="repository",
        foreign_keys="ProcessModelModel.repository_id",
    )


class ProcessModelVersionModel(IDMixin, CreatedAtMixin, Base):
    """ORM model for Process Model Versions - versioning for models."""

    __tablename__ = "process_model_versions"

    model_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_models.id"), nullable=False, index=True
    )
    discovery_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("process_discovery_runs.id"), nullable=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    version_label: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, active, archived
    notation_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # petri_net, bpmn, process_tree, dfg
    model_serialized_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_pnml: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_bpmn_xml: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_image_svg: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    canvas_layout_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    petri_places: Mapped[list["PetriNetPlaceModel"]] = relationship(
        "PetriNetPlaceModel", back_populates="version", cascade="all, delete-orphan"
    )
    petri_transitions: Mapped[list["PetriNetTransitionModel"]] = relationship(
        "PetriNetTransitionModel", back_populates="version", cascade="all, delete-orphan"
    )
    petri_arcs: Mapped[list["PetriNetArcModel"]] = relationship(
        "PetriNetArcModel", back_populates="version", cascade="all, delete-orphan"
    )
    dfg_edges: Mapped[list["DirectlyFollowsEdgeModel"]] = relationship(
        "DirectlyFollowsEdgeModel", back_populates="version", cascade="all, delete-orphan"
    )
    quality_metrics: Mapped[list["ModelQualityMetricModel"]] = relationship(
        "ModelQualityMetricModel", back_populates="version", cascade="all, delete-orphan"
    )


class ProcessDiscoveryRunModel(Base):
    """ORM model for Process Discovery Runs - discovery job tracking."""

    __tablename__ = "process_discovery_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    event_log_version_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("event_log_versions.id"), nullable=True
    )
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    initiated_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    algorithm: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # alpha, alpha_plus, heuristic, inductive, dfg
    output_notation: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # petri_net, bpmn, process_tree, dfg
    status: Mapped[str] = mapped_column(
        String(50), default="queued"
    )  # queued, preprocessing, mining, evaluating, completed, failed
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    events_processed: Mapped[int] = mapped_column(Integer, default=0)
    parameters_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ModelQualityMetricModel(Base):
    """ORM model for Model Quality Metrics - fitness, precision, etc."""

    __tablename__ = "model_quality_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_model_versions.id"), nullable=False, index=True
    )
    evaluated_against_log_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=True
    )
    metric_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # fitness, precision, generalization, simplicity, soundness
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_details_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    version: Mapped["ProcessModelVersionModel"] = relationship(
        "ProcessModelVersionModel", back_populates="quality_metrics"
    )


class PetriNetPlaceModel(Base):
    """ORM model for Petri Net Places."""

    __tablename__ = "petri_net_places"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_model_versions.id"), nullable=False, index=True
    )
    place_id_internal: Mapped[str] = mapped_column(String(100), nullable=False)
    place_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    initial_tokens: Mapped[int] = mapped_column(Integer, default=0)
    is_initial_place: Mapped[bool] = mapped_column(Integer, default=False)
    is_final_place: Mapped[bool] = mapped_column(Integer, default=False)
    position_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    version: Mapped["ProcessModelVersionModel"] = relationship(
        "ProcessModelVersionModel", back_populates="petri_places"
    )


class PetriNetTransitionModel(Base):
    """ORM model for Petri Net Transitions."""

    __tablename__ = "petri_net_transitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_model_versions.id"), nullable=False, index=True
    )
    mapped_activity_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    transition_id_internal: Mapped[str] = mapped_column(String(100), nullable=False)
    transition_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_silent: Mapped[bool] = mapped_column(Integer, default=False)
    avg_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    firing_frequency: Mapped[int] = mapped_column(Integer, default=0)
    position_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    version: Mapped["ProcessModelVersionModel"] = relationship(
        "ProcessModelVersionModel", back_populates="petri_transitions"
    )


class PetriNetArcModel(Base):
    """ORM model for Petri Net Arcs."""

    __tablename__ = "petri_net_arcs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_model_versions.id"), nullable=False, index=True
    )
    from_place_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("petri_net_places.id"), nullable=True
    )
    from_transition_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("petri_net_transitions.id"), nullable=True
    )
    to_place_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("petri_net_places.id"), nullable=True
    )
    to_transition_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("petri_net_transitions.id"), nullable=True
    )
    arc_type: Mapped[str] = mapped_column(
        String(50), default="normal"
    )  # normal, inhibitor, reset, read
    arc_weight: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    version: Mapped["ProcessModelVersionModel"] = relationship(
        "ProcessModelVersionModel", back_populates="petri_arcs"
    )


class DirectlyFollowsEdgeModel(Base):
    """ORM model for DFG edges with enhanced metrics."""

    __tablename__ = "directly_follows_edges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_model_versions.id"), nullable=False, index=True
    )
    source_activity_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    target_activity_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    source_activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_transition_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_transition_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    version: Mapped["ProcessModelVersionModel"] = relationship(
        "ProcessModelVersionModel", back_populates="dfg_edges"
    )


# =============================================================================
# PHASE 3: CONFORMANCE & COMPLIANCE
# =============================================================================


class ReferenceModelModel(Base):
    """ORM model for Reference/Normative Models."""

    __tablename__ = "reference_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    process_model_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_model_versions.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(
        String(50), default="discovered"
    )  # discovered, imported, designed, regulatory
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, active, deprecated
    is_normative: Mapped[bool] = mapped_column(Integer, default=False)
    regulatory_framework: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    effective_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    conformance_runs: Mapped[list["ConformanceCheckRunModel"]] = relationship(
        "ConformanceCheckRunModel", back_populates="reference_model", cascade="all, delete-orphan"
    )
    compliance_rules: Mapped[list["ComplianceRuleModel"]] = relationship(
        "ComplianceRuleModel", back_populates="reference_model", cascade="all, delete-orphan"
    )


class ConformanceCheckRunModel(Base):
    """ORM model for Conformance Check Runs - job tracking."""

    __tablename__ = "conformance_check_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    event_log_version_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("event_log_versions.id"), nullable=True
    )
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    reference_model_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("reference_models.id"), nullable=False, index=True
    )
    initiated_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    algorithm: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # token_replay, alignment, footprint, behavioral_profile
    status: Mapped[str] = mapped_column(
        String(50), default="queued"
    )  # queued, replaying, aligning, analyzing, completed, failed
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    overall_fitness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_precision_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_cases_checked: Mapped[int] = mapped_column(Integer, default=0)
    fitting_cases_count: Mapped[int] = mapped_column(Integer, default=0)
    non_fitting_cases_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    reference_model: Mapped["ReferenceModelModel"] = relationship(
        "ReferenceModelModel", back_populates="conformance_runs"
    )
    case_results: Mapped[list["CaseConformanceResultModel"]] = relationship(
        "CaseConformanceResultModel", back_populates="check_run", cascade="all, delete-orphan"
    )
    deviation_types: Mapped[list["DeviationTypeModel"]] = relationship(
        "DeviationTypeModel", back_populates="check_run", cascade="all, delete-orphan"
    )


class CaseConformanceResultModel(Base):
    """ORM model for per-case conformance results."""

    __tablename__ = "case_conformance_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    check_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conformance_check_runs.id"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    is_fitting: Mapped[bool] = mapped_column(Integer, default=False)
    case_fitness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    alignment_cost: Mapped[int] = mapped_column(Integer, default=0)
    synchronous_moves: Mapped[int] = mapped_column(Integer, default=0)
    model_moves: Mapped[int] = mapped_column(Integer, default=0)
    log_moves: Mapped[int] = mapped_column(Integer, default=0)
    deviation_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    check_run: Mapped["ConformanceCheckRunModel"] = relationship(
        "ConformanceCheckRunModel", back_populates="case_results"
    )
    alignment_steps: Mapped[list["AlignmentStepModel"]] = relationship(
        "AlignmentStepModel", back_populates="case_result", cascade="all, delete-orphan"
    )
    deviation_instances: Mapped[list["DeviationInstanceModel"]] = relationship(
        "DeviationInstanceModel", back_populates="case_result", cascade="all, delete-orphan"
    )


class AlignmentStepModel(Base):
    """ORM model for alignment trace steps."""

    __tablename__ = "alignment_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_result_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("case_conformance_results.id"), nullable=False, index=True
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # sync, model_move, log_move, invisible
    log_activity_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model_activity_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    log_event_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    step_cost: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    case_result: Mapped["CaseConformanceResultModel"] = relationship(
        "CaseConformanceResultModel", back_populates="alignment_steps"
    )


class DeviationTypeModel(Base):
    """ORM model for deviation pattern catalog."""

    __tablename__ = "deviation_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    check_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conformance_check_runs.id"), nullable=False, index=True
    )
    activity_type_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # missing_activity, unexpected_activity, wrong_sequence, skipped_mandatory, repeated_activity, timing_violation
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(
        String(50), default="medium"
    )  # low, medium, high, critical
    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    occurrence_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    check_run: Mapped["ConformanceCheckRunModel"] = relationship(
        "ConformanceCheckRunModel", back_populates="deviation_types"
    )
    instances: Mapped[list["DeviationInstanceModel"]] = relationship(
        "DeviationInstanceModel", back_populates="deviation_type", cascade="all, delete-orphan"
    )


class DeviationInstanceModel(Base):
    """ORM model for individual deviation occurrences."""

    __tablename__ = "deviation_instances"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    deviation_type_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("deviation_types.id"), nullable=False, index=True
    )
    case_result_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("case_conformance_results.id"), nullable=False, index=True
    )
    event_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    deviation_type: Mapped["DeviationTypeModel"] = relationship(
        "DeviationTypeModel", back_populates="instances"
    )
    case_result: Mapped["CaseConformanceResultModel"] = relationship(
        "CaseConformanceResultModel", back_populates="deviation_instances"
    )


class ComplianceRuleModel(Base):
    """ORM model for declarative compliance rules (DECLARE patterns)."""

    __tablename__ = "compliance_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    reference_model_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("reference_models.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rule_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # existence, absence, exactly, response, precedence, succession, chain_response
    ltl_expression: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(
        String(50), default="error"
    )  # info, warning, error, critical
    is_mandatory: Mapped[bool] = mapped_column(Integer, default=True)
    is_enabled: Mapped[bool] = mapped_column(Integer, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    reference_model: Mapped["ReferenceModelModel"] = relationship(
        "ReferenceModelModel", back_populates="compliance_rules"
    )
    violations: Mapped[list["ComplianceViolationModel"]] = relationship(
        "ComplianceViolationModel", back_populates="rule", cascade="all, delete-orphan"
    )


class ComplianceViolationModel(Base):
    """ORM model for compliance rule violations."""

    __tablename__ = "compliance_violations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    check_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conformance_check_runs.id"), nullable=False, index=True
    )
    rule_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("compliance_rules.id"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    rule: Mapped["ComplianceRuleModel"] = relationship(
        "ComplianceRuleModel", back_populates="violations"
    )


# =============================================================================
# PHASE 4: PERFORMANCE ANALYTICS & KPIs
# =============================================================================


class PerformanceAnalysisRunModel(Base):
    """ORM model for Performance Analysis Runs."""

    __tablename__ = "performance_analysis_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    event_log_version_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("event_log_versions.id"), nullable=True
    )
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    initiated_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    analysis_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # duration, frequency, bottleneck, throughput, workload
    status: Mapped[str] = mapped_column(
        String(50), default="queued"
    )  # queued, processing, completed, failed
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    summary_statistics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    activity_metrics: Mapped[list["ActivityPerformanceMetricModel"]] = relationship(
        "ActivityPerformanceMetricModel",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )
    transition_metrics: Mapped[list["TransitionPerformanceMetricModel"]] = relationship(
        "TransitionPerformanceMetricModel",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )
    resource_metrics: Mapped[list["ResourcePerformanceMetricModel"]] = relationship(
        "ResourcePerformanceMetricModel",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )
    bottleneck_findings: Mapped[list["BottleneckFindingModel"]] = relationship(
        "BottleneckFindingModel", back_populates="analysis_run", cascade="all, delete-orphan"
    )


class ActivityPerformanceMetricModel(Base):
    """ORM model for per-activity performance metrics."""

    __tablename__ = "activity_performance_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("performance_analysis_runs.id"), nullable=False, index=True
    )
    activity_type_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    distinct_cases: Mapped[int] = mapped_column(Integer, default=0)
    min_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    p95_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_waiting_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    analysis_run: Mapped["PerformanceAnalysisRunModel"] = relationship(
        "PerformanceAnalysisRunModel", back_populates="activity_metrics"
    )


class TransitionPerformanceMetricModel(Base):
    """ORM model for per-transition performance metrics."""

    __tablename__ = "transition_performance_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("performance_analysis_runs.id"), nullable=False, index=True
    )
    from_activity_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    to_activity_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    from_activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    to_activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    transition_count: Mapped[int] = mapped_column(Integer, default=0)
    min_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    transition_probability: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    analysis_run: Mapped["PerformanceAnalysisRunModel"] = relationship(
        "PerformanceAnalysisRunModel", back_populates="transition_metrics"
    )


class ResourcePerformanceMetricModel(Base):
    """ORM model for per-resource performance metrics."""

    __tablename__ = "resource_performance_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("performance_analysis_runs.id"), nullable=False, index=True
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("resource_profiles.id"), nullable=True
    )
    resource_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    events_handled: Mapped[int] = mapped_column(Integer, default=0)
    cases_touched: Mapped[int] = mapped_column(Integer, default=0)
    distinct_activities: Mapped[int] = mapped_column(Integer, default=0)
    total_active_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_handling_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    utilization_rate: Mapped[float] = mapped_column(Float, default=0.0)
    handoff_count_out: Mapped[int] = mapped_column(Integer, default=0)
    handoff_count_in: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    analysis_run: Mapped["PerformanceAnalysisRunModel"] = relationship(
        "PerformanceAnalysisRunModel", back_populates="resource_metrics"
    )


class BottleneckFindingModel(Base):
    """ORM model for detected bottlenecks."""

    __tablename__ = "bottleneck_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("performance_analysis_runs.id"), nullable=False, index=True
    )
    activity_type_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    from_activity_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    to_activity_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("activity_types.id"), nullable=True
    )
    location: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # activity, transition, resource, batch_point
    bottleneck_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # processing_time, waiting_time, resource_contention, batching
    severity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_delay_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_time_impact_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cases_affected: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    analysis_run: Mapped["PerformanceAnalysisRunModel"] = relationship(
        "PerformanceAnalysisRunModel", back_populates="bottleneck_findings"
    )


class ProcessKPIModel(Base):
    """ORM model for KPI definitions."""

    __tablename__ = "process_kpis"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # time, cost, quality, throughput, compliance, custom
    formula: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    direction: Mapped[str] = mapped_column(
        String(50), default="lower_is_better"
    )  # higher_is_better, lower_is_better
    is_enabled: Mapped[bool] = mapped_column(Integer, default=True)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    measurements: Mapped[list["KPIMeasurementModel"]] = relationship(
        "KPIMeasurementModel", back_populates="kpi", cascade="all, delete-orphan"
    )
    targets: Mapped[list["KPITargetModel"]] = relationship(
        "KPITargetModel", back_populates="kpi", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["KPIAlertModel"]] = relationship(
        "KPIAlertModel", back_populates="kpi", cascade="all, delete-orphan"
    )


class KPIMeasurementModel(Base):
    """ORM model for KPI time-series measurements."""

    __tablename__ = "kpi_measurements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    kpi_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_kpis.id"), nullable=False, index=True
    )
    event_log_version_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("event_log_versions.id"), nullable=True
    )
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    previous_period_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    change_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sample_size: Mapped[int] = mapped_column(Integer, default=0)
    measured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    kpi: Mapped["ProcessKPIModel"] = relationship("ProcessKPIModel", back_populates="measurements")


class KPITargetModel(Base):
    """ORM model for KPI target values."""

    __tablename__ = "kpi_targets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    kpi_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_kpis.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    target_type: Mapped[str] = mapped_column(
        String(50), default="maximum"
    )  # minimum, maximum, exact, range
    range_low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    range_high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    set_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    kpi: Mapped["ProcessKPIModel"] = relationship("ProcessKPIModel", back_populates="targets")


class KPIAlertModel(Base):
    """ORM model for KPI breach alerts."""

    __tablename__ = "kpi_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    kpi_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_kpis.id"), nullable=False, index=True
    )
    target_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kpi_targets.id"), nullable=False, index=True
    )
    measurement_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("kpi_measurements.id"), nullable=False, index=True
    )
    alert_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # target_breach, trend_decline, anomaly
    actual_value: Mapped[float] = mapped_column(Float, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    deviation_percent: Mapped[float] = mapped_column(Float, nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_acknowledged: Mapped[bool] = mapped_column(Integer, default=False)
    acknowledged_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    kpi: Mapped["ProcessKPIModel"] = relationship("ProcessKPIModel", back_populates="alerts")


# =============================================================================
# PHASE 5: OBJECT-CENTRIC PROCESS MINING (OCPM) / OCEL 2.0
# =============================================================================


class OCELLogModel(Base):
    """ORM model for Object-Centric Event Logs (OCEL 2.0)."""

    __tablename__ = "ocel_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_format: Mapped[str] = mapped_column(
        String(50), default="jsonocel"
    )  # jsonocel, sqlite, xml
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_objects: Mapped[int] = mapped_column(Integer, default=0)
    total_object_types: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    object_types: Mapped[list["OCELObjectTypeModel"]] = relationship(
        "OCELObjectTypeModel", back_populates="log", cascade="all, delete-orphan"
    )
    objects: Mapped[list["OCELObjectModel"]] = relationship(
        "OCELObjectModel", back_populates="log", cascade="all, delete-orphan"
    )
    events: Mapped[list["OCELEventModel"]] = relationship(
        "OCELEventModel", back_populates="log", cascade="all, delete-orphan"
    )
    relationships: Mapped[list["OCELObjectRelationshipModel"]] = relationship(
        "OCELObjectRelationshipModel", back_populates="log", cascade="all, delete-orphan"
    )
    petri_nets: Mapped[list["OCPetriNetModel"]] = relationship(
        "OCPetriNetModel", back_populates="log", cascade="all, delete-orphan"
    )


class OCELObjectTypeModel(Base):
    """ORM model for OCEL Object Types."""

    __tablename__ = "ocel_object_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ocel_logs.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    attributes_schema_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # {attr_name: data_type}
    object_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    log: Mapped["OCELLogModel"] = relationship("OCELLogModel", back_populates="object_types")
    objects: Mapped[list["OCELObjectModel"]] = relationship(
        "OCELObjectModel", back_populates="object_type", cascade="all, delete-orphan"
    )


class OCELObjectModel(Base):
    """ORM model for OCEL Object Instances."""

    __tablename__ = "ocel_objects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ocel_logs.id"), nullable=False, index=True
    )
    object_type_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ocel_object_types.id"), nullable=False, index=True
    )
    object_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )  # Business ID (e.g., "ORD-123")
    attributes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    log: Mapped["OCELLogModel"] = relationship("OCELLogModel", back_populates="objects")
    object_type: Mapped["OCELObjectTypeModel"] = relationship(
        "OCELObjectTypeModel", back_populates="objects"
    )
    event_links: Mapped[list["OCELEventObjectModel"]] = relationship(
        "OCELEventObjectModel", back_populates="object", cascade="all, delete-orphan"
    )


class OCELEventModel(Base):
    """ORM model for OCEL Events."""

    __tablename__ = "ocel_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ocel_logs.id"), nullable=False, index=True
    )
    ocel_event_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )  # Original OCEL event ID
    activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    attributes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    log: Mapped["OCELLogModel"] = relationship("OCELLogModel", back_populates="events")
    object_links: Mapped[list["OCELEventObjectModel"]] = relationship(
        "OCELEventObjectModel", back_populates="event", cascade="all, delete-orphan"
    )


class OCELEventObjectModel(Base):
    """ORM model for Event-to-Object relationships (many-to-many junction table)."""

    __tablename__ = "ocel_event_objects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ocel_events.id"), nullable=False, index=True
    )
    object_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ocel_objects.id"), nullable=False, index=True
    )
    qualifier: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # Role qualifier (e.g., "primary", "related")

    # Relationships
    event: Mapped["OCELEventModel"] = relationship("OCELEventModel", back_populates="object_links")
    object: Mapped["OCELObjectModel"] = relationship(
        "OCELObjectModel", back_populates="event_links"
    )


class OCELObjectRelationshipModel(Base):
    """ORM model for Object-to-Object relationships."""

    __tablename__ = "ocel_object_relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ocel_logs.id"), nullable=False, index=True
    )
    source_object_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ocel_objects.id"), nullable=False, index=True
    )
    target_object_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ocel_objects.id"), nullable=False, index=True
    )
    relationship_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # e.g., "order_contains_item"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    log: Mapped["OCELLogModel"] = relationship("OCELLogModel", back_populates="relationships")


class OCPetriNetModel(Base):
    """ORM model for Object-Centric Petri Nets discovered from OCEL."""

    __tablename__ = "oc_petri_nets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ocel_logs.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    serialized_model: Mapped[Optional[bytes]] = mapped_column(
        LargeBinary, nullable=True
    )  # Pickled OC-PN
    visualization_svg: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    object_types_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # List of object types included
    discovery_algorithm: Mapped[str] = mapped_column(String(100), default="oc_petri_net")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    log: Mapped["OCELLogModel"] = relationship("OCELLogModel", back_populates="petri_nets")


# =============================================================================
# PHASE 6: MULTI-TENANCY & FILTERING FOUNDATION
# =============================================================================


class WorkspaceModel(Base):
    """ORM model for Workspaces - top-level organization unit for multi-tenancy."""

    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True
    )  # URL-friendly identifier
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    settings_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Workspace-level settings
    is_active: Mapped[bool] = mapped_column(Integer, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    projects: Mapped[list["ProjectModel"]] = relationship(
        "ProjectModel", back_populates="workspace", cascade="all, delete-orphan"
    )
    members: Mapped[list["WorkspaceMemberModel"]] = relationship(
        "WorkspaceMemberModel", back_populates="workspace", cascade="all, delete-orphan"
    )
    shared_assets: Mapped[list["SharedAssetModel"]] = relationship(
        "SharedAssetModel", back_populates="workspace", cascade="all, delete-orphan"
    )


class ProjectModel(Base):
    """ORM model for Projects - containers for event logs and analyses within a workspace."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # Short project key like "PM-1"
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, archived, deleted
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # HEX color for UI
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Icon identifier
    settings_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Project-level settings
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # User ID
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    workspace: Mapped["WorkspaceModel"] = relationship("WorkspaceModel", back_populates="projects")
    event_logs: Mapped[list["EventLogModel"]] = relationship(
        "EventLogModel", back_populates="project", foreign_keys="EventLogModel.project_id"
    )
    saved_filters: Mapped[list["SavedFilterModel"]] = relationship(
        "SavedFilterModel", back_populates="project", cascade="all, delete-orphan"
    )
    dashboards: Mapped[list["DashboardModel"]] = relationship(
        "DashboardModel", back_populates="project", cascade="all, delete-orphan"
    )


class WorkspaceMemberModel(Base):
    """ORM model for Workspace Members - user memberships in workspaces."""

    __tablename__ = "workspace_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # External user ID
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default="member"
    )  # owner, admin, member, viewer
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, invited, suspended
    invited_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    invited_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    workspace: Mapped["WorkspaceModel"] = relationship("WorkspaceModel", back_populates="members")


class SharedAssetModel(Base):
    """ORM model for Shared Assets - reusable assets shared within a workspace."""

    __tablename__ = "shared_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    asset_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # filter, dashboard, report_template, kpi_definition
    asset_id: Mapped[str] = mapped_column(String(36), nullable=False)  # FK to actual asset
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shared_by: Mapped[str] = mapped_column(String(36), nullable=False)  # User ID
    shared_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    workspace: Mapped["WorkspaceModel"] = relationship(
        "WorkspaceModel", back_populates="shared_assets"
    )


# =============================================================================
# FILTERING & SEGMENTATION
# =============================================================================


class SavedFilterModel(Base):
    """ORM model for Saved Filters - reusable filter configurations."""

    __tablename__ = "saved_filters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False, index=True
    )
    log_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_quick_filter: Mapped[bool] = mapped_column(
        Integer, default=False
    )  # Show in quick filter bar
    is_shared: Mapped[bool] = mapped_column(Integer, default=False)  # Shared with workspace
    matched_case_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # Last computed count
    matched_event_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_applied: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="saved_filters")
    conditions: Mapped[list["FilterConditionModel"]] = relationship(
        "FilterConditionModel", back_populates="saved_filter", cascade="all, delete-orphan"
    )


class FilterConditionModel(Base):
    """ORM model for Filter Conditions - individual filter rules."""

    __tablename__ = "filter_conditions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    filter_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("saved_filters.id"), nullable=False, index=True
    )
    condition_order: Mapped[int] = mapped_column(Integer, default=0)  # Order of evaluation
    filter_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: temporal, attribute, variant, performance, conformance, activity, path, endpoint, resource
    field: Mapped[str] = mapped_column(String(255), nullable=False)  # Field or attribute name
    operator: Mapped[str] = mapped_column(String(50), nullable=False)
    # Operators: eq, neq, gt, gte, lt, lte, contains, not_contains, starts_with, ends_with, in, not_in, between, is_null, is_not_null
    value_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-encoded value(s)
    logical_group: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # Group name for AND/OR logic
    logical_operator: Mapped[str] = mapped_column(String(10), default="AND")  # AND, OR
    is_negated: Mapped[bool] = mapped_column(Integer, default=False)  # NOT operator

    # Relationships
    saved_filter: Mapped["SavedFilterModel"] = relationship(
        "SavedFilterModel", back_populates="conditions"
    )


# =============================================================================
# DASHBOARDS (Forward declaration for Project relationship)
# =============================================================================


class DashboardModel(Base):
    """ORM model for Dashboards - customizable views of process data."""

    __tablename__ = "dashboards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    layout_config_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Grid layout config
    is_default: Mapped[bool] = mapped_column(
        Integer, default=False
    )  # Default dashboard for project
    is_shared: Mapped[bool] = mapped_column(Integer, default=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    project: Mapped["ProjectModel"] = relationship("ProjectModel", back_populates="dashboards")
    widgets: Mapped[list["DashboardWidgetModel"]] = relationship(
        "DashboardWidgetModel", back_populates="dashboard", cascade="all, delete-orphan"
    )


class DashboardWidgetModel(Base):
    """ORM model for Dashboard Widgets - individual components on a dashboard."""

    __tablename__ = "dashboard_widgets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    dashboard_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("dashboards.id"), nullable=False, index=True
    )
    widget_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: kpi_card, bar_chart, line_chart, pie_chart, heatmap, table, process_map, variant_list, activity_list
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    configuration_json: Mapped[str] = mapped_column(Text, nullable=False)  # Widget-specific config
    position_json: Mapped[str] = mapped_column(Text, nullable=False)  # {x, y, w, h} grid position
    data_source_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # log, analysis, kpi
    data_source_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    filter_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("saved_filters.id"), nullable=True
    )
    refresh_interval_seconds: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # Auto-refresh interval

    # Relationships
    dashboard: Mapped["DashboardModel"] = relationship("DashboardModel", back_populates="widgets")


# =============================================================================
# PHASE 7: TEMPORAL ANALYSIS & COMPARISONS
# =============================================================================


class TimeSeriesModel(Base):
    """ORM model for Time Series - metric trends over time."""

    __tablename__ = "time_series"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Metrics: case_count, avg_duration, throughput, variant_count, etc.
    granularity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # hour, day, week, month, quarter, year
    data_points_json: Mapped[str] = mapped_column(Text, nullable=False)  # [{timestamp, value}, ...]
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    trend_direction: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # increasing, decreasing, stable
    trend_slope: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    trend_analysis_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Additional trend metrics
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DriftDetectionModel(Base):
    """ORM model for Drift Detection - process drift over time."""

    __tablename__ = "drift_detections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    baseline_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    baseline_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    comparison_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    comparison_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    drift_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: control_flow, resource, performance, data_attribute
    drift_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    affected_aspects_json: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Which activities/resources changed
    severity: Mapped[str] = mapped_column(
        String(20), default="medium"
    )  # low, medium, high, critical
    is_significant: Mapped[bool] = mapped_column(Integer, default=False)
    p_value: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )  # Statistical significance


class PeriodComparisonModel(Base):
    """ORM model for Period Comparisons - comparing two time periods."""

    __tablename__ = "period_comparisons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    period_a_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_a_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_b_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_b_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_a_case_count: Mapped[int] = mapped_column(Integer, default=0)
    period_b_case_count: Mapped[int] = mapped_column(Integer, default=0)
    comparison_results_json: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Metrics for both periods
    significant_changes_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Significant differences
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SeasonalityPatternModel(Base):
    """ORM model for Seasonality Patterns - recurring temporal patterns."""

    __tablename__ = "seasonality_patterns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    metric: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # What metric shows seasonality
    pattern_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # daily, weekly, monthly, yearly
    pattern_data_json: Mapped[str] = mapped_column(Text, nullable=False)  # Pattern values
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    period_length: Mapped[int] = mapped_column(Integer, nullable=False)  # Length in hours
    amplitude: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ComparisonModel(Base):
    """ORM model for Cohort Comparisons - comparing filtered segments."""

    __tablename__ = "comparisons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    segment_a_filter_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("saved_filters.id"), nullable=False
    )
    segment_b_filter_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("saved_filters.id"), nullable=False
    )
    segment_a_name: Mapped[str] = mapped_column(String(100), nullable=False)
    segment_b_name: Mapped[str] = mapped_column(String(100), nullable=False)
    summary_stats_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    dimensions: Mapped[list["ComparisonDimensionModel"]] = relationship(
        "ComparisonDimensionModel", back_populates="comparison", cascade="all, delete-orphan"
    )


class ComparisonDimensionModel(Base):
    """ORM model for Comparison Dimensions - individual metrics compared."""

    __tablename__ = "comparison_dimensions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    comparison_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("comparisons.id"), nullable=False, index=True
    )
    dimension_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: duration, variant_distribution, activity_frequency, resource_workload
    segment_a_value_json: Mapped[str] = mapped_column(Text, nullable=False)
    segment_b_value_json: Mapped[str] = mapped_column(Text, nullable=False)
    difference_absolute: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    difference_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    difference_significance: Mapped[float] = mapped_column(Float, default=0.0)  # p-value
    is_significant: Mapped[bool] = mapped_column(Integer, default=False)

    # Relationships
    comparison: Mapped["ComparisonModel"] = relationship(
        "ComparisonModel", back_populates="dimensions"
    )


class RootCauseAnalysisModel(Base):
    """ORM model for Root Cause Analysis - identifying drivers of outcomes."""

    __tablename__ = "root_cause_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    outcome_definition: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # e.g., "duration > 5 days"
    outcome_metric: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # duration, cost, rework, etc.
    analysis_method: Mapped[str] = mapped_column(String(50), nullable=False)
    # Methods: decision_tree, correlation, regression, feature_importance
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, running, completed, failed
    total_cases_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    positive_outcome_count: Mapped[int] = mapped_column(Integer, default=0)
    run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    factors: Mapped[list["RootCauseFactorModel"]] = relationship(
        "RootCauseFactorModel", back_populates="analysis", cascade="all, delete-orphan"
    )


class RootCauseFactorModel(Base):
    """ORM model for Root Cause Factors - individual drivers identified."""

    __tablename__ = "root_cause_factors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("root_cause_analyses.id"), nullable=False, index=True
    )
    factor_rank: Mapped[int] = mapped_column(Integer, nullable=False)  # Importance ranking
    factor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: attribute, activity_presence, activity_sequence, resource, variant, timing
    factor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    factor_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    correlation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    importance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    statistical_significance: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )  # p-value
    affected_cases: Mapped[int] = mapped_column(Integer, default=0)
    impact_on_outcome: Mapped[str] = mapped_column(
        String(20), default="positive"
    )  # positive, negative
    impact_metrics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    analysis: Mapped["RootCauseAnalysisModel"] = relationship(
        "RootCauseAnalysisModel", back_populates="factors"
    )


class CorrelationAnalysisModel(Base):
    """ORM model for Correlation Analysis - feature correlations with target."""

    __tablename__ = "correlation_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    target_variable: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # duration, cost, etc.
    feature_correlations_json: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # {feature: correlation}
    significant_features_json: Mapped[str] = mapped_column(Text, nullable=False)  # Significant only
    method: Mapped[str] = mapped_column(String(50), default="pearson")  # pearson, spearman, kendall
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# =============================================================================
# PHASE 8: ADVANCED VARIANT & PATH ANALYSIS
# =============================================================================


class VariantClusterModel(Base):
    """ORM model for Variant Clusters - groups of similar variants."""

    __tablename__ = "variant_clusters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    clustering_method: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # kmeans, hierarchical, dbscan
    variant_count: Mapped[int] = mapped_column(Integer, default=0)
    case_count: Mapped[int] = mapped_column(Integer, default=0)
    centroid_sequence_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Representative sequence
    cluster_characteristics_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Avg duration, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LoopPatternModel(Base):
    """ORM model for Loop Patterns - detected rework/repetition patterns."""

    __tablename__ = "loop_patterns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    activity_sequence_json: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Activities in the loop
    loop_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # self_loop, tandem, nested, long_distance
    entry_activity: Mapped[str] = mapped_column(String(255), nullable=False)
    exit_activity: Mapped[str] = mapped_column(String(255), nullable=False)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    affected_case_count: Mapped[int] = mapped_column(Integer, default=0)
    affected_case_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    avg_iterations: Mapped[float] = mapped_column(Float, default=0.0)
    max_iterations: Mapped[int] = mapped_column(Integer, default=0)
    added_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    cost_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    instances: Mapped[list["LoopInstanceModel"]] = relationship(
        "LoopInstanceModel", back_populates="pattern", cascade="all, delete-orphan"
    )


class LoopInstanceModel(Base):
    """ORM model for Loop Instances - individual loop occurrences in cases."""

    __tablename__ = "loop_instances"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    loop_pattern_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("loop_patterns.id"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    iteration_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    start_event_index: Mapped[int] = mapped_column(Integer, nullable=True)
    end_event_index: Mapped[int] = mapped_column(Integer, nullable=True)

    # Relationships
    pattern: Mapped["LoopPatternModel"] = relationship(
        "LoopPatternModel", back_populates="instances"
    )


class PathQueryModel(Base):
    """ORM model for Path Queries - saved pattern matching queries."""

    __tablename__ = "path_queries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pattern_json: Mapped[str] = mapped_column(Text, nullable=False)  # Activity pattern to match
    pattern_type: Mapped[str] = mapped_column(
        String(50), default="sequence"
    )  # sequence, eventually_follows, parallel
    matched_count: Mapped[int] = mapped_column(Integer, default=0)
    matched_case_ids_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SequencePatternModel(Base):
    """ORM model for Sequence Patterns - frequent subsequences discovered."""

    __tablename__ = "sequence_patterns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    activity_sequence_json: Mapped[str] = mapped_column(Text, nullable=False)
    pattern_length: Mapped[int] = mapped_column(Integer, nullable=False)
    support: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # Fraction of cases containing pattern
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    is_closed: Mapped[bool] = mapped_column(Integer, default=False)  # Closed frequent pattern
    is_maximal: Mapped[bool] = mapped_column(Integer, default=False)  # Maximal frequent pattern
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# =============================================================================
# PHASE 9: COLLABORATION & ANALYSIS SESSIONS
# =============================================================================


class AnalysisSessionModel(Base):
    """ORM model for Analysis Sessions - guided analysis workflows."""

    __tablename__ = "analysis_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False, index=True
    )
    log_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="draft"
    )  # draft, in_progress, completed, archived
    analysis_type: Mapped[str] = mapped_column(String(50), default="exploratory")
    # Types: exploratory, root_cause, conformance, performance, comparison
    configuration_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    steps: Mapped[list["AnalysisStepModel"]] = relationship(
        "AnalysisStepModel", back_populates="session", cascade="all, delete-orphan"
    )
    findings: Mapped[list["AnalysisFindingModel"]] = relationship(
        "AnalysisFindingModel", back_populates="session", cascade="all, delete-orphan"
    )
    comments: Mapped[list["AnalysisCommentModel"]] = relationship(
        "AnalysisCommentModel", back_populates="session", cascade="all, delete-orphan"
    )


class AnalysisStepModel(Base):
    """ORM model for Analysis Steps - individual steps in an analysis."""

    __tablename__ = "analysis_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_sessions.id"), nullable=False, index=True
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: filter, discovery, conformance, performance, comparison, root_cause, visualization
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False)
    results_summary_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_filter_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("saved_filters.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, running, completed, failed
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    session: Mapped["AnalysisSessionModel"] = relationship(
        "AnalysisSessionModel", back_populates="steps"
    )


class AnalysisFindingModel(Base):
    """ORM model for Analysis Findings - insights discovered during analysis."""

    __tablename__ = "analysis_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_sessions.id"), nullable=False, index=True
    )
    step_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("analysis_steps.id"), nullable=True
    )
    finding_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: bottleneck, deviation, pattern, anomaly, trend, correlation, recommendation
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), default="medium"
    )  # info, low, medium, high, critical
    impact_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    supporting_data_json: Mapped[str] = mapped_column(Text, nullable=False)  # Evidence/metrics
    linked_elements_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # Related activities, cases
    is_actionable: Mapped[bool] = mapped_column(Integer, default=True)
    status: Mapped[str] = mapped_column(
        String(50), default="open"
    )  # open, acknowledged, resolved, dismissed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped["AnalysisSessionModel"] = relationship(
        "AnalysisSessionModel", back_populates="findings"
    )


class AnalysisCommentModel(Base):
    """ORM model for Analysis Comments - collaborative discussion on analysis."""

    __tablename__ = "analysis_comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_sessions.id"), nullable=False, index=True
    )
    finding_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("analysis_findings.id"), nullable=True
    )
    parent_comment_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("analysis_comments.id"), nullable=True
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    session: Mapped["AnalysisSessionModel"] = relationship(
        "AnalysisSessionModel", back_populates="comments"
    )


class CaseAnnotationModel(Base):
    """ORM model for Case Annotations - notes on specific cases."""

    __tablename__ = "case_annotations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_db_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_cases.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    annotation_type: Mapped[str] = mapped_column(
        String(50), default="note"
    )  # note, question, decision, todo
    is_resolved: Mapped[bool] = mapped_column(Integer, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CaseFlagModel(Base):
    """ORM model for Case Flags - flagged cases for review."""

    __tablename__ = "case_flags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_db_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("process_cases.id"), nullable=False, index=True
    )
    flag_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # review, escalate, investigate, outlier
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    flagged_by: Mapped[str] = mapped_column(String(36), nullable=False)
    priority: Mapped[str] = mapped_column(
        String(20), default="medium"
    )  # low, medium, high, critical
    status: Mapped[str] = mapped_column(
        String(50), default="open"
    )  # open, in_progress, resolved, dismissed
    resolved_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InvestigationModel(Base):
    """ORM model for Investigations - structured case investigations."""

    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("event_logs.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    hypothesis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="open"
    )  # open, investigating, concluded
    conclusion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    concluded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    threads: Mapped[list["InvestigationThreadModel"]] = relationship(
        "InvestigationThreadModel", back_populates="investigation", cascade="all, delete-orphan"
    )


class InvestigationThreadModel(Base):
    """ORM model for Investigation Threads - lines of inquiry in investigations."""

    __tablename__ = "investigation_threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    investigation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("investigations.id"), nullable=False, index=True
    )
    thread_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # pattern, outlier, comparison, timeline
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    linked_cases_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Case IDs
    linked_findings_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Finding IDs
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    investigation: Mapped["InvestigationModel"] = relationship(
        "InvestigationModel", back_populates="threads"
    )


# =============================================================================
# PHASE 10: REPORTS
# =============================================================================


class ReportModel(Base):
    """ORM model for Reports - structured report definitions."""

    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    template_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: executive_summary, technical_analysis, compliance, performance, custom
    configuration_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_template: Mapped[bool] = mapped_column(Integer, default=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    sections: Mapped[list["ReportSectionModel"]] = relationship(
        "ReportSectionModel", back_populates="report", cascade="all, delete-orphan"
    )
    scheduled_runs: Mapped[list["ScheduledReportRunModel"]] = relationship(
        "ScheduledReportRunModel", back_populates="report", cascade="all, delete-orphan"
    )


class ReportSectionModel(Base):
    """ORM model for Report Sections - individual sections in a report."""

    __tablename__ = "report_sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    report_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("reports.id"), nullable=False, index=True
    )
    section_order: Mapped[int] = mapped_column(Integer, nullable=False)
    section_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: overview, kpi_summary, variant_analysis, conformance, bottlenecks, recommendations, custom
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_config_json: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Section-specific config
    filter_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("saved_filters.id"), nullable=True
    )

    # Relationships
    report: Mapped["ReportModel"] = relationship("ReportModel", back_populates="sections")


class ScheduledReportRunModel(Base):
    """ORM model for Scheduled Report Runs - automated report generation."""

    __tablename__ = "scheduled_report_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    report_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("reports.id"), nullable=False, index=True
    )
    schedule_cron: Mapped[str] = mapped_column(String(100), nullable=False)  # Cron expression
    output_format: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, excel, html, json
    recipients_json: Mapped[str] = mapped_column(Text, nullable=False)  # Email list
    is_active: Mapped[bool] = mapped_column(Integer, default=True)
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_run_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    next_run: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    report: Mapped["ReportModel"] = relationship("ReportModel", back_populates="scheduled_runs")


# =============================================================================
# PHASE 11: SYSTEM INFRASTRUCTURE
# =============================================================================


class AuditLogModel(Base):
    """ORM model for Audit Logs - tracking all user actions."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: create, read, update, delete, export, login, logout, share, analyze
    entity_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # EventLog, ProcessModel, etc.
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    entity_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    changes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Before/after diff
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Additional context
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class ExportModel(Base):
    """ORM model for Exports - tracking data exports."""

    __tablename__ = "exports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    export_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # log, model, report, analysis, data
    format: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # csv, xes, pnml, bpmn, pdf, xlsx, json
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, processing, completed, failed, expired
    source_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # Entity type being exported
    source_id: Mapped[str] = mapped_column(String(36), nullable=False)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class AsyncJobModel(Base):
    """ORM model for Async Jobs - enhanced background job tracking (replaces BackgroundJobModel)."""

    __tablename__ = "async_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Types: log_ingestion, discovery, conformance, performance, export, report_generation, drift_detection
    job_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", index=True)
    # Status: queued, running, completed, failed, cancelled, paused
    priority: Mapped[int] = mapped_column(Integer, default=5)  # 1-10, lower = higher priority
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    progress_message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_entity_type: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # Created entity type
    result_entity_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True
    )  # Created entity ID
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    queued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
