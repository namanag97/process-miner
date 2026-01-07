"""Domain events for auditing and async processing.

Provides an event-driven architecture foundation with:
- Immutable domain events
- Event publisher for async processing
- Event store for audit trail
- Event handlers for side effects

Usage:
    # Publish an event
    await event_publisher.publish(ProcessCreated(
        process_id=ProcessId("..."),
        name="Order Process",
        source_format="csv",
    ))

    # Subscribe to events
    @event_publisher.subscribe(ProcessCreated)
    async def on_process_created(event: ProcessCreated):
        await send_notification(...)
"""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar
from uuid import uuid4

from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound="DomainEvent")


# =============================================================================
# Base Domain Event
# =============================================================================


@dataclass(frozen=True)
class DomainEvent(ABC):
    """Base class for all domain events.

    All events are immutable and timestamped.
    """

    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: str | None = None

    @property
    @abstractmethod
    def event_type(self) -> str:
        """Return the event type name for serialization."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage/transmission."""
        result = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id

        # Add all other fields
        for key, value in self.__dict__.items():
            if key not in result and not key.startswith("_"):
                if hasattr(value, "value"):  # Handle Value Objects
                    result[key] = value.value
                elif hasattr(value, "to_dict"):
                    result[key] = value.to_dict()
                elif isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value

        return result


# =============================================================================
# Process/Event Log Events
# =============================================================================


@dataclass(frozen=True)
class ProcessCreated(DomainEvent):
    """Raised when a new event log is uploaded and processed."""

    process_id: str = ""
    name: str = ""
    source_format: str = ""
    total_events: int = 0
    total_cases: int = 0
    user_id: str | None = None

    @property
    def event_type(self) -> str:
        return "process.created"


@dataclass(frozen=True)
class ProcessDeleted(DomainEvent):
    """Raised when an event log is deleted."""

    process_id: str = ""
    name: str = ""
    user_id: str | None = None

    @property
    def event_type(self) -> str:
        return "process.deleted"


@dataclass(frozen=True)
class ProcessAnalysisStarted(DomainEvent):
    """Raised when analysis begins on a process."""

    process_id: str = ""
    analysis_type: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        return "process.analysis_started"


@dataclass(frozen=True)
class ProcessAnalysisCompleted(DomainEvent):
    """Raised when analysis completes successfully."""

    process_id: str = ""
    analysis_type: str = ""
    duration_ms: float = 0.0
    result_summary: dict[str, Any] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        return "process.analysis_completed"


@dataclass(frozen=True)
class ProcessAnalysisFailed(DomainEvent):
    """Raised when analysis fails."""

    process_id: str = ""
    analysis_type: str = ""
    error_message: str = ""
    error_code: str | None = None

    @property
    def event_type(self) -> str:
        return "process.analysis_failed"


# =============================================================================
# Dataset CQRS Events (for read model synchronization)
# =============================================================================


@dataclass(frozen=True)
class DatasetIngestedEvent(DomainEvent):
    """Raised after dataset ingestion completes successfully.

    Used by CQRS projections to:
    - Pre-compute analytics (DFG, variants, statistics)
    - Populate read model caches
    - Trigger downstream processing
    """

    dataset_id: str = ""
    parquet_path: str = ""
    total_events: int = 0
    total_cases: int = 0
    total_activities: int = 0
    user_id: str | None = None

    @property
    def event_type(self) -> str:
        return "dataset.ingested"


@dataclass(frozen=True)
class DatasetDeletedEvent(DomainEvent):
    """Raised when a dataset is deleted.

    Used by CQRS projections to:
    - Invalidate cached analytics
    - Clean up read model entries
    """

    dataset_id: str = ""
    user_id: str | None = None

    @property
    def event_type(self) -> str:
        return "dataset.deleted"


# =============================================================================
# Model Discovery Events
# =============================================================================


@dataclass(frozen=True)
class ModelDiscovered(DomainEvent):
    """Raised when a process model is discovered."""

    model_id: str = ""
    process_id: str = ""
    miner_type: str = ""
    model_format: str = ""
    fitness: float | None = None
    precision: float | None = None

    @property
    def event_type(self) -> str:
        return "model.discovered"


@dataclass(frozen=True)
class ConformanceChecked(DomainEvent):
    """Raised when conformance checking completes."""

    process_id: str = ""
    model_id: str = ""
    method: str = ""
    fitness: float = 0.0
    precision: float | None = None
    is_conformant: bool = False

    @property
    def event_type(self) -> str:
        return "conformance.checked"


# =============================================================================
# Project Events
# =============================================================================


@dataclass(frozen=True)
class ProjectCreated(DomainEvent):
    """Raised when a new project is created."""

    project_id: str = ""
    name: str = ""
    user_id: str | None = None

    @property
    def event_type(self) -> str:
        return "project.created"


@dataclass(frozen=True)
class ProjectDeleted(DomainEvent):
    """Raised when a project is deleted."""

    project_id: str = ""
    name: str = ""

    @property
    def event_type(self) -> str:
        return "project.deleted"


# =============================================================================
# Event Publisher
# =============================================================================

EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventPublisher:
    """Publishes domain events to registered handlers.

    Supports:
    - Async event handlers
    - Multiple handlers per event type
    - Fire-and-forget publishing
    - Error isolation between handlers
    """

    def __init__(self):
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = {}
        self._global_handlers: list[EventHandler] = []

    def subscribe(self, event_type: type[T]) -> Callable[[EventHandler], EventHandler]:
        """Decorator to subscribe a handler to an event type.

        Usage:
            @event_publisher.subscribe(ProcessCreated)
            async def on_process_created(event: ProcessCreated):
                ...
        """

        def decorator(handler: EventHandler) -> EventHandler:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            return handler

        return decorator

    def subscribe_all(self, handler: EventHandler) -> EventHandler:
        """Subscribe to all events (for logging, auditing)."""
        self._global_handlers.append(handler)
        return handler

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered handlers.

        Handlers are called concurrently. Errors in one handler
        don't affect others.
        """
        logger.info(
            "domain_event_published",
            event_type=event.event_type,
            event_id=event.event_id,
        )

        handlers = list(self._global_handlers)
        handlers.extend(self._handlers.get(type(event), []))

        if not handlers:
            return

        # Run handlers concurrently
        tasks = [self._safe_call(handler, event) for handler in handlers]
        await asyncio.gather(*tasks)

    async def _safe_call(self, handler: EventHandler, event: DomainEvent) -> None:
        """Call handler with error isolation."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(
                "event_handler_failed",
                event_type=event.event_type,
                event_id=event.event_id,
                handler=handler.__name__,
                error=str(e),
            )

    def publish_sync(self, event: DomainEvent) -> None:
        """Publish event synchronously (creates new event loop if needed).

        Use sparingly - prefer async publish() when possible.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(event))
        except RuntimeError:
            # No running loop, create one
            asyncio.run(self.publish(event))


# =============================================================================
# In-Memory Event Store (for audit trail)
# =============================================================================


class InMemoryEventStore:
    """Simple in-memory event store for development/testing.

    In production, replace with a persistent store (PostgreSQL, EventStoreDB).
    """

    def __init__(self, max_events: int = 10000):
        self._events: list[DomainEvent] = []
        self._max_events = max_events

    async def append(self, event: DomainEvent) -> None:
        """Append an event to the store."""
        self._events.append(event)
        # Evict old events if over limit
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events :]

    async def get_by_aggregate(
        self, aggregate_id: str, aggregate_type: str = "process"
    ) -> list[DomainEvent]:
        """Get all events for an aggregate."""
        id_field = f"{aggregate_type}_id"
        return [e for e in self._events if getattr(e, id_field, None) == aggregate_id]

    async def get_by_type(self, event_type: str) -> list[DomainEvent]:
        """Get all events of a specific type."""
        return [e for e in self._events if e.event_type == event_type]

    async def get_recent(self, limit: int = 100) -> list[DomainEvent]:
        """Get most recent events."""
        return list(reversed(self._events[-limit:]))

    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()


# =============================================================================
# Global Instances
# =============================================================================

# Global event publisher
event_publisher = EventPublisher()

# Global event store (for audit trail)
event_store = InMemoryEventStore()


# Auto-wire event store to publisher
@event_publisher.subscribe_all
async def _store_event(event: DomainEvent) -> None:
    """Store all events for audit trail."""
    await event_store.append(event)
