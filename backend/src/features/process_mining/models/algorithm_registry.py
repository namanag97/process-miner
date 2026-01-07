"""Algorithm Registry Models.

Database-backed algorithm registry with metadata and parameters.
Enables dynamic recommendations and UI-driven parameter configuration.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base


class Algorithm(Base):
    """Algorithm registry - stores metadata about mining algorithms."""

    __tablename__ = "algorithms"

    # Primary key is the algorithm identifier (e.g., 'inductive', 'alpha')
    id: Mapped[str] = mapped_column(String(50), primary_key=True)

    # Display info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Categories: 'discovery', 'conformance', 'enhancement', 'declarative'

    # Output format
    output_format: Mapped[str] = mapped_column(String(50), nullable=False)
    # Formats: 'petri_net', 'process_tree', 'bpmn', 'dfg', 'heuristics_net', 'declare'

    # Characteristics
    requires_external: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    external_dependency: Mapped[str | None] = mapped_column(String(100), nullable=True)
    guarantees_soundness: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Performance ratings (1-5 scale)
    noise_tolerance: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    speed_rating: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    # Complexity
    complexity_class: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Classes: 'O(n)', 'O(n²)', 'O(n log n)', 'O(2^n)'

    # Recommendations
    max_recommended_events: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_recommended_activities: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_recommended_events: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Documentation
    documentation_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Ordering for UI
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_recommended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    parameters: Mapped[list["AlgorithmParameter"]] = relationship(
        back_populates="algorithm",
        cascade="all, delete-orphan",
        order_by="AlgorithmParameter.display_order",
    )


class AlgorithmParameter(Base):
    """Algorithm parameters with types and validation."""

    __tablename__ = "algorithm_parameters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    algorithm_id: Mapped[str] = mapped_column(
        ForeignKey("algorithms.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Parameter identity
    param_name: Mapped[str] = mapped_column(String(50), nullable=False)
    param_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Types: 'float', 'int', 'bool', 'string', 'enum'

    # Values
    default_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    min_value: Mapped[str | None] = mapped_column(String(50), nullable=True)
    max_value: Mapped[str | None] = mapped_column(String(50), nullable=True)
    enum_values: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

    # Display
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # UI hints
    is_advanced: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    algorithm: Mapped["Algorithm"] = relationship(back_populates="parameters")

    __table_args__ = (Index("ix_algo_param_unique", "algorithm_id", "param_name", unique=True),)
