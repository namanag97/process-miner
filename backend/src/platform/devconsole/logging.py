"""Simple logging functions for DevConsole."""

import asyncio
import time
from collections import deque

import psutil

from .models import (
    DevLogEntry,
    LogLevel,
    SystemMetrics,
    create_log_entry,
)

# Metrics tracking (module-level state)
_request_times: deque[float] = deque(maxlen=100)
_request_timestamps: deque[float] = deque(maxlen=100)
_error_count = 0
_slow_request_count = 0
_active_requests = 0


def log_info(source: str, message: str, **data) -> None:
    """Log general information to DevConsole.

    Args:
        source: Source identifier (e.g., "BE Dataset")
        message: Log message
        **data: Additional structured data
    """
    entry = create_log_entry(
        level=LogLevel.INFO,
        source=f"BE {source}",
        message=message,
        data=data if data else None,
        tags=["info"],
        importance=2,
    )
    _emit_log(entry)


def log_error(
    source: str,
    message: str,
    error_code: str | None = None,
    **details,
) -> None:
    """Log error to DevConsole.

    Args:
        source: Source identifier
        message: Error message
        error_code: Optional error code
        **details: Additional error details
    """
    global _error_count
    _error_count += 1

    data = {}
    if error_code:
        data["error_code"] = error_code
    if details:
        data.update(details)

    entry = create_log_entry(
        level=LogLevel.ERROR,
        source=f"BE {source}",
        message=f"⚠ {message}",
        data=data if data else None,
        tags=["error", error_code] if error_code else ["error"],
        importance=5,
    )
    _emit_log(entry)


def log_api_request(
    method: str,
    path: str,
    request_id: str | None = None,
) -> None:
    """Log incoming API request.

    Args:
        method: HTTP method
        path: Request path
        request_id: Optional request ID
    """
    global _active_requests
    _active_requests += 1

    # Classify request type
    tags = ["api", method.lower()]
    if any(p in path for p in ["/datasets", "/discovery", "/visualization", "/conformance"]):
        tags.append("user-action")
        importance = 4
    else:
        tags.append("background")
        importance = 1

    entry = create_log_entry(
        level=LogLevel.API_REQ,
        source=f"BE {method} {path}",
        message="→ Request",
        request_id=request_id,
        tags=tags,
        importance=importance,
    )
    _emit_log(entry)


def log_api_response(
    method: str,
    path: str,
    status: int,
    duration_ms: int,
    request_id: str | None = None,
    timing: dict[str, float] | None = None,
) -> None:
    """Log API response with timing.

    Args:
        method: HTTP method
        path: Request path
        status: HTTP status code
        duration_ms: Request duration in milliseconds
        request_id: Optional request ID
        timing: Optional timing breakdown
    """
    global _active_requests, _error_count, _slow_request_count
    _active_requests = max(0, _active_requests - 1)

    # Track metrics
    _request_times.append(duration_ms)
    _request_timestamps.append(time.time())

    if status >= 400:
        _error_count += 1
    if duration_ms > 1000:
        _slow_request_count += 1

    # Build message
    status_emoji = "✓" if status < 400 else "✗" if status < 500 else "⚠"
    message = f"← {status_emoji} {status}"

    # Classify speed
    if duration_ms < 100:
        speed_tag = "fast"
    elif duration_ms < 500:
        speed_tag = "normal"
    elif duration_ms < 1000:
        speed_tag = "slow"
    else:
        speed_tag = "very-slow"

    tags = ["api", method.lower(), speed_tag, f"status-{status // 100}xx"]

    if any(p in path for p in ["/datasets", "/discovery", "/visualization", "/conformance"]):
        tags.append("user-action")
    else:
        tags.append("background")

    if status >= 400:
        tags.append("error")
    if status >= 500:
        tags.append("critical")

    # Determine importance
    if status >= 500:
        importance = 5
    elif status >= 400:
        importance = 4
    elif duration_ms > 3000:
        importance = 4
    elif "user-action" in tags:
        importance = 3
    else:
        importance = 1

    entry = create_log_entry(
        level=LogLevel.API_RES,
        source=f"BE {method} {path}",
        message=message,
        status=status,
        duration=duration_ms,
        request_id=request_id,
        timing=timing,
        tags=tags,
        importance=importance,
    )
    _emit_log(entry)


def get_system_metrics() -> SystemMetrics:
    """Collect current system metrics."""
    now = time.time()

    # Calculate RPS (requests in last 10 seconds)
    recent_requests = sum(1 for t in _request_timestamps if now - t < 10)
    rps = recent_requests / 10.0

    # Average response time
    avg_response = sum(_request_times) / len(_request_times) if _request_times else 0

    # Error rate
    total_recent = len(_request_times)
    error_rate = (_error_count / total_recent * 100) if total_recent > 0 else 0

    return SystemMetrics(
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        cpu_percent=psutil.cpu_percent(),
        memory_percent=psutil.virtual_memory().percent,
        memory_mb=psutil.Process().memory_info().rss / (1024 * 1024),
        active_requests=_active_requests,
        requests_per_second=round(rps, 2),
        avg_response_time_ms=round(avg_response, 2),
        error_rate_percent=round(error_rate, 2),
    )


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


def _emit_log(entry: DevLogEntry) -> None:
    """Emit log entry to broker."""
    try:
        from .broker import log_broker

        # Add to local buffer
        log_broker._local_buffer.append(entry.model_dump())

        # Publish to Redis if event loop available
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(log_broker.publish_log(entry.model_dump()))
        except RuntimeError:
            pass  # No event loop
    except Exception:
        pass  # Don't let logging errors break the app


def log_auth_event(event_type: str, **kwargs) -> None:
    """Log authentication event.
    
    Args:
        event_type: Type of auth event (login, logout, etc)
        **kwargs: Additional details (user_id, success, reason)
    """
    log_info("Auth", f"Event: {event_type}", **kwargs)


__all__ = [
    "log_info",
    "log_error",
    "log_api_request",
    "log_api_response",
    "get_system_metrics",
    "get_error_count",
    "get_slow_request_count",
    "reset_metrics",
    "log_auth_event",
]
