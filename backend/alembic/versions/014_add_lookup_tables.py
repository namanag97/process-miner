"""Add lookup tables and ProcessEvent normalization.

Revision ID: 014_add_lookup_tables
Revises: 013_storage_architecture
Create Date: 2026-01-05

Wave 1 of Database Architecture Cleanup:
- Creates lookup_activities and lookup_resources tables for normalized string storage
- Adds activity_id and resource_id FK columns to process_events
- Adds composite indexes for common query patterns
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "014_add_lookup_tables"
down_revision = "013_storage_architecture"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # Create lookup tables
    # ==========================================================================
    
    op.create_table(
        "lookup_activities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("dataset_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["datasets.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_activity_dataset_name",
        "lookup_activities",
        ["dataset_id", "name"],
        unique=True,
    )
    op.create_index(
        "ix_lookup_activities_dataset_id",
        "lookup_activities",
        ["dataset_id"],
    )

    op.create_table(
        "lookup_resources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("dataset_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["datasets.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_resource_dataset_name",
        "lookup_resources",
        ["dataset_id", "name"],
        unique=True,
    )
    op.create_index(
        "ix_lookup_resources_dataset_id",
        "lookup_resources",
        ["dataset_id"],
    )

    # ==========================================================================
    # Add FK columns to process_events
    # ==========================================================================
    
    op.add_column(
        "process_events",
        sa.Column("activity_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "process_events",
        sa.Column("resource_id", sa.Integer(), nullable=True),
    )
    
    # Create foreign key constraints
    op.create_foreign_key(
        "fk_events_activity_id",
        "process_events",
        "lookup_activities",
        ["activity_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_events_resource_id",
        "process_events",
        "lookup_resources",
        ["resource_id"],
        ["id"],
        ondelete="SET NULL",
    )
    
    # Create indexes on FK columns
    op.create_index(
        "ix_process_events_activity_id",
        "process_events",
        ["activity_id"],
    )
    op.create_index(
        "ix_process_events_case_ref_id",
        "process_events",
        ["case_ref_id"],
    )

    # ==========================================================================
    # Add composite indexes for common query patterns
    # ==========================================================================
    
    op.create_index(
        "ix_events_case_timestamp",
        "process_events",
        ["case_ref_id", "timestamp"],
    )
    op.create_index(
        "ix_events_activity_timestamp",
        "process_events",
        ["activity_id", "timestamp"],
    )
    op.create_index(
        "ix_events_timestamp_activity",
        "process_events",
        ["timestamp", "activity_id"],
    )


def downgrade() -> None:
    # Drop composite indexes
    op.drop_index("ix_events_timestamp_activity", table_name="process_events")
    op.drop_index("ix_events_activity_timestamp", table_name="process_events")
    op.drop_index("ix_events_case_timestamp", table_name="process_events")
    
    # Drop FK indexes
    op.drop_index("ix_process_events_case_ref_id", table_name="process_events")
    op.drop_index("ix_process_events_activity_id", table_name="process_events")
    
    # Drop foreign keys
    op.drop_constraint("fk_events_resource_id", "process_events", type_="foreignkey")
    op.drop_constraint("fk_events_activity_id", "process_events", type_="foreignkey")
    
    # Drop FK columns
    op.drop_column("process_events", "resource_id")
    op.drop_column("process_events", "activity_id")
    
    # Drop lookup tables
    op.drop_index("ix_lookup_resources_dataset_id", table_name="lookup_resources")
    op.drop_index("ix_resource_dataset_name", table_name="lookup_resources")
    op.drop_table("lookup_resources")
    
    op.drop_index("ix_lookup_activities_dataset_id", table_name="lookup_activities")
    op.drop_index("ix_activity_dataset_name", table_name="lookup_activities")
    op.drop_table("lookup_activities")
