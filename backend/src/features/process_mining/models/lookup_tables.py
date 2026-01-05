"""Lookup tables for normalized string values.

These tables provide efficient storage and querying for high-cardinality
string values that repeat across millions of event records.

Benefits:
- Storage savings: Integer FK (4 bytes) vs VARCHAR(255)
- Query performance: JOIN on integer is faster than string comparison
- Data integrity: Prevents typos/variations in activity names
- Analytics: Easy aggregation by activity_id
"""

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base


class Activity(Base):
    """Normalized activity names for efficient storage and querying.
    
    Each unique activity name within a dataset gets a single row here.
    ProcessEvent.activity_id references this table.
    
    Example:
        dataset_id: "abc-123"
        id: 1, name: "Create Order"
        id: 2, name: "Approve Invoice"
        id: 3, name: "Ship Goods"
    """

    __tablename__ = "lookup_activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        # Ensure uniqueness within a dataset
        Index("ix_activity_dataset_name", "dataset_id", "name", unique=True),
    )


class Resource(Base):
    """Normalized resource/performer names.
    
    Resources represent who performed an activity (users, systems, roles).
    Similar normalization benefits as Activity.
    """

    __tablename__ = "lookup_resources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        Index("ix_resource_dataset_name", "dataset_id", "name", unique=True),
    )


# =============================================================================
# Helper functions for lookup table operations
# =============================================================================


async def get_or_create_activity(session, dataset_id: str, name: str) -> Activity:
    """Get existing activity or create new one.
    
    Uses INSERT ... ON CONFLICT DO NOTHING pattern for concurrent safety.
    """
    from sqlalchemy import select
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    
    # Try to get existing
    result = await session.execute(
        select(Activity).where(
            Activity.dataset_id == dataset_id,
            Activity.name == name
        )
    )
    activity = result.scalar_one_or_none()
    
    if activity:
        return activity
    
    # Create new
    activity = Activity(dataset_id=dataset_id, name=name)
    session.add(activity)
    await session.flush()
    return activity


async def get_or_create_resource(session, dataset_id: str, name: str) -> Resource:
    """Get existing resource or create new one."""
    from sqlalchemy import select
    
    result = await session.execute(
        select(Resource).where(
            Resource.dataset_id == dataset_id,
            Resource.name == name
        )
    )
    resource = result.scalar_one_or_none()
    
    if resource:
        return resource
    
    resource = Resource(dataset_id=dataset_id, name=name)
    session.add(resource)
    await session.flush()
    return resource
