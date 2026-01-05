"""Structured logging configuration with structlog.

Provides:
- JSON output for production
- Colored console output for development
- Request ID tracking
- Performance timing

Note: DevConsole integration is handled separately in the API middleware
to maintain clean architecture (core layer should not depend on infrastructure).
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from src.platform.core.config import get_settings


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

    if settings.log_json or not settings.debug:
        # Production: JSON output
        processors: list[Processor] = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
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
    logger_name: str = "metrics",
) -> None:
    """Log a business/domain metric for monitoring.

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
