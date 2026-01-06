"""Add workflow_id and workflow_run_id to async_jobs.

Revision ID: 016_add_workflow_ids
Revises: 015_dag_orchestration
Create Date: 2026-01-06
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "016_add_workflow_ids"
down_revision = "015_dag_orchestration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Temporal workflow tracking columns to async_jobs."""
    # Add workflow_id - Temporal workflow ID
    op.add_column(
        "async_jobs",
        sa.Column("workflow_id", sa.String(255), nullable=True),
    )
    
    # Add workflow_run_id - Temporal run ID (for distinguishing retries)
    op.add_column(
        "async_jobs",
        sa.Column("workflow_run_id", sa.String(255), nullable=True),
    )
    
    # Add index for workflow_id lookups
    op.create_index(
        "ix_async_jobs_workflow_id",
        "async_jobs",
        ["workflow_id"],
    )


def downgrade() -> None:
    """Remove workflow tracking columns."""
    op.drop_index("ix_async_jobs_workflow_id", table_name="async_jobs")
    op.drop_column("async_jobs", "workflow_run_id")
    op.drop_column("async_jobs", "workflow_id")
