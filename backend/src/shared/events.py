"""Event Sourcing - Audit Trail for Domain Events.

Store all domain events as immutable facts for full audit trail,
time-travel debugging, and replay capability.

Usage:
    # Log an event
    await event_store.append(
        DatasetEvent(
            aggregate_id=dataset.id,
            event_type="dataset.columns_mapped",
            payload={"mapping": mapping_dict},
        )
    )
    
    # Rebuild state from events
    events = await event_store.get_events(dataset_id)
    state = reduce(apply_event, events, DatasetState())
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select

from src.shared.database import Base


# =============================================================================
# Event Store Model
# =============================================================================


class DomainEvent(Base):
    """Immutable domain event for audit trail."""
    
    __tablename__ = "domain_events"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Aggregate identification
    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_version: Mapped[int] = mapped_column(default=1)
    
    # Payload
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    
    # Timestamp
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )


# =============================================================================
# Event Definitions
# =============================================================================


@dataclass
class EventEnvelope:
    """Event envelope for publishing."""
    
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: dict[str, Any]
    user_id: str | None = None
    correlation_id: str | None = None
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# Dataset Events
DATASET_CREATED = "dataset.created"
DATASET_VALIDATED = "dataset.validated"
DATASET_COLUMNS_MAPPED = "dataset.columns_mapped"
DATASET_INGESTION_STARTED = "dataset.ingestion_started"
DATASET_INGESTION_COMPLETED = "dataset.ingestion_completed"
DATASET_INGESTION_FAILED = "dataset.ingestion_failed"
DATASET_DELETED = "dataset.deleted"

# Analysis Events
ANALYSIS_STARTED = "analysis.started"
ANALYSIS_COMPLETED = "analysis.completed"
ANALYSIS_FAILED = "analysis.failed"

# Model Events
MODEL_DISCOVERED = "model.discovered"
MODEL_EXPORTED = "model.exported"


# =============================================================================
# Event Store
# =============================================================================


class EventStore:
    """Append-only event store for domain events."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def append(self, event: EventEnvelope) -> DomainEvent:
        """Append an event to the store."""
        import json
        
        db_event = DomainEvent(
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            event_type=event.event_type,
            payload_json=json.dumps(event.payload, default=str),
            user_id=event.user_id,
            correlation_id=event.correlation_id,
            occurred_at=event.occurred_at,
        )
        
        self._session.add(db_event)
        await self._session.flush()
        return db_event
    
    async def append_many(self, events: list[EventEnvelope]) -> list[DomainEvent]:
        """Append multiple events atomically."""
        db_events = []
        for event in events:
            db_event = await self.append(event)
            db_events.append(db_event)
        return db_events
    
    async def get_events(
        self,
        aggregate_type: str,
        aggregate_id: str,
        after: datetime | None = None,
    ) -> list[DomainEvent]:
        """Get all events for an aggregate."""
        stmt = (
            select(DomainEvent)
            .where(DomainEvent.aggregate_type == aggregate_type)
            .where(DomainEvent.aggregate_id == aggregate_id)
            .order_by(DomainEvent.occurred_at)
        )
        
        if after:
            stmt = stmt.where(DomainEvent.occurred_at > after)
        
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_events_by_type(
        self,
        event_type: str,
        limit: int = 100,
    ) -> list[DomainEvent]:
        """Get recent events of a specific type."""
        stmt = (
            select(DomainEvent)
            .where(DomainEvent.event_type == event_type)
            .order_by(DomainEvent.occurred_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_events_for_user(
        self,
        user_id: str,
        limit: int = 100,
    ) -> list[DomainEvent]:
        """Get recent events by a user."""
        stmt = (
            select(DomainEvent)
            .where(DomainEvent.user_id == user_id)
            .order_by(DomainEvent.occurred_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


# =============================================================================
# Event Publisher Helper
# =============================================================================


async def publish_event(
    session: AsyncSession,
    aggregate_type: str,
    aggregate_id: str,
    event_type: str,
    payload: dict[str, Any],
    user_id: str | None = None,
) -> DomainEvent:
    """Helper to publish a single domain event."""
    store = EventStore(session)
    return await store.append(
        EventEnvelope(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=payload,
            user_id=user_id,
        )
    )


# =============================================================================
# Dataset Event Helpers
# =============================================================================


async def log_dataset_event(
    session: AsyncSession,
    dataset_id: str,
    event_type: str,
    payload: dict[str, Any],
    user_id: str | None = None,
) -> DomainEvent:
    """Log a dataset domain event."""
    return await publish_event(
        session=session,
        aggregate_type="dataset",
        aggregate_id=dataset_id,
        event_type=event_type,
        payload=payload,
        user_id=user_id,
    )
