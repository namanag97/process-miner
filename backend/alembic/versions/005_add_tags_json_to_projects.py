"""Sync projects table with ORM model

Revision ID: 005_add_tags_json
Revises: 004_sync_event_logs_schema
Create Date: 2024-12-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_add_tags_json'
down_revision: Union[str, None] = '004_sync_event_logs_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add all missing columns to projects table
    conn = op.get_bind()
    result = conn.execute(sa.text("PRAGMA table_info(projects)"))
    existing_columns = {row[1] for row in result}

    columns_to_add = {
        "tags_json": "TEXT",
        "total_files": "INTEGER DEFAULT 0",
        "total_analyses": "INTEGER DEFAULT 0",
        "updated_at": "DATETIME",
    }

    for col_name, col_def in columns_to_add.items():
        if col_name not in existing_columns:
            try:
                op.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_def}")
            except Exception:
                pass  # Column might already exist


def downgrade() -> None:
    pass  # Don't remove columns to prevent data loss
