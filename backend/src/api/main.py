"""FastAPI Application - Main Entry Point.

Clean, minimal setup with CORS for React frontend.
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers import (
    analytics_router,
    conformance_router,
    dev_log_router,
    discovery_router,
    filtering_router,
    ocpm_router,
    organizational_router,
    predictions_router,
    processes_router,
    projects_router,
    simulation_router,
    visualization_router,
    workflows_router,
)
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
    logger.info("application_ready")
    yield
    # Shutdown
    logger.info("application_shutting_down")
    await close_database()
    logger.info("application_stopped")


# =============================================================================
# App Factory
# =============================================================================


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Process Mining API - Clean Architecture",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Logging middleware (order matters - performance first, then request logging)
    app.add_middleware(PerformanceLoggingMiddleware, slow_request_threshold_ms=1000)
    app.add_middleware(RequestLoggingMiddleware)

    # Exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "application_exception",
            exception_type=type(exc).__name__,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url.path),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "error",
                "title": type(exc).__name__,
                "status": exc.status_code,
                "detail": exc.message,
                "instance": str(request.url),
                **exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler for unhandled errors.

        Ensures CORS headers are returned even for 500 errors.
        """
        logger.error(
            "unhandled_exception",
            exception_type=type(exc).__name__,
            message=str(exc),
            path=str(request.url.path),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "type": "error",
                "title": "InternalServerError",
                "status": 500,
                "detail": str(exc) if settings.debug else "Internal server error",
                "instance": str(request.url),
            },
        )

    # Health endpoints
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.app_version,
        }

    @app.get("/", tags=["Health"])
    async def root() -> dict[str, Any]:
        """Root endpoint with API info."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    # Include routers with API prefix
    app.include_router(projects_router, prefix=settings.api_prefix)
    app.include_router(processes_router, prefix=settings.api_prefix)
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
    app.include_router(dev_log_router, prefix=settings.api_prefix)

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
