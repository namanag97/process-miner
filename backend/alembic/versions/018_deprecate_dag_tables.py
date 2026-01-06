"""Deprecate DAG tables - prepare for removal.

Revision ID: 018_deprecate_dag_tables
Revises: 017_add_dataset_workflow
Create Date: 2026-01-06

This migration adds a comment to DAG tables marking them for deprecation.
The Temporal workflow system replaces the custom DAG orchestration.
Tables are NOT dropped here to allow for rollback if needed.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "018_deprecate_dag_tables"
down_revision = "017_add_dataset_workflow"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Mark DAG tables as deprecated with comments.
    
    These tables are superseded by Temporal workflows:
    - dag_definitions → Temporal workflow definitions
    - dag_definition_steps → Temporal activities
    - dag_definition_edges → Temporal workflow logic
    - dag_runs → Temporal workflow executions
    - dag_run_steps → Temporal activity executions
    """
    # Add deprecation comment to dag_definitions table
    op.execute(
        "COMMENT ON TABLE dag_definitions IS "
        "'DEPRECATED: Migrate to Temporal workflows. See src.platform.temporal'"
    )
    
    # Add deprecation comment to dag_definition_steps table
    op.execute(
        "COMMENT ON TABLE dag_definition_steps IS "
        "'DEPRECATED: Use Temporal activities instead'"
    )
    
    # Add deprecation comment to dag_definition_edges table
    op.execute(
        "COMMENT ON TABLE dag_definition_edges IS "
        "'DEPRECATED: Workflow logic now handled by Temporal'"
    )
    
    # Add deprecation comment to dag_runs table
    op.execute(
        "COMMENT ON TABLE dag_runs IS "
        "'DEPRECATED: Use Temporal workflow executions instead'"
    )
    
    # Add deprecation comment to dag_run_steps table
    op.execute(
        "COMMENT ON TABLE dag_run_steps IS "
        "'DEPRECATED: Use Temporal activity results instead'"
    )


def downgrade() -> None:
    """Remove deprecation comments."""
    op.execute("COMMENT ON TABLE dag_definitions IS NULL")
    op.execute("COMMENT ON TABLE dag_definition_steps IS NULL")
    op.execute("COMMENT ON TABLE dag_definition_edges IS NULL")
    op.execute("COMMENT ON TABLE dag_runs IS NULL")
    op.execute("COMMENT ON TABLE dag_run_steps IS NULL")
