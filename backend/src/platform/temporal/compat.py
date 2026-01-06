"""Celery/Temporal Compatibility Layer.

Provides a feature-flag-based dispatcher that can route workflow execution
to either Celery or Temporal based on configuration.

Usage:
    from src.platform.temporal.compat import dispatch_workflow

    # Routes to Celery or Temporal based on USE_TEMPORAL env var
    job_id = await dispatch_workflow(
        workflow_type="dataset_ingestion",
        args={"dataset_id": "123"},
    )
"""

import os
from typing import Any
from uuid import uuid4

from src.platform.temporal.config import get_temporal_config

# Feature flag for Temporal migration
USE_TEMPORAL = os.getenv("USE_TEMPORAL", "false").lower() == "true"


async def dispatch_workflow(
    workflow_type: str,
    args: dict[str, Any],
    entity_type: str | None = None,
    entity_id: str | None = None,
) -> dict[str, str]:
    """Dispatch workflow to either Celery or Temporal.

    Args:
        workflow_type: Type of workflow (e.g., "dataset_ingestion", "analysis")
        args: Arguments to pass to the workflow
        entity_type: Optional entity type for tracking (e.g., "dataset")
        entity_id: Optional entity ID for tracking

    Returns:
        Dict with job_id and optionally workflow_id
    """
    config = get_temporal_config()

    if config.use_temporal or USE_TEMPORAL:
        return await _dispatch_temporal(workflow_type, args, entity_type, entity_id)
    else:
        return await _dispatch_celery(workflow_type, args, entity_type, entity_id)


async def _dispatch_celery(
    workflow_type: str,
    args: dict[str, Any],
    entity_type: str | None,
    entity_id: str | None,
) -> dict[str, str]:
    """Route to existing Celery tasks."""
    from src.platform.infrastructure.tasks.dataset_tasks import (
        ingest_dataset_task,
        validate_dataset_task,
    )

    job_id = str(uuid4())

    # Map workflow types to Celery tasks
    task_map = {
        "validate_dataset": validate_dataset_task,
        "dataset_ingestion": ingest_dataset_task,
    }

    task = task_map.get(workflow_type)
    if task is None:
        raise ValueError(f"Unknown workflow type: {workflow_type}")

    # Dispatch Celery task
    result = task.apply_async(
        kwargs=args,
        task_id=job_id,
    )

    return {
        "job_id": job_id,
        "task_id": result.id,
    }


async def _dispatch_temporal(
    workflow_type: str,
    args: dict[str, Any],
    entity_type: str | None,
    entity_id: str | None,
) -> dict[str, str]:
    """Route to Temporal workflows."""
    from src.platform.temporal.client import get_temporal_client
    from src.platform.temporal.config import get_temporal_config

    config = get_temporal_config()
    client = await get_temporal_client()

    # Generate IDs
    job_id = str(uuid4())
    workflow_id = f"{workflow_type}-{entity_id or job_id}"

    # Map workflow types to Temporal workflows and queues
    workflow_map = {
        "validate_dataset": {
            "queue": config.QUEUE_INGESTION,
            # "workflow": ValidationWorkflow,  # TODO: Import when created
        },
        "dataset_ingestion": {
            "queue": config.QUEUE_INGESTION,
            # "workflow": DatasetIngestionWorkflow,  # TODO: Import when created
        },
        "process_discovery": {
            "queue": config.QUEUE_ANALYSIS,
            # "workflow": AnalysisWorkflow,  # TODO: Import when created
        },
    }

    mapping = workflow_map.get(workflow_type)
    if mapping is None:
        raise ValueError(f"Unknown workflow type for Temporal: {workflow_type}")

    # TODO: Uncomment when workflows are implemented
    # handle = await client.start_workflow(
    #     mapping["workflow"].run,
    #     args=[args],
    #     id=workflow_id,
    #     task_queue=mapping["queue"],
    # )

    # For now, return placeholder
    return {
        "job_id": job_id,
        "workflow_id": workflow_id,
        "workflow_run_id": "pending-implementation",
    }


def is_temporal_enabled() -> bool:
    """Check if Temporal is enabled."""
    config = get_temporal_config()
    return config.use_temporal or USE_TEMPORAL
