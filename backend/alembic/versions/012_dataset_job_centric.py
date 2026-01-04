"""Add dataset job-centric fields.

Revision ID: 012_dataset_job_centric
Revises: 011_job_centric_architecture
Create Date: 2026-01-03

Adds job-centric fields to datasets table:
- column_suggestions_json: AI-detected column mappings
- detected_columns_json: List of detected columns
- file_size_bytes: File size for display
- validation_job_id: FK to validation job
- ingestion_job_id: FK to ingestion job
- Index on status for efficient queries
"""

from alembic import op
import sqlalchemy as sa


revision = '012_dataset_job_centric'
down_revision = '011_job_centric_architecture'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to datasets
    op.add_column('datasets', sa.Column('column_suggestions_json', sa.Text(), nullable=True))
    op.add_column('datasets', sa.Column('detected_columns_json', sa.Text(), nullable=True))
    op.add_column('datasets', sa.Column('file_size_bytes', sa.Integer(), nullable=True))
    op.add_column('datasets', sa.Column('validation_job_id', sa.String(36), nullable=True))
    op.add_column('datasets', sa.Column('ingestion_job_id', sa.String(36), nullable=True))
    
    # Add index on status for efficient filtering
    op.create_index('ix_datasets_status', 'datasets', ['status'])
    
    # Note: Foreign keys for job tracking skipped - SQLite doesn't support
    # ALTER TABLE ADD CONSTRAINT. Referential integrity enforced at app level.
    
    # Migrate existing data: UNSTRUCTURED -> awaiting_mapping, ANALYZING -> ingesting
    # This preserves backward compatibility
    op.execute("UPDATE datasets SET status = 'awaiting_mapping' WHERE status = 'unstructured'")
    op.execute("UPDATE datasets SET status = 'ingesting' WHERE status = 'analyzing'")


def downgrade() -> None:
    # Migrate back: awaiting_mapping -> UNSTRUCTURED, ingesting -> ANALYZING
    op.execute("UPDATE datasets SET status = 'unstructured' WHERE status = 'awaiting_mapping'")
    op.execute("UPDATE datasets SET status = 'unstructured' WHERE status = 'pending'")
    op.execute("UPDATE datasets SET status = 'unstructured' WHERE status = 'validating'")
    op.execute("UPDATE datasets SET status = 'analyzing' WHERE status = 'ingesting'")

    
    # Remove index
    op.drop_index('ix_datasets_status', table_name='datasets')
    
    # Remove columns
    op.drop_column('datasets', 'ingestion_job_id')
    op.drop_column('datasets', 'validation_job_id')
    op.drop_column('datasets', 'file_size_bytes')
    op.drop_column('datasets', 'detected_columns_json')
    op.drop_column('datasets', 'column_suggestions_json')
