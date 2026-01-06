"""Platform layer schemas - Re-exports from platform.users for backward compatibility.

Contains schemas for:
- Generic pagination
- Organizations, Workspaces, Users
- Projects
- Error responses
"""

# Re-export from platform.users for backward compatibility
from src.platform.users.schemas import (  # noqa: E402
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
