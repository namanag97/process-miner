"""merge_all_heads

Revision ID: 858c1bf60a3b
Revises: a1b2c3d4e5f6, 73e54e8b10ef
Create Date: 2026-01-07 01:55:33.265909

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '858c1bf60a3b'
down_revision: Union[str, None] = ('a1b2c3d4e5f6', '73e54e8b10ef')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
