"""Process Model Models.

Discovered process models, metrics, and graph caches.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, deferred, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from .dataset import Dataset


class ProcessModel(Base):
    """Discovered or uploaded process model."""

    __tablename__ = "process_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Model type and format
    model_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # 'petri_net', 'process_tree', 'bpmn', 'dfg', 'heuristics_net', 'declare', 'transition_system'
    model_format: Mapped[str] = mapped_column(String(50), nullable=False)
    # 'pnml', 'bpmn_xml', 'json', 'dot', 'pm4py_pickle'

    # Storage (file path preferred over BLOB)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Legacy BLOB storage (deprecated - use storage_path)
    serialized_model: Mapped[bytes | None] = deferred(mapped_column(LargeBinary, nullable=True))

    # Quick-access graph structure (for rendering without loading full model)
    graph_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Discovery metadata (null if manually uploaded)
    discovery_algorithm: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    discovery_params_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    discovery_workflow_id: Mapped[str | None] = mapped_column(
        ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Model source
    is_discovered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_reference: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    # Version tracking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_model_id: Mapped[str | None] = mapped_column(
        ForeignKey("process_models.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Quick metrics (duplicated from ProcessModelMetrics for listing)
    fitness: Mapped[float | None] = mapped_column(Float, nullable=True)
    precision: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Legacy fields (for backward compatibility)
    miner_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # Deprecated: use model_type
    standard_content_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # Deprecated: use storage_path
    graph_structure_json: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Deprecated: use graph_json
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    source_dataset: Mapped[Optional["Dataset"]] = relationship(back_populates="models")
    parent_model: Mapped[Optional["ProcessModel"]] = relationship(
        remote_side=[id], foreign_keys=[parent_model_id], lazy="selectin"
    )
    metrics: Mapped[Optional["ProcessModelMetrics"]] = relationship(
        back_populates="model", uselist=False, cascade="all, delete-orphan"
    )
    graph_caches: Mapped[list["GraphCache"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )


class ProcessModelMetrics(Base):
    """Process model quality metrics (can have multiple evaluations per model)."""

    __tablename__ = "process_model_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    model_id: Mapped[str] = mapped_column(
        ForeignKey("process_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dataset_id: Mapped[str | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # The Four Quality Dimensions
    fitness: Mapped[float | None] = mapped_column(Float, nullable=True)
    precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    generalization: Mapped[float | None] = mapped_column(Float, nullable=True)
    simplicity: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Composite score
    f_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Conformance details
    fitting_traces_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    non_fitting_traces_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fitting_traces_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_trace_fitness: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Alignment-based metrics
    average_alignment_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    alignment_details_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Structural metrics
    total_places: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_transitions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_arcs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    silent_transitions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    complexity_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Legacy fields
    total_activities: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fitness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    precision_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Evaluation metadata
    evaluation_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    computation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    model: Mapped["ProcessModel"] = relationship(back_populates="metrics")

    __table_args__ = (Index("ix_model_metrics_model_dataset", "model_id", "dataset_id"),)


class GraphCache(Base):
    """Cached graph layouts (expensive to compute)."""

    __tablename__ = "graph_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    model_id: Mapped[str] = mapped_column(
        ForeignKey("process_models.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Cache key components
    abstraction_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    layout_algorithm: Mapped[str] = mapped_column(String(50), default="dagre", nullable=False)
    filter_params_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Cached content
    layout_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    svg_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Legacy field
    cached_layout_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Cache management
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    access_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    model: Mapped["ProcessModel"] = relationship(back_populates="graph_caches")

    __table_args__ = (
        Index(
            "ix_graph_cache_unique",
            "model_id",
            "abstraction_level",
            "layout_algorithm",
            "filter_params_hash",
            unique=True,
        ),
    )
