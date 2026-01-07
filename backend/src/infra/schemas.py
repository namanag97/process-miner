"""Platform layer schemas - Re-exports from platform.users for backward compatibility.

Contains schemas for:
- Generic pagination
- Organizations, Workspaces, Users
- Projects
- Error responses
"""

# Re-export from platform.users for backward compatibility
from src.infra.users.schemas import (
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
    "CurrentUserResponse",
    "OrganizationResponse",
    "ProjectCreateRequest",
    "ProjectDetailResponse",
    "ProjectListResponse",
    "ProjectResponse",
    "ProjectUpdateRequest",
    "UserResponse",
    "WorkspaceCreateRequest",
    "WorkspaceDetailResponse",
    "WorkspaceListResponse",
    "WorkspaceMemberResponse",
    "WorkspaceResponse",
    "WorkspaceUpdateRequest",
]
