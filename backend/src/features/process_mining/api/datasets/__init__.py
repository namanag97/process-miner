"""Datasets API Router - Combined from modular routers.

4-Phase Upload Architecture:
1. Upload (upload.py) - Direct/presigned file upload
2. Validate & Detect (background job)  
3. Map (mapping.py) - Column detection and mapping
4. Ingest (ingest.py) - Trigger ingestion job

Plus:
- CRUD (crud.py) - List, get, delete
- Analytics (analytics.py) - Statistics, cases, variants, events
- Statistics (statistics.py) - Cached computed statistics
- Export (export.py) - Export and download
"""

from fastapi import APIRouter

# Use relative imports to avoid circular dependency
from . import analytics, crud, export, ingest, mapping, statistics, upload

# Create main router
router = APIRouter(prefix="/datasets", tags=["Datasets"])

# Include all sub-routers
# Order matters for route matching - more specific routes first

# Upload routes: POST /datasets, POST /datasets/presign, POST /datasets/{id}/uploaded
router.include_router(upload.router)

# Mapping routes: GET /datasets/{id}/columns, POST/GET/PUT /datasets/{id}/mapping
router.include_router(mapping.router)

# Ingest routes: POST /datasets/{id}/ingest, POST /datasets/{id}/reingest
router.include_router(ingest.router)

# Statistics routes: GET /datasets/{id}/statistics (cached computed stats)
router.include_router(statistics.router)

# Export routes: POST /datasets/{id}/export, GET /datasets/{id}/download
router.include_router(export.router)

# Analytics routes: GET /datasets/{id}/statistics, cases, variants, activities, events, metadata
router.include_router(analytics.router)

# CRUD routes: GET /datasets, GET /datasets/{id}, DELETE /datasets/{id}
# Include last as it has generic routes
router.include_router(crud.router)


__all__ = ["router"]
