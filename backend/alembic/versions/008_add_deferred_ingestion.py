"""Add deferred ingestion support (mapping_json, status updates).

Revision ID: 008_deferred_ingestion
Revises: 007_add_workspace_members
Create Date: 2025-01-02
"""

from alembic import op
import sqlalchemy as sa

revision = "008_deferred_ingestion"
down_revision = "007_add_workspace_members"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add mapping_json column for storing user's column mapping choice
    op.add_column(
        "datasets",
        sa.Column("mapping_json", sa.Text(), nullable=True),
    )

    # Update existing datasets to READY status (they were already ingested)
    op.execute("UPDATE datasets SET status = 'ready' WHERE status IS NULL OR status = ''")


def downgrade() -> None:
    op.drop_column("datasets", "mapping_json")
