from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from .common import generate_uuid

if TYPE_CHECKING:
    from .organization import Organization
    from .upload import Upload
    from .audit_log import AuditLog

class UserBase(SQLModel):
    """Base user fields."""
    display_name: Optional[str] = None
    email: Optional[str] = None


class User(UserBase, table=True):
    """User table - for no-auth session management."""
    __tablename__ = "users"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    org_id: Optional[str] = Field(default=None, foreign_key="organizations.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="users")
    uploads: list["Upload"] = Relationship(back_populates="user", cascade_delete=True)
    audit_logs: list["AuditLog"] = Relationship(back_populates="user")


class UserResponse(SQLModel):
    """User API response."""
    id: str
    org_id: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    last_active_at: datetime
