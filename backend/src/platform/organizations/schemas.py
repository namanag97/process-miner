"""Organization schemas.

Request and response models for organization management endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Request Models
# =============================================================================


class OrganizationCreateRequest(BaseModel):
    """Create organization request."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=100, pattern=r"^[a-z0-9-]+$")


class OrganizationUpdateRequest(BaseModel):
    """Update organization request."""

    name: str | None = Field(None, min_length=1, max_length=255)


class InviteMemberRequest(BaseModel):
    """Invite member request."""

    email: str = Field(..., description="Email of user to invite")
    role: str = Field("member", pattern=r"^(owner|admin|member)$")


class UpdateRoleRequest(BaseModel):
    """Update member role request."""

    role: str = Field(..., pattern=r"^(owner|admin|member)$")


# =============================================================================
# Response Models
# =============================================================================


class OrganizationResponse(BaseModel):
    """Organization response."""

    id: str
    name: str
    slug: str
    plan: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationListResponse(BaseModel):
    """Paginated organization list."""

    items: list[OrganizationResponse]
    total: int
    page: int
    page_size: int


class MemberResponse(BaseModel):
    """Organization member response."""

    user_id: str
    email: str
    name: str
    role: str
    joined_at: datetime | None = None


class MemberListResponse(BaseModel):
    """Paginated member list."""

    items: list[MemberResponse]
    total: int


class BillingResponse(BaseModel):
    """Billing info response (placeholder)."""

    plan: str
    status: str = "active"
    message: str = "Billing integration not implemented"


class UsageResponse(BaseModel):
    """Usage stats response."""

    workspace_count: int
    user_count: int
    dataset_count: int
    storage_bytes: int = 0


__all__ = [
    # Requests
    "OrganizationCreateRequest",
    "OrganizationUpdateRequest",
    "InviteMemberRequest",
    "UpdateRoleRequest",
    # Responses
    "OrganizationResponse",
    "OrganizationListResponse",
    "MemberResponse",
    "MemberListResponse",
    "BillingResponse",
    "UsageResponse",
]
