"""
Structured logging configuration using structlog.

Provides JSON logs in production (searchable) and pretty console logs in development.
Configuration is controlled by DEBUG environment variable.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.typing import Processor

from ..config import get_settings


def configure_logging() -> None:
    """
    Configure structlog with environment-appropriate processors.
    
    - DEBUG=true: Pretty console output with colors
    - DEBUG=false: JSON output for log aggregation
    """
    settings = get_settings()
    
    # Shared processors for all environments
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    
    if settings.debug:
        # Development: pretty console output
        processors: list[Processor] = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # Production: JSON output
        processors = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging to work with structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.debug else logging.INFO,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured structlog logger
        
    Usage:
        log = get_logger(__name__)
        log.info("upload_complete", upload_id="abc-123", row_count=1000)
    """
    return structlog.get_logger(name)


def log_context(**kwargs: Any) -> None:
    """
    Add context variables that will be included in all subsequent log messages.
    
    Usage:
        log_context(request_id="abc-123", user_id="user-456")
        log.info("processing")  # Will include request_id and user_id
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_log_context() -> None:
    """Clear all context variables."""
    structlog.contextvars.clear_contextvars()
