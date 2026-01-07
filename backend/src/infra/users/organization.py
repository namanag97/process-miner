"""Organization Model - Root of multi-tenancy hierarchy.

Organizations own workspaces and users. They are the billing entity.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from src.infra.users.user import User
    from src.infra.users.workspace import Workspace


class Organization(Base):
    """Organization - root of multi-tenancy hierarchy."""

    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    workspaces: Mapped[list["Workspace"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="organization",
        lazy="selectin",
    )
