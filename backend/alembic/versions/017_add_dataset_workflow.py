"""Add workflow_id to datasets table.

Revision ID: 017_add_dataset_workflow
Revises: 016_add_workflow_ids
Create Date: 2026-01-06
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "017_add_dataset_workflow"
down_revision = "016_add_workflow_ids"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add workflow tracking column to datasets."""
    # Add workflow_id - Temporal workflow ID for ingestion
    op.add_column(
        "datasets",
        sa.Column("workflow_id", sa.String(255), nullable=True),
    )
    
    # Add index for workflow_id lookups
    op.create_index(
        "ix_datasets_workflow_id",
        "datasets",
        ["workflow_id"],
    )
    
    # Add workflow_id to analyses table as well
    op.add_column(
        "analyses",
        sa.Column("workflow_id", sa.String(255), nullable=True),
    )
    
    op.create_index(
        "ix_analyses_workflow_id",
        "analyses",
        ["workflow_id"],
    )


def downgrade() -> None:
    """Remove workflow tracking columns."""
    op.drop_index("ix_analyses_workflow_id", table_name="analyses")
    op.drop_column("analyses", "workflow_id")
    op.drop_index("ix_datasets_workflow_id", table_name="datasets")
    op.drop_column("datasets", "workflow_id")
