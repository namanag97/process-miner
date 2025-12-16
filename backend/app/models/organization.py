"""
Organization model - Groups users and processes.

Organizations provide the top-level container for multi-tenancy.
All processes and users belong to exactly one organization.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .models import User, Process


def generate_uuid() -> str:
    import uuid
    return str(uuid.uuid4())


def generate_slug(name: str) -> str:
    """Generate URL-safe slug from name."""
    import re
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug


# =============================================================================
# Organization Models
# =============================================================================

class OrganizationBase(SQLModel):
    """Base organization fields."""
    name: str
    slug: str = Field(index=True, unique=True)
    description: Optional[str] = None


class Organization(OrganizationBase, table=True):
    """Organization table - top-level container for multi-tenancy."""
    __tablename__ = "organizations"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    users: list["User"] = Relationship(back_populates="organization")
    processes: list["Process"] = Relationship(back_populates="organization", cascade_delete=True)


class OrganizationCreate(SQLModel):
    """Organization creation request."""
    name: str
    description: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    """Organization API response."""
    id: str
    created_at: datetime
    user_count: int = 0
    process_count: int = 0
