"""Datasets Domain API Routers.

Provides dataset lifecycle management endpoints:
- CRUD operations (list, get, delete)
- File upload (direct and presigned)
- Column detection and mapping
- Ingestion triggering
- Export functionality
"""

from fastapi import APIRouter

# Re-export from current locations for gradual migration
from src.features.process_mining.api.datasets.crud import router as crud_router
from src.features.process_mining.api.datasets.export import router as export_router
from src.features.process_mining.api.datasets.ingest import router as ingest_router
from src.features.process_mining.api.datasets.mapping import router as mapping_router
from src.features.process_mining.api.datasets.upload import router as upload_router

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
