"""Organizational Mining Models.

Social networks, activity mappings, and hierarchical process models.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from .dataset import Dataset


class SocialNetwork(Base):
    """Social network from organizational mining."""

    __tablename__ = "social_networks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    network_type: Mapped[str] = mapped_column(String(50), nullable=False)
    graph_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ActivityMapping(Base):
    """Activity mapping for hierarchical abstraction."""

    __tablename__ = "activity_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mapping_rules: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    dataset: Mapped["Dataset"] = relationship(back_populates="activity_mappings")
    hierarchical_models: Mapped[list["HierarchicalProcessModel"]] = relationship(
        back_populates="mapping", cascade="all, delete-orphan"
    )


class HierarchicalProcessModel(Base):
    """Process model at a specific abstraction level."""

    __tablename__ = "hierarchical_process_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    mapping_id: Mapped[str] = mapped_column(
        ForeignKey("activity_mappings.id", ondelete="CASCADE"), nullable=False
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    graph_structure_json: Mapped[str] = mapped_column(Text, nullable=False)
    pnml_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    activity_count: Mapped[int] = mapped_column(Integer, nullable=False)
    edge_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    mapping: Mapped["ActivityMapping"] = relationship(back_populates="hierarchical_models")
