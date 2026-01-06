"""User Model - User entity with organization and workspace associations.

This is the primary user model for authentication and authorization.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from src.domains.admin.models.organization import Organization
    from src.domains.admin.models.workspace import WorkspaceMember


class User(Base):
    """User entity with organization and workspace associations."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    org_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(50), default="local", nullable=False)
    auth_provider_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="users")
    workspace_memberships: Mapped[list["WorkspaceMember"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
