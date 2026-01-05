"""DevConsole types and core log creation functions.

This module contains the shared types and functions for DevConsole logging
that are used by both the logging_config (core) and the dev_logs_stream API router.

Architecture Note:
- This lives in infrastructure because it deals with log transport/buffering
- The API router (dev_logs_stream) imports from here for SSE endpoints
- Core logging_config imports from here for DevConsole integration
- This breaks no layered architecture constraints
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# Log Level Enum
# =============================================================================


class LogLevel(str, Enum):
    """Log levels for DevConsole categorization."""

    INFO = "info"
    API_REQ = "api-req"
    API_RES = "api-res"
    ERROR = "error"
    ACTION = "action"
    STATE = "state"
    METRIC = "metric"
    PERF = "perf"
    CIRCUIT = "circuit"
    # New categories for comprehensive logging
    DB_QUERY = "db-query"
    CACHE = "cache"
    AUTH = "auth"
    VALIDATION = "validation"
    PM4PY = "pm4py"


# =============================================================================
# Pydantic Models for DevConsole
# =============================================================================


class DevLogEntry(BaseModel):
    """Enhanced log entry with rich metadata."""

    id: str
    timestamp: str
    level: str
    source: str
    message: str
    data: dict[str, Any] | None = None
    duration: int | None = None  # ms
    status: int | None = None
    request_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    parent_span_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    # Performance breakdown (for API responses)
    timing: dict[str, float] | None = None  # db_ms, pm4py_ms, serialize_ms
    # Importance level (1-5): 1=noise, 2=low, 3=medium, 4=high, 5=critical
    importance: int = 3


class TraceSpan(BaseModel):
    """OpenTelemetry trace span for DevConsole visualization."""

    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    name: str
    kind: str  # INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER
    start_time: str  # ISO timestamp
    end_time: str  # ISO timestamp
    duration_ms: float
    status: str  # OK, ERROR, UNSET
    attributes: dict[str, Any] = Field(default_factory=dict)
    events: list[dict[str, Any]] = Field(default_factory=list)
    links: list[dict[str, Any]] = Field(default_factory=list)


class SystemMetrics(BaseModel):
    """Real-time system metrics snapshot."""

    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    active_requests: int
    requests_per_second: float
    avg_response_time_ms: float
    error_rate_percent: float
    circuit_breakers: dict[str, str]  # name -> state


class HeartbeatMessage(BaseModel):
    """Periodic heartbeat with system state."""

    type: str = "heartbeat"
    timestamp: str
    metrics: SystemMetrics
    recent_errors: int
    slow_requests: int


# =============================================================================
# Log ID Counter (module-level singleton)
# =============================================================================

_log_id_counter = 0


def _get_next_log_id() -> int:
    """Get next log ID (thread-safe for async context)."""
    global _log_id_counter
    _log_id_counter += 1
    return _log_id_counter


# =============================================================================
# Core Log Entry Creation Function
# =============================================================================


def create_log_entry(
    level: LogLevel,
    source: str,
    message: str,
    data: dict | None = None,
    duration: int | None = None,
    status: int | None = None,
    request_id: str | None = None,
    tags: list[str] | None = None,
    timing: dict[str, float] | None = None,
    importance: int = 3,
) -> DevLogEntry:
    """Create an enhanced log entry and publish to log broker.

    This is the core function for creating DevConsole log entries.
    It adds the entry to the local buffer and attempts to publish to Redis.

    Args:
        level: Log level (LogLevel enum)
        source: Source identifier (e.g., "BE mining", "BE GET /api/...")
        message: Log message
        data: Optional structured data
        duration: Optional duration in milliseconds
        status: Optional HTTP status code
        request_id: Optional request ID for correlation
        tags: Optional list of tags for filtering
        timing: Optional timing breakdown dict
        importance: Importance level 1-5 (1=noise, 2=low, 3=medium, 4=high, 5=critical)

    Returns:
        The created DevLogEntry
    """
    log_id = _get_next_log_id()

    entry = DevLogEntry(
        id=f"be-{log_id}",
        timestamp=datetime.utcnow().isoformat() + "Z",
        level=level.value,
        source=source,
        message=message,
        data=data,
        duration=duration,
        status=status,
        request_id=request_id,
        tags=tags or [],
        timing=timing,
        importance=importance,
    )

    # Add to local buffer (synchronous, always works)
    # Import here to avoid circular imports
    from src.infrastructure.log_broker import log_broker

    log_broker._local_buffer.append(entry.model_dump())

    # Publish to Redis (broadcast to all workers) if event loop is available
    try:
        loop = asyncio.get_running_loop()
        # Schedule publish as background task (don't await)
        loop.create_task(log_broker.publish_log(entry.model_dump()))
    except RuntimeError:
        # No event loop - logs are in local buffer
        pass
    except Exception:
        # Don't let logging errors break the application
        pass

    return entry


# =============================================================================
# Trace Span Logging (for OpenTelemetry integration)
# =============================================================================


def log_trace_span(span: TraceSpan) -> None:
    """Log OpenTelemetry span to DevConsole for trace visualization.

    This publishes the span to Redis for real-time visibility in the
    DevConsole trace viewer.
    """
    try:
        from src.infrastructure.log_broker import log_broker

        # Get or create event loop
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running, skip
            return

        # Publish span directly to Redis (for trace visualization)
        asyncio.create_task(
            log_broker.publish_log(
                {
                    "type": "trace_span",
                    "span": span.model_dump(),
                }
            )
        )
    except Exception:
        # Don't let logging errors break the application
        pass
