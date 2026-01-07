"""FastAPI Application - Main Entry Point.

Enterprise-grade setup with:
- RFC 7807 Problem Details error responses
- OpenTelemetry distributed tracing
- Prometheus metrics
- Comprehensive health checks
- CORS for React frontend
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers import (
    ai_router,
    algorithms_router,
    analyses_router,
    analytics_router,
    auth_router,
    business_use_cases_router,
    conformance_router,
    # dags_router,  # Removed - use Temporal workflows via /operations API
    datasets_router,
    dev_log_router,
    discovery_router,
    filtering_router,
    health_router,
    jobs_router,
    ocpm_router,
    operations_router,  # Unified Temporal operations API
    organizational_router,
    organizations_router,
    predictions_router,
    projects_router,
    quality_metrics_router,
    simulation_router,
    # telemetry_router,  # TODO: Create telemetry router
    visualization_router,
    workflows_api_router,
    workflows_router,
    workspaces_router,
)
from src.infra.audit.router import router as audit_router
from src.infra.core.api_logging import APILoggingMiddleware
from src.infra.core.config import get_settings
from src.infra.core.exceptions import AppException
from src.infra.core.logging_config import configure_logging, get_logger
from src.infra.core.middleware import PerformanceLoggingMiddleware, RequestLoggingMiddleware
from src.infra.devconsole.streaming import router as dev_logs_stream_router
from src.infra.devtools.dev_data import router as dev_data_router
from src.infra.health.router import mark_startup_complete
from src.infra.infrastructure.database import close_database, init_database

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

    # Initialize CQRS infrastructure
    from src.application.bootstrap import init_cqrs
    await init_cqrs()

    # Seed MVP data (org, workspace, user) for development
    await _seed_mvp_data()

    # Connect log broker for DevConsole
    if settings.debug:
        from src.infra.devconsole.broker import startup_log_broker

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
        from src.infra.devconsole.broker import shutdown_log_broker

        await shutdown_log_broker()

    logger.info("application_stopped")


async def _seed_mvp_data() -> None:
    """Seed MVP development data if not exists.

    Creates:
    - mvp-org-001: Demo Organization
    - mvp-ws-001: Default Workspace
    - mvp-proj-001: Default Project
    - mvp-user-001: Process Analyst user

    This ensures the frontend's hardcoded IDs work out of the box.
    """
    from sqlalchemy import select

    from src.infra.core.security import hash_password
    from src.infra.infrastructure.database import write_session_maker
    from src.infra.users import Organization, Project, User, Workspace, WorkspaceMember

    try:
        async with write_session_maker() as db:
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

            # Create default project
            project = Project(
                id="mvp-proj-001",
                workspace_id="mvp-ws-001",
                name="Default Project",
                description="Your default process mining project",
            )
            db.add(project)

            # Create user with password for testing
            # Password: TestPass123 (simple, no special chars for shell compat)
            user = User(
                id="mvp-user-001",
                org_id="mvp-org-001",
                email="analyst@example.com",
                name="Process Analyst",
                role="admin",
                password_hash=hash_password("TestPass123"),
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
                project_id="mvp-proj-001",
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
        # Getting Started (First)
        # =====================================================================
        {
            "name": "Health",
            "description": "Health checks for k8s probes. `/health/live` for liveness, `/health/ready` for readiness.",
        },
        {
            "name": "Auth",
            "description": """**Start here!** JWT authentication.

**Quick Login:**
```
POST /auth/login
{"email": "analyst@example.com", "password": "TestPass123"}
```
Returns `access_token` for Bearer auth.""",
        },
        # =====================================================================
        # Platform - Multi-Tenant Structure
        # =====================================================================
        {
            "name": "Organizations",
            "description": "Multi-tenant orgs. Users belong to one org.",
        },
        {
            "name": "Workspaces",
            "description": "Collaborative containers within orgs. Supports RBAC (owner/admin/editor/viewer).",
        },
        {
            "name": "Projects",
            "description": "Group datasets and analyses. Use `mvp-proj-001` for dev.",
        },
        # =====================================================================
        # Core Flow: Datasets
        # =====================================================================
        {
            "name": "Datasets",
            "description": """**Main user flow starts here.**

**Upload Flow:**
1. `POST /presign` → get S3 URL
2. `PUT <url>` → upload file
3. `POST /{id}/uploaded` → confirm
4. `GET /{id}/columns` → see detected columns
5. `POST /{id}/mapping` → set case_id, activity, timestamp
6. `POST /{id}/ingest` → start processing

**Status progression:** PENDING → UPLOADED → MAPPED → INGESTING → READY""",
        },
        # =====================================================================
        # Core Flow: Discovery
        # =====================================================================
        {
            "name": "Discovery",
            "description": """Discover process models from event logs.

**Miners:** `alpha`, `inductive`, `heuristic`, `split`

**Usage:**
1. `GET /miners` → list algorithms
2. `POST /discover` → start (returns workflow_id)
3. `GET /models` → view results""",
        },
        # =====================================================================
        # Core Flow: Analytics
        # =====================================================================
        {
            "name": "Analytics",
            "description": """Performance analysis of process data.

**Key endpoints:**
- `/bottlenecks` - Identify slow activities
- `/cycle-time` - Duration distribution
- `/throughput` - Volume trends
- `/rework` - Rework patterns
- `/service-times` - Per-activity timing""",
        },
        # =====================================================================
        # Core Flow: Conformance
        # =====================================================================
        {
            "name": "Conformance",
            "description": """Compare actual execution vs expected model.

**Methods:** `token_replay`, `alignments`, `footprints`

**Usage:**
1. `POST /check` → run conformance
2. `GET /deviations/{ds}/{model}` → view issues
3. `GET /alignments/{ds}/{model}` → case details""",
        },
        # =====================================================================
        # Visualization
        # =====================================================================
        {
            "name": "Visualization",
            "description": """Graph data for rendering.

**Endpoints:**
- `/{id}/dfg` - Directly-Follows Graph (JSON)
- `/{id}/dfg/svg` - DFG as SVG image
- `/models/{id}/petri` - Petri net structure
- `/{id}/explorer-data` - Variant explorer data""",
        },
        # =====================================================================
        # Real-Time Operations
        # =====================================================================
        {
            "name": "Operations",
            "description": """**Real-time progress tracking (SSE).**

Long operations return `workflow_id`. Subscribe:
```javascript
new EventSource('/api/v1/operations/{id}/stream')
```

**Events:** `step:progress`, `workflow:completed`, `workflow:failed`""",
        },
        {
            "name": "Jobs",
            "description": "Async job tracking. Alternative to SSE for polling.",
        },
        # =====================================================================
        # Advanced Features
        # =====================================================================
        {
            "name": "AI",
            "description": "AI chat assistant for process insights.",
        },
        {
            "name": "Analyses",
            "description": "Save and retrieve analysis results.",
        },
        {
            "name": "Predictions",
            "description": "ML predictions: next activity, remaining time.",
        },
        {
            "name": "Simulation",
            "description": "What-if analysis and process simulation.",
        },
        {
            "name": "Filtering",
            "description": "Filter event logs by criteria.",
        },
        {
            "name": "Organizational",
            "description": "Resource analysis and social networks.",
        },
        {
            "name": "OCPM",
            "description": "Object-Centric Process Mining (OCEL 2.0).",
        },
        {
            "name": "Business Use Cases",
            "description": "P2P, O2C, Customer Journey templates.",
        },
    ]

    description = """
# Process Mining SaaS API

Enterprise-grade process mining platform for discovering, analyzing, and optimizing business processes.

---

## 🧪 Quick Start (Dev Credentials)

```
Email:    analyst@example.com
Password: TestPass123
```

Pre-seeded IDs: `mvp-org-001`, `mvp-ws-001`, `mvp-proj-001`, `mvp-user-001`

---

## 🔐 Authentication

1. **Login**: `POST /api/v1/auth/login` → Returns `access_token`
2. **Use Token**: Click **Authorize** button (top-right) → Enter token
3. **Refresh**: `POST /api/v1/auth/refresh` when token expires

---

## 📊 User Flows

### Flow 1: Upload Dataset → Analyze

```
1. POST /datasets/presign        → Get S3 upload URL
2. PUT  <upload_url>             → Upload file to S3
3. POST /datasets/{id}/uploaded  → Confirm upload, get detected columns
4. POST /datasets/{id}/mapping   → Map columns (case_id, activity, timestamp)
5. POST /datasets/{id}/ingest    → Start ingestion (returns workflow_id)
6. GET  /operations/{workflow_id}/stream → SSE progress (real-time)
7. GET  /datasets/{id}/statistics → View dataset stats when READY
```

### Flow 2: Discover Process Model

```
1. GET  /discovery/miners           → List available algorithms
2. POST /discovery/discover         → Start discovery (returns workflow_id)
3. GET  /operations/{workflow_id}/stream → SSE progress
4. GET  /discovery/models           → List discovered models
5. GET  /visualization/{id}/dfg     → Get DFG graph data
```

### Flow 3: Analyze Performance

```
1. GET /analytics/datasets/{id}/bottlenecks   → Identify slow activities
2. GET /analytics/datasets/{id}/cycle-time    → Duration analysis
3. GET /analytics/datasets/{id}/throughput    → Volume trends
4. GET /analytics/datasets/{id}/rework        → Rework patterns
```

### Flow 4: Check Conformance

```
1. GET  /conformance/methods                      → List methods
2. POST /conformance/check                        → Run check
3. GET  /conformance/deviations/{dataset}/{model} → View deviations
4. GET  /conformance/alignments/{dataset}/{model} → Case alignments
```

---

## 📡 Real-Time Progress (SSE)

Long operations (ingestion, discovery) return a `workflow_id`. Subscribe to progress:

```javascript
const es = new EventSource('/api/v1/operations/{workflow_id}/stream');
es.addEventListener('step:progress', e => console.log(JSON.parse(e.data)));
es.addEventListener('workflow:completed', e => { console.log('Done!'); es.close(); });
```

**Events**: `workflow:progress`, `step:started`, `step:progress`, `step:completed`, `workflow:completed`, `workflow:failed`

---

## ⚠️ Error Format (RFC 7807)

```json
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Dataset with id 'xyz' not found",
  "error_code": "RESOURCE_NOT_FOUND",
  "correlation_id": "req-abc123"
}
```

**Common Codes**: `VALIDATION_ERROR` (400), `INVALID_CREDENTIALS` (401), `TOKEN_EXPIRED` (401), `PERMISSION_DENIED` (403), `RESOURCE_NOT_FOUND` (404)

---

## 📦 Rate Limits

| Type | Limit |
|------|-------|
| Standard | 100 req/min |
| Uploads | 10 req/min |

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
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
        expose_headers=[
            "X-Request-ID",
            "X-Trace-ID",
            "X-Correlation-ID",
            "X-Request-Duration-Ms",
            "ETag",
            "Retry-After",
        ],
    )

    # Logging middleware (order matters - API logging first, then performance, then request)
    # APILoggingMiddleware: Comprehensive request/response logging with correlation IDs
    app.add_middleware(APILoggingMiddleware)
    app.add_middleware(PerformanceLoggingMiddleware, slow_request_threshold_ms=1000)
    app.add_middleware(RequestLoggingMiddleware)

    # Rate limiting (prevents abuse and DDoS)
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    from src.infra.core.rate_limit import limiter

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
            "timestamp": datetime.now(timezone.utc).isoformat(),
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

    # =========================================================================
    # Admin Domain Routers
    # =========================================================================
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(organizations_router, prefix=settings.api_prefix)
    app.include_router(workspaces_router, prefix=settings.api_prefix)
    app.include_router(projects_router, prefix=settings.api_prefix)

    # =========================================================================
    # Datasets Domain Routers
    # =========================================================================
    app.include_router(datasets_router, prefix=settings.api_prefix)

    # =========================================================================
    # Analysis Domain Routers
    # =========================================================================
    app.include_router(ai_router, prefix=settings.api_prefix)  # AI Chat
    app.include_router(analyses_router, prefix=settings.api_prefix)
    app.include_router(discovery_router, prefix=settings.api_prefix)
    app.include_router(conformance_router, prefix=settings.api_prefix)
    app.include_router(analytics_router, prefix=settings.api_prefix)
    app.include_router(visualization_router, prefix=settings.api_prefix)
    app.include_router(predictions_router, prefix=settings.api_prefix)
    app.include_router(filtering_router, prefix=settings.api_prefix)
    app.include_router(organizational_router, prefix=settings.api_prefix)
    app.include_router(simulation_router, prefix=settings.api_prefix)
    app.include_router(ocpm_router, prefix=settings.api_prefix)
    app.include_router(business_use_cases_router, prefix=settings.api_prefix)
    app.include_router(workflows_router, prefix=settings.api_prefix)
    app.include_router(algorithms_router, prefix=settings.api_prefix)  # Algorithm registry
    app.include_router(quality_metrics_router, prefix=settings.api_prefix)  # Quality metrics

    # =========================================================================
    # Platform Infrastructure Routers
    # =========================================================================
    app.include_router(jobs_router, prefix=settings.api_prefix)
    app.include_router(
        operations_router, prefix=settings.api_prefix
    )  # Unified Temporal operations (v2) - replaces DAG system
    app.include_router(workflows_api_router, prefix=settings.api_prefix)  # Temporal workflow status
    # DAG router removed - use operations_router for Temporal workflows
    app.include_router(audit_router, prefix=settings.api_prefix)

    # Dev/Debug endpoints - ONLY in development/staging (NOT production)
    if settings.environment.lower() in ["development", "staging"]:
        logger.warning(
            "dev_endpoints_enabled",
            environment=settings.environment,
            message="Dev/debug endpoints are ENABLED. These should be disabled in production!",
        )
        app.include_router(dev_log_router, prefix=settings.api_prefix)
        app.include_router(dev_logs_stream_router, prefix=settings.api_prefix)
        app.include_router(dev_data_router, prefix=settings.api_prefix)
    else:
        logger.info(
            "dev_endpoints_disabled",
            environment=settings.environment,
            message="Dev/debug endpoints are disabled for production safety.",
        )

    # app.include_router(telemetry_router, prefix=settings.api_prefix)  # TODO: Create telemetry router

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
