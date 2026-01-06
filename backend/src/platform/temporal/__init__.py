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
        args=["dataset-123"],
        id="dataset-123-ingest",
        task_queue="ingestion-queue",
    )
"""

from src.platform.temporal.client import get_temporal_client
from src.platform.temporal.config import TemporalConfig, get_temporal_config

__all__ = [
    "get_temporal_client",
    "get_temporal_config",
    "TemporalConfig",
]
