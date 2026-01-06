"""Dataset Models - Re-exports from domains for backward compatibility.

DEPRECATED: These models have been moved to src.domains.datasets.models
Import from the new location instead.
"""

# Re-export from datasets domain
from src.domains.datasets.models.dataset import (  # noqa: F401
    Dataset,
    DatasetColumn,
    DatasetColumnMapping,
    DatasetMetadata,
)
from src.domains.datasets.models.uploaded_file import UploadedFile  # noqa: F401

__all__ = [
    "Dataset",
    "DatasetColumn",
    "DatasetColumnMapping",
    "DatasetMetadata",
    "UploadedFile",
]
