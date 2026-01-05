"""Add dataset_columns, dataset_column_mappings, and dataset_metadata tables

Revision ID: 8e4879a6c308
Revises: e8d19b5573b2
Create Date: 2026-01-05 20:27:09.686405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e4879a6c308'
down_revision: Union[str, None] = 'e8d19b5573b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create dataset_columns table
    op.create_table(
        'dataset_columns',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('dataset_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('dtype', sa.String(length=50), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('sample_values_json', sa.Text(), nullable=True),
        sa.Column('null_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('null_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('unique_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('suggested_role', sa.String(length=50), nullable=True),
        sa.Column('suggestion_confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_dataset_columns_dataset_id', 'dataset_columns', ['dataset_id'])
    op.create_index('ix_dataset_columns_dataset_position', 'dataset_columns', ['dataset_id', 'position'], unique=True)

    # Create dataset_column_mappings table
    op.create_table(
        'dataset_column_mappings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('dataset_id', sa.String(length=36), nullable=False),
        sa.Column('case_id_column', sa.String(length=255), nullable=False),
        sa.Column('activity_column', sa.String(length=255), nullable=False),
        sa.Column('timestamp_column', sa.String(length=255), nullable=False),
        sa.Column('timestamp_format', sa.String(length=100), nullable=True),
        sa.Column('resource_column', sa.String(length=255), nullable=True),
        sa.Column('additional_columns_json', sa.Text(), nullable=True),
        sa.Column('confidence_scores_json', sa.Text(), nullable=True),
        sa.Column('auto_mapped', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dataset_id')
    )

    # Create dataset_metadata table
    op.create_table(
        'dataset_metadata',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('dataset_id', sa.String(length=36), nullable=False),
        sa.Column('total_events', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_cases', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_activities', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_variants', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('first_event_at', sa.DateTime(), nullable=True),
        sa.Column('last_event_at', sa.DateTime(), nullable=True),
        sa.Column('avg_case_duration', sa.Float(), nullable=True),
        sa.Column('min_case_duration', sa.Float(), nullable=True),
        sa.Column('max_case_duration', sa.Float(), nullable=True),
        sa.Column('total_resources', sa.Integer(), nullable=True),
        sa.Column('computed_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('computation_time_ms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dataset_id')
    )


def downgrade() -> None:
    op.drop_table('dataset_metadata')
    op.drop_table('dataset_column_mappings')
    op.drop_index('ix_dataset_columns_dataset_position', table_name='dataset_columns')
    op.drop_index('ix_dataset_columns_dataset_id', table_name='dataset_columns')
    op.drop_table('dataset_columns')
