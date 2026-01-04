"""Add user_id column to async_jobs table.

Revision ID: 010_add_user_id_to_async_jobs
Revises: 009_add_result_json
Create Date: 2026-01-03

This migration adds the user_id column that was added to the ORM model
as part of BUG-046 FIX for owner tracking / security to prevent job
result information leaks.
"""

from alembic import op
import sqlalchemy as sa


revision = '010_add_user_id_to_async_jobs'
down_revision = '009_add_result_json'
branch_labels = None
depends_on = None


def upgrade():
    """Add user_id column to async_jobs table if it doesn't exist."""
    # Check if column already exists (SQLite doesn't support IF NOT EXISTS for columns)
    conn = op.get_bind()
    result = conn.execute(sa.text("PRAGMA table_info(async_jobs)"))
    columns = [row[1] for row in result.fetchall()]
    
    if "user_id" not in columns:
        op.add_column(
            "async_jobs",
            sa.Column("user_id", sa.String(36), nullable=True)
        )
        # Add index for efficient lookups by user
        op.create_index(
            "ix_async_jobs_user_id",
            "async_jobs",
            ["user_id"]
        )


def downgrade():
    """Remove user_id column from async_jobs table."""
    op.drop_index("ix_async_jobs_user_id", table_name="async_jobs")
    op.drop_column("async_jobs", "user_id")
