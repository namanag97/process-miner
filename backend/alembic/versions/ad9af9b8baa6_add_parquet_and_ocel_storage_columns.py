"""add parquet and ocel storage columns

Revision ID: ad9af9b8baa6
Revises: 858c1bf60a3b
Create Date: 2026-01-07 14:21:33.739914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad9af9b8baa6'
down_revision: Union[str, None] = '858c1bf60a3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing storage columns to datasets and ocel_logs tables."""
    from sqlalchemy import text
    bind = op.get_bind()

    def column_exists(table_name: str, column_name: str) -> bool:
        """Check if column exists in table (SQLite compatible)."""
        result = bind.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in result.fetchall()]
        return column_name in columns

    # Add parquet storage columns to datasets table
    if not column_exists('datasets', 'parquet_s3_key'):
        op.add_column('datasets', sa.Column('parquet_s3_key', sa.String(length=512), nullable=True))

    if not column_exists('datasets', 'parquet_size_bytes'):
        op.add_column('datasets', sa.Column('parquet_size_bytes', sa.Integer(), nullable=True))

    if not column_exists('datasets', 'parquet_row_count'):
        op.add_column('datasets', sa.Column('parquet_row_count', sa.Integer(), nullable=True))

    # Add ocel storage key to ocel_logs table
    if not column_exists('ocel_logs', 'ocel_storage_key'):
        op.add_column('ocel_logs', sa.Column('ocel_storage_key', sa.String(length=64), nullable=True))
        # Create index for ocel_storage_key
        op.create_index('ix_ocel_logs_ocel_storage_key', 'ocel_logs', ['ocel_storage_key'], unique=False)


def downgrade() -> None:
    """Remove storage columns."""
    from sqlalchemy import text
    bind = op.get_bind()

    def column_exists(table_name: str, column_name: str) -> bool:
        """Check if column exists in table (SQLite compatible)."""
        result = bind.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in result.fetchall()]
        return column_name in columns

    # SQLite requires table recreation to drop columns
    # For safety, we'll just mark this as irreversible for now
    # In production, you'd want to recreate tables without these columns

    # Drop index first
    try:
        op.drop_index('ix_ocel_logs_ocel_storage_key', table_name='ocel_logs')
    except:
        pass

    # Note: SQLite doesn't support DROP COLUMN directly
    # Would need table recreation for full downgrade
    # For development, we'll leave columns in place
    pass
