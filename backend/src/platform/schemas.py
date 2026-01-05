"""Platform layer schemas.

Contains schemas for:
- Generic pagination
- Organizations, Workspaces, Users
- Projects
- Error responses
"""

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.shared.schemas import ErrorResponse, PaginatedResponse, PaginationParams

if TYPE_CHECKING:
    from src.features.process_mining.schemas.datasets import DatasetResponse
else:
    # Import at runtime for Pydantic forward references
    from src.features.process_mining.schemas.datasets import DatasetResponse


# =============================================================================
# Organization → Workspace → User
# =============================================================================


class OrganizationResponse(BaseModel):
    """Organization response."""

    id: str
    name: str
    slug: str
    plan: str
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class WorkspaceCreateRequest(BaseModel):
    """Request to create a workspace."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)


class WorkspaceUpdateRequest(BaseModel):
    """Request to update a workspace."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class WorkspaceResponse(BaseModel):
    """Workspace response."""

    id: str
    org_id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class WorkspaceListResponse(PaginatedResponse):
    """Paginated workspace list."""

    items: list[WorkspaceResponse]


class WorkspaceDetailResponse(WorkspaceResponse):
    """Workspace detail with projects."""

    projects: list["ProjectResponse"] = []


class UserResponse(BaseModel):
    """User response."""

    id: str
    email: str
    name: str | None
    role: str
    created_at: datetime
    last_login_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class WorkspaceMemberResponse(BaseModel):
    """Workspace member response."""

    id: str
    workspace_id: str
    user_id: str
    role: str
    joined_at: datetime
    user: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class CurrentUserResponse(BaseModel):
    """Current user context response (for auth/me endpoint)."""

    user: UserResponse
    organization: OrganizationResponse | None = None
    workspaces: list[WorkspaceResponse] = []
    current_workspace_id: str | None = None


# =============================================================================
# Projects
# =============================================================================


class ProjectCreateRequest(BaseModel):
    """Request to create a project."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    tags: list[str] = Field(default_factory=list)


class ProjectUpdateRequest(BaseModel):
    """Request to update a project."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] | None = None


class ProjectResponse(BaseModel):
    """Project response."""

    id: str
    name: str
    description: str | None
    tags: list[str] = []
    total_files: int
    total_analyses: int
    created_at: datetime
    updated_at: datetime | None

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse tags_json to tags list."""
        if hasattr(data, "__dict__"):
            # ORM object - convert to dict
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "name",
                    "description",
                    "tags_json",
                    "total_files",
                    "total_analyses",
                    "created_at",
                    "updated_at",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("tags_json"):
                try:
                    data["tags"] = json.loads(data["tags_json"])
                except (json.JSONDecodeError, TypeError):
                    data["tags"] = []
            elif "tags" not in data:
                data["tags"] = []
        return data

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(PaginatedResponse):
    """Paginated project list."""

    items: list[ProjectResponse]


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with datasets."""

    datasets: list["DatasetResponse"] = []
