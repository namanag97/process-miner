"""Base Schema Classes - Reduce Pydantic Boilerplate.

Provides reusable base classes and mixins for common schema patterns.
Reduces duplication across the 45+ Pydantic models in the codebase.

Usage:
    class DatasetResponse(TimestampMixin, IDMixin, BaseSchema):
        name: str
        status: str
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# =============================================================================
# Core Base Schema
# =============================================================================


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode
        populate_by_name=True,  # Allow both alias and field name
        str_strip_whitespace=True,  # Auto-strip strings
        validate_assignment=True,  # Validate on assignment
    )


# =============================================================================
# Common Mixins
# =============================================================================


class IDMixin(BaseModel):
    """Mixin for entities with UUID IDs."""
    
    id: str = Field(..., description="Unique identifier")


class TimestampMixin(BaseModel):
    """Mixin for entities with created/updated timestamps."""
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class CreatedAtMixin(BaseModel):
    """Mixin for entities with only created timestamp."""
    
    created_at: datetime = Field(..., description="Creation timestamp")


class SoftDeleteMixin(BaseModel):
    """Mixin for soft-deletable entities."""
    
    deleted_at: datetime | None = Field(None, description="Deletion timestamp")
    is_deleted: bool = Field(False, description="Whether entity is deleted")


# =============================================================================
# Column Mapping (Shared across multiple schemas)
# =============================================================================


class ColumnMappingBase(BaseModel):
    """Base column mapping - shared between ingestion and mapping schemas."""
    
    case_id: str = Field(..., alias="case_id_column", description="Column for case ID")
    activity: str = Field(..., alias="activity_column", description="Column for activity")
    timestamp: str = Field(..., alias="timestamp_column", description="Column for timestamp")
    resource: str | None = Field(None, alias="resource_column", description="Column for resource")
    
    model_config = ConfigDict(populate_by_name=True)


class ColumnMappingWithFormat(ColumnMappingBase):
    """Column mapping with timestamp format."""
    
    timestamp_format: str | None = Field(None, description="Timestamp format string")


# =============================================================================
# Pagination
# =============================================================================


class PaginationParams(BaseModel):
    """Standard pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response wrapper."""
    
    items: list[T]
    total: int = Field(..., description="Total item count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total pages")
    
    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """Factory method to create paginated response."""
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )


# =============================================================================
# API Response Wrappers
# =============================================================================


class SuccessResponse(BaseSchema):
    """Standard success response."""
    
    success: bool = True
    message: str = "Operation completed successfully"


class ErrorResponse(BaseSchema):
    """Standard error response."""
    
    success: bool = False
    error: str
    error_code: str | None = None
    details: dict[str, Any] | None = None


class JobResponse(BaseSchema):
    """Response for async job creation."""
    
    job_id: str = Field(..., description="Job ID for tracking")
    status: str = Field("pending", description="Initial job status")
    message: str = Field("Job created", description="Status message")


# =============================================================================
# Consolidated Entity Responses (Phase 4 Schema Consolidation)
# =============================================================================


class BaseEntityResponse(IDMixin, TimestampMixin, BaseSchema):
    """Base response for any persisted entity with ID and timestamps.
    
    Use this as a base class for API responses that represent database entities.
    Provides consistent id, created_at, and updated_at fields.
    
    Example:
        class DatasetResponse(BaseEntityResponse):
            name: str
            status: str
    """
    pass


class BaseTaskResponse(BaseEntityResponse):
    """Base response for async tasks/jobs with execution status.
    
    Extends BaseEntityResponse with status and timing fields for
    long-running operations like DAG runs, analysis jobs, etc.
    
    Example:
        class DAGRunResponse(BaseTaskResponse):
            definition_id: str
            steps: list[StepResponse]
    """
    
    status: str = Field(..., description="Current status (pending/running/completed/failed)")
    started_at: datetime | None = Field(None, description="Execution start time")
    completed_at: datetime | None = Field(None, description="Execution end time")
    error_message: str | None = Field(None, description="Error details if failed")
    
    @property
    def duration_seconds(self) -> float | None:
        """Calculate execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


# =============================================================================
# Statistics Mixins
# =============================================================================


class CountStatsMixin(BaseModel):
    """Mixin for count-based statistics."""
    
    total_events: int = Field(0, description="Total event count")
    total_cases: int = Field(0, description="Total case count")
    total_activities: int = Field(0, description="Total unique activities")


class TimeRangeMixin(BaseModel):
    """Mixin for time range data."""
    
    first_event_at: datetime | None = Field(None, description="Earliest event timestamp")
    last_event_at: datetime | None = Field(None, description="Latest event timestamp")


class DurationStatsMixin(BaseModel):
    """Mixin for duration statistics."""
    
    avg_duration_seconds: float | None = Field(None, description="Average duration in seconds")
    min_duration_seconds: float | None = Field(None, description="Minimum duration in seconds")
    max_duration_seconds: float | None = Field(None, description="Maximum duration in seconds")


# =============================================================================
# Entity Reference
# =============================================================================


class EntityRef(BaseSchema):
    """Lightweight entity reference for relationships."""
    
    id: str
    name: str | None = None
    type: str | None = None


class DatasetRef(EntityRef):
    """Reference to a dataset."""
    
    type: str = "dataset"
    status: str | None = None


class ProjectRef(EntityRef):
    """Reference to a project."""
    
    type: str = "project"
