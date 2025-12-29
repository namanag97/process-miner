"""In-memory event bus (mock Kafka)."""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional

from src.application.ports import EventBusPort
from src.domain.events import DomainEvent

logger = logging.getLogger(__name__)


@dataclass
class EventMessage:
    """Wrapper for domain events in the bus."""

    event: DomainEvent
    topic: str
    published_at: datetime = field(default_factory=datetime.utcnow)


class InMemoryEventBus(EventBusPort):
    """
    In-memory event bus for domain event publishing/subscribing.
    Simulates Kafka-like behavior for local development.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_log: List[EventMessage] = []
        self._max_log_size = 1000

    def subscribe(self, topic: str, handler: Callable) -> None:
        """Subscribe a handler to a topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
        logger.info(f"Handler subscribed to topic: {topic}")

    def unsubscribe(self, topic: str, handler: Callable) -> None:
        """Unsubscribe a handler from a topic."""
        if topic in self._subscribers:
            self._subscribers[topic] = [h for h in self._subscribers[topic] if h != handler]

    async def publish(self, event: DomainEvent, topic: Optional[str] = None) -> None:
        """Publish a domain event to a topic."""
        topic = topic or event.event_type
        message = EventMessage(event=event, topic=topic)

        # Log the event
        self._event_log.append(message)
        if len(self._event_log) > self._max_log_size:
            self._event_log = self._event_log[-self._max_log_size :]

        logger.info(f"Event published to {topic}: {event.event_type}")

        # Dispatch to subscribers
        if topic in self._subscribers:
            for handler in self._subscribers[topic]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")

    async def publish_all(self, events: List[DomainEvent]) -> None:
        """Publish multiple events."""
        for event in events:
            await self.publish(event)

    def get_event_log(self, topic: str = None, limit: int = 100) -> List[EventMessage]:
        """Get recent events from the log (for debugging)."""
        if topic:
            events = [e for e in self._event_log if e.topic == topic]
        else:
            events = self._event_log
        return events[-limit:]

    def clear_event_log(self) -> None:
        """Clear the event log."""
        self._event_log.clear()


# Singleton instance
event_bus = InMemoryEventBus()


# Convenience function for publishing events
async def publish_events(events: List[DomainEvent]) -> None:
    """Publish domain events to the event bus."""
    await event_bus.publish_all(events)
