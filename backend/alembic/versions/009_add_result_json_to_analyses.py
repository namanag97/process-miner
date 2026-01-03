"""Add result_json to analyses for caching full results (BUG-003 fix).

Revision ID: 009_add_result_json
Revises: 008_deferred_ingestion
Create Date: 2025-01-03
"""

from alembic import op
import sqlalchemy as sa

revision = "009_add_result_json"
down_revision = "008_deferred_ingestion"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add result_json column for storing full analysis results
    # This prevents O(N) recomputation on every GET request (BUG-003)
    op.add_column(
        "analyses",
        sa.Column("result_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("analyses", "result_json")
