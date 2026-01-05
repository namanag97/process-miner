"""Platform ORM Models - Organization, Workspace, User, Project, AsyncJob, ErrorLog.

These models are INDEPENDENT of Feature layer.
Feature models reference these via foreign keys only.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.platform.core.enums import JobStatus
from src.shared.database import Base

# Note: Dataset is referenced as string to avoid circular imports with features layer
# This is intentional for proper DDD layering - Platform should not import Features


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


class Workspace(Base):
    """Workspace - work context within an organization containing projects."""

    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="workspaces")
    projects: Mapped[list["Project"]] = relationship(
        back_populates="workspace",
        lazy="selectin",
    )
    members: Mapped[list["WorkspaceMember"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


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


class WorkspaceMember(Base):
    """User membership in a workspace with role."""

    __tablename__ = "workspace_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default="member", nullable=False
    )  # owner, admin, member, viewer

    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="workspace_memberships")


class Project(Base):
    """Project container for organizing event logs and analyses."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workspace_id: Mapped[str | None] = mapped_column(
        ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Statistics
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    total_analyses: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    workspace: Mapped[Optional["Workspace"]] = relationship(back_populates="projects")
    # Note: datasets relationship defined via backref from Feature layer
    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="project",
        lazy="selectin",
    )


# =============================================================================
# Async Jobs (Platform Infrastructure)
# =============================================================================


class AsyncJob(Base):
    """Async job tracking for long-running operations.

    Job-Centric Architecture: Every mutation taking >2s returns a Job object.
    """

    __tablename__ = "async_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    job_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default=JobStatus.PENDING.value, index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    stage: Mapped[str | None] = mapped_column(String(100), nullable=True)

    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    parent_job_id: Mapped[str | None] = mapped_column(
        ForeignKey("async_jobs.id", ondelete="SET NULL"), nullable=True
    )

    parameters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    parent_job: Mapped[Optional["AsyncJob"]] = relationship(
        "AsyncJob", remote_side="AsyncJob.id", foreign_keys=[parent_job_id], lazy="selectin"
    )


# =============================================================================
# Error Tracking (Platform Observability)
# =============================================================================


class ErrorLog(Base):
    """Application error tracking for monitoring and debugging."""

    __tablename__ = "error_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    exception_type: Mapped[str] = mapped_column(String(255), nullable=False)
    exception_message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)

    request_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    endpoint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    context_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
