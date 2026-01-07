"""Auth Router.

JWT-based authentication with local username/password and future OAuth support.
Supports both real auth (AUTH_ENABLED=true) and mock auth for development.
"""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select

from src.api.dependencies import CurrentUser, ReadDBSession
from src.infra.core.config import get_settings
from src.infra.core.exceptions import AuthenticationError, BadRequestError
from src.infra.core.logging_config import get_logger
from src.infra.core.security import (
    TokenPair,
    create_token_pair,
    hash_password,
    validate_refresh_token,
    verify_password,
)
from src.infra.schemas import (
    CurrentUserResponse,
    OrganizationResponse,
    UserResponse,
    WorkspaceResponse,
)
from src.infra.users import Organization, User, Workspace, WorkspaceMember

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = get_logger(__name__)
settings = get_settings()


# =============================================================================
# Request/Response Models
# =============================================================================


class LoginRequest(BaseModel):
    """Login request with email and password."""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request."""

    email: EmailStr
    password: str
    name: str
    organization_name: str | None = None


class TokenResponse(BaseModel):
    """Token response after login/register."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


# =============================================================================
# Helper Functions
# =============================================================================


def _user_to_response(user: User) -> UserResponse:
    """Convert User ORM to UserResponse."""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )


def _org_to_response(org: Organization) -> OrganizationResponse:
    """Convert Organization ORM to OrganizationResponse."""
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        created_at=org.created_at,
        updated_at=org.updated_at,
    )


def _workspace_to_response(workspace: Workspace) -> WorkspaceResponse:
    """Convert Workspace ORM to WorkspaceResponse."""
    return WorkspaceResponse(
        id=workspace.id,
        org_id=workspace.org_id,
        name=workspace.name,
        description=workspace.description,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )


# =============================================================================
# Auth Endpoints
# =============================================================================


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: ReadDBSession,
) -> TokenResponse:
    """Register a new user account.

    Creates user, organization (if name provided), and default workspace.
    Returns JWT tokens for immediate authentication.
    """
    # Check if user already exists
    existing = await db.execute(select(User).filter(User.email == request.email))
    if existing.scalar_one_or_none():
        raise BadRequestError(message="Email already registered")

    # Create organization
    org_name = request.organization_name or f"{request.name}'s Organization"
    org_slug = org_name.lower().replace(" ", "-").replace("'", "")[:50]

    org = Organization(
        id=str(uuid4()),
        name=org_name,
        slug=org_slug,
        plan="free",
        created_at=datetime.utcnow(),
    )
    db.add(org)

    # Create user with hashed password
    user = User(
        id=str(uuid4()),
        org_id=org.id,
        email=request.email,
        name=request.name,
        password_hash=hash_password(request.password),
        auth_provider="local",
        role="admin",  # First user is admin
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow(),
    )
    db.add(user)

    # Create default workspace
    workspace = Workspace(
        id=str(uuid4()),
        org_id=org.id,
        name="Default Workspace",
        description="Your first workspace",
        created_at=datetime.utcnow(),
    )
    db.add(workspace)

    # Add user as workspace owner
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

    logger.info("user_registered", user_id=user.id, email=user.email)

    # Generate tokens
    tokens = create_token_pair(user.id, user.email, user.org_id)

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
        user=_user_to_response(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: ReadDBSession,
) -> TokenResponse:
    """Authenticate user and return JWT tokens.

    For development with AUTH_ENABLED=false, accepts any credentials.
    """
    # Find user
    result = await db.execute(select(User).filter(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError(message="Invalid email or password")

    # Verify password (skip in dev mode if no password hash)
    if settings.auth_enabled:
        if not user.password_hash or not verify_password(request.password, user.password_hash):
            raise AuthenticationError(message="Invalid email or password")

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    logger.info("user_logged_in", user_id=user.id, email=user.email)

    # Generate tokens
    tokens = create_token_pair(user.id, user.email, user.org_id)

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
        user=_user_to_response(user),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    request: RefreshRequest,
    db: ReadDBSession,
) -> TokenPair:
    """Refresh access token using refresh token."""
    token_data = validate_refresh_token(request.refresh_token)

    # Verify user still exists
    result = await db.execute(select(User).filter(User.id == token_data.sub))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError(message="User not found")

    # Generate new tokens
    return create_token_pair(user.id, user.email, user.org_id)


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_info(
    db: ReadDBSession,
    current_user: CurrentUser,
) -> CurrentUserResponse:
    """Get current authenticated user with organization and workspaces."""
    # Get organization
    org = None
    if current_user.org_id:
        org_result = await db.execute(
            select(Organization).filter(Organization.id == current_user.org_id)
        )
        org = org_result.scalar_one_or_none()

    # Get user's workspaces via memberships
    workspaces_result = await db.execute(
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == current_user.id)
    )
    workspaces: list[Workspace] = list(workspaces_result.scalars().all())

    return CurrentUserResponse(
        user=_user_to_response(current_user),
        organization=_org_to_response(org) if org else None,
        workspaces=[_workspace_to_response(w) for w in workspaces],
        current_workspace_id=workspaces[0].id if workspaces else None,
    )


@router.post("/logout")
async def logout() -> dict[str, str]:
    """Logout endpoint.

    JWT tokens are stateless - client should discard the token.
    For additional security, implement token blacklisting in production.
    """
    return {"status": "logged_out", "message": "Token should be discarded by client"}


# =============================================================================
# Legacy MVP Endpoint (for backwards compatibility)
# =============================================================================


@router.get("/me/legacy", response_model=CurrentUserResponse, deprecated=True)
async def get_current_user_legacy(
    db: ReadDBSession,
    email: str | None = Query(None, description="Email to identify user (MVP mode)"),
) -> CurrentUserResponse:
    """Legacy MVP endpoint - use /auth/me with JWT instead.

    DEPRECATED: This endpoint bypasses authentication.
    Only works when AUTH_ENABLED=false.
    """
    if settings.auth_enabled:
        raise BadRequestError(message="Legacy endpoint disabled when auth is enabled. Use /auth/login.")

    from src.api.dependencies import _get_mock_user

    user = await _get_mock_user(db)

    # Get organization
    org = None
    if user.org_id:
        org_result = await db.execute(select(Organization).filter(Organization.id == user.org_id))
        org = org_result.scalar_one_or_none()

    # Get workspaces
    workspaces_result = await db.execute(
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user.id)
    )
    workspaces: list[Workspace] = list(workspaces_result.scalars().all())

    return CurrentUserResponse(
        user=_user_to_response(user),
        organization=_org_to_response(org) if org else None,
        workspaces=[_workspace_to_response(w) for w in workspaces],
        current_workspace_id=workspaces[0].id if workspaces else None,
    )
