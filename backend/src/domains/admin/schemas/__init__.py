"""Admin Domain Schemas.

Pydantic schemas for admin operations.
"""

# Import from local domain schemas
from src.domains.admin.schemas.schemas import (
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
    "CurrentUserResponse",
    "WorkspaceResponse",
    "WorkspaceMemberResponse",
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
