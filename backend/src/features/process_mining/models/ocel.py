"""OCEL Service Models.

Models for OCEL log management, discovery, and analysis.
These models support the Object-Centric Process Mining (OCPM) features.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, deferred, mapped_column, relationship

from src.shared.database import Base


class OCELLog(Base):
    """Object-Centric Event Log (OCEL).

    Represents an uploaded OCEL file (JSON, SQLite, XML) and its metadata.
    Stores the raw file content for processing.
    """

    __tablename__ = "ocel_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_format: Mapped[str] = mapped_column(String(20), default="jsonocel")

    # Statistics
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_objects: Mapped[int] = mapped_column(Integer, default=0)
    total_object_types: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Raw Data (deferred loading for performance)
    ocel_data: Mapped[bytes | None] = deferred(mapped_column(LargeBinary, nullable=True))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    object_types: Mapped[list["OCELObjectType"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan", lazy="selectin"
    )
    petri_nets: Mapped[list["OCPetriNet"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )


class OCELObjectType(Base):
    """Object Type summary for an OCEL log.

    Stores the object types present in an OCEL log and their statistics.
    """

    __tablename__ = "ocel_object_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("ocel_logs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    object_count: Mapped[int] = mapped_column(Integer, default=0)
    attributes_schema_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    dataset: Mapped["OCELLog"] = relationship(back_populates="object_types")


class OCPetriNet(Base):
    """Object-Centric Petri Net (OC-PN).

    Represents a discovered object-centric process model.
    """

    __tablename__ = "oc_petri_nets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("ocel_logs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # List of object types included in this model
    object_types_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Serialized PM4Py OC-PN object
    serialized_model: Mapped[bytes | None] = deferred(mapped_column(LargeBinary, nullable=True))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    dataset: Mapped["OCELLog"] = relationship(back_populates="petri_nets")
