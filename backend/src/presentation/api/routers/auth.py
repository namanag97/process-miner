"""Authentication API Router."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from src.application.generic.auth_service import User, auth_service
from src.config import get_settings
from src.domain.constants import HttpStatus, DisplayLimits, PaginationDefaults

router = APIRouter(prefix="/auth")
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """Dependency to get current user from token."""
    settings = get_settings()

    if not settings.auth_enabled:
        # Return mock user when auth disabled
        return auth_service.get_current_user("")

    if not credentials:
        return None

    return auth_service.get_user_from_token(credentials.credentials)


async def require_auth(user: Optional[User] = Depends(get_current_user)) -> User:
    """Dependency that requires authentication."""
    settings = get_settings()

    if not settings.auth_enabled:
        # Return mock user when auth disabled
        return auth_service.get_current_user("")

    if not user:
        raise HTTPException(status_code=HttpStatus.UNAUTHORIZED, detail="Not authenticated")

    return user


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.
    Returns JWT access token.
    """
    result = auth_service.login(request.email, request.password)

    if "error" in result:
        raise HTTPException(status_code=HttpStatus.UNAUTHORIZED, detail=result["error"])

    return LoginResponse(**result)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(require_auth)):
    """Get current user profile."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
    )


@router.post("/logout")
async def logout():
    """Logout (client should discard token)."""
    return {"message": "Logged out successfully"}
