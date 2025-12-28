"""Process Mining SaaS - FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.infrastructure.persistence.database import init_database
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
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
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
    
    @app.get("/", tags=["Health"])
    async def root():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
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
