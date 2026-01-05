"""Jobs schemas.

Request and response models for async job management endpoints.
"""

from pydantic import BaseModel

from src.features.process_mining.schemas import JobStatusResponse
from src.platform.schemas import PaginatedResponse


# =============================================================================
# Response Models
# =============================================================================


class JobListResponse(PaginatedResponse):
    """Paginated job list."""

    items: list[JobStatusResponse]


class JobCancelResponse(BaseModel):
    """Response after cancelling or deleting a job."""

    id: str
    status: str
    message: str


class JobLogEntry(BaseModel):
    """Job log entry."""

    timestamp: str
    level: str
    message: str
    details: dict | None = None


class JobLogsResponse(BaseModel):
    """Job logs response."""

    job_id: str
    logs: list[JobLogEntry]
    total: int


__all__ = [
    "JobListResponse",
    "JobCancelResponse",
    "JobLogEntry",
    "JobLogsResponse",
]
