"""Event Models.

Process case and event models for event log storage.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from .dataset import Dataset
    from .variants import ProcessVariant


class ProcessCase(Base):
    """Individual case/trace in a dataset."""

    __tablename__ = "process_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(String(255), nullable=False)  # Original case ID from source
    
    # Variant reference (for efficient variant analysis)
    variant_id: Mapped[str | None] = mapped_column(
        ForeignKey("process_variants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    # Precomputed case-level metrics
    event_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)  # end - start
    
    # Case attributes (from source data)
    attributes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Legacy field (deprecated - use variant_id instead)
    variant_key: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="cases")
    variant: Mapped[Optional["ProcessVariant"]] = relationship(back_populates="cases")
    events: Mapped[list["ProcessEvent"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        lazy="raise",
        order_by="ProcessEvent.event_index",
    )
    
    # Composite indexes
    __table_args__ = (
        Index("ix_cases_dataset_case_id", "dataset_id", "case_id", unique=True),
    )


class ProcessEvent(Base):
    """Single event in a case.
    
    Scalability Note: This table can grow to millions of rows.
    Activity and resource are normalized via lookup tables for efficiency.
    """

    __tablename__ = "process_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Denormalized dataset_id for query performance (critical!)
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
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
    
    # Core event data
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # For duration
    
    # Position in case (for sequence queries)
    event_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0, 1, 2, ... within case
    
    # Event attributes
    attributes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Legacy string columns (retained for query compatibility - denormalized for DuckDB analytics)
    activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    resource: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    case: Mapped["ProcessCase"] = relationship(back_populates="events")
    
    # Composite indexes for common query patterns
    __table_args__ = (
        # Query: all events for a case, ordered by index
        Index("ix_events_case_index", "case_ref_id", "event_index"),
        # Query: time-range queries across dataset
        Index("ix_events_dataset_timestamp", "dataset_id", "timestamp"),
        # Query: activity filtering within dataset
        Index("ix_events_dataset_activity", "dataset_id", "activity_id"),
    )

