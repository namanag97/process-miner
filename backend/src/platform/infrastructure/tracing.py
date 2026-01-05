"""OpenTelemetry distributed tracing integration.

Provides distributed tracing for:
- HTTP requests
- PM4Py operations
- Database queries
- Background jobs

Usage:
    # Setup in main.py
    from src.platform.infrastructure.tracing import setup_tracing
    setup_tracing(app, service_name="process-mining-api")

    # Manual spans
    from src.platform.infrastructure.tracing import create_span
    with create_span("custom_operation") as span:
        span.set_attribute("key", "value")
        do_work()
"""

import functools
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, TypeVar

from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

# =============================================================================
# OpenTelemetry Imports (Optional Dependency)
# =============================================================================

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
        SimpleSpanProcessor,
    )
    from opentelemetry.trace import Span, Status, StatusCode

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None  # type: ignore
    Span = None  # type: ignore


# Global tracer instance
_tracer: Any | None = None


def setup_tracing(
    app: Any,
    service_name: str = "process-mining-api",
    service_version: str = "1.0.0",
    environment: str = "development",
    otlp_endpoint: str | None = None,
    console_export: bool = True,
    devconsole_export: bool = True,
) -> None:
    """Initialize OpenTelemetry tracing for the application.

    Args:
        app: FastAPI application instance
        service_name: Service identifier in traces
        service_version: Service version for traces
        environment: Deployment environment
        otlp_endpoint: OTLP exporter endpoint (optional)
        console_export: Whether to export to console (for dev)
        devconsole_export: Whether to export to DevConsole SSE stream (for dev)
    """
    global _tracer

    if not OTEL_AVAILABLE:
        logger.warning(
            "opentelemetry_not_available", message="Install opentelemetry-* packages for tracing"
        )
        return

    # Resource attributes
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": environment,
        }
    )

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Add exporters
    if console_export:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Add DevConsole exporter for real-time trace visualization
    # Use SimpleSpanProcessor for immediate export (no batching delay)
    if devconsole_export:
        try:
            from src.platform.infrastructure.devconsole_exporter import DevConsoleSpanExporter

            provider.add_span_processor(SimpleSpanProcessor(DevConsoleSpanExporter()))
            logger.info("devconsole_exporter_enabled")
        except ImportError:
            logger.debug("devconsole_exporter_not_available")

    if otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set as global provider
    trace.set_tracer_provider(provider)

    # Get tracer
    _tracer = trace.get_tracer(service_name, service_version)

    # Instrument FastAPI with excludelist for noisy endpoints
    # Exclude health checks, metrics, and other high-frequency endpoints
    # that don't provide value in traces
    excluded_urls = [
        "/health",
        "/metrics",
        "/api/v1/health",
        "/api/v1/metrics",
        "/api/v1/dev/logs/stream",  # SSE stream creates many spans
        "/api/v1/dev/logs/metrics",
    ]

    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls=",".join(excluded_urls),
    )

    logger.info(
        "tracing_initialized",
        service_name=service_name,
        otlp_endpoint=otlp_endpoint,
        console_export=console_export,
        devconsole_export=devconsole_export,
        excluded_endpoints=len(excluded_urls),
    )


def get_tracer() -> Any | None:
    """Get the global tracer instance."""
    return _tracer


@contextmanager
def create_span(
    name: str,
    attributes: dict[str, Any] | None = None,
    kind: Any | None = None,
):
    """Create a new span for tracing.

    Usage:
        with create_span("process_events", {"event_count": 100}) as span:
            result = process_events()
            span.set_attribute("result_count", len(result))
    """
    if not OTEL_AVAILABLE or _tracer is None:
        yield None
        return

    span_kind = kind or trace.SpanKind.INTERNAL

    with _tracer.start_as_current_span(name, kind=span_kind) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        try:
            yield span
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


def trace_function(
    name: str | None = None,
    attributes: dict[str, Any] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to trace a function.

    Usage:
        @trace_function("discover_process_model")
        def discover(log, miner_type):
            ...
    """

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        span_name = name or fn.__name__

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with create_span(span_name, attributes) as span:
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if span is not None:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            with create_span(span_name, attributes) as span:
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    if span is not None:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        import asyncio

        if asyncio.iscoroutinefunction(fn):
            return async_wrapper
        return wrapper

    return decorator


def add_span_attribute(key: str, value: Any) -> None:
    """Add an attribute to the current span if one exists."""
    if not OTEL_AVAILABLE:
        return

    span = trace.get_current_span()
    if span:
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: dict[str, Any] | None = None) -> None:
    """Add an event to the current span if one exists."""
    if not OTEL_AVAILABLE:
        return

    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes or {})


def get_trace_id() -> str | None:
    """Get the current trace ID as a string."""
    if not OTEL_AVAILABLE:
        return None

    span = trace.get_current_span()
    if span:
        context = span.get_span_context()
        if context.is_valid:
            return format(context.trace_id, "032x")
    return None


def get_span_id() -> str | None:
    """Get the current span ID as a string."""
    if not OTEL_AVAILABLE:
        return None

    span = trace.get_current_span()
    if span:
        context = span.get_span_context()
        if context.is_valid:
            return format(context.span_id, "016x")
    return None


# =============================================================================
# Instrumentation for SQLAlchemy
# =============================================================================


def instrument_database(engine: Any) -> None:
    """Instrument SQLAlchemy for tracing.

    Args:
        engine: SQLAlchemy engine instance
    """
    if not OTEL_AVAILABLE:
        return

    SQLAlchemyInstrumentor().instrument(engine=engine)
    logger.info("database_tracing_enabled")
