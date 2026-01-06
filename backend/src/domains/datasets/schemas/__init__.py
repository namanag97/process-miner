"""Datasets Domain Schemas.

Request/Response schemas for dataset operations:
- Upload schemas (presigned, direct)
- Column mapping schemas
- Dataset CRUD schemas
- Ingestion schemas
"""

from src.features.process_mining.schemas.datasets import (
    ColumnMapping,
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetResponse,
    DatasetUploadRequest,
    IngestRequest,
    PresignedUploadRequest,
    PresignedUploadResponse,
)

__all__ = [
    # Upload
    "PresignedUploadRequest",
    "PresignedUploadResponse",
    "DatasetUploadRequest",
    # Mapping
    "ColumnMapping",
    "IngestRequest",
    # CRUD
    "DatasetResponse",
    "DatasetListResponse",
    "DatasetDetailResponse",
]
