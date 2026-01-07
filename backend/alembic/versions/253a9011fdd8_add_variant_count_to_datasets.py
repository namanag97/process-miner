"""add variant_count to datasets

Revision ID: 253a9011fdd8
Revises: ad9af9b8baa6
Create Date: 2026-01-08 04:57:53.746078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '253a9011fdd8'
down_revision: Union[str, None] = 'ad9af9b8baa6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add variant_count column to datasets table for fast listing queries."""
    # Add variant_count as nullable - denormalized from DatasetMetadata
    op.add_column('datasets', sa.Column('variant_count', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Remove variant_count column from datasets table."""
    op.drop_column('datasets', 'variant_count')
