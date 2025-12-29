"""Metrics and health check endpoints for observability."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.observability import get_metrics_response
from src.infrastructure.persistence.database import get_session

router = APIRouter(tags=["Observability"])


@router.get("/metrics", include_in_schema=False)
async def prometheus_metrics():
    """Prometheus metrics endpoint.

    Returns metrics in Prometheus exposition format for scraping.
    """
    content, content_type = get_metrics_response()
    return Response(content=content, media_type=content_type)


@router.get("/health/live", tags=["Health"])
async def liveness_probe():
    """Kubernetes liveness probe.

    Returns 200 if the application is running.
    Used by orchestrators to determine if the container should be restarted.
    """
    return {"status": "alive", "checks": {"application": "running"}}


@router.get("/health/ready", tags=["Health"])
async def readiness_probe(session: AsyncSession = Depends(get_session)):
    """Kubernetes readiness probe.

    Returns 200 if the application is ready to accept traffic.
    Checks database connectivity and other dependencies.
    """
    checks = {}
    ready = True

    # Check database connectivity
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        ready = False

    status_code = 200 if ready else 503

    return Response(
        content=str({"status": "ready" if ready else "not_ready", "checks": checks}),
        status_code=status_code,
        media_type="application/json",
    )


@router.get("/health/detailed", tags=["Health"])
async def detailed_health(session: AsyncSession = Depends(get_session)):
    """Detailed health check with component status.

    Provides comprehensive health information for monitoring dashboards.
    """
    from sqlalchemy import func, select

    from src.config import get_settings
    from src.infrastructure.persistence.models import EventLogModel, ProcessModelModel

    settings = get_settings()

    # Get counts for business metrics
    try:
        log_count = await session.scalar(select(func.count(EventLogModel.id)))
        model_count = await session.scalar(select(func.count(ProcessModelModel.id)))
    except Exception:
        log_count = 0
        model_count = 0

    return {
        "status": "healthy",
        "version": settings.app_version,
        "components": {
            "database": {
                "status": "up",
                "type": "sqlite",
            },
            "auth": {
                "status": "up" if settings.auth_enabled else "disabled",
            },
        },
        "metrics": {
            "event_logs": log_count,
            "process_models": model_count,
        },
    }
