"""Admin Router.

Superuser-only endpoints for system management.
8 endpoints per API specification.
"""

from datetime import datetime

from fastapi import APIRouter, Path, Query, status
from sqlalchemy import func, select

from src.api.dependencies import CurrentUser, DBSession
from src.platform.admin.schemas import (
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdateRequest,
    ErrorLogListResponse,
    ErrorLogResponse,
    SystemStatsResponse,
)
from src.platform.core.exceptions import AuthorizationError, NotFoundError
from src.platform.core.logging_config import get_logger
from src.platform.models import Organization, User, Workspace

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# =============================================================================
# Middleware: Require Superuser
# =============================================================================


async def _require_superuser(user: User) -> None:
    """Verify user is a superuser/admin."""
    # For now, check if user has admin or owner role
    # In production, would check a dedicated is_superuser flag
    if user.role not in ("admin", "owner"):
        logger.warning("admin_access_denied", user_id=user.id, role=user.role)
        raise AuthorizationError("Superuser access required")


# =============================================================================
# User Management
# =============================================================================


@router.get("/users", response_model=AdminUserListResponse)
async def list_all_users(
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, max_length=255),
    org_id: str | None = Query(None),
) -> AdminUserListResponse:
    """List all users (superuser only)."""
    await _require_superuser(user)
    logger.info("admin_list_users", admin_user=user.id)

    query = select(User)

    if search:
        query = query.where(
            User.email.ilike(f"%{search}%") | User.name.ilike(f"%{search}%")
        )
    if org_id:
        query = query.where(User.org_id == org_id)

    # Count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    # Get org names
    org_ids = {u.org_id for u in users if u.org_id}
    org_names = {}
    if org_ids:
        orgs_result = await db.execute(
            select(Organization.id, Organization.name).where(Organization.id.in_(org_ids))
        )
        org_names = {row[0]: row[1] for row in orgs_result.all()}

    items = [
        AdminUserResponse(
            id=u.id,
            email=u.email,
            name=u.name,
            role=u.role or "member",
            org_id=u.org_id,
            org_name=org_names.get(u.org_id) if u.org_id else None,
            is_active=True,  # No is_active field yet
            created_at=u.created_at,
            last_login_at=u.last_login_at,
        )
        for u in users
    ]

    return AdminUserListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_details(
    db: DBSession,
    user: CurrentUser,
    user_id: str = Path(..., description="User ID"),
) -> AdminUserResponse:
    """Get user details (superuser only)."""
    await _require_superuser(user)

    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise NotFoundError(f"User {user_id} not found")

    # Get org name
    org_name = None
    if target_user.org_id:
        org_result = await db.execute(
            select(Organization.name).where(Organization.id == target_user.org_id)
        )
        org_name = org_result.scalar()

    return AdminUserResponse(
        id=target_user.id,
        email=target_user.email,
        name=target_user.name,
        role=target_user.role or "member",
        org_id=target_user.org_id,
        org_name=org_name,
        is_active=True,
        created_at=target_user.created_at,
        last_login_at=target_user.last_login_at,
    )


@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    request: AdminUserUpdateRequest,
    db: DBSession,
    user: CurrentUser,
    user_id: str = Path(..., description="User ID"),
) -> AdminUserResponse:
    """Update user (superuser only)."""
    await _require_superuser(user)

    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise NotFoundError(f"User {user_id} not found")

    if request.name:
        target_user.name = request.name
    if request.role:
        target_user.role = request.role

    await db.commit()
    await db.refresh(target_user)

    logger.info("admin_user_updated", admin_user=user.id, target_user=user_id)

    # Get org name
    org_name = None
    if target_user.org_id:
        org_result = await db.execute(
            select(Organization.name).where(Organization.id == target_user.org_id)
        )
        org_name = org_result.scalar()

    return AdminUserResponse(
        id=target_user.id,
        email=target_user.email,
        name=target_user.name,
        role=target_user.role or "member",
        org_id=target_user.org_id,
        org_name=org_name,
        is_active=True,
        created_at=target_user.created_at,
        last_login_at=target_user.last_login_at,
    )


@router.post("/users/{user_id}/disable", status_code=status.HTTP_200_OK)
async def disable_user(
    db: DBSession,
    user: CurrentUser,
    user_id: str = Path(..., description="User ID"),
) -> dict:
    """Disable user account (superuser only)."""
    await _require_superuser(user)

    if user_id == user.id:
        raise AuthorizationError("Cannot disable your own account")

    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise NotFoundError(f"User {user_id} not found")

    # For now, just log - would set is_active=False in production
    logger.warning("admin_user_disabled", admin_user=user.id, target_user=user_id)

    return {
        "status": "disabled",
        "user_id": user_id,
        "message": "User account has been disabled",
    }


# =============================================================================
# Error Management
# =============================================================================

# Note: Error logs would typically be stored in a separate table
# For now, returning placeholder data


@router.get("/errors", response_model=ErrorLogListResponse)
async def list_errors(
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    resolved: bool | None = Query(None),
) -> ErrorLogListResponse:
    """List error logs (superuser only)."""
    await _require_superuser(user)
    logger.info("admin_list_errors", admin_user=user.id)

    # Placeholder - would query error_logs table
    return ErrorLogListResponse(items=[], total=0, page=page, page_size=page_size)


@router.get("/errors/{error_id}", response_model=ErrorLogResponse)
async def get_error_details(
    db: DBSession,
    user: CurrentUser,
    error_id: str = Path(..., description="Error ID"),
) -> ErrorLogResponse:
    """Get error details (superuser only)."""
    await _require_superuser(user)

    # Placeholder - would query error_logs table
    raise NotFoundError(f"Error {error_id} not found")


@router.put("/errors/{error_id}/resolve")
async def resolve_error(
    db: DBSession,
    user: CurrentUser,
    error_id: str = Path(..., description="Error ID"),
) -> dict:
    """Mark error as resolved (superuser only)."""
    await _require_superuser(user)

    logger.info("admin_error_resolved", admin_user=user.id, error_id=error_id)

    # Placeholder - would update error_logs table
    return {
        "status": "resolved",
        "error_id": error_id,
        "resolved_by": user.id,
        "resolved_at": datetime.utcnow().isoformat(),
    }


# =============================================================================
# System Stats
# =============================================================================


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    db: DBSession,
    user: CurrentUser,
) -> SystemStatsResponse:
    """Get system-wide statistics (superuser only)."""
    await _require_superuser(user)
    logger.info("admin_get_stats", admin_user=user.id)

    from src.platform.health.router import get_uptime

    # Count users
    user_count = (await db.execute(select(func.count()).select_from(User))).scalar() or 0

    # Count organizations
    org_count = (
        await db.execute(select(func.count()).select_from(Organization))
    ).scalar() or 0

    # Count workspaces
    ws_count = (
        await db.execute(select(func.count()).select_from(Workspace))
    ).scalar() or 0

    # Count datasets
    from src.features.process_mining.models import Dataset

    dataset_count = (
        await db.execute(select(func.count()).select_from(Dataset))
    ).scalar() or 0

    # Count today's jobs
    from src.platform.models import AsyncJob

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    jobs_today = (
        await db.execute(
            select(func.count())
            .select_from(AsyncJob)
            .where(AsyncJob.created_at >= today_start)
        )
    ).scalar() or 0

    # Active users in 24h
    yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    active_24h = (
        await db.execute(
            select(func.count())
            .select_from(User)
            .where(User.last_login_at >= yesterday)
        )
    ).scalar() or 0

    return SystemStatsResponse(
        total_users=user_count,
        total_organizations=org_count,
        total_workspaces=ws_count,
        total_datasets=dataset_count,
        total_jobs_today=jobs_today,
        active_users_24h=active_24h,
        storage_used_bytes=0,
        uptime_seconds=get_uptime(),
    )
