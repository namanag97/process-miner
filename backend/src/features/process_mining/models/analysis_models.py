"""Analysis Models.

Analysis, conformance, and analytics cache models.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, deferred, mapped_column, relationship

from src.shared.database import Base

from .enums import AnalysisStatus

if TYPE_CHECKING:
    from .dataset import Dataset
    from .process_model import ProcessModel


class Analysis(Base):
    """Generic analysis run (conformance, bottleneck, social network, etc.)."""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Analysis identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: 'conformance', 'bottleneck', 'social_network', 'variant_analysis',
    #        'root_cause', 'decision_point', 'batching', 'resource_utilization'

    # Configuration
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Reference model (for conformance)
    model_id: Mapped[str | None] = mapped_column(
        ForeignKey("process_models.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default=AnalysisStatus.PENDING.value, index=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    workflow_id: Mapped[str | None] = mapped_column(
        ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Results
    result_summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = deferred(mapped_column(Text, nullable=True))
    result_full_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="analyses")
    process_model: Mapped[Optional["ProcessModel"]] = relationship(lazy="selectin")


class ConformanceResult(Base):
    """Conformance checking results (detailed)."""

    __tablename__ = "conformance_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    analysis_id: Mapped[str | None] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=True, unique=True, index=True
    )
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_id: Mapped[str] = mapped_column(
        ForeignKey("process_models.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Overall metrics
    fitness: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    generalization: Mapped[float | None] = mapped_column(Float, nullable=True)
    simplicity: Mapped[float | None] = mapped_column(Float, nullable=True)
    f_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Method used
    method: Mapped[str] = mapped_column(String(50), default="token_replay")
    # 'token_replay', 'alignment', 'footprint'

    # Detailed conformance info
    total_traces: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fitting_traces: Mapped[int | None] = mapped_column(Integer, nullable=True)
    non_fitting_traces: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Deviation analysis
    deviations_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    deviation_patterns_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Alignment metrics
    average_alignment_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    diagnostics_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_conformance_dataset_model", "dataset_id", "model_id"),)


class AnalyticsCache(Base):
    """Cached analytics results (for dashboard widgets)."""

    __tablename__ = "analytics_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Cache key
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: 'activity_frequency', 'case_duration_distribution', 'resource_workload',
    #        'throughput_time', 'bottleneck_activities', 'daily_case_volume'
    parameters_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Cached result
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Cache management
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ttl_seconds: Mapped[int] = mapped_column(Integer, default=3600)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)

    __table_args__ = (
        Index(
            "ix_analytics_cache_unique", "dataset_id", "metric_type", "parameters_hash", unique=True
        ),
    )
