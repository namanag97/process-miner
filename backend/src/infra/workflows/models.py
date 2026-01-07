"""Workflow Models.

Durable workflow orchestration models for Temporal.io integration.
Replaces the legacy AsyncJob pattern with Temporal-native tracking.

Key Features:
- Maps directly to Temporal workflow/run IDs
- Task-level granularity for progress tracking
- Entity relationships for context
- Full error handling with retry support
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base


class Workflow(Base):
    """Workflow execution tracking for Temporal.io integration.

    Maps to Temporal workflows with full status and progress tracking.
    Replaces async_jobs for new code - maintains backward compatibility.
    """

    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Temporal integration
    temporal_workflow_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    temporal_run_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Ownership
    org_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True
    )

    # Workflow definition
    workflow_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: 'ingestion', 'discovery', 'conformance', 'prediction', 'export', 'batch_analysis'

    # Context: what entity is this workflow for?
    entity_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # 'dataset', 'model', 'analysis'
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Input/Output (stored as JSON text)
    input_params_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    output_result_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status tracking
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    # 'pending', 'running', 'completed', 'failed', 'cancelled', 'timed_out'
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_step: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Error handling
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timeout configuration
    timeout_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    tasks: Mapped[list["WorkflowTask"]] = relationship(
        back_populates="workflow",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="WorkflowTask.task_order",
    )

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_workflows_entity", "entity_type", "entity_id"),
        Index("ix_workflows_status_type", "status", "workflow_type"),
    )


class WorkflowTask(Base):
    """Individual task within a workflow.

    Tracks granular progress within a workflow execution.
    Maps to Temporal activities.
    """

    __tablename__ = "workflow_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    workflow_id: Mapped[str] = mapped_column(
        ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Task identity
    task_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g., 'validate_file', 'parse_columns', 'ingest_events'
    task_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Temporal activity mapping
    temporal_activity_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status tracking
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    # 'pending', 'running', 'completed', 'failed', 'skipped'
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Input/Output for this specific task
    input_params_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_result_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Error details
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_details_json: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Stack trace, context

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    workflow: Mapped["Workflow"] = relationship(back_populates="tasks")

    # Composite index for ordered task retrieval
    __table_args__ = (Index("ix_workflow_tasks_order", "workflow_id", "task_order"),)
