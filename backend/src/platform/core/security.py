"""Security module - JWT authentication and authorization.

Provides:
- JWT token generation and validation
- Password hashing
- Auth dependencies for route protection
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.platform.core.config import get_settings
from src.platform.core.error_codes import ErrorCode
from src.platform.core.exceptions import AuthenticationError
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# =============================================================================
# Token Models
# =============================================================================


class TokenData(BaseModel):
    """JWT token payload data."""

    sub: str  # Subject (user_id)
    email: str | None = None
    org_id: str | None = None
    exp: datetime | None = None
    iat: datetime | None = None
    type: str = "access"  # access, refresh


class TokenPair(BaseModel):
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


# =============================================================================
# Password Hashing
# =============================================================================


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)


# =============================================================================
# JWT Token Operations
# =============================================================================


def create_access_token(
    user_id: str,
    email: str | None = None,
    org_id: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a new access token.

    Args:
        user_id: Unique user identifier (stored as 'sub')
        email: User email
        org_id: Organization ID for multi-tenancy
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token string
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )

    to_encode: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "org_id": org_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )

    logger.debug("access_token_created", user_id=user_id, expires=expire.isoformat())
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a new refresh token.

    Refresh tokens have longer expiration and can only be used to get new access tokens.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=7)  # 7 day refresh token
    )

    to_encode: dict[str, Any] = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    return jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )


def create_token_pair(
    user_id: str,
    email: str | None = None,
    org_id: str | None = None,
) -> TokenPair:
    """Create both access and refresh tokens."""
    access_token = create_access_token(user_id, email, org_id)
    refresh_token = create_refresh_token(user_id)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_expire_minutes * 60,
    )


def decode_token(token: str) -> TokenData:
    """Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        TokenData with decoded claims

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )

        user_id: str = payload.get("sub", "")
        if not user_id:
            raise AuthenticationError(
                message="Invalid token: missing subject",
                code=ErrorCode.VALIDATION_FAILED,
            )

        return TokenData(
            sub=user_id,
            email=payload.get("email"),
            org_id=payload.get("org_id"),
            exp=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc),
            iat=datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.utc),
            type=payload.get("type", "access"),
        )

    except JWTError as e:
        logger.warning("jwt_decode_failed", error=str(e))
        raise AuthenticationError(
            message="Invalid or expired token",
            code=ErrorCode.VALIDATION_FAILED,
        ) from e


def validate_refresh_token(token: str) -> TokenData:
    """Validate a refresh token specifically.

    Ensures the token is a refresh token, not an access token.
    """
    token_data = decode_token(token)

    if token_data.type != "refresh":
        raise AuthenticationError(
            message="Invalid token type: expected refresh token",
            code=ErrorCode.VALIDATION_FAILED,
        )

    return token_data
