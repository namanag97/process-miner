"""Add state machine fields to AsyncJob and EventLog.

Adds:
- AsyncJob: task_id, parameters_json, started_at, completed_at
- EventLog: status, error_message

Revision ID: 006_add_state_machine_fields
Revises: 005_add_tags_json
Create Date: 2024-12-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_add_state_machine_fields'
down_revision: Union[str, None] = '005_add_tags_json'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # === AsyncJob enhancements ===
    result = conn.execute(sa.text("PRAGMA table_info(async_jobs)"))
    existing_async_cols = {row[1] for row in result}

    async_columns = {
        "task_id": "VARCHAR(255) UNIQUE",
        "parameters_json": "TEXT",
        "started_at": "DATETIME",
        "completed_at": "DATETIME",
    }

    for col_name, col_def in async_columns.items():
        if col_name not in existing_async_cols:
            try:
                op.execute(f"ALTER TABLE async_jobs ADD COLUMN {col_name} {col_def}")
            except Exception:
                pass  # Column might already exist

    # Create index on task_id if not exists
    try:
        op.execute("CREATE INDEX IF NOT EXISTS ix_async_jobs_task_id ON async_jobs (task_id)")
    except Exception:
        pass

    # === EventLog enhancements ===
    result = conn.execute(sa.text("PRAGMA table_info(event_logs)"))
    existing_log_cols = {row[1] for row in result}

    log_columns = {
        "status": "VARCHAR(20) DEFAULT 'ready'",
        "error_message": "TEXT",
    }

    for col_name, col_def in log_columns.items():
        if col_name not in existing_log_cols:
            try:
                op.execute(f"ALTER TABLE event_logs ADD COLUMN {col_name} {col_def}")
            except Exception:
                pass  # Column might already exist


def downgrade() -> None:
    # Don't remove columns to prevent data loss
    # If needed, columns can be removed manually:
    # - async_jobs: task_id, parameters_json, started_at, completed_at
    # - event_logs: status, error_message
    pass
