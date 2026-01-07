"""Structured logging configuration with structlog.

Provides:
- JSON output for production
- Colored console output for development
- Request ID tracking
- Performance timing
- Operation logging decorators
- Scoped context management

Note: DevConsole integration is handled separately in the API middleware
to maintain clean architecture (core layer should not depend on infrastructure).
"""

import logging
import sys
import time
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any, ParamSpec, TypeVar

import structlog
from structlog.types import Processor

from src.platform.core.config import get_settings

# Type hints for decorator
P = ParamSpec("P")
R = TypeVar("R")


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
# Operation Logging Decorator
# =============================================================================


def log_operation(
    operation_name: str,
    *,
    include_args: list[str] | None = None,
    log_result: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator for automatic operation logging.

    Logs:
    - Operation start with context
    - Operation success with duration
    - Operation failure with error details

    Args:
        operation_name: Name for this operation (e.g., "create_dataset")
        include_args: List of argument names to include in logs (by name)
        log_result: Whether to log the result (be careful with sensitive data)

    Example:
        @router.post("/datasets")
        @log_operation("create_dataset", include_args=["project_id"])
        async def create_dataset(project_id: str, ...):
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        logger = get_logger(func.__module__)

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Extract loggable context from kwargs
            log_context: dict[str, Any] = {"operation": operation_name}
            if include_args:
                for arg_name in include_args:
                    if arg_name in kwargs:
                        log_context[arg_name] = kwargs[arg_name]

            # Log operation start
            logger.info(f"🚀 {operation_name}_started", **log_context)
            start_time = time.perf_counter()

            try:
                result = await func(*args, **kwargs)  # type: ignore[misc]
                duration_ms = (time.perf_counter() - start_time) * 1000

                # Log success
                success_context = {**log_context, "duration_ms": round(duration_ms, 2)}
                if log_result and result is not None:
                    # Only log simple types to avoid huge log entries
                    if isinstance(result, (str, int, float, bool)):
                        success_context["result"] = result
                    elif hasattr(result, "id"):
                        success_context["result_id"] = getattr(result, "id", None)

                logger.info(f"✅ {operation_name}_completed", **success_context)
                return result

            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                error_context = {
                    **log_context,
                    "duration_ms": round(duration_ms, 2),
                    "error_type": type(e).__name__,
                    "error_message": str(e)[:500],  # Truncate long errors
                }
                logger.error(f"❌ {operation_name}_failed", **error_context, exc_info=True)
                raise

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Extract loggable context from kwargs
            log_context: dict[str, Any] = {"operation": operation_name}
            if include_args:
                for arg_name in include_args:
                    if arg_name in kwargs:
                        log_context[arg_name] = kwargs[arg_name]

            logger.info(f"🚀 {operation_name}_started", **log_context)
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.info(
                    f"✅ {operation_name}_completed",
                    **log_context,
                    duration_ms=round(duration_ms, 2),
                )
                return result

            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.error(
                    f"❌ {operation_name}_failed",
                    **log_context,
                    duration_ms=round(duration_ms, 2),
                    error_type=type(e).__name__,
                    error_message=str(e)[:500],
                    exc_info=True,
                )
                raise

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


# =============================================================================
# Scoped Context Manager
# =============================================================================


@contextmanager
def operation_context(**kwargs: Any):
    """Context manager for scoped log context binding.

    Binds context variables for the duration of the 'with' block,
    then restores previous context.

    Example:
        with operation_context(user_id=user.id, workspace_id=ws.id):
            logger.info("processing")  # Includes user_id and workspace_id
            do_work()
        # Context is cleared after block
    """
    # Get current context to restore later
    previous_context = structlog.contextvars.get_contextvars()

    try:
        bind_context(**kwargs)
        yield
    finally:
        # Restore previous context
        clear_context()
        if previous_context:
            bind_context(**previous_context)


# =============================================================================
# API Error Logging Helper
# =============================================================================


def log_api_error(
    logger: structlog.stdlib.BoundLogger,
    error: Exception,
    *,
    operation: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    user_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Log an API error with consistent structure.

    Use this for explicit error logging in exception handlers.

    Args:
        logger: The logger instance to use
        error: The exception that occurred
        operation: What operation failed (e.g., "create_dataset")
        resource_type: Type of resource involved (e.g., "Dataset", "Project")
        resource_id: ID of the resource if applicable
        user_id: ID of the user if applicable
        extra: Additional context to include
    """
    context: dict[str, Any] = {
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error)[:500],
    }

    if resource_type:
        context["resource_type"] = resource_type
    if resource_id:
        context["resource_id"] = resource_id
    if user_id:
        context["user_id"] = user_id
    if extra:
        context.update(extra)

    # Use warning for expected errors (NotFound, Validation), error for unexpected
    from src.platform.core.exceptions import AppException

    if isinstance(error, AppException) and error.status_code < 500:
        logger.warning(f"⚠️ {operation}_failed", **context)
    else:
        logger.error(f"🔥 {operation}_failed", **context, exc_info=True)


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
