"""Add storage architecture tables and columns.

Revision ID: 013_storage_architecture
Revises: 012_dataset_job_centric
Create Date: 2026-01-04

Adds new storage architecture for eliminating pickle:
- process_models: Add standard_content_path, graph_structure_json, metadata_json
- process_model_metrics: New table for precomputed metrics
- graph_cache: New table for cached graph layouts
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


revision = '013_storage_architecture'
down_revision = '012_dataset_job_centric'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add new columns to process_models table
    op.add_column('process_models', sa.Column('standard_content_path', sa.String(500), nullable=True))
    op.add_column('process_models', sa.Column('graph_structure_json', sa.Text(), nullable=True))
    op.add_column('process_models', sa.Column('metadata_json', sa.Text(), nullable=True))

    # 2. Create process_model_metrics table
    op.create_table(
        'process_model_metrics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('model_id', sa.String(36), sa.ForeignKey('process_models.id', ondelete='CASCADE'), nullable=False),
        sa.Column('total_activities', sa.Integer(), nullable=True),
        sa.Column('total_transitions', sa.Integer(), nullable=True),
        sa.Column('complexity_score', sa.Float(), nullable=True),
        sa.Column('fitness_score', sa.Float(), nullable=True),
        sa.Column('precision_score', sa.Float(), nullable=True),
        sa.Column('computed_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    # Add index on model_id for efficient lookups
    op.create_index('ix_process_model_metrics_model_id', 'process_model_metrics', ['model_id'])

    # 3. Create graph_cache table
    op.create_table(
        'graph_cache',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('model_id', sa.String(36), sa.ForeignKey('process_models.id', ondelete='CASCADE'), nullable=False),
        sa.Column('abstraction_level', sa.Integer(), nullable=False, default=0),
        sa.Column('layout_algorithm', sa.String(50), nullable=False, default='dagre'),
        sa.Column('cached_layout_json', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    # Add composite index for efficient cache lookups
    op.create_index(
        'ix_graph_cache_lookup',
        'graph_cache',
        ['model_id', 'abstraction_level', 'layout_algorithm']
    )


def downgrade() -> None:
    # Drop graph_cache table and its indexes
    op.drop_index('ix_graph_cache_lookup', table_name='graph_cache')
    op.drop_table('graph_cache')

    # Drop process_model_metrics table and its indexes
    op.drop_index('ix_process_model_metrics_model_id', table_name='process_model_metrics')
    op.drop_table('process_model_metrics')

    # Drop columns from process_models
    op.drop_column('process_models', 'metadata_json')
    op.drop_column('process_models', 'graph_structure_json')
    op.drop_column('process_models', 'standard_content_path')
