"""FastAPI dependencies - DB session, auth, etc."""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.exceptions import AuthenticationError
from src.core.logging_config import get_logger
from src.models.database import get_session

if TYPE_CHECKING:
    from src.models.orm import User
    from src.services.authorization import AuthorizationService

logger = get_logger(__name__)
settings = get_settings()

# HTTP Bearer scheme for JWT tokens
security = HTTPBearer(auto_error=False)


# =============================================================================
# Database Session Dependency
# =============================================================================


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async for session in get_session():
        yield session


# Type alias for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]


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
    from src.core.security import decode_token
    from src.models.orm import User

    # If auth is disabled, return mock user for development
    if not settings.auth_enabled:
        return await _get_mock_user(db)

    # Auth is enabled - require valid token
    if not credentials:
        raise AuthenticationError(
            message="Missing authentication token",
        )

    token_data = decode_token(credentials.credentials)

    # Fetch user from database
    result = await db.execute(select(User).filter(User.id == token_data.sub))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("user_not_found", user_id=token_data.sub)
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
        raise AuthenticationError(
            message="Organization access denied",
        )

    return user


async def get_current_user_optional(
    db: DBSession,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> "User | None":
    """Get current user if authenticated, None otherwise.

    Use this for endpoints that work with or without auth.
    """
    from src.core.security import decode_token
    from src.models.orm import User

    if not credentials:
        return None

    try:
        token_data = decode_token(credentials.credentials)
        result = await db.execute(select(User).filter(User.id == token_data.sub))
        return result.scalar_one_or_none()
    except Exception:
        return None


async def _get_mock_user(db: AsyncSession) -> "User":
    """Get or create mock user for development when auth is disabled."""
    from datetime import datetime
    from uuid import uuid4

    from src.models.orm import Organization, User, Workspace, WorkspaceMember

    # Try to find existing demo user
    result = await db.execute(
        select(User).filter(User.email == "demo@processminer.io")
    )
    user = result.scalar_one_or_none()

    if user:
        return user

    # Create demo setup
    org = Organization(
        id=str(uuid4()),
        name="Demo Organization",
        slug="demo-org",
        plan="free",
        created_at=datetime.utcnow(),
    )
    db.add(org)

    workspace = Workspace(
        id=str(uuid4()),
        org_id=org.id,
        name="Default Workspace",
        description="Demo workspace",
        created_at=datetime.utcnow(),
    )
    db.add(workspace)

    user = User(
        id=str(uuid4()),
        org_id=org.id,
        email="demo@processminer.io",
        name="Demo User",
        auth_provider="local",
        role="admin",
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow(),
    )
    db.add(user)

    membership = WorkspaceMember(
        id=str(uuid4()),
        workspace_id=workspace.id,
        user_id=user.id,
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

    Example usage in router:
        auth_service: AuthorizationService = Depends(get_authorization_service)
        await auth_service.verify_workspace_access(
            workspace_id, user, Permission.DATASET_READ
        )
    """
    from src.services.authorization import AuthorizationService

    return AuthorizationService(db)


# Type alias for dependency injection
AuthService = Annotated["AuthorizationService", Depends(get_authorization_service)]
