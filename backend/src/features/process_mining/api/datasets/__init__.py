"""Datasets API Router - Combined from modular routers.

4-Phase Upload Architecture:
1. Upload (upload.py) - Direct/presigned file upload
2. Validate & Detect (background job)  
3. Map (mapping.py) - Column detection and mapping
4. Ingest (ingest.py) - Trigger ingestion job

Plus:
- CRUD (crud.py) - List, get, delete
- Analytics (analytics.py) - Statistics, cases, variants
"""

from fastapi import APIRouter

# Use relative imports to avoid circular dependency
from . import analytics, crud, ingest, mapping, upload

# Create main router
router = APIRouter(prefix="/datasets", tags=["Datasets"])

# Include all sub-routers
# Order matters for route matching - more specific routes first

# Upload routes: POST /datasets, POST /datasets/presign, POST /datasets/{id}/uploaded
router.include_router(upload.router)

# Mapping routes: GET /datasets/{id}/columns, POST /datasets/{id}/mapping
router.include_router(mapping.router)

# Ingest routes: POST /datasets/{id}/ingest
router.include_router(ingest.router)

# Analytics routes: GET /datasets/{id}/statistics, cases, variants, activities
router.include_router(analytics.router)

# CRUD routes: GET /datasets, GET /datasets/{id}, DELETE /datasets/{id}
# Include last as it has generic routes
router.include_router(crud.router)


__all__ = ["router"]

