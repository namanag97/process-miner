"""SQLAlchemy ORM models for persistence."""

from datetime import datetime
from typing import Optional
from uuid import uuid4
import json

from sqlalchemy import (
    String,
    Text,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    LargeBinary,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.database import Base


def generate_uuid() -> str:
    """Generate a UUID string for primary keys."""
    return str(uuid4())


class EventLogModel(Base):
    """ORM model for Event Logs."""
    __tablename__ = "event_logs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
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


class ProcessCaseModel(Base):
    """ORM model for Process Cases."""
    __tablename__ = "process_cases"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False)
    variant_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attributes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    event_log: Mapped["EventLogModel"] = relationship("EventLogModel", back_populates="cases")
    events: Mapped[list["ProcessEventModel"]] = relationship(
        "ProcessEventModel",
        back_populates="process_case",
        cascade="all, delete-orphan",
        order_by="ProcessEventModel.timestamp",
    )


class ProcessEventModel(Base):
    """ORM model for Process Events."""
    __tablename__ = "process_events"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_db_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_cases.id"), nullable=False)
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    resource: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    attributes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    process_case: Mapped["ProcessCaseModel"] = relationship("ProcessCaseModel", back_populates="events")


class ProcessModelModel(Base):
    """ORM model for Process Models."""
    __tablename__ = "process_models"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    format: Mapped[str] = mapped_column(String(50), nullable=False)  # petri_net, bpmn, etc.
    miner_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    state: Mapped[str] = mapped_column(String(50), default="discovering", nullable=False)  # ProcessModelState
    source_log_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=True)
    repository_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("process_model_repositories.id"), nullable=True, index=True)
    serialized_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    filter_config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # FilterConfig
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    source_log: Mapped[Optional["EventLogModel"]] = relationship("EventLogModel", back_populates="models")
    repository: Mapped[Optional["ProcessModelRepositoryModel"]] = relationship(
        "ProcessModelRepositoryModel", back_populates="models", foreign_keys=[repository_id]
    )
    conformance_results: Mapped[list["ConformanceResultModel"]] = relationship(
        "ConformanceResultModel",
        back_populates="model",
        cascade="all, delete-orphan",
    )


class ConformanceResultModel(Base):
    """ORM model for Conformance Results."""
    __tablename__ = "conformance_results"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False)
    model_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_models.id"), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="requested", nullable=False)  # ConformanceResultState
    fitness: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    generalization: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    simplicity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deviation_count: Mapped[int] = mapped_column(Integer, default=0)
    deviation_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    deviations_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # List[Deviation]
    deviation_summary_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # DeviationSummary
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    model: Mapped["ProcessModelModel"] = relationship("ProcessModelModel", back_populates="conformance_results")


class DomainEventModel(Base):
    """ORM model for storing domain events."""
    __tablename__ = "domain_events"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    processed: Mapped[bool] = mapped_column(Integer, default=False)  # SQLite doesn't have native bool


class BackgroundJobModel(Base):
    """ORM model for background jobs/tasks."""
    __tablename__ = "background_jobs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # pending, running, completed, failed
    payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


# =============================================================================
# PHASE 1: CORE PROCESS MINING MODELS
# =============================================================================

class EventLogVersionModel(Base):
    """ORM model for Event Log Versions - enables log versioning."""
    __tablename__ = "event_log_versions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    version_label: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    version_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)  # draft, active, superseded, archived
    observation_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    observation_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


class ActivityTypeModel(Base):
    """ORM model for Activity Types - rich activity metadata."""
    __tablename__ = "activity_types"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False, index=True)
    version_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("event_log_versions.id"), nullable=True, index=True)
    activity_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    activity_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activity_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activity_type: Mapped[str] = mapped_column(String(50), default="task", nullable=False)  # task, decision, start, end, intermediate, subprocess
    is_automated: Mapped[bool] = mapped_column(Integer, default=False)
    is_value_adding: Mapped[bool] = mapped_column(Integer, default=True)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ProcessVariantModel(Base):
    """ORM model for Process Variants - unique activity sequences."""
    __tablename__ = "process_variants"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False, index=True)
    version_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("event_log_versions.id"), nullable=True, index=True)
    variant_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # MD5/SHA hash of activity trace
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class VariantActivityModel(Base):
    """ORM model for Variant Activities - activities in sequence within a variant."""
    __tablename__ = "variant_activities"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    variant_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_variants.id"), nullable=False, index=True)
    activity_type_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
    activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence_position: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-indexed position


# =============================================================================
# TRANSITION / DFG MODELS (Process Perspective)
# =============================================================================

class TransitionModel(Base):
    """ORM model for DFG transitions (edges between activities)."""
    __tablename__ = "transitions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False, index=True)
    source_activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    min_duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    max_duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# =============================================================================
# RESOURCE PERSPECTIVE MODELS
# =============================================================================

class ResourceProfileModel(Base):
    """ORM model for resource profiles extracted from event logs."""
    __tablename__ = "resource_profiles"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False, index=True)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    avg_activities_per_case: Mapped[float] = mapped_column(Float, default=0.0)
    frequent_activities_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HandoffModel(Base):
    """ORM model for resource handoffs."""
    __tablename__ = "handoffs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False, index=True)
    from_resource: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    to_resource: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    activity: Mapped[str] = mapped_column(String(255), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_handoff_time_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# =============================================================================
# SLA MODELS (Time Perspective)
# =============================================================================

class SLADefinitionModel(Base):
    """ORM model for SLA definitions."""
    __tablename__ = "sla_definitions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    warning_threshold_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    scope: Mapped[str] = mapped_column(String(50), nullable=False)  # case, activity, transition
    activity_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_activity: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_activity: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Integer, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SLABreachModel(Base):
    """ORM model for SLA breach records."""
    __tablename__ = "sla_breaches"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    sla_id: Mapped[str] = mapped_column(String(36), ForeignKey("sla_definitions.id"), nullable=False, index=True)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False, index=True)
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    actual_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    exceeded_by_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # met, warning, breached
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# =============================================================================
# PHASE 2: PROCESS DISCOVERY & MODEL MANAGEMENT
# =============================================================================

class ProcessModelRepositoryModel(Base):
    """ORM model for Process Model Repositories - catalogs of models."""
    __tablename__ = "process_model_repositories"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    repository_type: Mapped[str] = mapped_column(String(50), default="discovered")  # discovered, reference, imported
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    models: Mapped[list["ProcessModelModel"]] = relationship(
        "ProcessModelModel",
        back_populates="repository",
        foreign_keys="ProcessModelModel.repository_id",
    )


class ProcessModelVersionModel(Base):
    """ORM model for Process Model Versions - versioning for models."""
    __tablename__ = "process_model_versions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    model_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_models.id"), nullable=False, index=True)
    discovery_run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("process_discovery_runs.id"), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    version_label: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, active, archived
    notation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # petri_net, bpmn, process_tree, dfg
    model_serialized_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_pnml: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_bpmn_xml: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_image_svg: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    canvas_layout_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
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
    event_log_version_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("event_log_versions.id"), nullable=True)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False, index=True)
    initiated_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False)  # alpha, alpha_plus, heuristic, inductive, dfg
    output_notation: Mapped[str] = mapped_column(String(50), nullable=False)  # petri_net, bpmn, process_tree, dfg
    status: Mapped[str] = mapped_column(String(50), default="queued")  # queued, preprocessing, mining, evaluating, completed, failed
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
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_model_versions.id"), nullable=False, index=True)
    evaluated_against_log_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=True)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)  # fitness, precision, generalization, simplicity, soundness
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metric_details_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    version: Mapped["ProcessModelVersionModel"] = relationship("ProcessModelVersionModel", back_populates="quality_metrics")


class PetriNetPlaceModel(Base):
    """ORM model for Petri Net Places."""
    __tablename__ = "petri_net_places"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_model_versions.id"), nullable=False, index=True)
    place_id_internal: Mapped[str] = mapped_column(String(100), nullable=False)
    place_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    initial_tokens: Mapped[int] = mapped_column(Integer, default=0)
    is_initial_place: Mapped[bool] = mapped_column(Integer, default=False)
    is_final_place: Mapped[bool] = mapped_column(Integer, default=False)
    position_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    version: Mapped["ProcessModelVersionModel"] = relationship("ProcessModelVersionModel", back_populates="petri_places")


class PetriNetTransitionModel(Base):
    """ORM model for Petri Net Transitions."""
    __tablename__ = "petri_net_transitions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_model_versions.id"), nullable=False, index=True)
    mapped_activity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
    transition_id_internal: Mapped[str] = mapped_column(String(100), nullable=False)
    transition_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_silent: Mapped[bool] = mapped_column(Integer, default=False)
    avg_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    firing_frequency: Mapped[int] = mapped_column(Integer, default=0)
    position_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    version: Mapped["ProcessModelVersionModel"] = relationship("ProcessModelVersionModel", back_populates="petri_transitions")


class PetriNetArcModel(Base):
    """ORM model for Petri Net Arcs."""
    __tablename__ = "petri_net_arcs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_model_versions.id"), nullable=False, index=True)
    from_place_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("petri_net_places.id"), nullable=True)
    from_transition_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("petri_net_transitions.id"), nullable=True)
    to_place_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("petri_net_places.id"), nullable=True)
    to_transition_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("petri_net_transitions.id"), nullable=True)
    arc_type: Mapped[str] = mapped_column(String(50), default="normal")  # normal, inhibitor, reset, read
    arc_weight: Mapped[int] = mapped_column(Integer, default=1)
    
    # Relationships
    version: Mapped["ProcessModelVersionModel"] = relationship("ProcessModelVersionModel", back_populates="petri_arcs")


class DirectlyFollowsEdgeModel(Base):
    """ORM model for DFG edges with enhanced metrics."""
    __tablename__ = "directly_follows_edges"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_model_versions.id"), nullable=False, index=True)
    source_activity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
    target_activity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
    source_activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_transition_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_transition_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    version: Mapped["ProcessModelVersionModel"] = relationship("ProcessModelVersionModel", back_populates="dfg_edges")


# =============================================================================
# PHASE 3: CONFORMANCE & COMPLIANCE
# =============================================================================

class ReferenceModelModel(Base):
    """ORM model for Reference/Normative Models."""
    __tablename__ = "reference_models"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    process_model_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_model_versions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="discovered")  # discovered, imported, designed, regulatory
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
    event_log_version_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("event_log_versions.id"), nullable=True)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False, index=True)
    reference_model_id: Mapped[str] = mapped_column(String(36), ForeignKey("reference_models.id"), nullable=False, index=True)
    initiated_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False)  # token_replay, alignment, footprint, behavioral_profile
    status: Mapped[str] = mapped_column(String(50), default="queued")  # queued, replaying, aligning, analyzing, completed, failed
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
    reference_model: Mapped["ReferenceModelModel"] = relationship("ReferenceModelModel", back_populates="conformance_runs")
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
    check_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("conformance_check_runs.id"), nullable=False, index=True)
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    is_fitting: Mapped[bool] = mapped_column(Integer, default=False)
    case_fitness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    alignment_cost: Mapped[int] = mapped_column(Integer, default=0)
    synchronous_moves: Mapped[int] = mapped_column(Integer, default=0)
    model_moves: Mapped[int] = mapped_column(Integer, default=0)
    log_moves: Mapped[int] = mapped_column(Integer, default=0)
    deviation_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    check_run: Mapped["ConformanceCheckRunModel"] = relationship("ConformanceCheckRunModel", back_populates="case_results")
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
    case_result_id: Mapped[str] = mapped_column(String(36), ForeignKey("case_conformance_results.id"), nullable=False, index=True)
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[str] = mapped_column(String(50), nullable=False)  # sync, model_move, log_move, invisible
    log_activity_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    model_activity_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    log_event_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    step_cost: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    case_result: Mapped["CaseConformanceResultModel"] = relationship("CaseConformanceResultModel", back_populates="alignment_steps")


class DeviationTypeModel(Base):
    """ORM model for deviation pattern catalog."""
    __tablename__ = "deviation_types"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    check_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("conformance_check_runs.id"), nullable=False, index=True)
    activity_type_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # missing_activity, unexpected_activity, wrong_sequence, skipped_mandatory, repeated_activity, timing_violation
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="medium")  # low, medium, high, critical
    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    occurrence_rate: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Relationships
    check_run: Mapped["ConformanceCheckRunModel"] = relationship("ConformanceCheckRunModel", back_populates="deviation_types")
    instances: Mapped[list["DeviationInstanceModel"]] = relationship(
        "DeviationInstanceModel", back_populates="deviation_type", cascade="all, delete-orphan"
    )


class DeviationInstanceModel(Base):
    """ORM model for individual deviation occurrences."""
    __tablename__ = "deviation_instances"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    deviation_type_id: Mapped[str] = mapped_column(String(36), ForeignKey("deviation_types.id"), nullable=False, index=True)
    case_result_id: Mapped[str] = mapped_column(String(36), ForeignKey("case_conformance_results.id"), nullable=False, index=True)
    event_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    deviation_type: Mapped["DeviationTypeModel"] = relationship("DeviationTypeModel", back_populates="instances")
    case_result: Mapped["CaseConformanceResultModel"] = relationship("CaseConformanceResultModel", back_populates="deviation_instances")


class ComplianceRuleModel(Base):
    """ORM model for declarative compliance rules (DECLARE patterns)."""
    __tablename__ = "compliance_rules"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    reference_model_id: Mapped[str] = mapped_column(String(36), ForeignKey("reference_models.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # existence, absence, exactly, response, precedence, succession, chain_response
    ltl_expression: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(50), default="error")  # info, warning, error, critical
    is_mandatory: Mapped[bool] = mapped_column(Integer, default=True)
    is_enabled: Mapped[bool] = mapped_column(Integer, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reference_model: Mapped["ReferenceModelModel"] = relationship("ReferenceModelModel", back_populates="compliance_rules")
    violations: Mapped[list["ComplianceViolationModel"]] = relationship(
        "ComplianceViolationModel", back_populates="rule", cascade="all, delete-orphan"
    )


class ComplianceViolationModel(Base):
    """ORM model for compliance rule violations."""
    __tablename__ = "compliance_violations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    check_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("conformance_check_runs.id"), nullable=False, index=True)
    rule_id: Mapped[str] = mapped_column(String(36), ForeignKey("compliance_rules.id"), nullable=False, index=True)
    case_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rule: Mapped["ComplianceRuleModel"] = relationship("ComplianceRuleModel", back_populates="violations")


# =============================================================================
# PHASE 4: PERFORMANCE ANALYTICS & KPIs
# =============================================================================

class PerformanceAnalysisRunModel(Base):
    """ORM model for Performance Analysis Runs."""
    __tablename__ = "performance_analysis_runs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    event_log_version_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("event_log_versions.id"), nullable=True)
    log_id: Mapped[str] = mapped_column(String(36), ForeignKey("event_logs.id"), nullable=False, index=True)
    initiated_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)  # duration, frequency, bottleneck, throughput, workload
    status: Mapped[str] = mapped_column(String(50), default="queued")  # queued, processing, completed, failed
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    summary_statistics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    activity_metrics: Mapped[list["ActivityPerformanceMetricModel"]] = relationship(
        "ActivityPerformanceMetricModel", back_populates="analysis_run", cascade="all, delete-orphan"
    )
    transition_metrics: Mapped[list["TransitionPerformanceMetricModel"]] = relationship(
        "TransitionPerformanceMetricModel", back_populates="analysis_run", cascade="all, delete-orphan"
    )
    resource_metrics: Mapped[list["ResourcePerformanceMetricModel"]] = relationship(
        "ResourcePerformanceMetricModel", back_populates="analysis_run", cascade="all, delete-orphan"
    )
    bottleneck_findings: Mapped[list["BottleneckFindingModel"]] = relationship(
        "BottleneckFindingModel", back_populates="analysis_run", cascade="all, delete-orphan"
    )


class ActivityPerformanceMetricModel(Base):
    """ORM model for per-activity performance metrics."""
    __tablename__ = "activity_performance_metrics"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("performance_analysis_runs.id"), nullable=False, index=True)
    activity_type_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
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
    analysis_run: Mapped["PerformanceAnalysisRunModel"] = relationship("PerformanceAnalysisRunModel", back_populates="activity_metrics")


class TransitionPerformanceMetricModel(Base):
    """ORM model for per-transition performance metrics."""
    __tablename__ = "transition_performance_metrics"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("performance_analysis_runs.id"), nullable=False, index=True)
    from_activity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
    to_activity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
    from_activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    to_activity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    transition_count: Mapped[int] = mapped_column(Integer, default=0)
    min_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_time_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    transition_probability: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Relationships
    analysis_run: Mapped["PerformanceAnalysisRunModel"] = relationship("PerformanceAnalysisRunModel", back_populates="transition_metrics")


class ResourcePerformanceMetricModel(Base):
    """ORM model for per-resource performance metrics."""
    __tablename__ = "resource_performance_metrics"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("performance_analysis_runs.id"), nullable=False, index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("resource_profiles.id"), nullable=True)
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
    analysis_run: Mapped["PerformanceAnalysisRunModel"] = relationship("PerformanceAnalysisRunModel", back_populates="resource_metrics")


class BottleneckFindingModel(Base):
    """ORM model for detected bottlenecks."""
    __tablename__ = "bottleneck_findings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("performance_analysis_runs.id"), nullable=False, index=True)
    activity_type_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
    from_activity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
    to_activity_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("activity_types.id"), nullable=True)
    location: Mapped[str] = mapped_column(String(50), nullable=False)  # activity, transition, resource, batch_point
    bottleneck_type: Mapped[str] = mapped_column(String(50), nullable=False)  # processing_time, waiting_time, resource_contention, batching
    severity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_delay_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_time_impact_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cases_affected: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    analysis_run: Mapped["PerformanceAnalysisRunModel"] = relationship("PerformanceAnalysisRunModel", back_populates="bottleneck_findings")


class ProcessKPIModel(Base):
    """ORM model for KPI definitions."""
    __tablename__ = "process_kpis"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # time, cost, quality, throughput, compliance, custom
    formula: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    direction: Mapped[str] = mapped_column(String(50), default="lower_is_better")  # higher_is_better, lower_is_better
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
    kpi_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_kpis.id"), nullable=False, index=True)
    event_log_version_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("event_log_versions.id"), nullable=True)
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
    kpi_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_kpis.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), default="maximum")  # minimum, maximum, exact, range
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
    kpi_id: Mapped[str] = mapped_column(String(36), ForeignKey("process_kpis.id"), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(36), ForeignKey("kpi_targets.id"), nullable=False, index=True)
    measurement_id: Mapped[str] = mapped_column(String(36), ForeignKey("kpi_measurements.id"), nullable=False, index=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)  # target_breach, trend_decline, anomaly
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

