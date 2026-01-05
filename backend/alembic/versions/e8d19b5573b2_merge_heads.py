"""Merge heads

Revision ID: e8d19b5573b2
Revises: 014_add_lookup_tables, 9a6a7d6d2bb4
Create Date: 2026-01-05 20:26:16.422563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8d19b5573b2'
down_revision: Union[str, None] = ('014_add_lookup_tables', '9a6a7d6d2bb4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
