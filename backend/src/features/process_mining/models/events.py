"""Event Models.

Process case and event models for event log storage.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from .dataset import Dataset


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
    
    
    # Legacy string columns (retained for query compatibility - denormalized for DuckDB analytics)
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
