"""Sync event_logs table to match ORM model.

Revision ID: 004_sync_event_logs_schema
Revises: 003_add_source_format
Create Date: 2025-12-31

This migration synchronizes the event_logs table schema with the ORM model.
The database had a different schema from a previous evolution.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004_sync_event_logs_schema"
down_revision: Union[str, None] = "003_add_source_format"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if we need to rename/add columns
    # Using batch operations for SQLite compatibility
    
    # First, check what exists and add missing columns
    conn = op.get_bind()
    
    # Get current columns
    result = conn.execute(sa.text("PRAGMA table_info(event_logs)"))
    existing_columns = {row[1] for row in result}
    
    # Add columns that don't exist
    columns_to_add = {
        "total_activities": "INTEGER DEFAULT 0",
        "activities_json": "TEXT",
        "source_log_id": "VARCHAR(36)",
        "filter_config_json": "TEXT",
        "is_filtered": "BOOLEAN DEFAULT 0",
        "filter_stats_json": "TEXT",
    }
    
    for col_name, col_def in columns_to_add.items():
        if col_name not in existing_columns:
            try:
                op.execute(f"ALTER TABLE event_logs ADD COLUMN {col_name} {col_def}")
            except Exception:
                pass  # Column might already exist
    
    # If activity_count exists but total_activities doesn't, copy data
    if "activity_count" in existing_columns:
        try:
            op.execute("UPDATE event_logs SET total_activities = activity_count WHERE total_activities IS NULL")
        except Exception:
            pass


def downgrade() -> None:
    # Don't remove columns on downgrade to prevent data loss
    pass
