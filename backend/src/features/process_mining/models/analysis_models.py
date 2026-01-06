"""Analysis Models.

Analysis, conformance, and analytics cache models.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, deferred, mapped_column, relationship

from src.shared.database import Base

from .enums import AnalysisStatus

if TYPE_CHECKING:
    from .dataset import Dataset
    from .process_model import ProcessModel


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
