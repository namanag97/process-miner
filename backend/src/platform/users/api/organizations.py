"""Organizations Router.

Multi-tenant organization management for the Process Mining SaaS platform.

## Business Context
Organizations are the top-level tenant container:
- Each user belongs to one organization
- Organizations contain workspaces, which contain projects and datasets
- Members have roles: owner, admin, member, viewer

## Testing Instructions

### Prerequisites
- Register a user: `POST /api/v1/auth/register` → Creates user + org automatically
- Get org_id from `GET /api/v1/auth/me`

### Endpoints
1. **List Orgs**: `GET /api/v1/organizations/` → User's organizations
2. **Create Org**: `POST /api/v1/organizations/` with `{"name": "My Company"}`
3. **Get Org**: `GET /api/v1/organizations/{org_id}`
4. **Update Org**: `PUT /api/v1/organizations/{org_id}` (admin only)
5. **Delete Org**: `DELETE /api/v1/organizations/{org_id}` (owner only)
6. **List Members**: `GET /api/v1/organizations/{org_id}/members`
7. **Invite Member**: `POST /api/v1/organizations/{org_id}/members/invite`
8. **Remove Member**: `DELETE /api/v1/organizations/{org_id}/members/{user_id}`
9. **Update Role**: `PUT /api/v1/organizations/{org_id}/members/{user_id}/role`
10. **Billing**: `GET /api/v1/organizations/{org_id}/billing` (placeholder)
11. **Usage**: `GET /api/v1/organizations/{org_id}/usage`

### Common Errors
- **403**: Not a member of this organization
- **404**: Organization not found
- **422**: Slug already exists, invalid input
"""

import secrets
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Path, Query, status
from sqlalchemy import func, select

from src.api.dependencies import CurrentUser, DBSession
from src.platform.core.exceptions import (
    AuthorizationError,
    NotFoundError,
    ValidationError,
)
from src.platform.core.logging_config import get_logger
from src.platform.core.security import hash_password
from src.platform.models import Organization, User, Workspace
from src.platform.organizations.schemas import (
    BillingResponse,
    InviteMemberRequest,
    MemberListResponse,
    MemberResponse,
    OrganizationCreateRequest,
    OrganizationListResponse,
    OrganizationResponse,
    OrganizationUpdateRequest,
    UpdateRoleRequest,
    UsageResponse,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/organizations", tags=["Organizations"])


# =============================================================================
# Helper Functions
# =============================================================================


def _org_to_response(org: Organization) -> OrganizationResponse:
    """Convert Organization ORM to response."""
    return OrganizationResponse(
        id=org.id,
        name=org.name or "",
        slug=org.slug,
        plan=org.plan or "free",
        created_at=org.created_at,
        updated_at=org.updated_at,
    )


async def _require_org_permission(
    db, org_id: str, user: User, required_role: str = "member"
) -> Organization:
    """Verify user has permission on organization."""
    # Get organization
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()

    if not org:
        logger.warning("org_not_found", org_id=org_id, user_id=user.id)
        raise NotFoundError("Organization", org_id)

    # Check membership via org_id on user
    if user.org_id != org_id:
        logger.warning(
            "org_permission_denied", org_id=org_id, user_id=user.id, user_org=user.org_id
        )
        raise AuthorizationError("Not a member of this organization")

    # Check role if required
    if required_role == "admin" and user.role not in ("admin", "owner"):
        raise AuthorizationError("Admin role required")
    if required_role == "owner" and user.role != "owner":
        raise AuthorizationError("Owner role required")

    return org


# =============================================================================
# CRUD Endpoints
# =============================================================================


@router.get("/", response_model=OrganizationListResponse)
async def list_organizations(
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> OrganizationListResponse:
    """List user's organizations."""
    logger.debug("list_organizations", user_id=user.id)

    # Get user's organization(s) - currently single org per user
    query = select(Organization).where(Organization.id == user.org_id)

    # Count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    orgs = result.scalars().all()

    return OrganizationListResponse(
        items=[_org_to_response(o) for o in orgs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    request: OrganizationCreateRequest,
    db: DBSession,
    user: CurrentUser,
) -> OrganizationResponse:
    """Create new organization."""
    logger.info("create_organization", user_id=user.id, name=request.name)

    # Generate slug if not provided
    slug = request.slug or request.name.lower().replace(" ", "-").replace("'", "")[:50]

    # Check slug uniqueness
    existing = await db.execute(select(Organization).where(Organization.slug == slug))
    if existing.scalar_one_or_none():
        raise ValidationError(f"Organization slug '{slug}' already exists")

    org = Organization(
        id=str(uuid4()),
        name=request.name or "",
        slug=slug,
        plan="free",
        created_at=datetime.utcnow(),
    )
    db.add(org)

    # Update user's org_id
    user.org_id = org.id
    await db.commit()
    await db.refresh(org)

    logger.info("organization_created", org_id=org.id, slug=slug)
    return _org_to_response(org)


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    db: DBSession,
    user: CurrentUser,
    org_id: str = Path(..., description="Organization ID"),
) -> OrganizationResponse:
    """Get organization details."""
    org = await _require_org_permission(db, org_id, user)
    return _org_to_response(org)


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    request: OrganizationUpdateRequest,
    db: DBSession,
    user: CurrentUser,
    org_id: str = Path(..., description="Organization ID"),
) -> OrganizationResponse:
    """Update organization (admin only)."""
    org = await _require_org_permission(db, org_id, user, required_role="admin")

    if request.name:
        org.name = request.name
    org.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(org)

    logger.info("organization_updated", org_id=org_id, user_id=user.id)
    return _org_to_response(org)


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    db: DBSession,
    user: CurrentUser,
    org_id: str = Path(..., description="Organization ID"),
) -> None:
    """Delete organization (owner only)."""
    org = await _require_org_permission(db, org_id, user, required_role="owner")

    # Check for workspaces
    ws_count = await db.execute(
        select(func.count()).select_from(Workspace).where(Workspace.org_id == org_id)
    )
    if ws_count.scalar() > 0:
        raise ValidationError("Cannot delete organization with existing workspaces")

    await db.delete(org)
    await db.commit()

    logger.info("organization_deleted", org_id=org_id, user_id=user.id)


# =============================================================================
# Member Endpoints
# =============================================================================


@router.get("/{org_id}/members", response_model=MemberListResponse)
async def list_members(
    db: DBSession,
    user: CurrentUser,
    org_id: str = Path(..., description="Organization ID"),
) -> MemberListResponse:
    """List organization members."""
    await _require_org_permission(db, org_id, user)

    result = await db.execute(select(User).where(User.org_id == org_id))
    users = result.scalars().all()

    members = [
        MemberResponse(
            user_id=u.id,
            email=u.email,
            name=u.name or "",
            role=u.role or "member",
            joined_at=u.created_at,
        )
        for u in users
    ]

    return MemberListResponse(items=members, total=len(members))


@router.post("/{org_id}/members/invite", response_model=MemberResponse)
async def invite_member(
    request: InviteMemberRequest,
    db: DBSession,
    user: CurrentUser,
    org_id: str = Path(..., description="Organization ID"),
) -> MemberResponse:
    """Invite user to organization (admin only)."""
    await _require_org_permission(db, org_id, user, required_role="admin")

    # Check if user exists
    result = await db.execute(select(User).where(User.email == request.email.lower()))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.org_id == org_id:
            raise ValidationError("User is already a member of this organization")
        # Move user to this org
        existing_user.org_id = org_id
        existing_user.role = request.role
        await db.commit()

        logger.info("member_added", org_id=org_id, user_id=existing_user.id, by_user=user.id)

        return MemberResponse(
            user_id=existing_user.id,
            email=existing_user.email,
            name=existing_user.name or "",
            role=request.role,
            joined_at=datetime.utcnow(),
        )
    # Create user with temporary password
    # User will need to use "forgot password" flow to set their own password
    temp_password = secrets.token_urlsafe(16)
    new_user = User(
        id=str(uuid4()),
        org_id=org_id,
        email=request.email.lower(),
        name=request.email.split("@")[0],
        password_hash=hash_password(temp_password),
        role=request.role,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    await db.commit()

    logger.info(
        "member_invited",
        org_id=org_id,
        email=request.email,
        by_user=user.id,
        note="User should use forgot-password flow to set password",
    )

    return MemberResponse(
        user_id=new_user.id,
        email=new_user.email,
        name=new_user.name or "",
        role=request.role,
        joined_at=datetime.utcnow(),
    )


@router.delete("/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    db: DBSession,
    user: CurrentUser,
    org_id: str = Path(..., description="Organization ID"),
    user_id: str = Path(..., description="User ID to remove"),
) -> None:
    """Remove member from organization (admin only)."""
    await _require_org_permission(db, org_id, user, required_role="admin")

    if user_id == user.id:
        raise ValidationError("Cannot remove yourself from organization")

    result = await db.execute(select(User).where(User.id == user_id, User.org_id == org_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise NotFoundError("User", "organization_member")

    # Remove from org (set to null)
    target_user.org_id = None
    await db.commit()

    logger.info("member_removed", org_id=org_id, removed_user=user_id, by_user=user.id)


@router.put("/{org_id}/members/{user_id}/role", response_model=MemberResponse)
async def update_member_role(
    request: UpdateRoleRequest,
    db: DBSession,
    user: CurrentUser,
    org_id: str = Path(..., description="Organization ID"),
    user_id: str = Path(..., description="User ID"),
) -> MemberResponse:
    """Change member role (owner only)."""
    await _require_org_permission(db, org_id, user, required_role="owner")

    result = await db.execute(select(User).where(User.id == user_id, User.org_id == org_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise NotFoundError("User", "organization_member")

    target_user.role = request.role
    await db.commit()

    logger.info(
        "member_role_updated",
        org_id=org_id,
        user_id=user_id,
        new_role=request.role,
        by_user=user.id,
    )

    return MemberResponse(
        user_id=target_user.id,
        email=target_user.email,
        name=target_user.name or "",
        role=request.role,
        joined_at=target_user.created_at,
    )


# =============================================================================
# Billing & Usage (Placeholders)
# =============================================================================


@router.get("/{org_id}/billing", response_model=BillingResponse)
async def get_billing(
    db: DBSession,
    user: CurrentUser,
    org_id: str = Path(..., description="Organization ID"),
) -> BillingResponse:
    """Get billing info (placeholder - admin only)."""
    org = await _require_org_permission(db, org_id, user, required_role="admin")

    return BillingResponse(
        plan=org.plan or "free",
        status="active",
        message="Billing integration not yet implemented",
    )


@router.get("/{org_id}/usage", response_model=UsageResponse)
async def get_usage(
    db: DBSession,
    user: CurrentUser,
    org_id: str = Path(..., description="Organization ID"),
) -> UsageResponse:
    """Get usage stats (admin only)."""
    await _require_org_permission(db, org_id, user, required_role="admin")

    # Count workspaces
    ws_result = await db.execute(
        select(func.count()).select_from(Workspace).where(Workspace.org_id == org_id)
    )
    workspace_count = ws_result.scalar() or 0

    # Count users
    user_result = await db.execute(
        select(func.count()).select_from(User).where(User.org_id == org_id)
    )
    user_count = user_result.scalar() or 0

    # Count datasets (via projects in workspaces)
    from src.features.process_mining.models import Dataset
    from src.platform.models import Project

    dataset_result = await db.execute(
        select(func.count())
        .select_from(Dataset)
        .join(Project, Project.id == Dataset.project_id)
        .join(Workspace, Workspace.id == Project.workspace_id)
        .where(Workspace.org_id == org_id)
    )
    dataset_count = dataset_result.scalar() or 0

    return UsageResponse(
        workspace_count=workspace_count,
        user_count=user_count,
        dataset_count=dataset_count,
        storage_bytes=0,  # Not tracking yet
    )
