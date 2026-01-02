"""Structured logging configuration with structlog.

Provides:
- JSON output for production
- Colored console output for development
- Request ID tracking
- Performance timing
- Real-time DevConsole integration
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor, EventDict, WrappedLogger

from src.core.config import get_settings


# =============================================================================
# DevConsole Integration Processor
# =============================================================================

class DevConsoleProcessor:
    """Send structlog events to DevConsole SSE stream in real-time.

    This bridges structured application logs into the DevConsole for
    comprehensive observability during development.
    """

    def __call__(
        self,
        logger: WrappedLogger,
        method_name: str,
        event_dict: EventDict
    ) -> EventDict:
        """Process log event and send to DevConsole."""
        # Only send to DevConsole in debug mode
        settings = get_settings()
        if not settings.debug:
            return event_dict

        try:
            # Avoid circular import
            from src.api.routers.dev_logs_stream import _create_log_entry, LogLevel

            # Map structlog levels to DevConsole levels
            level_map = {
                "debug": LogLevel.INFO,
                "info": LogLevel.INFO,
                "warning": LogLevel.ACTION,
                "error": LogLevel.ERROR,
                "critical": LogLevel.ERROR,
            }

            log_level = level_map.get(event_dict.get("level", "info"), LogLevel.INFO)

            # Extract source (logger name)
            logger_name = event_dict.get("logger", "app")
            if isinstance(logger_name, str):
                # Shorten logger name for readability (e.g., src.services.mining → mining)
                logger_parts = logger_name.split(".")
                source = logger_parts[-1] if logger_parts else logger_name
            else:
                source = "app"

            # Extract message
            message = event_dict.get("event", "")

            # Extract additional data (exclude standard fields)
            excluded_keys = {"event", "logger", "level", "timestamp"}
            data = {
                k: v for k, v in event_dict.items()
                if k not in excluded_keys and not k.startswith("_")
            }

            # Extract timing if present
            duration = None
            if "duration" in data:
                try:
                    duration = int(float(data["duration"]) * 1000)  # Convert to ms
                except (ValueError, TypeError):
                    pass

            # Send to DevConsole
            _create_log_entry(
                level=log_level,
                source=f"BE {source}",
                message=message,
                data=data if data else None,
                duration=duration,
            )
        except Exception:
            # Don't break logging if DevConsole fails
            # Silently ignore - the log will still go to console/JSON
            pass

        return event_dict


def configure_logging() -> None:
    """Configure structlog for the application.

    Call this once at application startup.
    """
    settings = get_settings()

    # Determine log level
    log_level = logging.DEBUG if settings.debug else logging.INFO

    # Common processors for all environments
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Add DevConsole processor in debug mode (before rendering)
    # This sends logs to real-time SSE stream for in-browser visibility
    if settings.debug:
        shared_processors.append(DevConsoleProcessor())

    if settings.log_json or not settings.debug:
        # Production: JSON output
        processors: list[Processor] = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
        # Configure standard logging to use structlog
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=log_level,
        )
    else:
        # Development: Colored console output
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=log_level,
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.debug else logging.WARNING
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance for a module.

    Args:
        name: Module name (usually __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """Bind context variables to all subsequent log calls.

    Use this to add request-scoped context (e.g., request_id, user_id).
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all bound context variables.

    Call this at the end of each request.
    """
    structlog.contextvars.clear_contextvars()


# =============================================================================
# Business Metrics Helper
# =============================================================================

def log_business_metric(
    name: str,
    value: float,
    unit: str = "",
    tags: dict[str, Any] | None = None,
    logger_name: str = "metrics"
) -> None:
    """Log a business/domain metric to DevConsole for real-time monitoring.

    Examples:
        log_business_metric("variants_discovered", 42, "variants", {"miner": "alpha"})
        log_business_metric("conformance_score", 0.87, tags={"dataset": "orders"})
        log_business_metric("cache_hit_rate", 75.5, "%", {"cache": "event_logs"})

    Args:
        name: Metric name (e.g., "variants_discovered", "conformance_score")
        value: Metric value
        unit: Unit of measurement (e.g., "%", "ms", "MB")
        tags: Additional tags/dimensions for the metric
        logger_name: Logger name for categorization
    """
    logger = get_logger(logger_name)
    logger.info(
        f"📊 {name}",
        metric_name=name,
        metric_value=value,
        metric_unit=unit,
        **(tags or {}),
    )
