"""Mock Authentication Service."""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from uuid import UUID, uuid4

import jwt
from passlib.context import CryptContext

from src.config import get_settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class User:
    """User entity for mock auth."""
    id: UUID
    email: str
    name: str
    role: str = "user"
    is_active: bool = True


# Mock user database
MOCK_USERS: Dict[str, User] = {
    "admin@example.com": User(
        id=uuid4(),
        email="admin@example.com",
        name="Admin User",
        role="admin",
    ),
    "user@example.com": User(
        id=uuid4(),
        email="user@example.com",
        name="Demo User",
        role="user",
    ),
}


class AuthService:
    """
    Mock Authentication Service.
    Provides JWT-based authentication for local development.
    """
    
    def __init__(self):
        self.settings = get_settings()
    
    def create_access_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.settings.jwt_expire_minutes)
        
        to_encode = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        
        return jwt.encode(
            to_encode,
            self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
        )
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token and return payload."""
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user from token payload."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        email = payload.get("email")
        if email and email in MOCK_USERS:
            return MOCK_USERS[email]
        
        # Return a mock user from token data
        return User(
            id=UUID(payload.get("sub", str(uuid4()))),
            email=email or "unknown@example.com",
            name=payload.get("name", "Unknown"),
            role=payload.get("role", "user"),
        )
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user (mock - accepts any password).
        """
        if email in MOCK_USERS:
            return MOCK_USERS[email]
        
        # For demo, create a user on the fly
        if email.endswith("@example.com"):
            user = User(
                id=uuid4(),
                email=email,
                name=email.split("@")[0].title(),
                role="user",
            )
            MOCK_USERS[email] = user
            return user
        
        return None
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login endpoint - returns token and user info.
        """
        user = self.authenticate_user(email, password)
        if not user:
            return {"error": "Invalid credentials"}
        
        token = self.create_access_token(user)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": self.settings.jwt_expire_minutes * 60,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role,
            },
        }
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from authorization header."""
        if not self.settings.auth_enabled:
            # Return mock user when auth is disabled
            return MOCK_USERS.get("user@example.com")
        
        return self.get_user_from_token(token)
    
    def check_permission(self, user: User, permission: str) -> bool:
        """Check if user has permission (mock RBAC)."""
        if user.role == "admin":
            return True
        
        # Define role permissions
        permissions = {
            "user": ["read", "create_log", "run_discovery", "run_conformance"],
            "analyst": ["read", "create_log", "run_discovery", "run_conformance", "run_analytics"],
            "admin": ["*"],
        }
        
        user_permissions = permissions.get(user.role, [])
        return "*" in user_permissions or permission in user_permissions


# Singleton instance
auth_service = AuthService()
