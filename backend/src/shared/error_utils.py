"""Shared Error Handling Utilities.

Provides helper functions for safe operations with proper error handling
and logging, avoiding silent exception swallowing.
"""

import json
from typing import Any, TypeVar

from src.infra.core.exceptions import PM4PyError
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def safe_json_loads(
    data: str | None,
    default: T = None,
    context: str = "",
) -> Any | T:
    """Parse JSON with proper error logging.

    Args:
        data: JSON string to parse
        default: Default value to return on failure
        context: Description for logging (e.g., "dataset.statistics_json")

    Returns:
        Parsed JSON or default value on failure
    """
    if data is None:
        return default

    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.warning(
            "json_parse_failed",
            context=context,
            error=str(e),
            data_preview=data[:100] if data else None,
        )
        return default
    except TypeError as e:
        logger.warning(
            "json_parse_type_error",
            context=context,
            error=str(e),
        )
        return default


def wrap_pm4py_exception(e: Exception, operation: str) -> PM4PyError:
    """Convert PM4Py exceptions to typed app exceptions.

    Args:
        e: The original exception
        operation: Description of the PM4Py operation that failed

    Returns:
        PM4PyError with proper context
    """
    return PM4PyError(
        message=f"PM4Py {operation} failed: {e!s}",
        operation=operation,
        original_error=str(e),
    )


def log_and_suppress(
    e: Exception,
    operation: str,
    level: str = "warning",
    **extra_context: Any,
) -> None:
    """Log an exception that will be suppressed.

    Use this instead of bare `except Exception: pass` to ensure
    errors are at least logged for debugging.

    Args:
        e: The exception to log
        operation: Description of what operation failed
        level: Log level ("debug", "warning", "error")
        **extra_context: Additional context to include in log
    """
    log_fn = getattr(logger, level, logger.warning)
    log_fn(
        f"{operation}_suppressed",
        error=str(e),
        error_type=type(e).__name__,
        **extra_context,
    )
