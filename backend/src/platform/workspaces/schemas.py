"""Workspaces schemas.

Request and response models for workspace management endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field


# =============================================================================
# Member Management Schemas
# =============================================================================


class WorkspaceMemberResponseInline(BaseModel):
    """Workspace member response."""

    user_id: str
    email: str
    name: str
    role: str
    joined_at: datetime | None = None


class WorkspaceMemberListResponse(BaseModel):
    """Workspace member list response."""

    items: list[WorkspaceMemberResponseInline]
    total: int


class AddMemberRequest(BaseModel):
    """Add member request."""

    user_id: str = Field(..., description="User ID to add")
    role: str = Field("viewer", pattern=r"^(owner|admin|editor|analyst|viewer)$")


class UpdateMemberRoleRequest(BaseModel):
    """Update member role request."""

    role: str = Field(..., pattern=r"^(owner|admin|editor|analyst|viewer)$")


__all__ = [
    "WorkspaceMemberResponseInline",
    "WorkspaceMemberListResponse",
    "AddMemberRequest",
    "UpdateMemberRoleRequest",
]
