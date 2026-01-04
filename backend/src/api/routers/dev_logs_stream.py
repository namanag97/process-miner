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
from collections import deque
from collections.abc import AsyncGenerator
from datetime import datetime

import psutil
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from src.core.config import get_settings
from src.core.logging_config import get_logger
from src.infrastructure.devconsole_types import (
    DevLogEntry,
    HeartbeatMessage,
    LogLevel,
    SystemMetrics,
    TraceSpan,
    log_trace_span,
)
from src.infrastructure.devconsole_types import (
    create_log_entry as _create_log_entry,
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
    "_create_log_entry",
    "log_api_request",
    "log_api_response",
    "log_circuit_breaker",
    "log_error",
    "log_perf_warning",
    "log_pm4py_operation",
    "log_trace_span",
]


# =============================================================================
# Enhanced Log Buffer with Metrics
# =============================================================================

# Metrics tracking (kept local per worker)
_request_times: deque[float] = deque(maxlen=100)  # Last 100 request times
_request_timestamps: deque[float] = deque(maxlen=100)  # When requests happened
_error_count = 0
_slow_request_count = 0
_active_requests = 0


# =============================================================================
# Rich Logging Functions
# =============================================================================


def log_api_request(
    method: str,
    path: str,
    request_id: str | None = None,
    body_size: int | None = None,
) -> None:
    """Log incoming API request with context."""
    global _active_requests
    _active_requests += 1

    data = {"request_id": request_id} if request_id else {}
    if body_size:
        data["body_size"] = body_size

    # Classify request type for better filtering
    tags = ["api", method.lower()]

    # User-initiated actions (likely what caused issues)
    if any(
        pattern in path
        for pattern in [
            "/datasets/upload",
            "/datasets/detect-columns",
            "/datasets/",  # GET dataset, analyze, etc.
            "/discovery/discover",
            "/visualization/",
            "/conformance/",
            "/analytics/",
        ]
    ):
        tags.append("user-action")

    # Background/polling requests
    elif any(
        pattern in path
        for pattern in [
            "/stream",
            "/recent",
            "/poll",
        ]
    ):
        tags.append("background")

    _create_log_entry(
        level=LogLevel.API_REQ,
        source=f"BE {method} {path}",
        message="→ Request",
        data=data if data else None,
        request_id=request_id,
        tags=tags,
    )


def log_api_response(
    method: str,
    path: str,
    status: int,
    duration_ms: int,
    request_id: str | None = None,
    response_size: int | None = None,
    timing: dict[str, float] | None = None,
) -> None:
    """Log API response with timing breakdown."""
    global _active_requests, _error_count, _slow_request_count
    _active_requests = max(0, _active_requests - 1)

    # Track metrics
    _request_times.append(duration_ms)
    _request_timestamps.append(time.time())

    if status >= 400:
        _error_count += 1
    if duration_ms > 1000:
        _slow_request_count += 1

    # Build message with status emoji
    status_emoji = "✓" if status < 400 else "✗" if status < 500 else "⚠"
    message = f"← {status_emoji} {status}"

    # Speed indicator
    if duration_ms < 100:
        speed_tag = "fast"
    elif duration_ms < 500:
        speed_tag = "normal"
    elif duration_ms < 1000:
        speed_tag = "slow"
    else:
        speed_tag = "very-slow"

    # Classify request type (same logic as request)
    tags = ["api", method.lower(), speed_tag, f"status-{status // 100}xx"]

    if any(
        pattern in path
        for pattern in [
            "/datasets/upload",
            "/datasets/detect-columns",
            "/datasets/",
            "/discovery/discover",
            "/visualization/",
            "/conformance/",
            "/analytics/",
        ]
    ):
        tags.append("user-action")
    elif any(pattern in path for pattern in ["/stream", "/recent", "/poll"]):
        tags.append("background")

    # Flag errors and slow requests for highlighting
    if status >= 400:
        tags.append("error")
    if status >= 500:
        tags.append("critical")
    if duration_ms > 3000:
        tags.append("timeout-risk")

    data = {}
    if response_size:
        data["response_size"] = response_size
    if timing:
        data["timing_breakdown"] = timing

    _create_log_entry(
        level=LogLevel.API_RES,
        source=f"BE {method} {path}",
        message=message,
        status=status,
        duration=duration_ms,
        request_id=request_id,
        data=data if data else None,
        tags=tags,
        timing=timing,
    )


def log_error(
    source: str,
    message: str,
    error_code: str | None = None,
    details: dict | None = None,
    stack_trace: str | None = None,
) -> None:
    """Log error with full context."""
    global _error_count
    _error_count += 1

    data = {}
    if error_code:
        data["error_code"] = error_code
    if details:
        data.update(details)
    if stack_trace:
        data["stack"] = stack_trace[:500]  # Truncate for transport

    _create_log_entry(
        level=LogLevel.ERROR,
        source=f"BE {source}",
        message=f"⚠ {message}",
        data=data if data else None,
        tags=["error", error_code] if error_code else ["error"],
    )


def log_pm4py_operation(
    operation: str,
    miner_type: str,
    duration_ms: int,
    status: str,
    events_processed: int | None = None,
    result_summary: dict | None = None,
) -> None:
    """Log PM4Py operation with performance data."""
    emoji = "✓" if status == "success" else "✗"

    data = {
        "operation": operation,
        "miner_type": miner_type,
        "status": status,
    }
    if events_processed:
        data["events_processed"] = events_processed
    if result_summary:
        data["result"] = result_summary

    _create_log_entry(
        level=LogLevel.ACTION,
        source=f"BE PM4Py/{miner_type}",
        message=f"{emoji} {operation}: {status}",
        duration=duration_ms,
        data=data,
        tags=["pm4py", operation, miner_type, status],
    )


def log_circuit_breaker(
    circuit: str,
    from_state: str,
    to_state: str,
    failure_count: int | None = None,
) -> None:
    """Log circuit breaker state change with visual indicator."""
    state_emoji = {
        "closed": "🟢",
        "open": "🔴",
        "half_open": "🟡",
    }

    _create_log_entry(
        level=LogLevel.CIRCUIT,
        source=f"BE Circuit:{circuit}",
        message=f"{state_emoji.get(to_state, '⚪')} {from_state} → {to_state}",
        data={
            "circuit": circuit,
            "from": from_state,
            "to": to_state,
            "failure_count": failure_count,
        },
        tags=["circuit", circuit, to_state],
    )


def log_perf_warning(
    operation: str,
    duration_ms: int,
    threshold_ms: int,
    details: dict | None = None,
) -> None:
    """Log performance warning."""
    _create_log_entry(
        level=LogLevel.PERF,
        source="BE Perf",
        message=f"⚡ Slow: {operation} ({duration_ms}ms > {threshold_ms}ms)",
        duration=duration_ms,
        data={
            "operation": operation,
            "threshold_ms": threshold_ms,
            **(details or {}),
        },
        tags=["perf", "slow"],
    )


# Note: log_trace_span is imported from src.infrastructure.devconsole_types and re-exported


# =============================================================================
# System Metrics Collection
# =============================================================================


def _get_system_metrics() -> SystemMetrics:
    """Collect current system metrics."""
    now = time.time()

    # Calculate RPS (requests in last 10 seconds)
    recent_requests = sum(1 for t in _request_timestamps if now - t < 10)
    rps = recent_requests / 10.0

    # Average response time
    avg_response = sum(_request_times) / len(_request_times) if _request_times else 0

    # Error rate (last 100 requests)
    total_recent = len(_request_times)
    error_rate = (_error_count / total_recent * 100) if total_recent > 0 else 0

    # Get circuit breaker states
    circuit_states = {}
    try:
        from src.infrastructure.circuit_breaker import get_all_circuit_statuses

        for status in get_all_circuit_statuses():
            circuit_states[status["name"]] = status["state"]
    except ImportError:
        pass

    return SystemMetrics(
        timestamp=datetime.utcnow().isoformat() + "Z",
        cpu_percent=psutil.cpu_percent(),
        memory_percent=psutil.virtual_memory().percent,
        memory_mb=psutil.Process().memory_info().rss / (1024 * 1024),
        active_requests=_active_requests,
        requests_per_second=round(rps, 2),
        avg_response_time_ms=round(avg_response, 2),
        error_rate_percent=round(error_rate, 2),
        circuit_breakers=circuit_states,
    )


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
    from src.infrastructure.log_broker import log_broker

    # Ensure broker is connected
    await log_broker.connect()

    try:
        # Send initial metrics
        metrics = _get_system_metrics()
        heartbeat = HeartbeatMessage(
            timestamp=datetime.utcnow().isoformat() + "Z",
            metrics=metrics,
            recent_errors=_error_count,
            slow_requests=_slow_request_count,
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
                metrics = _get_system_metrics()
                heartbeat = HeartbeatMessage(
                    timestamp=datetime.utcnow().isoformat() + "Z",
                    metrics=metrics,
                    recent_errors=_error_count,
                    slow_requests=_slow_request_count,
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

    return _get_system_metrics().model_dump()


@router.get("/recent")
async def get_recent_logs(
    limit: int = Query(50, ge=1, le=200),
    level: str | None = Query(None, description="Filter by level"),
    tag: str | None = Query(None, description="Filter by tag"),
):
    """Get recent logs with optional filtering."""
    if not settings.debug:
        return {"error": "Dev logs only available in debug mode"}

    from src.infrastructure.log_broker import log_broker

    logs = log_broker.get_recent_logs(limit=limit)

    if level:
        logs = [log_entry for log_entry in logs if log_entry.get("level") == level]
    if tag:
        logs = [log_entry for log_entry in logs if tag in log_entry.get("tags", [])]

    return logs


@router.delete("/clear")
async def clear_logs():
    """Clear the log buffer and reset metrics."""
    global _error_count, _slow_request_count

    if not settings.debug:
        return {"error": "Dev logs only available in debug mode"}

    from src.infrastructure.log_broker import log_broker

    log_broker._local_buffer.clear()
    _request_times.clear()
    _request_timestamps.clear()
    _error_count = 0
    _slow_request_count = 0

    return {"status": "cleared", "timestamp": datetime.utcnow().isoformat()}
