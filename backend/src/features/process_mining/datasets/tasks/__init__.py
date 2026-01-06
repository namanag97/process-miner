"""Datasets Domain Tasks.

Background tasks for dataset processing.
"""

# Re-export from platform for backward compatibility
from src.platform.infrastructure.tasks.dataset_tasks import (
    ingest_dataset_task,
    validate_uploaded_file_task,
)

__all__ = [
    "validate_uploaded_file_task",
    "ingest_dataset_task",
]
