"""Datasets Domain Schemas.

Pydantic schemas for dataset operations.
"""

# Import from local domain schemas
from src.domains.datasets.schemas.dataset import (
    ColumnDetectionResponse,
    ColumnMapping,
    ColumnTypeInfo,
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetResponse,
    DownloadResponse,
    MappingResponse,
    MappingUpdateRequest,
    PreviewResponse,
    PresignedUploadRequest,
    PresignedUploadResponse,
)

# Import job status from features (will be in shared location later)
from src.features.process_mining.schemas.analysis import JobStatusResponse

__all__ = [
    # Dataset CRUD
    "DatasetResponse",
    "DatasetDetailResponse",
    "DatasetListResponse",
    # Upload
    "PresignedUploadRequest",
    "PresignedUploadResponse",
    "DownloadResponse",
    # Mapping
    "ColumnDetectionResponse",
    "ColumnTypeInfo",
    "ColumnMapping",
    "MappingResponse",
    "MappingUpdateRequest",
    "PreviewResponse",
    # Jobs
    "JobStatusResponse",
]
