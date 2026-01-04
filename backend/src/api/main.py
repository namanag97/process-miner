"""FastAPI Application - Main Entry Point.

Enterprise-grade setup with:
- RFC 7807 Problem Details error responses
- OpenTelemetry distributed tracing
- Prometheus metrics
- Comprehensive health checks
- CORS for React frontend
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers import (
    analyses_router,
    analytics_router,
    auth_router,
    conformance_router,
    datasets_router,
    dev_log_router,
    discovery_router,
    filtering_router,
    ocpm_router,
    organizational_router,
    predictions_router,
    projects_router,
    simulation_router,
    visualization_router,
    workflows_router,
    workspaces_router,
)
from src.api.routers.dev_logs_stream import router as dev_logs_stream_router
from src.api.routers.health import mark_startup_complete
from src.api.routers.health import router as health_router
from src.api.routers.jobs import router as jobs_router
from src.api.routers.telemetry_proxy import router as telemetry_proxy_router
from src.api.routers.telemetry_test import router as telemetry_test_router
from src.core.config import get_settings
from src.core.exceptions import AppException
from src.core.logging_config import configure_logging, get_logger
from src.core.middleware import PerformanceLoggingMiddleware, RequestLoggingMiddleware
from src.models.database import close_database, init_database

settings = get_settings()

# Configure logging before anything else
configure_logging()
logger = get_logger(__name__)


# =============================================================================
# Lifespan
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    await init_database()

    # Setup observability (optional dependencies)
    _setup_observability(app)

    # Mark startup complete for health checks
    mark_startup_complete()

    logger.info("application_ready")
    yield

    # Shutdown
    logger.info("application_shutting_down")
    await close_database()
    logger.info("application_stopped")


def _setup_observability(app: FastAPI) -> None:
    """Initialize optional observability components."""
    try:
        from src.infrastructure.metrics import set_app_info
        from src.infrastructure.tracing import setup_tracing

        # Setup OpenTelemetry tracing
        setup_tracing(
            app,
            service_name="process-mining-api",
            service_version=settings.app_version,
            environment="development" if settings.debug else "production",
            console_export=settings.debug,
            devconsole_export=settings.debug,  # Real-time trace visualization in DevConsole
        )

        # Set app info metric
        set_app_info(
            version=settings.app_version,
            environment="development" if settings.debug else "production",
        )

        logger.info("observability_initialized")
    except ImportError as e:
        logger.warning("observability_not_available", reason=str(e))
    except Exception as e:
        logger.warning("observability_setup_failed", error=str(e))


# =============================================================================
# App Factory
# =============================================================================


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    # OpenAPI tags for documentation organization
    openapi_tags = [
        {
            "name": "Health",
            "description": "Application health and readiness endpoints",
        },
        {
            "name": "Auth",
            "description": "Authentication and authorization (JWT-based)",
        },
        {
            "name": "Workspaces",
            "description": "Multi-tenant workspace management",
        },
        {
            "name": "Projects",
            "description": "Project organization for event logs and analyses",
        },
        {
            "name": "Datasets",
            "description": "Dataset upload, management, and statistics",
        },
        {
            "name": "Analyses",
            "description": "Stored analyses and results",
        },
        {
            "name": "Discovery",
            "description": "Process model discovery (Alpha, Inductive, Heuristics miners)",
        },
        {
            "name": "Visualization",
            "description": "DFG, Petri net, and BPMN visualization",
        },
        {
            "name": "Conformance",
            "description": "Conformance checking, fitness, precision, and deviation analysis",
        },
        {
            "name": "Analytics",
            "description": "Performance analytics, bottleneck detection, and KPIs",
        },
        {
            "name": "Filtering",
            "description": "Event log filtering and subsetting",
        },
        {
            "name": "Organizational",
            "description": "Organizational mining, social networks, and resource analysis",
        },
        {
            "name": "Predictions",
            "description": "ML-based predictions (next activity, remaining time)",
        },
        {
            "name": "Simulation",
            "description": "Process simulation and what-if analysis",
        },
        {
            "name": "OCPM",
            "description": "Object-Centric Process Mining (OCEL 2.0)",
        },
        {
            "name": "Workflows",
            "description": "Automation workflows and pipelines",
        },
        {
            "name": "Jobs",
            "description": "Unified async job tracking and progress monitoring",
        },
        {
            "name": "Observability",
            "description": "Metrics, tracing, and logging",
        },
    ]

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
# Process Mining SaaS API

Enterprise-grade process mining platform powered by PM4Py.

## Features

- **Event Log Management**: Upload CSV, XES, OCEL files with column auto-detection
- **Process Discovery**: Alpha, Inductive, Heuristics miners with quality metrics
- **Conformance Checking**: Token replay, alignments with deviation analysis
- **Performance Analytics**: Bottleneck detection, cycle time, throughput
- **Predictions**: ML-based next activity and remaining time predictions
- **OCEL Support**: Object-Centric Process Mining with OCEL 2.0

## Error Handling

All errors follow RFC 7807 Problem Details format with typed error codes.

## Authentication

JWT-based authentication with optional workspace context.
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=openapi_tags,
        lifespan=lifespan,
    )

    # CORS for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Trace-ID", "ETag", "Retry-After"],
    )

    # Logging middleware (order matters - performance first, then request logging)
    app.add_middleware(PerformanceLoggingMiddleware, slow_request_threshold_ms=1000)
    app.add_middleware(RequestLoggingMiddleware)

    # Exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle application exceptions with RFC 7807 Problem Details format."""
        # Add correlation ID from exception or request context
        correlation_id = exc.correlation_id
        if not correlation_id:
            correlation_id = request.headers.get("X-Request-ID")

        logger.warning(
            "application_exception",
            exception_type=type(exc).__name__,
            error_code=exc.error_code.value if hasattr(exc, "error_code") else None,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url.path),
            correlation_id=correlation_id,
        )

        # Build RFC 7807 response
        content = (
            exc.to_dict()
            if hasattr(exc, "to_dict")
            else {
                "type": "error",
                "title": type(exc).__name__,
                "status": exc.status_code,
                "detail": exc.message,
                "instance": str(request.url),
                **exc.details,
            }
        )
        content["instance"] = str(request.url)

        # Build response with appropriate headers
        headers = {}
        if correlation_id:
            headers["X-Request-ID"] = correlation_id
        if exc.retry_after:
            headers["Retry-After"] = str(exc.retry_after)

        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=headers if headers else None,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler for unhandled errors.

        Ensures CORS headers are returned even for 500 errors.
        Follows RFC 7807 Problem Details format.
        """
        correlation_id = request.headers.get("X-Request-ID")

        logger.error(
            "unhandled_exception",
            exception_type=type(exc).__name__,
            message=str(exc),
            path=str(request.url.path),
            correlation_id=correlation_id,
            exc_info=True,
        )

        content = {
            "type": "https://api.processmining.io/errors/ERR_500",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
            "error_code": "ERR_500",
            "instance": str(request.url),
            "timestamp": datetime.utcnow().isoformat(),
        }

        if correlation_id:
            content["correlation_id"] = correlation_id

        return JSONResponse(
            status_code=500,
            content=content,
            headers={"X-Request-ID": correlation_id} if correlation_id else None,
        )

    # Metrics endpoint
    @app.get("/metrics", tags=["Observability"], include_in_schema=False)
    async def prometheus_metrics() -> Response:
        """Prometheus metrics endpoint."""
        try:
            from src.infrastructure.metrics import get_metrics

            return Response(
                content=get_metrics(),
                media_type="text/plain; charset=utf-8",
            )
        except ImportError:
            return Response(
                content=b"# Prometheus client not installed\n",
                media_type="text/plain; charset=utf-8",
            )

    # Root endpoint
    @app.get("/", tags=["Health"])
    async def root() -> dict[str, Any]:
        """Root endpoint with API info."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
        }

    # Include health router (replaces inline /health endpoint)
    app.include_router(health_router)

    # Include API routers with prefix
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(workspaces_router, prefix=settings.api_prefix)
    app.include_router(projects_router, prefix=settings.api_prefix)
    app.include_router(datasets_router, prefix=settings.api_prefix)
    app.include_router(analyses_router, prefix=settings.api_prefix)
    app.include_router(discovery_router, prefix=settings.api_prefix)
    app.include_router(visualization_router, prefix=settings.api_prefix)
    app.include_router(conformance_router, prefix=settings.api_prefix)
    app.include_router(ocpm_router, prefix=settings.api_prefix)
    app.include_router(workflows_router, prefix=settings.api_prefix)
    app.include_router(filtering_router, prefix=settings.api_prefix)
    app.include_router(analytics_router, prefix=settings.api_prefix)
    app.include_router(organizational_router, prefix=settings.api_prefix)
    app.include_router(predictions_router, prefix=settings.api_prefix)
    app.include_router(simulation_router, prefix=settings.api_prefix)
    app.include_router(jobs_router, prefix=settings.api_prefix)  # Job-Centric Architecture
    app.include_router(dev_log_router, prefix=settings.api_prefix)
    app.include_router(dev_logs_stream_router, prefix=settings.api_prefix)
    app.include_router(telemetry_proxy_router, prefix=settings.api_prefix)
    app.include_router(jobs_router, prefix=settings.api_prefix)

    # Test endpoint for telemetry (debug mode only)
    if settings.debug:
        app.include_router(telemetry_test_router, prefix=settings.api_prefix)

    return app


# =============================================================================
# Application Instance
# =============================================================================

app = create_app()


# =============================================================================
# Development Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
