"""Add job-centric architecture fields to async_jobs.

Revision ID: 011_job_centric_architecture
Revises: 010_add_user_id_to_async_jobs
Create Date: 2026-01-03

Adds:
- stage: Current processing stage (e.g., "parsing", "computing_variants")
- entity_type: Type of entity being created (dataset, model, analysis, etc.)
- entity_id: ID of created entity
- parent_job_id: For chained job support
- Indexes on job_type, status, entity_type, entity_id
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '011_job_centric_architecture'
down_revision = '010_add_user_id_to_async_jobs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check existing columns (SQLite doesn't support IF NOT EXISTS for columns)
    conn = op.get_bind()
    result = conn.execute(sa.text("PRAGMA table_info(async_jobs)"))
    existing_columns = {row[1] for row in result.fetchall()}
    
    # Add new columns to async_jobs (if they don't exist)
    if 'stage' not in existing_columns:
        op.add_column('async_jobs', sa.Column('stage', sa.String(100), nullable=True))
    if 'entity_type' not in existing_columns:
        op.add_column('async_jobs', sa.Column('entity_type', sa.String(50), nullable=True))
    if 'entity_id' not in existing_columns:
        op.add_column('async_jobs', sa.Column('entity_id', sa.String(36), nullable=True))
    if 'parent_job_id' not in existing_columns:
        op.add_column('async_jobs', sa.Column('parent_job_id', sa.String(36), nullable=True))
    
    # Check existing indexes
    result = conn.execute(sa.text("PRAGMA index_list(async_jobs)"))
    existing_indexes = {row[1] for row in result.fetchall()}
    
    # Add indexes for efficient queries (if they don't exist)
    if 'ix_async_jobs_job_type' not in existing_indexes:
        op.create_index('ix_async_jobs_job_type', 'async_jobs', ['job_type'])
    if 'ix_async_jobs_status' not in existing_indexes:
        op.create_index('ix_async_jobs_status', 'async_jobs', ['status'])
    if 'ix_async_jobs_entity_type' not in existing_indexes:
        op.create_index('ix_async_jobs_entity_type', 'async_jobs', ['entity_type'])
    if 'ix_async_jobs_entity_id' not in existing_indexes:
        op.create_index('ix_async_jobs_entity_id', 'async_jobs', ['entity_id'])
    
    # Note: Foreign key for parent_job_id skipped - SQLite doesn't support
    # ALTER TABLE ADD CONSTRAINT. Referential integrity enforced at app level.


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_async_jobs_entity_id', table_name='async_jobs')
    op.drop_index('ix_async_jobs_entity_type', table_name='async_jobs')
    op.drop_index('ix_async_jobs_status', table_name='async_jobs')
    op.drop_index('ix_async_jobs_job_type', table_name='async_jobs')
    
    # Remove columns
    op.drop_column('async_jobs', 'parent_job_id')
    op.drop_column('async_jobs', 'entity_id')
    op.drop_column('async_jobs', 'entity_type')
    op.drop_column('async_jobs', 'stage')
