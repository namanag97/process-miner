"""Add ocel_data blob column to ocel_logs

Revision ID: 001_add_ocel_data
Revises:
Create Date: 2025-12-30

Adds the ocel_data BLOB column to store raw OCEL file content
for re-parsing and advanced analyses like OC-DFG discovery.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_add_ocel_data"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add ocel_data column to store raw OCEL file bytes
    op.add_column(
        "ocel_logs",
        sa.Column("ocel_data", sa.LargeBinary(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ocel_logs", "ocel_data")
