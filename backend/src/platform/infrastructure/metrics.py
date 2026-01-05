"""Prometheus metrics for monitoring and alerting.

Provides standardized metrics for:
- HTTP request latency and throughput
- PM4Py operation performance
- Business metrics (processes, analyses)
- System health indicators

Usage:
    # Metrics are automatically collected via middleware
    # Access at GET /metrics in Prometheus format
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

try:
    from prometheus_client import (
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        Info,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

T = TypeVar("T")


# =============================================================================
# Custom Registry (allows testing without global state)
# =============================================================================

if PROMETHEUS_AVAILABLE:
    REGISTRY = CollectorRegistry()

    # =============================================================================
    # HTTP Metrics
    # =============================================================================

    http_requests_total = Counter(
        "http_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
        registry=REGISTRY,
    )

    http_request_duration_seconds = Histogram(
        "http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "endpoint"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
        registry=REGISTRY,
    )

    http_requests_in_progress = Gauge(
        "http_requests_in_progress",
        "Number of HTTP requests currently being processed",
        ["method", "endpoint"],
        registry=REGISTRY,
    )

    # =============================================================================
    # PM4Py Operation Metrics
    # =============================================================================

    pm4py_operations_total = Counter(
        "pm4py_operations_total",
        "Total PM4Py operations",
        ["operation", "miner_type", "status"],
        registry=REGISTRY,
    )

    pm4py_operation_duration_seconds = Histogram(
        "pm4py_operation_duration_seconds",
        "PM4Py operation duration in seconds",
        ["operation", "miner_type"],
        buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
        registry=REGISTRY,
    )

    pm4py_log_events_processed = Counter(
        "pm4py_log_events_processed_total",
        "Total events processed by PM4Py operations",
        ["operation"],
        registry=REGISTRY,
    )

    # =============================================================================
    # Business Metrics
    # =============================================================================

    processes_created_total = Counter(
        "processes_created_total",
        "Total event logs uploaded and processed",
        registry=REGISTRY,
    )

    processes_active = Gauge(
        "processes_active",
        "Number of active event logs in the system",
        registry=REGISTRY,
    )

    analyses_completed_total = Counter(
        "analyses_completed_total",
        "Total analyses completed",
        ["analysis_type"],
        registry=REGISTRY,
    )

    models_discovered_total = Counter(
        "models_discovered_total",
        "Total process models discovered",
        ["miner_type"],
        registry=REGISTRY,
    )

    # =============================================================================
    # System Metrics
    # =============================================================================

    circuit_breaker_state = Gauge(
        "circuit_breaker_state",
        "Circuit breaker state (0=closed, 1=open, 2=half_open)",
        ["circuit"],
        registry=REGISTRY,
    )

    cache_hits_total = Counter(
        "cache_hits_total",
        "Total cache hits",
        ["cache_name"],
        registry=REGISTRY,
    )

    cache_misses_total = Counter(
        "cache_misses_total",
        "Total cache misses",
        ["cache_name"],
        registry=REGISTRY,
    )

    active_async_jobs = Gauge(
        "active_async_jobs",
        "Number of active async jobs",
        ["job_type"],
        registry=REGISTRY,
    )

    # =============================================================================
    # Application Info
    # =============================================================================

    app_info = Info(
        "app",
        "Application information",
        registry=REGISTRY,
    )


# =============================================================================
# Metric Recording Helpers
# =============================================================================


def record_http_request(
    method: str,
    endpoint: str,
    status: int,
    duration: float,
) -> None:
    """Record HTTP request metrics."""
    if not PROMETHEUS_AVAILABLE:
        return

    # Normalize endpoint for cardinality control
    normalized_endpoint = _normalize_endpoint(endpoint)

    http_requests_total.labels(
        method=method,
        endpoint=normalized_endpoint,
        status=str(status),
    ).inc()

    http_request_duration_seconds.labels(
        method=method,
        endpoint=normalized_endpoint,
    ).observe(duration)


def record_pm4py_operation(
    operation: str,
    miner_type: str,
    status: str,
    duration: float,
    events_count: int = 0,
) -> None:
    """Record PM4Py operation metrics."""
    if not PROMETHEUS_AVAILABLE:
        return

    pm4py_operations_total.labels(
        operation=operation,
        miner_type=miner_type,
        status=status,
    ).inc()

    pm4py_operation_duration_seconds.labels(
        operation=operation,
        miner_type=miner_type,
    ).observe(duration)

    if events_count > 0:
        pm4py_log_events_processed.labels(operation=operation).inc(events_count)


def record_process_created() -> None:
    """Record new process creation."""
    if not PROMETHEUS_AVAILABLE:
        return
    processes_created_total.inc()


def record_analysis_completed(analysis_type: str) -> None:
    """Record completed analysis."""
    if not PROMETHEUS_AVAILABLE:
        return
    analyses_completed_total.labels(analysis_type=analysis_type).inc()


def record_model_discovered(miner_type: str) -> None:
    """Record discovered model."""
    if not PROMETHEUS_AVAILABLE:
        return
    models_discovered_total.labels(miner_type=miner_type).inc()


def update_circuit_breaker_metric(circuit: str, state: str) -> None:
    """Update circuit breaker state metric."""
    if not PROMETHEUS_AVAILABLE:
        return
    state_value = {"closed": 0, "open": 1, "half_open": 2}.get(state, -1)
    circuit_breaker_state.labels(circuit=circuit).set(state_value)


def record_cache_hit(cache_name: str) -> None:
    """Record cache hit."""
    if not PROMETHEUS_AVAILABLE:
        return
    cache_hits_total.labels(cache_name=cache_name).inc()


def record_cache_miss(cache_name: str) -> None:
    """Record cache miss."""
    if not PROMETHEUS_AVAILABLE:
        return
    cache_misses_total.labels(cache_name=cache_name).inc()


def set_app_info(version: str, environment: str) -> None:
    """Set application info metric."""
    if not PROMETHEUS_AVAILABLE:
        return
    app_info.info(
        {
            "version": version,
            "environment": environment,
        }
    )


def _normalize_endpoint(endpoint: str) -> str:
    """Normalize endpoint path to reduce cardinality.

    Replaces UUIDs and numeric IDs with placeholders.
    """
    import re

    # Replace UUIDs
    endpoint = re.sub(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "{id}",
        endpoint,
        flags=re.IGNORECASE,
    )

    # Replace numeric IDs in paths
    return re.sub(r"/\d+(/|$)", "/{id}\\1", endpoint)


# =============================================================================
# Decorator for Instrumenting Functions
# =============================================================================


def instrument_pm4py(operation: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to instrument PM4Py operations with metrics.

    Usage:
        @instrument_pm4py("discover_dfg")
        def discover_dfg(log): ...
    """

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            miner_type = kwargs.get("miner_type", "unknown")
            if hasattr(miner_type, "value"):
                miner_type = miner_type.value

            start_time = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
                duration = time.perf_counter() - start_time
                record_pm4py_operation(operation, str(miner_type), "success", duration)
                return result
            except Exception:
                duration = time.perf_counter() - start_time
                record_pm4py_operation(operation, str(miner_type), "error", duration)
                raise

        return wrapper

    return decorator


# =============================================================================
# Metrics Endpoint
# =============================================================================


def get_metrics() -> bytes:
    """Generate Prometheus metrics in text format."""
    if not PROMETHEUS_AVAILABLE:
        return b"# Prometheus client not installed\n"
    return generate_latest(REGISTRY)
