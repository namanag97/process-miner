"""add error tracking table

Revision ID: b20423328879
Revises: d855465851fc
Create Date: 2026-01-05 00:23:02.163601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b20423328879'
down_revision: Union[str, None] = 'd855465851fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create error_logs table for application error tracking."""
    op.create_table(
        'error_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('level', sa.String(length=20), nullable=False),
        sa.Column('exception_type', sa.String(length=255), nullable=False),
        sa.Column('exception_message', sa.Text(), nullable=False),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('request_id', sa.String(length=36), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('endpoint', sa.String(length=255), nullable=True),
        sa.Column('method', sa.String(length=10), nullable=True),
        sa.Column('context_json', sa.Text(), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.String(length=36), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_error_logs_timestamp', 'timestamp'),
        sa.Index('ix_error_logs_level', 'level'),
        sa.Index('ix_error_logs_user_id', 'user_id'),
        sa.Index('ix_error_logs_resolved', 'resolved'),
    )


def downgrade() -> None:
    """Drop error_logs table."""
    op.drop_table('error_logs')
