"""Workflow Schemas.

Schemas for workflow orchestration (legacy - superceded by DAGs).
These are kept for backward compatibility with existing API contracts.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    """A step in a workflow."""

    name: str = Field(..., description="Step name")
    task_type: str = Field(..., description="Type of task to execute")
    config: dict | None = Field(default=None, description="Step configuration")
    depends_on: list[str] = Field(default_factory=list, description="Dependencies")


class WorkflowTemplate(BaseModel):
    """Predefined workflow template."""

    id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    description: str | None = Field(default=None, description="Template description")
    steps: list[WorkflowStep] = Field(default_factory=list, description="Workflow steps")


class WorkflowCreateRequest(BaseModel):
    """Request to create a new workflow."""

    name: str = Field(..., min_length=1, max_length=255, description="Workflow name")
    description: str | None = Field(default=None, max_length=1000, description="Description")
    template_id: str | None = Field(default=None, description="Template to use")
    steps: list[WorkflowStep] = Field(default_factory=list, description="Custom steps")
    dataset_id: str | None = Field(default=None, description="Associated dataset")


class WorkflowResponse(BaseModel):
    """Workflow response."""

    id: str = Field(..., description="Workflow ID")
    name: str = Field(..., description="Workflow name")
    description: str | None = Field(default=None, description="Description")
    status: str = Field(default="draft", description="Workflow status")
    steps: list[WorkflowStep] = Field(default_factory=list, description="Workflow steps")
    dataset_id: str | None = Field(default=None, description="Associated dataset")
    created_at: datetime | None = Field(default=None, description="Creation time")
    updated_at: datetime | None = Field(default=None, description="Last update time")

    model_config = {"from_attributes": True}


class WorkflowRunRequest(BaseModel):
    """Request to run a workflow."""

    parameters: dict = Field(default_factory=dict, description="Runtime parameters")


class WorkflowRunResponse(BaseModel):
    """Response for a workflow run."""

    id: str = Field(..., description="Run ID")
    workflow_id: str = Field(..., description="Workflow ID")
    status: str = Field(..., description="Run status")
    started_at: datetime | None = Field(default=None, description="Start time")
    completed_at: datetime | None = Field(default=None, description="Completion time")
    result: dict | None = Field(default=None, description="Run result")
    error: str | None = Field(default=None, description="Error message if failed")

    model_config = {"from_attributes": True}


__all__ = [
    "WorkflowCreateRequest",
    "WorkflowResponse",
    "WorkflowRunRequest",
    "WorkflowRunResponse",
    "WorkflowStep",
    "WorkflowTemplate",
]
