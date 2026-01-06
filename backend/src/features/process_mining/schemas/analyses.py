"""Saved analysis schemas - Persisted analysis state.

Contains schemas for:
- Analysis creation and response
- Analysis details with results
- Job status
- Uploaded file metadata
- Patterns and performance dashboards
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.features.process_mining.schemas.analytics import (
    BottleneckResponse,
    CycleTimeResponse,
    ThroughputResponse,
)
from src.features.process_mining.schemas.datasets import (
    StatisticsResponse,
    VariantResponse,
)
from src.features.process_mining.schemas.visualization import DFGResponse
from src.shared.schemas import PaginatedResponse


class AnalysisCreateRequest(BaseModel):
    """Request to create a new analysis."""

    name: str = Field(..., min_length=1, max_length=255)
    analysis_type: str = Field(
        ..., description="Type: discovery, conformance, variants, bottleneck"
    )
    config: dict[str, Any] = Field(default_factory=dict, description="Analysis configuration")


class AnalysisResponse(BaseModel):
    """Analysis response."""

    id: str
    dataset_id: str
    created_by: str | None = None  # User who created the analysis
    name: str
    analysis_type: str
    status: str
    config: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    result_full_path: str | None = None  # Path to full results file for large results
    model_id: str | None = None
    workflow_id: str | None = None  # Temporal workflow tracking
    created_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse config_json and result_summary_json."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "dataset_id",
                    "created_by",
                    "name",
                    "analysis_type",
                    "status",
                    "config_json",
                    "result_summary_json",
                    "result_full_path",
                    "model_id",
                    "workflow_id",
                    "created_at",
                    "completed_at",
                    "error_message",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("config_json"):
                try:
                    data["config"] = json.loads(data["config_json"])
                except (json.JSONDecodeError, TypeError):
                    data["config"] = None
            if data.get("result_summary_json"):
                try:
                    data["result_summary"] = json.loads(data["result_summary_json"])
                except (json.JSONDecodeError, TypeError):
                    data["result_summary"] = None
        return data

    model_config = ConfigDict(from_attributes=True)


class AnalysisListResponse(PaginatedResponse):
    """Paginated analysis list."""

    items: list[AnalysisResponse]


class AnalysisDetailResponse(AnalysisResponse):
    """Detailed analysis with full results."""

    dfg: DFGResponse | None = None
    variants: list[VariantResponse] | None = None
    statistics: StatisticsResponse | None = None


class JobStatusResponse(BaseModel):
    """Async job status."""

    id: str
    job_type: str
    status: str
    progress: int
    stage: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse result_json to result dict."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "job_type",
                    "status",
                    "progress",
                    "stage",
                    "result_json",
                    "error",
                    "created_at",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("result_json"):
                try:
                    data["result"] = json.loads(data["result_json"])
                except (json.JSONDecodeError, TypeError):
                    data["result"] = None
            elif "result" not in data:
                data["result"] = None
        return data

    model_config = ConfigDict(from_attributes=True)


class UploadedFileResponse(BaseModel):
    """Uploaded file metadata response."""

    id: str
    filename: str
    storage_path: str
    size_bytes: int | None = None
    mime_type: str | None = None
    checksum: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Misc Patterns (Performance)
# =============================================================================


class PatternResponse(BaseModel):
    """Frequent pattern/subsequence."""

    pattern: str
    frequency: int
    support: float


class PerformanceDashboardResponse(BaseModel):
    """Performance summary dashboard."""

    dataset_id: str
    cycle_time: CycleTimeResponse
    throughput: ThroughputResponse
    top_bottlenecks: list[BottleneckResponse]
    rework_summary: dict[str, Any]
