"""Observability infrastructure: OpenTelemetry tracing and Prometheus metrics."""

import time
from functools import wraps
from typing import Callable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Prometheus metrics
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Gauge,
        Histogram,
        Info,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# OpenTelemetry
try:
    from opentelemetry import trace
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


# =============================================================================
# Prometheus Metrics Definitions
# =============================================================================

if PROMETHEUS_AVAILABLE:
    # Request metrics
    REQUEST_COUNT = Counter(
        "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
    )

    REQUEST_LATENCY = Histogram(
        "http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "endpoint"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    )

    REQUESTS_IN_PROGRESS = Gauge(
        "http_requests_in_progress", "Number of HTTP requests in progress", ["method", "endpoint"]
    )

    # Business metrics
    EVENT_LOGS_COUNT = Gauge(
        "process_mining_event_logs_total", "Total number of event logs in system"
    )

    PROCESS_MODELS_COUNT = Gauge(
        "process_mining_models_total", "Total number of process models discovered"
    )

    DISCOVERY_RUNS = Counter(
        "process_mining_discovery_runs_total",
        "Total number of process discovery runs",
        ["miner_type", "status"],
    )

    CONFORMANCE_CHECKS = Counter(
        "process_mining_conformance_checks_total",
        "Total number of conformance checks performed",
        ["status"],
    )

    # Application info
    APP_INFO = Info("process_mining_app", "Application information")


def get_metrics_response() -> tuple[bytes, str]:
    """Generate Prometheus metrics response."""
    if not PROMETHEUS_AVAILABLE:
        return b"# Prometheus client not installed", "text/plain"
    return generate_latest(), CONTENT_TYPE_LATEST


def set_app_info(version: str, name: str) -> None:
    """Set application info metric."""
    if PROMETHEUS_AVAILABLE:
        APP_INFO.info(
            {
                "version": version,
                "name": name,
            }
        )


def update_business_metrics(event_logs: int, models: int) -> None:
    """Update business metrics gauges."""
    if PROMETHEUS_AVAILABLE:
        EVENT_LOGS_COUNT.set(event_logs)
        PROCESS_MODELS_COUNT.set(models)


def record_discovery_run(miner_type: str, success: bool) -> None:
    """Record a discovery run."""
    if PROMETHEUS_AVAILABLE:
        DISCOVERY_RUNS.labels(
            miner_type=miner_type, status="success" if success else "failure"
        ).inc()


def record_conformance_check(success: bool) -> None:
    """Record a conformance check."""
    if PROMETHEUS_AVAILABLE:
        CONFORMANCE_CHECKS.labels(status="success" if success else "failure").inc()


# =============================================================================
# OpenTelemetry Setup
# =============================================================================

_tracer: Optional[trace.Tracer] = None


def setup_tracing(service_name: str = "process-mining-api", enable_console: bool = False) -> None:
    """Initialize OpenTelemetry tracing."""
    global _tracer

    if not OTEL_AVAILABLE:
        return

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if enable_console:
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(__name__)


def get_tracer() -> Optional[trace.Tracer]:
    """Get the configured tracer."""
    return _tracer


def instrument_fastapi(app) -> None:
    """Instrument FastAPI with OpenTelemetry."""
    if OTEL_AVAILABLE:
        FastAPIInstrumentor.instrument_app(app)


# =============================================================================
# Metrics Middleware
# =============================================================================


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting Prometheus metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not PROMETHEUS_AVAILABLE:
            return await call_next(request)

        method = request.method
        # Normalize endpoint to avoid high cardinality
        endpoint = self._normalize_path(request.url.path)

        # Track in-progress requests
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            # Record metrics
            duration = time.perf_counter() - start_time

            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()

            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

            REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()

        return response

    def _normalize_path(self, path: str) -> str:
        """Normalize path to reduce cardinality (replace IDs with placeholders)."""
        import re

        # Replace UUIDs
        path = re.sub(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            "{id}",
            path,
        )
        # Replace numeric IDs
        path = re.sub(r"/\d+(?=/|$)", "/{id}", path)
        return path


# =============================================================================
# Tracing Decorator
# =============================================================================


def traced(name: Optional[str] = None):
    """Decorator to add tracing to a function."""

    def decorator(func: Callable) -> Callable:
        span_name = name or func.__name__

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if _tracer:
                with _tracer.start_as_current_span(span_name):
                    return await func(*args, **kwargs)
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if _tracer:
                with _tracer.start_as_current_span(span_name):
                    return func(*args, **kwargs)
            return func(*args, **kwargs)

        if asyncio_iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def asyncio_iscoroutinefunction(func: Callable) -> bool:
    """Check if function is async."""
    import asyncio

    return asyncio.iscoroutinefunction(func)
