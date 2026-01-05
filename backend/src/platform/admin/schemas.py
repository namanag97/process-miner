"""Admin schemas.

Request and response models for admin management endpoints.
Superuser-only system administration.
"""

from datetime import datetime

from pydantic import BaseModel, Field


# =============================================================================
# Request Models
# =============================================================================


class AdminUserUpdateRequest(BaseModel):
    """Admin user update request."""

    name: str | None = None
    role: str | None = Field(None, pattern=r"^(viewer|analyst|editor|admin|owner)$")
    is_active: bool | None = None


# =============================================================================
# Response Models
# =============================================================================


class AdminUserResponse(BaseModel):
    """Admin user response with full details."""

    id: str
    email: str
    name: str
    role: str
    org_id: str | None
    org_name: str | None = None
    is_active: bool = True
    created_at: datetime
    last_login_at: datetime | None = None


class AdminUserListResponse(BaseModel):
    """Paginated admin user list."""

    items: list[AdminUserResponse]
    total: int
    page: int
    page_size: int


class ErrorLogResponse(BaseModel):
    """Error log entry response."""

    id: str
    error_type: str
    message: str
    stack_trace: str | None = None
    user_id: str | None = None
    path: str | None = None
    resolved: bool = False
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    created_at: datetime


class ErrorLogListResponse(BaseModel):
    """Paginated error log list."""

    items: list[ErrorLogResponse]
    total: int
    page: int
    page_size: int


class SystemStatsResponse(BaseModel):
    """System-wide statistics."""

    total_users: int
    total_organizations: int
    total_workspaces: int
    total_datasets: int
    total_jobs_today: int
    active_users_24h: int
    storage_used_bytes: int = 0
    uptime_seconds: float


__all__ = [
    # Requests
    "AdminUserUpdateRequest",
    # Responses
    "AdminUserResponse",
    "AdminUserListResponse",
    "ErrorLogResponse",
    "ErrorLogListResponse",
    "SystemStatsResponse",
]
