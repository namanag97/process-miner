"""Add DAG orchestration tables.

Revision ID: 015_dag_orchestration
Revises: 014_add_lookup_tables
Create Date: 2026-01-06

Adds tables for DAG-based workflow orchestration:
- dag_definitions: Reusable workflow templates
- dag_definition_steps: Task nodes within a DAG
- dag_definition_edges: Dependencies between steps
- dag_runs: Execution instances of DAGs
- dag_run_steps: Individual step execution records

Also adds dag_run_id and dag_step_id to async_jobs for linkage.
"""

import sqlalchemy as sa
from alembic import op

revision = "015_dag_orchestration"
down_revision = "014_add_lookup_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create DAG orchestration tables and modify async_jobs."""
    
    # === 1. dag_definitions: Reusable DAG templates ===
    op.create_table(
        "dag_definitions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_dag_definitions_name", "dag_definitions", ["name"])
    op.create_index("ix_dag_definitions_is_active", "dag_definitions", ["is_active"])

    # === 2. dag_definition_steps: Task nodes within a DAG ===
    op.create_table(
        "dag_definition_steps",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "dag_definition_id",
            sa.String(36),
            sa.ForeignKey("dag_definitions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("task_name", sa.String(100), nullable=False),  # Maps to registered task
        sa.Column("default_params_json", sa.Text, nullable=True),
        sa.Column("retry_policy_json", sa.Text, nullable=True),
        sa.Column("timeout_seconds", sa.Integer, nullable=True, server_default="3600"),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index(
        "ix_dag_definition_steps_dag_id",
        "dag_definition_steps",
        ["dag_definition_id"],
    )
    op.create_unique_constraint(
        "uq_dag_definition_steps_name",
        "dag_definition_steps",
        ["dag_definition_id", "name"],
    )

    # === 3. dag_definition_edges: Dependencies between steps ===
    op.create_table(
        "dag_definition_edges",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "dag_definition_id",
            sa.String(36),
            sa.ForeignKey("dag_definitions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "from_step_id",
            sa.String(36),
            sa.ForeignKey("dag_definition_steps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "to_step_id",
            sa.String(36),
            sa.ForeignKey("dag_definition_steps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("condition_json", sa.Text, nullable=True),  # Optional conditional logic
    )
    op.create_index(
        "ix_dag_definition_edges_dag_id",
        "dag_definition_edges",
        ["dag_definition_id"],
    )
    op.create_unique_constraint(
        "uq_dag_definition_edges_from_to",
        "dag_definition_edges",
        ["dag_definition_id", "from_step_id", "to_step_id"],
    )

    # === 4. dag_runs: Execution instances of DAGs ===
    op.create_table(
        "dag_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "dag_definition_id",
            sa.String(36),
            sa.ForeignKey("dag_definitions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("trigger_type", sa.String(50), nullable=True),  # api, scheduled, webhook
        sa.Column("context_json", sa.Text, nullable=True),  # Shared context for all steps
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_dag_runs_dag_definition_id", "dag_runs", ["dag_definition_id"])
    op.create_index("ix_dag_runs_user_id", "dag_runs", ["user_id"])
    op.create_index("ix_dag_runs_status", "dag_runs", ["status"])

    # === 5. dag_run_steps: Individual step execution records ===
    op.create_table(
        "dag_run_steps",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "dag_run_id",
            sa.String(36),
            sa.ForeignKey("dag_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "definition_step_id",
            sa.String(36),
            sa.ForeignKey("dag_definition_steps.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("step_name", sa.String(100), nullable=False),  # Denormalized for queries
        sa.Column("task_name", sa.String(100), nullable=False),  # Denormalized for queries
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("parameters_json", sa.Text, nullable=True),
        sa.Column("result_json", sa.Text, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_dag_run_steps_dag_run_id", "dag_run_steps", ["dag_run_id"])
    op.create_index("ix_dag_run_steps_status", "dag_run_steps", ["status"])
    op.create_index("ix_dag_run_steps_celery_task_id", "dag_run_steps", ["celery_task_id"])

    # === 6. Modify async_jobs to link to DAG runs ===
    # Check for SQLite (can't add FK constraints easily)
    conn = op.get_bind()
    if conn.dialect.name == "sqlite":
        # SQLite: just add columns without FK
        op.add_column("async_jobs", sa.Column("dag_run_id", sa.String(36), nullable=True))
        op.add_column("async_jobs", sa.Column("dag_step_id", sa.String(36), nullable=True))
    else:
        # PostgreSQL/MySQL: add columns with FK
        op.add_column(
            "async_jobs",
            sa.Column(
                "dag_run_id",
                sa.String(36),
                sa.ForeignKey("dag_runs.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
        op.add_column(
            "async_jobs",
            sa.Column(
                "dag_step_id",
                sa.String(36),
                sa.ForeignKey("dag_run_steps.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )

    op.create_index("ix_async_jobs_dag_run_id", "async_jobs", ["dag_run_id"])
    op.create_index("ix_async_jobs_dag_step_id", "async_jobs", ["dag_step_id"])


def downgrade() -> None:
    """Remove DAG orchestration tables and async_jobs columns."""
    # Remove indexes and columns from async_jobs
    op.drop_index("ix_async_jobs_dag_step_id", table_name="async_jobs")
    op.drop_index("ix_async_jobs_dag_run_id", table_name="async_jobs")
    op.drop_column("async_jobs", "dag_step_id")
    op.drop_column("async_jobs", "dag_run_id")

    # Drop tables in reverse order
    op.drop_table("dag_run_steps")
    op.drop_table("dag_runs")
    op.drop_table("dag_definition_edges")
    op.drop_table("dag_definition_steps")
    op.drop_table("dag_definitions")
