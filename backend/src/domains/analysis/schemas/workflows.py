"""Workflow schemas - Automated workflow definitions and execution.

Contains schemas for:
- Workflow steps and definitions
- Workflow creation and response
- Workflow runs and templates
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WorkflowStep(BaseModel):
    """Workflow step definition."""

    name: str
    type: str  # ingest, discover, check_conformance, export
    params: dict[str, Any] = Field(default_factory=dict)


class WorkflowCreateRequest(BaseModel):
    """Request to create a workflow."""

    name: str
    steps: list[WorkflowStep]
    schedule: str | None = None  # Cron expression


class WorkflowResponse(BaseModel):
    """Workflow response."""

    id: str
    name: str
    steps: list[WorkflowStep] = []
    schedule: str | None
    is_active: bool
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse steps_json to steps list."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in ["id", "name", "steps_json", "schedule", "is_active", "created_at"]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("steps_json"):
                try:
                    data["steps"] = json.loads(data["steps_json"])
                except (json.JSONDecodeError, TypeError):
                    data["steps"] = []
            elif "steps" not in data:
                data["steps"] = []
        return data

    model_config = ConfigDict(from_attributes=True)


class WorkflowRunRequest(BaseModel):
    """Request to run a workflow."""

    dataset_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class WorkflowRunResponse(BaseModel):
    """Workflow run response."""

    id: str
    workflow_id: str
    dataset_id: str | None
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    error: str | None

    model_config = ConfigDict(from_attributes=True)


class WorkflowTemplate(BaseModel):
    """Pre-defined workflow template."""

    id: str
    name: str
    description: str
    steps: list[WorkflowStep]
