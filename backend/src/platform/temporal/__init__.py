"""Temporal Workflow Orchestration.

This module provides Temporal-based workflow orchestration as a replacement
for Celery task queues. It offers:

- Durable workflow execution with automatic recovery
- Activity heartbeats for long-running tasks
- Built-in retry policies with exponential backoff
- Workflow visibility via Temporal Web UI

Usage:
    from src.platform.temporal import get_temporal_client, start_workflow

    client = await get_temporal_client()
    handle = await client.start_workflow(
        DatasetIngestionWorkflow.run,
        args=["dataset-123", "storage-key", "case_id", "activity", "timestamp"],
        id="dataset-123-ingest",
        task_queue="ingestion-queue",
    )

Dispatching (with Celery fallback):
    from src.platform.temporal.compat import dispatch_workflow

    result = await dispatch_workflow(
        workflow_type="dataset_ingestion",
        args={"dataset_id": "123", "storage_key": "..."},
    )
"""

from src.platform.temporal.client import get_temporal_client
from src.platform.temporal.compat import (
    cancel_workflow,
    dispatch_workflow,
    get_workflow_status,
    is_temporal_enabled,
)
from src.platform.temporal.config import TemporalConfig, get_temporal_config

__all__ = [
    # Client
    "get_temporal_client",
    # Config
    "get_temporal_config",
    "TemporalConfig",
    # Compat layer
    "dispatch_workflow",
    "get_workflow_status",
    "cancel_workflow",
    "is_temporal_enabled",
]
