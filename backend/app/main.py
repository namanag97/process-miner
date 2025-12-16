"""
Process Mining Platform - FastAPI Backend

Main application entry point with:
- Structured logging configuration
- CORS middleware
- All API routers
- Global error handling
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from .config import get_settings
from .database import engine
from .core import get_logger, configure_logging
from .routers import (
    health_router,
    users_router,
    uploads_router,
    mappings_router,
    processing_router,
    analysis_router,
)

# Configure structured logging
configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    settings = get_settings()
    
    # Create all tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Log startup info
    log.info(
        "api_starting",
        debug_mode=settings.debug,
        upload_dir=str(settings.upload_path),
        frontend_url=settings.frontend_url,
    )
    
    yield
    
    # Shutdown
    log.info("api_shutting_down")


# Create FastAPI app
app = FastAPI(
    title="Process Mining Platform API",
    description="Backend API for process mining with PM4Py",
    version="0.1.0",
    lifespan=lifespan,
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions with structured logging."""
    log.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else None,
        },
    )


# Include routers - all under /api prefix
app.include_router(health_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(uploads_router, prefix="/api")
app.include_router(mappings_router, prefix="/api")
app.include_router(processing_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Process Mining Platform API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
    }


# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
