"""Celery Tasks Package.

Re-exports all tasks and infrastructure for backward compatibility.

NOTE: For new workflows, prefer using Temporal via src.platform.temporal.
See src.platform.temporal.compat for the migration compatibility layer.
"""

# Base infrastructure
from src.platform.infrastructure.tasks.base import (
    AsyncSessionLocal,
    AsyncTask,
    async_engine,
    celery_app,
    get_task_status,
)

# Dataset tasks
from src.platform.infrastructure.tasks.dataset_tasks import (
    ingest_dataset_task,
    validate_dataset_task,
    validate_uploaded_file_task,
)

# Analysis tasks
from src.platform.infrastructure.tasks.analysis_tasks import (
    perform_analysis_task,
    perform_conformance_task,
    perform_discovery_task,
)

# ML tasks
from src.platform.infrastructure.tasks.ml_tasks import (
    train_prediction_model_task,
)

# Maintenance tasks
from src.platform.infrastructure.tasks.maintenance_tasks import (
    reap_zombie_jobs,
)

__all__ = [
    # Infrastructure
    "celery_app",
    "async_engine",
    "AsyncSessionLocal",
    "AsyncTask",
    "get_task_status",
    # Dataset tasks
    "validate_dataset_task",
    "validate_uploaded_file_task",
    "ingest_dataset_task",
    # Analysis tasks
    "perform_analysis_task",
    "perform_discovery_task",
    "perform_conformance_task",
    # ML tasks
    "train_prediction_model_task",
    # Maintenance tasks
    "reap_zombie_jobs",
]
