"""SSE Event Stream Manager - DEPRECATED MODULE.

This module is deprecated. Use the canonical location instead:
    from src.infra.jobs.stream import event_stream_manager, EventType, SSEEvent

Scheduled for removal: 2026-01-22
"""

import warnings

warnings.warn(
    "src.features.process_mining.services.ingestion.stream is deprecated. "
    "Use src.infra.jobs.stream instead. "
    "Scheduled for removal: 2026-01-22",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from canonical location for backwards compatibility
from src.infra.jobs.stream import (  # noqa: E402
    EventStreamManager,
    EventType,
    SSEEvent,
    event_stream_manager,
)

__all__ = [
    "EventStreamManager",
    "EventType",
    "SSEEvent",
    "event_stream_manager",
]
