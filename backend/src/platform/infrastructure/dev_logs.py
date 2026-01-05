"""DevConsole Logging Functions - Rich observability helpers.

Provides structured logging functions for DevConsole frontend:
- API request/response logging
- Error tracking
- Performance monitoring
- PM4Py operation tracking
- Circuit breaker events
- Authentication events
- Database query logging
- Cache operations
- Validation results

These functions use the devconsole_types infrastructure to emit structured
logs to the dev console stream.
"""

import time
from collections import deque
from datetime import datetime

import psutil

from src.platform.infrastructure.devconsole_types import (
    DevLogEntry,
    LogLevel,
    SystemMetrics,
    create_log_entry as _create_log_entry,
)


# =============================================================================
# Metrics Tracking (module-level state)
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

    importance = 4 if "user-action" in tags else 1  # User actions are important

    _create_log_entry(
        level=LogLevel.API_REQ,
        source=f"BE {method} {path}",
        message="→ Request",
        data=data if data else None,
        request_id=request_id,
        tags=tags,
        importance=importance,
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

    # Determine importance based on status and speed
    if status >= 500:
        importance = 5  # Server errors are critical
    elif status >= 400:
        importance = 4  # Client errors are high
    elif duration_ms > 3000:
        importance = 4  # Very slow requests are high
    elif "user-action" in tags:
        importance = 3  # User actions are medium
    else:
        importance = 1  # Background requests are low

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
        importance=importance,
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
        importance=5,  # Errors are always critical
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

    importance = 4 if status == "success" else 5  # Failed PM4Py operations are critical

    _create_log_entry(
        level=LogLevel.PM4PY,
        source=f"BE PM4Py/{miner_type}",
        message=f"{emoji} {operation}: {status}",
        duration=duration_ms,
        data=data,
        tags=["pm4py", operation, miner_type, status],
        importance=importance,
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

    importance = 5 if to_state == "open" else 4  # Circuit opening is critical

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
        importance=importance,
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
        importance=4,  # Performance warnings are high importance
    )


def log_database_query(
    query_type: str,
    table: str,
    duration_ms: int,
    row_count: int | None = None,
    is_slow: bool = False,
) -> None:
    """Log database query with timing and row count."""
    emoji = "⚡" if is_slow else "🗄"
    tags = ["db", query_type.lower(), table]
    if is_slow:
        tags.append("slow")

    data = {
        "query_type": query_type,
        "table": table,
    }
    if row_count is not None:
        data["row_count"] = row_count

    importance = 2 if not is_slow else 4  # Slow queries are more important

    _create_log_entry(
        level=LogLevel.DB_QUERY,
        source=f"BE DB/{table}",
        message=f"{emoji} {query_type} ({duration_ms}ms)",
        duration=duration_ms,
        data=data,
        tags=tags,
        importance=importance,
    )


def log_cache_operation(
    operation: str,
    key: str,
    hit: bool | None = None,
    ttl: int | None = None,
) -> None:
    """Log cache operation (get, set, delete, hit, miss)."""
    emoji_map = {
        "hit": "✓",
        "miss": "✗",
        "set": "→",
        "delete": "🗑",
    }

    emoji = emoji_map.get(operation, "💾")
    tags = ["cache", operation]

    data = {"operation": operation, "key": key}
    if hit is not None:
        data["hit"] = hit
    if ttl is not None:
        data["ttl"] = ttl

    importance = 1 if hit else 2  # Cache hits are low importance

    _create_log_entry(
        level=LogLevel.CACHE,
        source="BE Cache",
        message=f"{emoji} {operation}: {key}",
        data=data,
        tags=tags,
        importance=importance,
    )


def log_validation(
    entity: str,
    is_valid: bool,
    errors: list[str] | None = None,
    field_count: int | None = None,
) -> None:
    """Log input validation result."""
    emoji = "✓" if is_valid else "✗"
    tags = ["validation", entity, "valid" if is_valid else "invalid"]

    data = {"entity": entity, "is_valid": is_valid}
    if errors:
        data["errors"] = errors
    if field_count is not None:
        data["field_count"] = field_count

    importance = 2 if is_valid else 4  # Failed validation is important

    _create_log_entry(
        level=LogLevel.VALIDATION,
        source=f"BE Validation/{entity}",
        message=f"{emoji} {'Valid' if is_valid else f'Invalid ({len(errors or [])} errors)'}",
        data=data,
        tags=tags,
        importance=importance,
    )


def log_auth_event(
    event_type: str,
    user_id: str | None = None,
    success: bool = True,
    reason: str | None = None,
) -> None:
    """Log authentication/authorization event."""
    emoji_map = {
        "login": "🔓",
        "logout": "🔒",
        "permission_check": "🔑",
        "token_refresh": "🔄",
        "access_denied": "🚫",
    }

    emoji = emoji_map.get(event_type, "🔐")
    tags = ["auth", event_type, "success" if success else "failure"]

    data = {"event_type": event_type, "success": success}
    if user_id:
        data["user_id"] = user_id
    if reason:
        data["reason"] = reason

    importance = 4 if not success else 3  # Failed auth is high importance

    _create_log_entry(
        level=LogLevel.AUTH,
        source="BE Auth",
        message=f"{emoji} {event_type}" + (f": {reason}" if reason else ""),
        data=data,
        tags=tags,
        importance=importance,
    )


# =============================================================================
# System Metrics Collection
# =============================================================================


def get_system_metrics() -> SystemMetrics:
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
        from src.platform.infrastructure.circuit_breaker import get_all_circuit_statuses

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
# Metrics Accessors (for stream endpoint)
# =============================================================================


def get_error_count() -> int:
    """Get current error count."""
    return _error_count


def get_slow_request_count() -> int:
    """Get current slow request count."""
    return _slow_request_count


def reset_metrics() -> None:
    """Reset all metrics counters."""
    global _error_count, _slow_request_count
    _request_times.clear()
    _request_timestamps.clear()
    _error_count = 0
    _slow_request_count = 0


__all__ = [
    "log_api_request",
    "log_api_response",
    "log_auth_event",
    "log_cache_operation",
    "log_circuit_breaker",
    "log_database_query",
    "log_error",
    "log_perf_warning",
    "log_pm4py_operation",
    "log_validation",
    "get_system_metrics",
    "get_error_count",
    "get_slow_request_count",
    "reset_metrics",
]
