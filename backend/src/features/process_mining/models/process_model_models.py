"""Process Model Models.

Discovered process models, metrics, and graph caches.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, deferred, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from .dataset import Dataset


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
