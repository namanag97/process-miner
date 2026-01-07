"""Workflow Schemas.

Pydantic schemas for Temporal workflow tracking API responses.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.shared.schemas import PaginatedResponse

# =============================================================================
# Workflow Task Schemas
# =============================================================================


class WorkflowTaskResponse(BaseModel):
    """Individual task within a workflow execution."""

    id: str
    task_name: str = Field(..., description="Task name, e.g. 'validate_file', 'ingest_events'")
    task_order: int = Field(..., description="Execution order within workflow")
    status: str = Field(..., description="pending, running, completed, failed, skipped")
    progress_percent: int = Field(0, ge=0, le=100)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = Field(None, description="Task duration in milliseconds")
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Workflow Schemas
# =============================================================================


class WorkflowResponse(BaseModel):
    """Workflow execution tracking response."""

    id: str
    temporal_workflow_id: str | None = Field(None, description="Temporal's workflow ID")
    temporal_run_id: str | None = Field(None, description="Temporal's run ID")
    workflow_type: str = Field(
        ..., description="ingestion, discovery, conformance, prediction, export"
    )
    entity_type: str | None = Field(None, description="dataset, model, analysis")
    entity_id: str | None = None
    status: str = Field(
        ..., description="pending, running, completed, failed, cancelled, timed_out"
    )
    progress_percent: int = Field(0, ge=0, le=100)
    current_step: str | None = Field(None, description="Human-readable current step")
    error_code: str | None = None
    error_message: str | None = None
    retry_count: int = 0
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    tasks: list[WorkflowTaskResponse] = Field(
        default_factory=list, description="Task-level progress"
    )

    model_config = ConfigDict(from_attributes=True)


class WorkflowListResponse(PaginatedResponse):
    """Paginated workflow list."""

    items: list[WorkflowResponse]


class WorkflowSummaryResponse(BaseModel):
    """Lightweight workflow summary for listings."""

    id: str
    workflow_type: str
    status: str
    progress_percent: int
    current_step: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "WorkflowListResponse",
    "WorkflowResponse",
    "WorkflowSummaryResponse",
    "WorkflowTaskResponse",
]
