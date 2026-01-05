"""DevConsole - Simple real-time observability for development.

Provides:
- Real-time log streaming via SSE
- API request/response logging
- Error tracking
- System metrics

Usage:
    from src.platform.devconsole import log_info, log_error, log_api_request

    # Log general info
    log_info("Dataset", "Processing events", dataset_id=123, count=1000)

    # Log errors
    log_error("Dataset", "Failed to process", error_code="DS001", reason="Invalid CSV")

    # API logging is automatic via middleware
"""

from .logging import (
    get_error_count,
    get_slow_request_count,
    get_system_metrics,
    log_api_request,
    log_api_response,
    log_error,
    log_info,
    reset_metrics,
)
from .models import DevLogEntry, HeartbeatMessage, LogLevel, SystemMetrics

__all__ = [
    # Logging functions
    "log_info",
    "log_error",
    "log_api_request",
    "log_api_response",
    # Metrics
    "get_system_metrics",
    "get_error_count",
    "get_slow_request_count",
    "reset_metrics",
    # Models
    "DevLogEntry",
    "HeartbeatMessage",
    "LogLevel",
    "SystemMetrics",
]
