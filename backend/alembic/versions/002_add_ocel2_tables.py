"""Add OCEL 2.0 tables for object-centric process mining.

Revision ID: 002_add_ocel2_tables
Revises: 001_add_ocel_data_blob
Create Date: 2025-01-01

This migration adds the OCEL 2.0 standard tables:
- ocel2_event_types: Event type definitions
- ocel2_object_types: Object type definitions  
- ocel2_events: Events that can relate to multiple objects
- ocel2_objects: Business objects (Orders, Items, etc.)
- ocel2_e2o_relations: Event-to-Object relationships
- ocel2_o2o_relations: Object-to-Object relationships
- ocel2_object_attribute_changes: Attribute change history
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_ocel2_tables'
down_revision = '001_add_ocel_data'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Event Types
    op.create_table(
        'ocel2_event_types',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('attributes_schema', sa.JSON, nullable=True),
    )
    
    # Object Types
    op.create_table(
        'ocel2_object_types',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('attributes_schema', sa.JSON, nullable=True),
    )
    
    # Events
    op.create_table(
        'ocel2_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_type_id', sa.String(36), sa.ForeignKey('ocel2_event_types.id', ondelete='CASCADE'), nullable=False),
        sa.Column('activity', sa.String(255), nullable=False, index=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, index=True),
        sa.Column('attributes', sa.JSON, nullable=True),
        sa.Column('source_log_id', sa.String(36), sa.ForeignKey('event_logs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    
    # Objects
    op.create_table(
        'ocel2_objects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('object_type_id', sa.String(36), sa.ForeignKey('ocel2_object_types.id', ondelete='CASCADE'), nullable=False),
        sa.Column('object_id', sa.String(255), nullable=False, index=True),
        sa.Column('attributes', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    
    # E2O Relations (Event-to-Object)
    op.create_table(
        'ocel2_e2o_relations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('ocel2_events.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('object_id', sa.String(36), sa.ForeignKey('ocel2_objects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('qualifier', sa.String(50), default='involved'),
    )
    
    # O2O Relations (Object-to-Object)
    op.create_table(
        'ocel2_o2o_relations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('source_object_id', sa.String(36), sa.ForeignKey('ocel2_objects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('target_object_id', sa.String(36), sa.ForeignKey('ocel2_objects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('qualifier', sa.String(50), nullable=False),
        sa.Column('attributes', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    
    # Object Attribute Changes (for time-travel queries)
    op.create_table(
        'ocel2_object_attribute_changes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('object_id', sa.String(36), sa.ForeignKey('ocel2_objects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('event_id', sa.String(36), sa.ForeignKey('ocel2_events.id', ondelete='SET NULL'), nullable=True),
        sa.Column('attribute_name', sa.String(255), nullable=False),
        sa.Column('old_value', sa.Text, nullable=True),
        sa.Column('new_value', sa.Text, nullable=True),
        sa.Column('changed_at', sa.DateTime, default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('ocel2_object_attribute_changes')
    op.drop_table('ocel2_o2o_relations')
    op.drop_table('ocel2_e2o_relations')
    op.drop_table('ocel2_objects')
    op.drop_table('ocel2_events')
    op.drop_table('ocel2_object_types')
    op.drop_table('ocel2_event_types')
