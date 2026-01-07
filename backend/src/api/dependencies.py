"""FastAPI dependencies - DB session, auth, etc."""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.platform.core.config import get_settings
from src.platform.core.exceptions import AuthenticationError
from src.platform.core.logging_config import get_logger
from src.platform.devconsole import log_auth_event
from src.platform.infrastructure.database import get_session

if TYPE_CHECKING:
    from src.platform.models import User
    from src.platform.workspaces.authorization import AuthorizationService
    from src.shared.container import Container

logger = get_logger(__name__)
settings = get_settings()

# HTTP Bearer scheme for JWT tokens
security = HTTPBearer(auto_error=False)


# =============================================================================
# Database Session Dependencies (CQRS)
# =============================================================================


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (legacy - uses write session)."""
    async for session in get_session():
        yield session


async def get_write_db() -> AsyncGenerator[AsyncSession, None]:
    """Get write database session for commands (transactional operations)."""
    from src.platform.infrastructure.database import get_write_session

    async for session in get_write_session():
        yield session


async def get_read_db() -> AsyncGenerator[AsyncSession, None]:
    """Get read database session for queries (read-only operations)."""
    from src.platform.infrastructure.database import get_read_session

    async for session in get_read_session():
        yield session


def get_duckdb():
    """Get DuckDB connection for analytics queries."""
    from src.platform.infrastructure.duckdb import duckdb_manager

    return duckdb_manager


# Type aliases for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]
WriteDBSession = Annotated[AsyncSession, Depends(get_write_db)]
ReadDBSession = Annotated[AsyncSession, Depends(get_read_db)]

# DuckDB for analytics (OLAP queries on Parquet)
from src.platform.infrastructure.duckdb import DuckDBManager

AnalyticsDB = Annotated[DuckDBManager, Depends(get_duckdb)]


# =============================================================================
# Auth Dependencies
# =============================================================================


async def get_current_user(
    db: DBSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    x_org_id: str | None = Header(None, alias="X-Org-Id"),
) -> "User":
    """Get current authenticated user from JWT token.

    Args:
        db: Database session
        credentials: Bearer token from Authorization header
        x_org_id: Optional organization override header

    Returns:
        Authenticated User object

    Raises:
        AuthenticationError: If auth is enabled and token is invalid/missing
    """
    from src.platform.core.security import decode_token
    from src.platform.models import User

    # If auth is disabled, return mock user for development
    if not settings.auth_enabled:
        mock_user = await _get_mock_user(db)
        log_auth_event("mock_auth", user_id=mock_user.id, success=True, reason="Auth disabled")
        return mock_user

    # Auth is enabled - require valid token
    if not credentials:
        log_auth_event("login", success=False, reason="Missing token")
        raise AuthenticationError(
            message="Missing authentication token",
        )

    try:
        token_data = decode_token(credentials.credentials)
    except Exception as e:
        log_auth_event("login", success=False, reason=f"Invalid token: {e!s}")
        raise

    # Fetch user from database
    result = await db.execute(select(User).filter(User.id == token_data.sub))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("user_not_found", user_id=token_data.sub)
        log_auth_event("login", user_id=token_data.sub, success=False, reason="User not found")
        raise AuthenticationError(
            message="User not found",
        )

    # Verify org_id matches if provided
    if x_org_id and user.org_id != x_org_id:
        logger.warning(
            "org_mismatch",
            user_id=user.id,
            user_org=user.org_id,
            requested_org=x_org_id,
        )
        log_auth_event("permission_check", user_id=user.id, success=False, reason="Org mismatch")
        raise AuthenticationError(
            message="Organization access denied",
        )

    log_auth_event("login", user_id=user.id, success=True)
    return user


async def get_current_user_optional(
    db: DBSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> "User | None":
    """Get current user if authenticated, None otherwise.

    Use this for endpoints that work with or without auth.
    """
    from src.platform.core.security import decode_token
    from src.platform.models import User

    if not credentials:
        return None

    try:
        token_data = decode_token(credentials.credentials)
        result = await db.execute(select(User).filter(User.id == token_data.sub))
        return result.scalar_one_or_none()
    except Exception:
        return None


async def _get_mock_user(db: AsyncSession) -> "User":
    """Get the seeded MVP user for development when auth is disabled.

    This function returns the pre-seeded MVP user (analyst@example.com)
    which has access to mvp-ws-001 - the workspace the frontend is hardcoded to use.

    The seeding happens in main.py's _seed_mvp_data() during application startup.
    """
    from datetime import datetime

    from src.platform.models import Organization, User, Workspace, WorkspaceMember

    # First, try to find the seeded MVP user (preferred)
    result = await db.execute(select(User).filter(User.email == "analyst@example.com"))
    user = result.scalar_one_or_none()

    if user:
        return user

    # Fallback: If MVP user doesn't exist yet (rare edge case), create it
    # This matches the seeding in main.py's _seed_mvp_data()
    logger.warning("mvp_user_not_found", msg="Creating MVP user on-demand - seed may have failed")

    # Check if org exists
    org_result = await db.execute(select(Organization).filter(Organization.id == "mvp-org-001"))
    org = org_result.scalar_one_or_none()

    if not org:
        org = Organization(
            id="mvp-org-001",
            name="Demo Organization",
            slug="demo-org",
            plan="free",
            created_at=datetime.utcnow(),
        )
        db.add(org)

    # Check if workspace exists
    ws_result = await db.execute(select(Workspace).filter(Workspace.id == "mvp-ws-001"))
    workspace = ws_result.scalar_one_or_none()

    if not workspace:
        workspace = Workspace(
            id="mvp-ws-001",
            org_id="mvp-org-001",
            name="Default Workspace",
            description="Your default process mining workspace",
            created_at=datetime.utcnow(),
        )
        db.add(workspace)

    # Create MVP user
    user = User(
        id="mvp-user-001",
        org_id="mvp-org-001",
        email="analyst@example.com",
        name="Process Analyst",
        auth_provider="local",
        role="admin",
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow(),
    )
    db.add(user)

    # Add workspace membership
    membership = WorkspaceMember(
        id="mvp-member-001",
        workspace_id="mvp-ws-001",
        user_id="mvp-user-001",
        role="owner",
        joined_at=datetime.utcnow(),
    )
    db.add(membership)

    await db.commit()
    await db.refresh(user)
    return user


# Type aliases for dependency injection
CurrentUser = Annotated["User", Depends(get_current_user)]
OptionalUser = Annotated["User | None", Depends(get_current_user_optional)]


# =============================================================================
# Authorization Dependencies
# =============================================================================


async def get_authorization_service(db: DBSession) -> "AuthorizationService":
    """Get authorization service for permission checking.

    args:
        auth_service: AuthorizationService = Depends(get_authorization_service)
        await auth_service.verify_workspace_access(
            workspace_id, user, Permission.DATASET_READ
        )
    """
    from src.platform.workspaces.authorization import AuthorizationService

    return AuthorizationService(db)


# Type alias for dependency injection
AuthService = Annotated["AuthorizationService", Depends(get_authorization_service)]


# =============================================================================
# Service Container Dependency
# =============================================================================


async def get_container(
    db: DBSession,
    user: "User | None" = Depends(get_current_user_optional),
) -> "Container":
    """Get request-scoped service container.

    The container lazily instantiates services on first access,
    and all services share the same database session.

    Usage:
        @router.get("/example")
        async def example(container: Container = Depends(get_container)):
            await container.ingestion.process(...)
            await container.analytics.compute(...)
    """
    from src.shared.container import Container

    user_id = user.id if user else None
    return Container(db, user_id)


# Type alias for dependency injection
ServiceContainer = Annotated["Container", Depends(get_container)]
