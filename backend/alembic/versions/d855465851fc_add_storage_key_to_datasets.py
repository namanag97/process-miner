"""add_storage_key_to_datasets

Revision ID: d855465851fc
Revises: 013_storage_architecture
Create Date: 2026-01-04 23:37:06.279817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd855465851fc'
down_revision: Union[str, None] = '013_storage_architecture'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add storage_key column to datasets table
    op.add_column('datasets', sa.Column('storage_key', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove storage_key column from datasets table
    op.drop_column('datasets', 'storage_key')
