"""OCEL 2.0 Data Models - Object-Centric Event Log Support.

Implements the OCEL 2.0 standard for object-centric process mining.
Reference: https://ocel-standard.org

Key concepts:
- Events can relate to multiple objects (E2O relationships)
- Objects can relate to other objects (O2O relationships)
- Relationships are qualified (e.g., "created", "modified", "part_of")
- Dynamic object attributes tracked over time
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.orm import Base

# =============================================================================
# OCEL 2.0 Core Tables
# =============================================================================


class OCEL2EventType(Base):
    """Event type definition in OCEL 2.0."""

    __tablename__ = "ocel2_event_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Attribute schema for events of this type (JSON Schema format)
    attributes_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    events: Mapped[list["OCEL2Event"]] = relationship(back_populates="event_type", lazy="selectin")


class OCEL2ObjectType(Base):
    """Object type definition in OCEL 2.0."""

    __tablename__ = "ocel2_object_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Attribute schema for objects of this type
    attributes_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    objects: Mapped[list["OCEL2Object"]] = relationship(
        back_populates="object_type", lazy="selectin"
    )


class OCEL2Event(Base):
    """OCEL 2.0 compliant event.

    Unlike traditional events tied to a single case, OCEL events
    can relate to multiple objects through E2O relationships.
    """

    __tablename__ = "ocel2_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Event type reference
    event_type_id: Mapped[str] = mapped_column(
        ForeignKey("ocel2_event_types.id", ondelete="CASCADE"), nullable=False
    )

    # Activity name (denormalized for query performance)
    activity: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Dynamic attributes stored as JSON
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Source log reference (for imports from traditional logs)
    source_log_id: Mapped[str | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    event_type: Mapped["OCEL2EventType"] = relationship(back_populates="events")
    object_relations: Mapped[list["E2ORelation"]] = relationship(
        back_populates="event", cascade="all, delete-orphan", lazy="selectin"
    )


class OCEL2Object(Base):
    """OCEL 2.0 object instance.

    Objects represent business entities (Order, Item, Customer, etc.)
    that participate in events.
    """

    __tablename__ = "ocel2_objects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Object type reference
    object_type_id: Mapped[str] = mapped_column(
        ForeignKey("ocel2_object_types.id", ondelete="CASCADE"), nullable=False
    )

    # Business identifier (e.g., "ORD-12345")
    object_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Current attribute values (latest snapshot)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    object_type: Mapped["OCEL2ObjectType"] = relationship(back_populates="objects")
    event_relations: Mapped[list["E2ORelation"]] = relationship(
        back_populates="object", cascade="all, delete-orphan", lazy="selectin"
    )
    source_relations: Mapped[list["O2ORelation"]] = relationship(
        back_populates="source_object",
        foreign_keys="O2ORelation.source_object_id",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    target_relations: Mapped[list["O2ORelation"]] = relationship(
        back_populates="target_object",
        foreign_keys="O2ORelation.target_object_id",
        lazy="selectin",
    )


class E2ORelation(Base):
    """Event-to-Object relationship with qualifier.

    Represents the participation of an object in an event.
    The qualifier describes the role (e.g., "created", "read", "modified").
    """

    __tablename__ = "ocel2_e2o_relations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))

    event_id: Mapped[str] = mapped_column(
        ForeignKey("ocel2_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    object_id: Mapped[str] = mapped_column(
        ForeignKey("ocel2_objects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Qualifier describes the relationship type
    qualifier: Mapped[str] = mapped_column(String(50), default="involved")

    # Relationships
    event: Mapped["OCEL2Event"] = relationship(back_populates="object_relations")
    object: Mapped["OCEL2Object"] = relationship(back_populates="event_relations")


class O2ORelation(Base):
    """Object-to-Object relationship with qualifier.

    Represents relationships between objects independent of events.
    Examples: "part_of", "follows", "derived_from", "owned_by"
    """

    __tablename__ = "ocel2_o2o_relations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))

    source_object_id: Mapped[str] = mapped_column(
        ForeignKey("ocel2_objects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_object_id: Mapped[str] = mapped_column(
        ForeignKey("ocel2_objects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Qualifier describes the relationship type
    qualifier: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationship metadata
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    source_object: Mapped["OCEL2Object"] = relationship(
        back_populates="source_relations", foreign_keys=[source_object_id]
    )
    target_object: Mapped["OCEL2Object"] = relationship(
        back_populates="target_relations", foreign_keys=[target_object_id]
    )


class ObjectAttributeChange(Base):
    """Tracks dynamic attribute changes over time.

    OCEL 2.0 supports tracking how object attributes evolve.
    This enables "time machine" queries on historical state.
    """

    __tablename__ = "ocel2_object_attribute_changes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))

    object_id: Mapped[str] = mapped_column(
        ForeignKey("ocel2_objects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Which event caused this change (optional)
    event_id: Mapped[str | None] = mapped_column(
        ForeignKey("ocel2_events.id", ondelete="SET NULL"), nullable=True
    )

    # The attribute that changed
    attribute_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Old and new values
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
