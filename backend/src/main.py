"""Process Mining SaaS - FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
import os

from src.config import get_settings
from src.infrastructure.persistence.database import init_database
from src.infrastructure.logging import setup_logging, RequestResponseLoggingMiddleware
from src.presentation.api.routers import (
    logs,
    discovery,
    conformance,
    enhancement,
    analytics,
    models,
    auth,
    workflows,
    notifications,
    integrations,
    process_mining,
    transitions,
    performance,
    org,
    ocpm,
    processes,
    miners,
)
from src.presentation.api.errors import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
    domain_exception_handler,
    DomainError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()
    settings.ensure_directories()
    await init_database()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Process Mining SaaS API - Powered by PM4Py",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Initialize logging
    setup_logging(
        logs_dir=settings.logs_dir,
        log_level=settings.api_log_level,
    )
    
    # Request/Response Logging Middleware (must be added first to wrap all requests)
    app.add_middleware(
        RequestResponseLoggingMiddleware,
        log_request_body=settings.log_request_body,
        log_response_body=settings.log_response_body,
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register RFC 7807 Exception Handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(DomainError, domain_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    # Register API Routers
    api_prefix = settings.api_prefix
    
    app.include_router(auth.router, prefix=api_prefix, tags=["Authentication"])
    app.include_router(logs.router, prefix=api_prefix, tags=["Event Logs"])
    app.include_router(discovery.router, prefix=api_prefix, tags=["Process Discovery"])
    app.include_router(conformance.router, prefix=api_prefix, tags=["Conformance Checking"])
    app.include_router(enhancement.router, prefix=api_prefix, tags=["Process Enhancement"])
    app.include_router(analytics.router, prefix=api_prefix, tags=["Analytics"])
    app.include_router(models.router, prefix=api_prefix, tags=["Process Models"])
    app.include_router(workflows.router, prefix=api_prefix, tags=["Workflows"])
    app.include_router(notifications.router, prefix=api_prefix, tags=["Notifications"])
    app.include_router(integrations.router, prefix=api_prefix, tags=["Integrations"])
    app.include_router(process_mining.router, prefix=api_prefix, tags=["Process Mining"])
    app.include_router(transitions.router, prefix=api_prefix, tags=["Transitions"])
    app.include_router(performance.router, prefix=api_prefix, tags=["Performance Analysis"])
    app.include_router(org.router, prefix=api_prefix, tags=["Organizational Mining"])
    app.include_router(ocpm.router, prefix=api_prefix, tags=["Object-Centric Process Mining"])
    app.include_router(processes.router, prefix=api_prefix, tags=["Processes"])
    app.include_router(miners.router, prefix=api_prefix, tags=["Miners"])
    
    # Serve static files for test UI
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/", tags=["Health"])
    async def root():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
            "_links": {
                "docs": {"href": "/docs", "title": "API Documentation"},
                "redoc": {"href": "/redoc", "title": "ReDoc"},
                "health": {"href": "/health", "title": "Health Check"},
                "test-ui": {"href": "/static/index.html", "title": "API Test UI"},
            }
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Detailed health check."""
        return {
            "status": "healthy",
            "database": "connected",
            "auth_enabled": settings.auth_enabled,
        }
    
    return app


app = create_app()
