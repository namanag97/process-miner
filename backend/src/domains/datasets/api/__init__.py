"""Datasets Domain API Routers.

Provides dataset lifecycle management endpoints:
- CRUD operations (list, get, delete)
- File upload (direct and presigned)
- Column detection and mapping
- Ingestion triggering
- Export functionality
"""

from fastapi import APIRouter

# Import routers from domain locations
from src.domains.datasets.api.crud import router as crud_router
from src.domains.datasets.api.export import router as export_router
from src.domains.datasets.api.ingestion import router as ingest_router
from src.domains.datasets.api.mapping import router as mapping_router
from src.domains.datasets.api.upload import router as upload_router

# Combined datasets router
router = APIRouter(prefix="/datasets", tags=["Datasets"])

# Include sub-routers
router.include_router(crud_router)
router.include_router(upload_router)
router.include_router(mapping_router)
router.include_router(ingest_router)
router.include_router(export_router)

__all__ = [
    "router",
    "crud_router",
    "upload_router",
    "mapping_router",
    "ingest_router",
    "export_router",
]
