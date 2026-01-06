"""Platform ORM Models - Re-exports from domain models for backward compatibility.

DEPRECATED: This module re-exports models from their new domain locations.
New code should import directly from domain modules:
- Admin models: from src.domains.admin.models import Organization, User, Workspace, Project
- Platform infrastructure: AsyncJob, ErrorLog (remain here)

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

# =============================================================================
# Admin Domain Models (Re-exported from domains.admin for backward compatibility)
# =============================================================================
from src.domains.admin.models import (  # noqa: E402
    Organization,
    Project,
    User,
    Workspace,
    WorkspaceMember,
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
