"""Datasets Domain Schemas.

Pydantic schemas for dataset operations.
"""

# Import from local domain schemas
# Import job status from features (will be in shared location later)
from src.features.process_mining.schemas.analysis import JobStatusResponse
from src.features.process_mining.schemas.datasets.dataset import (
    ColumnDetectionResponse,
    ColumnMapping,
    ColumnTypeInfo,
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetResponse,
    DownloadResponse,
    MappingResponse,
    MappingUpdateRequest,
    PresignedUploadRequest,
    PresignedUploadResponse,
    PreviewResponse,
)

__all__ = [
    # Mapping
    "ColumnDetectionResponse",
    "ColumnMapping",
    "ColumnTypeInfo",
    "DatasetDetailResponse",
    "DatasetListResponse",
    # Dataset CRUD
    "DatasetResponse",
    "DownloadResponse",
    # Jobs
    "JobStatusResponse",
    "MappingResponse",
    "MappingUpdateRequest",
    # Upload
    "PresignedUploadRequest",
    "PresignedUploadResponse",
    "PreviewResponse",
]
