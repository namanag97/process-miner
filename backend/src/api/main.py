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
    business_use_cases_router,
    conformance_router,
    datasets_router,
    dev_log_router,
    discovery_router,
    filtering_router,
    health_router,
    jobs_router,
    ocpm_router,
    organizational_router,
    predictions_router,
    projects_router,
    simulation_router,
    visualization_router,
    workflows_router,
    workspaces_router,
)
from src.platform.admin.router import router as admin_router
from src.platform.organizations.router import router as organizations_router
from src.platform.devconsole.streaming import router as dev_logs_stream_router
from src.platform.devtools.dev_data import router as dev_data_router
from src.platform.health.router import mark_startup_complete
from src.platform.infrastructure.database import close_database, init_database
from src.platform.core.config import get_settings
from src.platform.core.exceptions import AppException
from src.platform.core.logging_config import configure_logging, get_logger
from src.platform.core.middleware import PerformanceLoggingMiddleware, RequestLoggingMiddleware

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

    # Seed MVP data (org, workspace, user) for development
    await _seed_mvp_data()

    # Connect log broker for DevConsole
    if settings.debug:
        from src.platform.devconsole.broker import startup_log_broker
        await startup_log_broker()

    # Mark startup complete for health checks
    mark_startup_complete()

    logger.info("application_ready")
    yield

    # Shutdown
    logger.info("application_shutting_down")
    await close_database()

    # Disconnect log broker
    if settings.debug:
        from src.platform.devconsole.broker import shutdown_log_broker
        await shutdown_log_broker()

    logger.info("application_stopped")


async def _seed_mvp_data() -> None:
    """Seed MVP development data if not exists.

    Creates:
    - mvp-org-001: Demo Organization
    - mvp-ws-001: Default Workspace
    - mvp-user-001: Process Analyst user

    This ensures the frontend's hardcoded IDs work out of the box.
    """
    from sqlalchemy import select

    from src.platform.infrastructure.database import async_session_maker
    from src.platform.models import Organization, User, Workspace, WorkspaceMember

    try:
        async with async_session_maker() as db:
            # Check if MVP org already exists
            result = await db.execute(select(Organization).where(Organization.id == "mvp-org-001"))
            if result.scalar_one_or_none():
                logger.debug("mvp_seed_data_exists", msg="Skipping seeding")
                return

            # Create organization
            org = Organization(
                id="mvp-org-001",
                name="Demo Organization",
                slug="demo-org",
                plan="free",
            )
            db.add(org)

            # Create workspace
            workspace = Workspace(
                id="mvp-ws-001",
                org_id="mvp-org-001",
                name="Default Workspace",
                description="Your default process mining workspace",
            )
            db.add(workspace)

            # Create user
            user = User(
                id="mvp-user-001",
                org_id="mvp-org-001",
                email="analyst@company.local",
                name="Process Analyst",
                role="admin",
            )
            db.add(user)

            # Add user to workspace as owner
            membership = WorkspaceMember(
                workspace_id="mvp-ws-001",
                user_id="mvp-user-001",
                role="owner",
            )
            db.add(membership)

            await db.commit()
            logger.info(
                "mvp_seed_data_created",
                org_id="mvp-org-001",
                workspace_id="mvp-ws-001",
                user_id="mvp-user-001",
            )

    except Exception as e:
        logger.warning("mvp_seed_data_failed", error=str(e))




# =============================================================================
# App Factory
# =============================================================================


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    # OpenAPI tags for documentation organization
    openapi_tags = [
        # =====================================================================
        # Platform Layer
        # =====================================================================
        {
            "name": "Auth",
            "description": "🔐 Authentication and authorization. Uses JWT (Access & Refresh Tokens).",
        },
        {
            "name": "Organizations",
            "description": "🏛️ Organization management. Multi-tenant org structure and billing.",
        },
        {
            "name": "Workspaces",
            "description": "🏢 Multi-tenant workspace management. Create, update, and manage workspaces.",
        },
        {
            "name": "Projects",
            "description": "📁 Project organization for event logs and analyses.",
        },
        {
            "name": "Jobs",
            "description": "⚡ Unified async job tracking and progress monitoring.",
        },
        {
            "name": "Admin",
            "description": "🛡️ Admin-only system management and monitoring.",
        },
        {
            "name": "Health",
            "description": "❤️ Application health and readiness endpoints for k8s/monitoring.",
        },
        {
            "name": "Observability",
            "description": "📊 Metrics, tracing, and logging endpoints.",
        },
        # =====================================================================
        # Process Mining Domain - Core
        # =====================================================================
        {
            "name": "Datasets",
            "description": "💾 Event log management. Upload, ingest, and manage CSV/XES/OCEL files.",
        },
        {
            "name": "Discovery",
            "description": "🔍 Process model discovery. Alpha, Inductive, Heuristics miners.",
        },
        {
            "name": "Conformance",
            "description": "✅ Conformance checking. Token replay, alignments, and deviation analysis.",
        },
        {
            "name": "Visualization",
            "description": "🎨 Process visualization. DFG, Petri nets, and BPMN layouts.",
        },
        # =====================================================================
        # Process Mining Domain - Advanced
        # =====================================================================
        {
            "name": "Analyses",
            "description": "📋 Stored analyses and results management.",
        },
        {
            "name": "Analytics",
            "description": "📈 Performance analytics. Bottlenecks, cycle times, and throughput.",
        },
        {
            "name": "Predictions",
            "description": "🔮 ML-based predictions. Next activity and remaining time estimation.",
        },
        {
            "name": "Simulation",
            "description": "🎲 Process simulation and what-if analysis.",
        },
        {
            "name": "Filtering",
            "description": "🔍 Event log filtering and subsetting.",
        },
        {
            "name": "Organizational",
            "description": "👥 Organizational mining. Social networks and resource analysis.",
        },
        {
            "name": "OCPM",
            "description": "📦 Object-Centric Process Mining (OCEL 2.0).",
        },
        {
            "name": "Business Use Cases",
            "description": "💼 Specific business scenarios (P2P, O2C, Customer Journey).",
        },
    ]

    description = """
# Process Mining SaaS API

Welcome to the **Process Mining SaaS API**. This API provides enterprise-grade process mining capabilities, allowing you to discover, analyze, and optimize business processes from event logs.

## 🚀 Key Features

*   **Event Log Management**: Upload and process CSV, XES, and OCEL files with automatic schema detection.
*   **Process Discovery**: Automatically generate process models (Petri nets, BPMN, DFG) using state-of-the-art algorithms (Alpha, Inductive, Heuristics).
*   **Conformance Checking**: Compare actual process execution against reference models to identify deviations and root causes.
*   **Performance Analytics**: Deep dive into bottlenecks, cycle times, and throughput efficiency.
*   **Predictive Process Monitoring**: Leverage Machine Learning to predict next activities and remaining process time.
*   **Object-Centric Process Mining (OCPM)**: Native support for OCEL 2.0 to analyze complex, multi-object processes.

## 🔐 Authentication

This API uses **JWT (JSON Web Token)** for authentication.

1.  **Register/Login**: Use `/api/v1/auth/login` to obtain an `access_token` and `refresh_token`.
2.  **Authorize**: Click the **Authorize** button at the top right and enter your token (Bearer format is handled automatically by the UI, just enter the token string if prompted, or follows the Scheme).
    *   *Note: For this specific Swagger UI, standard Bearer auth is configured.*

## 📦 Rate Limiting

API requests are rate-limited to ensure stability.
*   **Standard**: 100 requests/minute
*   **Uploads**: 10 requests/minute

Headers returned:
*   `X-RateLimit-Limit`
*   `X-RateLimit-Remaining`
*   `X-RateLimit-Reset`

## 🆘 Support

For support, please contact the developer team or refer to the internal documentation.
"""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=description,
        contact={
            "name": "Process Mining Platform Team",
            "url": "https://processmining.io/support",
            "email": "support@processmining.io",
        },
        license_info={
            "name": "Proprietary",
            "url": "https://processmining.io/license",
        },
        terms_of_service="https://processmining.io/terms",
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

    # Rate limiting (prevents abuse and DDoS)
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    from src.platform.core.rate_limit import limiter

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # Exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle application exceptions with RFC 7807 Problem Details format."""
        # Add correlation ID from exception or request context
        correlation_id = exc.correlation_id
        if not correlation_id:
            correlation_id = request.headers.get("X-Request-ID")

        logger.warning(
            "⚠️ [APP EXCEPTION] Application exception caught",
            exception_type=type(exc).__name__,
            exception_module=type(exc).__module__,
            error_code=exc.error_code.value if hasattr(exc, "error_code") else None,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url.path),
            method=request.method,
            client_host=request.client.host if request.client else None,
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

        # Enhanced logging for debugging
        logger.error(
            "🔥 [GLOBAL EXCEPTION] Unhandled exception caught",
            exception_type=type(exc).__name__,
            exception_module=type(exc).__module__,
            message=str(exc),
            path=str(request.url.path),
            method=request.method,
            correlation_id=correlation_id,
            client_host=request.client.host if request.client else None,
            headers=dict(request.headers),
            query_params=dict(request.query_params),
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


    # Root endpoint
    @app.get("/", tags=["Health"])
    async def root() -> dict[str, Any]:
        """Root endpoint with API info."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    # Include health router (replaces inline /health endpoint)
    app.include_router(health_router)

    # Include API routers with prefix
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(organizations_router, prefix=settings.api_prefix)  # New: Organizations
    app.include_router(admin_router, prefix=settings.api_prefix)  # New: Admin
    app.include_router(workspaces_router, prefix=settings.api_prefix)
    app.include_router(projects_router, prefix=settings.api_prefix)
    app.include_router(datasets_router, prefix=settings.api_prefix)
    app.include_router(analyses_router, prefix=settings.api_prefix)
    app.include_router(discovery_router, prefix=settings.api_prefix)
    app.include_router(visualization_router, prefix=settings.api_prefix)
    app.include_router(conformance_router, prefix=settings.api_prefix)
    app.include_router(business_use_cases_router, prefix=settings.api_prefix)  # Phase 9
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
    app.include_router(dev_data_router, prefix=settings.api_prefix)

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
