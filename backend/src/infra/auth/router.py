"""Auth Router.

JWT-based authentication for the Process Mining SaaS platform.

## Business Context
Authentication flow for multi-tenant process mining:
1. Users register and automatically get an organization + default workspace
2. JWT tokens (access + refresh) are issued on login
3. Access tokens expire after 30 minutes, use refresh endpoint to renew
4. All protected endpoints require `Authorization: Bearer {access_token}` header

## Testing Instructions

### Registration Flow
```bash
POST /api/v1/auth/register
{
  "email": "test@example.com",
  "password": "SecurePass123!",  # Min 8 chars, needs uppercase, lowercase, digit
  "name": "Test User"
}
# Returns: access_token, refresh_token, user info
```

### Login Flow
```bash
POST /api/v1/auth/login
{"email": "test@example.com", "password": "SecurePass123!"}
# Returns: access_token, refresh_token
```

### Token Refresh
```bash
POST /api/v1/auth/refresh
{"refresh_token": "{your_refresh_token}"}
# Returns: new access_token, refresh_token pair
```

### Get Current User
```bash
GET /api/v1/auth/me
Headers: Authorization: Bearer {access_token}
# Returns: user + organization + workspaces
```

### Common Errors
- **401**: Invalid credentials or expired token
- **409**: Email already registered (use login instead)
- **422**: Password doesn't meet requirements
"""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select

from src.api.dependencies import CurrentUser, ReadDBSession
from src.infra.core.config import get_settings
from src.infra.core.error_messages import ErrorMessages
from src.infra.core.exceptions import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ProcessingError,
)
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
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase for consistent matching."""
        return v.lower().strip()


class RegisterRequest(BaseModel):
    """Registration request for new SaaS users.

    Password Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """

    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (8-128 chars, must include uppercase, lowercase, and digit)",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's display name",
    )
    organization_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Organization name (auto-generated if not provided)",
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase for consistent matching."""
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password meets security requirements."""
        errors = []

        if len(v) < 8:
            errors.append("at least 8 characters")
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")

        if errors:
            raise ValueError(f"Password must contain: {', '.join(errors)}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean name."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty or whitespace-only")
        return cleaned


class TokenResponse(BaseModel):
    """Token response after login/register."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str = Field(..., min_length=1)


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
    """Register a new user account for the process mining SaaS platform.

    Creates:
    - User account with hashed password
    - Organization (auto-named if not provided)
    - Default workspace for collaboration
    - Workspace membership with owner role

    Returns JWT tokens for immediate authentication.
    """
    existing = await db.execute(select(User).filter(User.email == request.email))
    if existing.scalar_one_or_none():
        logger.warning(
            "registration_email_exists",
            email=request.email[:3] + "***",  # Mask email for privacy
        )
        raise ConflictError(
            message=ErrorMessages.resource_already_exists("Account", request.email),
            details={"field": "email", "code": "EMAIL_ALREADY_EXISTS"},
        )

    # Create organization with unique slug
    org_name = request.organization_name or f"{request.name}'s Organization"
    base_slug = org_name.lower().replace(" ", "-").replace("'", "")[:50]

    # Ensure slug uniqueness by checking and appending suffix if needed
    org_slug = base_slug
    suffix = 1
    while True:
        existing_org = await db.execute(select(Organization).filter(Organization.slug == org_slug))
        if not existing_org.scalar_one_or_none():
            break
        org_slug = f"{base_slug[:45]}-{suffix}"
        suffix += 1
        if suffix > 100:  # Safety limit
            logger.error("org_slug_generation_failed", base_slug=base_slug)
            raise ConflictError(
                message="Could not generate unique organization slug. Please try a different organization name.",
                details={"field": "organization_name", "code": "ORG_SLUG_CONFLICT"},
            )

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
        logger.debug("login_failed_user_not_found", email=request.email[:3] + "***")
        raise AuthenticationError(
            message=ErrorMessages.invalid_credentials(),
        )

    # Verify password (skip in dev mode if no password hash)
    if settings.auth_enabled:
        if not user.password_hash or not verify_password(request.password, user.password_hash):
            logger.warning("login_failed_invalid_password", user_id=user.id)
            raise AuthenticationError(
                message=ErrorMessages.invalid_credentials(),
            )

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
        logger.warning("token_refresh_user_not_found", user_id=token_data.sub)
        raise AuthenticationError(
            message=ErrorMessages.token_invalid(),
        )

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


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    db: ReadDBSession,
    current_user: CurrentUser,
    name: str | None = None,
) -> UserResponse:
    """Update current user's profile (name, etc.)."""
    if name:
        current_user.name = name.strip()
        await db.commit()
        await db.refresh(current_user)
        logger.info("user_profile_updated", user_id=current_user.id)

    return _user_to_response(current_user)


class ChangePasswordRequest(BaseModel):
    """Change password request."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    db: ReadDBSession,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Change password for logged in user."""
    if not current_user.password_hash or not verify_password(
        request.current_password, current_user.password_hash
    ):
        logger.warning(
            "change_password_failed", user_id=current_user.id, reason="invalid_current_password"
        )
        raise AuthenticationError(
            message="Current password is incorrect. Please verify and try again.",
        )

    # Update password
    current_user.password_hash = hash_password(request.new_password)
    await db.commit()

    logger.info("password_changed", user_id=current_user.id)
    return {"status": "success", "message": "Password changed successfully"}


class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""

    email: EmailStr


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: ReadDBSession,
) -> dict[str, str]:
    """Request password reset email.

    Always returns success to prevent email enumeration.
    """
    result = await db.execute(select(User).filter(User.email == request.email.lower()))
    user = result.scalar_one_or_none()

    if user:
        # In production: generate token, store it, send email
        logger.info("password_reset_requested", email=request.email)

    # Always return success to prevent email enumeration
    return {
        "status": "success",
        "message": "If an account exists, a password reset email will be sent",
    }


class ResetPasswordRequest(BaseModel):
    """Reset password request."""

    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: ReadDBSession,
) -> dict[str, str]:
    """Set new password with reset token.

    Note: Token validation not implemented - placeholder.
    """
    logger.warning("reset_password_attempted", msg="Token validation not implemented")

    raise ProcessingError(
        message="Password reset token validation is not yet available. Please contact support.",
        details={"code": "NOT_IMPLEMENTED"},
    )


@router.post("/logout")
async def logout() -> dict[str, str]:
    """Logout endpoint.

    JWT tokens are stateless - client should discard the token.
    For additional security, implement token blacklisting in production.
    """
    return {"status": "logged_out", "message": "Token should be discarded by client"}


# =============================================================================
# OAuth Endpoints (Placeholders)
# =============================================================================


@router.get("/oauth/google")
async def oauth_google_init() -> dict:
    """Initiate Google OAuth flow.

    Note: OAuth integration not yet implemented.
    """
    logger.info("oauth_google_init_attempted")
    raise ProcessingError(message="OAuth integration not yet implemented")


@router.get("/oauth/google/callback")
async def oauth_google_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
) -> dict:
    """Google OAuth callback.

    Note: OAuth integration not yet implemented.
    """
    raise ProcessingError(message="OAuth integration not yet implemented")


@router.get("/oauth/github")
async def oauth_github_init() -> dict:
    """Initiate GitHub OAuth flow.

    Note: OAuth integration not yet implemented.
    """
    logger.info("oauth_github_init_attempted")
    raise ProcessingError(message="OAuth integration not yet implemented")


@router.get("/oauth/github/callback")
async def oauth_github_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
) -> dict:
    """GitHub OAuth callback.

    Note: OAuth integration not yet implemented.
    """
    raise ProcessingError(message="OAuth integration not yet implemented")


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
