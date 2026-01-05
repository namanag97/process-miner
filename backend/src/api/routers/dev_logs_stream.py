"""Enhanced Server-Sent Events (SSE) endpoint for rich observability.

Provides a comprehensive real-time observability stream to frontend DevConsole:
- API request/response logs with full timing breakdown
- Real-time performance metrics
- Circuit breaker state visualization
- PM4Py operation tracking
- System health indicators
- Request waterfall data

Features:
- Heartbeat with system metrics every 5 seconds
- Deduplication support via client-tracking
- Efficient binary search for log retrieval
"""

import json
import time
from collections.abc import AsyncGenerator
from datetime import datetime

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from src.platform.core.config import get_settings
from src.platform.core.logging_config import get_logger
from src.platform.infrastructure.devconsole_types import (
    DevLogEntry,
    HeartbeatMessage,
    LogLevel,
    SystemMetrics,
    TraceSpan,
    log_trace_span,
)
from src.platform.infrastructure.dev_logs import (
    get_error_count,
    get_slow_request_count,
    get_system_metrics,
    log_api_request,
    log_api_response,
    log_auth_event,
    log_cache_operation,
    log_circuit_breaker,
    log_database_query,
    log_error,
    log_perf_warning,
    log_pm4py_operation,
    log_validation,
    reset_metrics,
)

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/dev/logs", tags=["DevLogs"])

# BUG-037 FIX: Rate limiting for log endpoints to prevent disk-filling DoS
_rate_limit_window = 60  # seconds
_max_requests_per_window = 100
_client_request_counts: dict = {}  # client_ip -> (count, window_start)


# Re-export for backward compatibility
__all__ = [
    "DevLogEntry",
    "HeartbeatMessage",
    "LogLevel",
    "SystemMetrics",
    "TraceSpan",
    "log_api_request",
    "log_api_response",
    "log_auth_event",
    "log_cache_operation",
    "log_circuit_breaker",
    "log_database_query",
    "log_error",
    "log_perf_warning",
    "log_pm4py_operation",
    "log_trace_span",
    "log_validation",
]


# =============================================================================
# SSE Streaming with Heartbeat
# =============================================================================


async def _stream_logs(
    request: Request, include_recent: bool = True, user_id: str | None = None
) -> AsyncGenerator[str, None]:
    """Generate SSE events with logs and periodic heartbeats using Redis pubsub.

    Args:
        request: FastAPI request for disconnect detection
        include_recent: Include recent logs from buffer
        user_id: Optional user ID for tenant filtering (BUG-034)
    """
    from src.platform.infrastructure.log_broker import log_broker

    # Ensure broker is connected
    await log_broker.connect()

    try:
        # Send initial metrics
        metrics = get_system_metrics()
        heartbeat = HeartbeatMessage(
            timestamp=datetime.utcnow().isoformat() + "Z",
            metrics=metrics,
            recent_errors=get_error_count(),
            slow_requests=get_slow_request_count(),
        )
        yield f"event: heartbeat\ndata: {heartbeat.model_dump_json()}\n\n"

        last_heartbeat = time.time()

        # BUG-034 FIX: Subscribe with user_id filtering
        async for event_type, data in log_broker.subscribe_logs(
            include_recent=include_recent, user_id=user_id
        ):
            # Check if client disconnected
            if await request.is_disconnected():
                break

            # Send log or heartbeat event
            if event_type == "log":
                yield f"data: {data}\n\n"
            elif event_type == "heartbeat":
                yield f"event: heartbeat\ndata: {data}\n\n"

            # Also send periodic heartbeats (every 15s)
            now = time.time()
            if now - last_heartbeat >= 15:
                metrics = get_system_metrics()
                heartbeat = HeartbeatMessage(
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    metrics=metrics,
                    recent_errors=get_error_count(),
                    slow_requests=get_slow_request_count(),
                )
                await log_broker.publish_heartbeat(heartbeat.model_dump())
                last_heartbeat = now

    except Exception as e:
        logger.error("stream_logs_error", error=str(e), exc_info=True)
        # Send error to client
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@router.get("/stream")
async def stream_logs(
    request: Request,
    include_recent: bool = Query(True, description="Include recent logs on connect"),
    user_id: str = Query(None, description="Optional user ID for tenant filtering (BUG-034)"),
):
    """Stream backend observability to frontend DevConsole via SSE.

    Returns:
    - `data:` events for log entries
    - `event: heartbeat` for system metrics every 5s

    BUG-034 FIX: Pass user_id to filter logs by tenant.
    Connect with: `new EventSource('/api/v1/dev/logs/stream?user_id=xxx')`
    """
    if not settings.debug:
        return {"error": "Dev logs only available in debug mode"}

    return StreamingResponse(
        _stream_logs(request, include_recent, user_id=user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/metrics")
async def get_current_metrics():
    """Get current system metrics snapshot."""
    if not settings.debug:
        return {"error": "Dev logs only available in debug mode"}

    return get_system_metrics().model_dump()


@router.get("/recent")
async def get_recent_logs(
    limit: int = Query(50, ge=1, le=200),
    level: str | None = Query(None, description="Filter by level"),
    tag: str | None = Query(None, description="Filter by tag"),
):
    """Get recent logs with optional filtering."""
    if not settings.debug:
        return {"error": "Dev logs only available in debug mode"}

    from src.platform.infrastructure.log_broker import log_broker

    logs = log_broker.get_recent_logs(limit=limit)

    if level:
        logs = [log_entry for log_entry in logs if log_entry.get("level") == level]
    if tag:
        logs = [log_entry for log_entry in logs if tag in log_entry.get("tags", [])]

    return logs


@router.delete("/clear")
async def clear_logs():
    """Clear the log buffer and reset metrics."""
    if not settings.debug:
        return {"error": "Dev logs only available in debug mode"}

    from src.platform.infrastructure.log_broker import log_broker

    log_broker._local_buffer.clear()
    reset_metrics()

    return {"status": "cleared", "timestamp": datetime.utcnow().isoformat()}
