"""Dataset Models.

Core dataset and file upload models for process mining.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

from .enums import DatasetStatus

if TYPE_CHECKING:
    from src.platform.models import Project


class Dataset(Base):
    """Uploaded dataset metadata."""

    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_format: Mapped[str] = mapped_column(String(20), default="csv")

    # Project association - references Platform layer
    project_id: Mapped[str | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )

    # Statistics
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)

    # JSON columns
    activities_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    statistics_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Lifecycle
    status: Mapped[str] = mapped_column(String(20), default=DatasetStatus.PENDING.value, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    mapping_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    column_suggestions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_columns_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # File metadata
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Job tracking
    validation_job_id: Mapped[str | None] = mapped_column(
        ForeignKey("async_jobs.id", ondelete="SET NULL"), nullable=True
    )
    ingestion_job_id: Mapped[str | None] = mapped_column(
        ForeignKey("async_jobs.id", ondelete="SET NULL"), nullable=True
    )

    # Filtering
    source_dataset_id: Mapped[str | None] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=True
    )
    filter_config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_filtered: Mapped[bool] = mapped_column(Boolean, default=False)
    filter_stats_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Temporal workflow tracking (Phase 4+ of migration)
    workflow_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Parquet-First Strategy (Phase 4): Store events as Parquet in S3 for analytics
    # When parquet_s3_key is set, analytics queries use DuckDB read_parquet() instead of DB
    parquet_s3_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    parquet_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parquet_row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships (use forward references for all relationships to avoid circular imports)
    uploaded_file: Mapped[Optional["UploadedFile"]] = relationship(
        back_populates="dataset", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )

    # Core relationships for process mining
    cases: Mapped[list["ProcessCase"]] = relationship(
        "ProcessCase", back_populates="dataset", cascade="all, delete-orphan", lazy="raise"
    )
    models: Mapped[list["ProcessModel"]] = relationship(
        "ProcessModel", back_populates="source_dataset", lazy="selectin"
    )
    analyses: Mapped[list["Analysis"]] = relationship(
        "Analysis", back_populates="dataset", cascade="all, delete-orphan", lazy="raise"
    )
    activity_mappings: Mapped[list["ActivityMapping"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan", lazy="raise"
    )

    # NEW: 4-Phase Upload Architecture relationships
    columns: Mapped[list["DatasetColumn"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan", lazy="select"
    )
    column_mapping: Mapped[Optional["DatasetColumnMapping"]] = relationship(
        back_populates="dataset", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )
    metadata_record: Mapped[Optional["DatasetMetadata"]] = relationship(
        back_populates="dataset", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )


class DatasetColumn(Base):
    """Detected column metadata from validation phase.
    
    Stores information about each column in the uploaded file,
    including type detection and sample values for mapping UI.
    """

    __tablename__ = "dataset_columns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Column info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dtype: Mapped[str] = mapped_column(String(50), nullable=False)  # STRING, INTEGER, DATETIME, FLOAT
    position: Mapped[int] = mapped_column(Integer, nullable=False)  # Column index in file
    
    # Statistics for mapping UI
    sample_values_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # First 5 unique values
    null_count: Mapped[int] = mapped_column(Integer, default=0)
    null_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    unique_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Process mining column suggestion
    suggested_role: Mapped[str | None] = mapped_column(String(50), nullable=True)  # case_id, activity, timestamp, resource
    suggestion_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0.0-1.0
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="columns")
    
    # Composite unique constraint: one entry per column per dataset
    __table_args__ = (
        Index("ix_dataset_columns_dataset_position", "dataset_id", "position", unique=True),
    )


class DatasetColumnMapping(Base):
    """Column mapping configuration for ingestion.
    
    Stores the mapping from file columns to process mining concepts.
    Can be auto-generated (high confidence) or user-provided.
    """

    __tablename__ = "dataset_column_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    
    # Required mappings
    case_id_column: Mapped[str] = mapped_column(String(255), nullable=False)
    activity_column: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp_column: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Optional mappings
    timestamp_format: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g., "%Y-%m-%d %H:%M:%S"
    resource_column: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Additional columns to preserve as event attributes
    additional_columns_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # ["cost", "department"]
    
    # Confidence scores for each mapping (used for display)
    confidence_scores_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # {"case_id": 0.95, ...}
    
    # Whether this was auto-mapped or user-provided
    auto_mapped: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="column_mapping")


class DatasetMetadata(Base):
    """Computed metadata after ingestion.
    
    Stores aggregate statistics computed after successful ingestion.
    Used for quick display without recomputing from events.
    """

    __tablename__ = "dataset_metadata"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    
    # Core counts
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)
    total_variants: Mapped[int] = mapped_column(Integer, default=0)
    
    # Time range
    first_event_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_event_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Duration stats (seconds)
    avg_case_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_case_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_case_duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Resource stats
    total_resources: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Computation tracking
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    computation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)


    # Relationships
    dataset: Mapped["Dataset"] = relationship(back_populates="metadata_record")
