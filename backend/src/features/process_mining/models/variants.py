"""Process Variant Models.

Normalized storage for unique activity sequences (variants).
Enables efficient variant analysis queries.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from .dataset import Dataset
    from .events_models import ProcessCase


class ProcessVariant(Base):
    """Unique activity sequence (variant) within a dataset.
    
    Each unique trace pattern gets a single row here.
    ProcessCase.variant_id references this table for efficient variant analysis.
    
    Example:
        activity_sequence: ["Create Order", "Approve", "Ship", "Close"]
        activity_sequence_hash: "a1b2c3d4e5f6..."
        case_count: 150 (150 cases follow this exact path)
    """

    __tablename__ = "process_variants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # The sequence (stored as JSON array of activity names or IDs)
    activity_sequence_json: Mapped[str] = mapped_column(Text, nullable=False)
    # Fast lookup hash (SHA-256 of normalized sequence)
    activity_sequence_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    
    # Statistics
    case_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    frequency_percent: Mapped[float | None] = mapped_column(Float, nullable=True)  # case_count / total * 100
    avg_duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    cases: Mapped[list["ProcessCase"]] = relationship(
        back_populates="variant",
        lazy="raise"  # Avoid N+1 on large datasets
    )
    
    # Indexes for common queries
    __table_args__ = (
        # Unique variant per dataset
        Index("ix_variants_dataset_hash", "dataset_id", "activity_sequence_hash", unique=True),
        # For frequency ranking
        Index("ix_variants_case_count", "dataset_id", "case_count"),
    )
