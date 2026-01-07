"""Cache Models for Performance Optimization.

DFG and Variant caching for faster discovery and visualization.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.database import Base


class DFGCache(Base):
    """Pre-computed Directly-Follows Graph for fast discovery/visualization.

    Computed during ingestion workflow to avoid repeated DFG computation.
    Used by:
    - DFG-based miners (Inductive-DFG)
    - Visualization endpoints
    - Explorer page frequency overlays
    """

    __tablename__ = "dfg_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Frequency-based DFG
    # JSON format: {"edges": [["A", "B", 100], ...], "start_activities": {"A": 50}, "end_activities": {"Z": 50}}
    dfg_data: Mapped[str] = mapped_column(Text, nullable=False)
    start_activities: Mapped[str] = mapped_column(Text, nullable=False)
    end_activities: Mapped[str] = mapped_column(Text, nullable=False)

    # Activity frequencies
    activity_counts: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Performance variant (with timing)
    has_performance_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    performance_dfg_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON format: {"edges": [["A", "B", {"mean": 3600, "median": 3000, "min": 100, "max": 10000}], ...]}

    # Metadata
    edge_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    activity_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    computation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (Index("ix_dfg_cache_dataset", "dataset_id", unique=True),)


class VariantCache(Base):
    """Pre-computed variant representation for fast analysis.

    Variants are unique activity sequences (traces) with their counts.
    Used by:
    - Variant analysis in Explorer
    - Filtering by variant
    - Inductive miners (can use variant representation for speed)
    """

    __tablename__ = "variant_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Variant data
    # JSON format: {"variants": [{"sequence": ["A", "B", "C"], "count": 150, "case_ids": ["c1", "c2"]}, ...]}
    variants_data: Mapped[str] = mapped_column(Text, nullable=False)
    variant_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Statistics
    top_variant_coverage: Mapped[float | None] = mapped_column(
        Integer, nullable=True
    )  # % of cases covered by top variant
    top_5_coverage: Mapped[float | None] = mapped_column(
        Integer, nullable=True
    )  # % of cases covered by top 5 variants
    avg_variant_length: Mapped[float | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    computation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (Index("ix_variant_cache_dataset", "dataset_id", unique=True),)
