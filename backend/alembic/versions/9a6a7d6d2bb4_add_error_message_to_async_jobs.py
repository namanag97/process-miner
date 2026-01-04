"""add_error_message_to_async_jobs

Revision ID: 9a6a7d6d2bb4
Revises: b20423328879
Create Date: 2026-01-05 02:28:44.190823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a6a7d6d2bb4'
down_revision: Union[str, None] = 'b20423328879'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add error_message column to async_jobs table
    op.add_column('async_jobs', sa.Column('error_message', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove error_message column from async_jobs table
    op.drop_column('async_jobs', 'error_message')
