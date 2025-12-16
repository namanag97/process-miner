"""
Process Mining Platform - FastAPI Backend

Main application entry point. Sets up:
- CORS middleware for frontend access
- All API routers
- Error handlers
- Logging configuration
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .routers import (
    health_router,
    uploads_router,
    mappings_router,
    processing_router,
    analysis_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    settings = get_settings()
    
    # Startup
    logger.info("=" * 50)
    logger.info("Process Mining API Starting...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Upload directory: {settings.upload_path}")
    logger.info(f"Frontend URL: {settings.frontend_url}")
    logger.info("=" * 50)
    
    yield
    
    # Shutdown
    logger.info("Process Mining API Shutting down...")


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


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else None,
        },
    )


# Include routers
app.include_router(health_router, prefix="/api")
app.include_router(uploads_router, prefix="/api")
app.include_router(mappings_router, prefix="/api")
app.include_router(processing_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")


# Root endpoint
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
