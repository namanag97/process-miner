"""Platform layer schemas - Re-exports from domain schemas for backward compatibility.

DEPRECATED: This module re-exports schemas from their new domain locations.
New code should import directly from domain modules:
- Admin schemas: from src.domains.admin.schemas import OrganizationResponse, WorkspaceResponse, etc.

Contains schemas for:
- Generic pagination
- Organizations, Workspaces, Users
- Projects
- Error responses
"""

# Re-export from admin domain for backward compatibility
from src.domains.admin.schemas import (  # noqa: E402
    CurrentUserResponse,
    OrganizationResponse,
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
    UserResponse,
    WorkspaceCreateRequest,
    WorkspaceDetailResponse,
    WorkspaceListResponse,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceUpdateRequest,
)

__all__ = [
    "OrganizationResponse",
    "UserResponse",
    "WorkspaceMemberResponse",
    "CurrentUserResponse",
    "WorkspaceResponse",
    "WorkspaceListResponse",
    "WorkspaceDetailResponse",
    "WorkspaceCreateRequest",
    "WorkspaceUpdateRequest",
    "ProjectResponse",
    "ProjectListResponse",
    "ProjectDetailResponse",
    "ProjectCreateRequest",
    "ProjectUpdateRequest",
]
