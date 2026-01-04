"""Health check endpoints for Kubernetes and monitoring.

Provides structured health checks following best practices:
- /health/live: Liveness probe (is the process alive?)
- /health/ready: Readiness probe (can we serve traffic?)
- /health/startup: Startup probe (is initialization complete?)
- /health/detailed: Full component status (for dashboards)

Usage:
    from src.api.routers.health import router as health_router
    app.include_router(health_router)
"""

import asyncio
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field

from src.core.config import get_settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/health", tags=["Health"])


# =============================================================================
# Response Models
# =============================================================================


class HealthStatus(BaseModel):
    """Basic health status response."""

    status: str = Field(..., examples=["healthy", "degraded", "unhealthy"])
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ComponentHealth(BaseModel):
    """Health status for a single component."""

    name: str
    status: str  # healthy, degraded, unhealthy
    latency_ms: float | None = None
    message: str | None = None
    details: dict[str, Any] | None = None


class DetailedHealthResponse(BaseModel):
    """Detailed health response with component breakdown."""

    status: str
    version: str
    uptime_seconds: float
    timestamp: datetime
    components: list[ComponentHealth]


# =============================================================================
# Startup Time Tracking
# =============================================================================

_startup_time: float | None = None
_startup_complete: bool = False


def mark_startup_complete() -> None:
    """Mark application startup as complete."""
    global _startup_time, _startup_complete
    _startup_time = time.monotonic()
    _startup_complete = True
    logger.info("health_startup_complete")


def get_uptime() -> float:
    """Get application uptime in seconds."""
    if _startup_time is None:
        return 0.0
    return time.monotonic() - _startup_time


# =============================================================================
# Health Check Functions
# =============================================================================


async def check_database() -> ComponentHealth:
    """Check database connectivity."""
    from sqlalchemy import text

    from src.models.database import async_engine

    start = time.perf_counter()
    try:
        # Simple connectivity check
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        latency = (time.perf_counter() - start) * 1000
        return ComponentHealth(
            name="database",
            status="healthy",
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return ComponentHealth(
            name="database",
            status="unhealthy",
            latency_ms=round(latency, 2),
            message=str(e),
        )


async def check_cache() -> ComponentHealth:
    """Check cache connectivity."""
    try:
        from src.infrastructure.cache import cache_service

        start = time.perf_counter()
        # Try to get a non-existent key (should return None quickly)
        cache_service.get("__health_check__")
        latency = (time.perf_counter() - start) * 1000

        return ComponentHealth(
            name="cache",
            status="healthy",
            latency_ms=round(latency, 2),
            details={"type": "in-memory"},
        )
    except Exception as e:
        return ComponentHealth(
            name="cache",
            status="degraded",  # Cache is optional
            message=str(e),
        )


async def check_pm4py() -> ComponentHealth:
    """Check PM4Py availability."""
    start = time.perf_counter()
    try:
        import pm4py

        version = pm4py.__version__
        latency = (time.perf_counter() - start) * 1000

        return ComponentHealth(
            name="pm4py",
            status="healthy",
            latency_ms=round(latency, 2),
            details={"version": version},
        )
    except Exception as e:
        return ComponentHealth(
            name="pm4py",
            status="unhealthy",
            message=str(e),
        )


async def check_circuit_breakers() -> ComponentHealth:
    """Check circuit breaker states."""
    try:
        from src.infrastructure.circuit_breaker import get_all_circuit_statuses

        statuses = get_all_circuit_statuses()
        open_circuits = [s for s in statuses if s["state"] == "open"]

        if open_circuits:
            return ComponentHealth(
                name="circuit_breakers",
                status="degraded",
                message=f"{len(open_circuits)} circuit(s) open",
                details={"circuits": statuses},
            )

        return ComponentHealth(
            name="circuit_breakers",
            status="healthy",
            details={"circuits": statuses},
        )
    except Exception:
        return ComponentHealth(
            name="circuit_breakers",
            status="healthy",  # If not configured, that's fine
            message="Not configured",
        )


async def check_disk_space() -> ComponentHealth:
    """Check available disk space."""
    import shutil

    try:
        usage = shutil.disk_usage(settings.upload_dir)
        free_gb = usage.free / (1024**3)
        total_gb = usage.total / (1024**3)
        used_percent = (usage.used / usage.total) * 100

        status = "healthy"
        if used_percent > 90:
            status = "unhealthy"
        elif used_percent > 80:
            status = "degraded"

        return ComponentHealth(
            name="disk",
            status=status,
            details={
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_percent": round(used_percent, 1),
            },
        )
    except Exception as e:
        return ComponentHealth(
            name="disk",
            status="unhealthy",
            message=str(e),
        )


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/live", response_model=HealthStatus)
async def liveness_probe() -> HealthStatus:
    """Kubernetes liveness probe.

    Returns 200 if the process is alive and responding.
    Used by Kubernetes to restart unhealthy pods.
    """
    return HealthStatus(status="healthy")


@router.get("/ready", response_model=HealthStatus)
async def readiness_probe(response: Response) -> HealthStatus:
    """Kubernetes readiness probe.

    Returns 200 if the service can handle traffic.
    Checks critical dependencies (database).
    """
    db_health = await check_database()

    if db_health.status == "unhealthy":
        response.status_code = 503
        return HealthStatus(status="unhealthy")

    return HealthStatus(status="healthy")


@router.get("/startup", response_model=HealthStatus)
async def startup_probe(response: Response) -> HealthStatus:
    """Kubernetes startup probe.

    Returns 200 once the application has completed initialization.
    Used to prevent premature health checks during slow startups.
    """
    if not _startup_complete:
        response.status_code = 503
        return HealthStatus(status="starting")

    return HealthStatus(status="healthy")


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health() -> DetailedHealthResponse:
    """Detailed health status for monitoring dashboards.

    Returns comprehensive status of all components with timing info.
    """
    # Run all health checks concurrently
    components = await asyncio.gather(
        check_database(),
        check_cache(),
        check_pm4py(),
        check_circuit_breakers(),
        check_disk_space(),
    )

    # Determine overall status
    statuses = [c.status for c in components]
    if "unhealthy" in statuses:
        overall = "unhealthy"
    elif "degraded" in statuses:
        overall = "degraded"
    else:
        overall = "healthy"

    return DetailedHealthResponse(
        status=overall,
        version=settings.app_version,
        uptime_seconds=round(get_uptime(), 2),
        timestamp=datetime.utcnow(),
        components=list(components),
    )


@router.get("", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """Basic health check endpoint.

    Quick check that the service is responding.
    Use /health/detailed for component-level status.
    """
    return HealthStatus(status="healthy")


# =============================================================================
# Metrics Endpoint (Phase 7 - Observability)
# =============================================================================


@router.get("/metrics")
async def prometheus_metrics() -> Response:
    """Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    Compatible with Prometheus, Grafana Cloud, Datadog, etc.

    Metrics include:
    - HTTP request latency and throughput
    - PM4Py operation performance
    - Business metrics (processes, analyses)
    - Circuit breaker states
    - Cache hit/miss rates
    """
    try:
        from src.infrastructure.metrics import get_metrics

        metrics_data = get_metrics()
        return Response(content=metrics_data, media_type="text/plain; version=0.0.4")
    except ImportError:
        # Prometheus client not installed
        return Response(
            content="# Prometheus client not installed\n# Install with: pip install prometheus-client\n",
            media_type="text/plain",
        )
