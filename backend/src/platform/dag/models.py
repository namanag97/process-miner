"""DAG Orchestration Models.

SQLAlchemy ORM models for DAG-based workflow orchestration:
- DAGDefinition: Reusable workflow templates
- DAGDefinitionStep: Task nodes within a DAG
- DAGDefinitionEdge: Dependencies between steps
- DAGRun: Execution instances of DAGs
- DAGRunStep: Individual step execution records
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from src.platform.models import AsyncJob


class DAGRunStatus(str, Enum):
    """DAG run lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"  # Some steps failed but others completed


class DAGStepStatus(str, Enum):
    """DAG step lifecycle states."""

    PENDING = "pending"
    QUEUED = "queued"  # Ready to run, waiting for worker
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"  # Skipped due to upstream failure
    CANCELLED = "cancelled"


# =============================================================================
# DAG Definition (Template/Blueprint)
# =============================================================================


class DAGDefinition(Base):
    """Reusable DAG workflow template.

    Defines a workflow as a directed acyclic graph of steps with dependencies.
    Multiple DAGRuns can be created from a single definition.
    """

    __tablename__ = "dag_definitions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    steps: Mapped[list["DAGDefinitionStep"]] = relationship(
        back_populates="dag_definition",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="DAGDefinitionStep.position",
    )
    edges: Mapped[list["DAGDefinitionEdge"]] = relationship(
        back_populates="dag_definition",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    runs: Mapped[list["DAGRun"]] = relationship(
        back_populates="dag_definition",
        lazy="dynamic",
    )


class DAGDefinitionStep(Base):
    """A task node within a DAG definition.

    Each step maps to a registered task function that will be executed
    as a Celery task during DAG run.
    """

    __tablename__ = "dag_definition_steps"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    dag_definition_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dag_definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    task_name: Mapped[str] = mapped_column(String(100), nullable=False)
    default_params_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_policy_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeout_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True, default=3600)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    dag_definition: Mapped["DAGDefinition"] = relationship(back_populates="steps")
    outgoing_edges: Mapped[list["DAGDefinitionEdge"]] = relationship(
        "DAGDefinitionEdge",
        foreign_keys="DAGDefinitionEdge.from_step_id",
        back_populates="from_step",
        lazy="selectin",
    )
    incoming_edges: Mapped[list["DAGDefinitionEdge"]] = relationship(
        "DAGDefinitionEdge",
        foreign_keys="DAGDefinitionEdge.to_step_id",
        back_populates="to_step",
        lazy="selectin",
    )


class DAGDefinitionEdge(Base):
    """A dependency edge between two steps in a DAG definition.

    Represents that to_step cannot execute until from_step completes.
    Optional condition_json allows for conditional execution.
    """

    __tablename__ = "dag_definition_edges"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    dag_definition_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dag_definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_step_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dag_definition_steps.id", ondelete="CASCADE"),
        nullable=False,
    )
    to_step_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dag_definition_steps.id", ondelete="CASCADE"),
        nullable=False,
    )
    condition_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    dag_definition: Mapped["DAGDefinition"] = relationship(back_populates="edges")
    from_step: Mapped["DAGDefinitionStep"] = relationship(
        foreign_keys=[from_step_id], back_populates="outgoing_edges"
    )
    to_step: Mapped["DAGDefinitionStep"] = relationship(
        foreign_keys=[to_step_id], back_populates="incoming_edges"
    )


# =============================================================================
# DAG Run (Execution Instance)
# =============================================================================


class DAGRun(Base):
    """An execution instance of a DAG definition.

    Tracks the overall status of a workflow execution and links to
    individual step executions.
    """

    __tablename__ = "dag_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    dag_definition_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("dag_definitions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=DAGRunStatus.PENDING.value, index=True
    )
    trigger_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    context_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    dag_definition: Mapped["DAGDefinition | None"] = relationship(back_populates="runs")
    steps: Mapped[list["DAGRunStep"]] = relationship(
        back_populates="dag_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DAGRunStep(Base):
    """An individual step execution within a DAG run.

    Tracks the status, parameters, result, and timing of a single task
    execution within a workflow run.
    """

    __tablename__ = "dag_run_steps"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    dag_run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dag_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    definition_step_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("dag_definition_steps.id", ondelete="SET NULL"),
        nullable=True,
    )
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)
    task_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=DAGStepStatus.PENDING.value, index=True
    )
    parameters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    dag_run: Mapped["DAGRun"] = relationship(back_populates="steps")
