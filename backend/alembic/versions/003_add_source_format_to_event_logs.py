"""Add source_format column to event_logs.

Revision ID: 003_add_source_format
Revises: 002_add_ocel2_tables
Create Date: 2025-12-31

Adds the source_format column to track the original file format (csv, xes, etc.).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_add_source_format"
down_revision: Union[str, None] = "002_add_ocel2_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add source_format column with default 'csv'
    op.add_column(
        "event_logs",
        sa.Column("source_format", sa.String(20), nullable=True, server_default="csv"),
    )


def downgrade() -> None:
    op.drop_column("event_logs", "source_format")
