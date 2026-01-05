"""Admin Module.

Admin-only system management endpoints.
Superuser access required for all endpoints.
"""

from src.platform.admin.router import router
from src.platform.admin.schemas import (
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdateRequest,
    ErrorLogListResponse,
    ErrorLogResponse,
    SystemStatsResponse,
)

__all__ = [
    "router",
    # Requests
    "AdminUserUpdateRequest",
    # Responses
    "AdminUserResponse",
    "AdminUserListResponse",
    "ErrorLogResponse",
    "ErrorLogListResponse",
    "SystemStatsResponse",
]

