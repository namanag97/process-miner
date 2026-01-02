"""add_workspace_members_table

Revision ID: 007_add_workspace_members
Revises: 8f48c262ebc2
Create Date: 2026-01-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007_add_workspace_members'
down_revision: Union[str, None] = '8f48c262ebc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create workspace_members table
    op.create_table('workspace_members',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workspace_members_workspace_id', 'workspace_members', ['workspace_id'])
    op.create_index('ix_workspace_members_user_id', 'workspace_members', ['user_id'])
    
    # Add auth_provider_id to users table if not exists
    # Note: This may already exist from the earlier migration, ignore if fails
    try:
        op.add_column('users', sa.Column('auth_provider_id', sa.String(length=255), nullable=True))
    except Exception:
        pass  # Column may already exist


def downgrade() -> None:
    op.drop_index('ix_workspace_members_user_id', table_name='workspace_members')
    op.drop_index('ix_workspace_members_workspace_id', table_name='workspace_members')
    op.drop_table('workspace_members')
