"""Routers package."""

from .health import router as health_router
from .uploads import router as uploads_router
from .mappings import router as mappings_router
from .processing import router as processing_router
from .analysis import router as analysis_router

__all__ = [
    "health_router",
    "uploads_router",
    "mappings_router",
    "processing_router",
    "analysis_router",
]
