"""Celery/Temporal Compatibility Layer.

Provides a feature-flag-based dispatcher that can route workflow execution
to either Celery or Temporal based on configuration.

Usage:
    from src.platform.temporal.compat import dispatch_workflow

    # Routes to Celery or Temporal based on USE_TEMPORAL env var
    result = await dispatch_workflow(
        workflow_type="dataset_ingestion",
        args={"dataset_id": "123", "storage_key": "..."},
    )
"""

import os
from typing import Any
from uuid import uuid4

from src.platform.core.logging_config import get_logger
from src.platform.temporal.config import get_temporal_config

logger = get_logger(__name__)

# Feature flag for Temporal migration - now defaults to TRUE for MVP
USE_TEMPORAL = os.getenv("USE_TEMPORAL", "true").lower() == "true"


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
    return await _dispatch_celery(workflow_type, args, entity_type, entity_id)


async def _dispatch_celery(
    workflow_type: str,
    args: dict[str, Any],
    entity_type: str | None,
    entity_id: str | None,
) -> dict[str, str]:
    """Route to existing Celery tasks."""
    from src.platform.infrastructure.tasks.analysis_tasks import (
        perform_conformance_task,
        perform_discovery_task,
    )
    from src.platform.infrastructure.tasks.dataset_tasks import (
        ingest_dataset_task,
        validate_dataset_task,
        validate_uploaded_file_task,
    )

    job_id = str(uuid4())

    # Map workflow types to Celery tasks
    task_map = {
        "validate_dataset": validate_dataset_task,
        "validate_uploaded_file": validate_uploaded_file_task,
        "dataset_ingestion": ingest_dataset_task,
        "process_discovery": perform_discovery_task,
        "conformance_check": perform_conformance_task,
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
    from src.platform.temporal.workflows.analysis import (
        ConformanceCheckWorkflow,
        ProcessDiscoveryWorkflow,
    )
    from src.platform.temporal.workflows.ingestion import (
        DatasetIngestionWorkflow,
        DatasetValidationWorkflow,
    )

    config = get_temporal_config()
    client = await get_temporal_client()

    # Generate IDs
    job_id = str(uuid4())
    workflow_id = f"{workflow_type}-{entity_id or job_id}"

    # Map workflow types to Temporal workflows and queues
    workflow_map = {
        "validate_dataset": {
            "queue": config.QUEUE_INGESTION,
            "workflow": DatasetValidationWorkflow,
        },
        "validate_uploaded_file": {
            "queue": config.QUEUE_INGESTION,
            "workflow": DatasetValidationWorkflow,
        },
        "dataset_ingestion": {
            "queue": config.QUEUE_INGESTION,
            "workflow": DatasetIngestionWorkflow,
        },
        "process_discovery": {
            "queue": config.QUEUE_ANALYSIS,
            "workflow": ProcessDiscoveryWorkflow,
        },
        "conformance_check": {
            "queue": config.QUEUE_ANALYSIS,
            "workflow": ConformanceCheckWorkflow,
        },
    }

    mapping = workflow_map.get(workflow_type)
    if mapping is None:
        raise ValueError(f"Unknown workflow type for Temporal: {workflow_type}")

    # Start workflow
    handle = await client.start_workflow(
        mapping["workflow"].run,
        args=[args.get("dataset_id", args.get("entity_id"))] + list(args.values())[1:],
        id=workflow_id,
        task_queue=mapping["queue"],
    )

    return {
        "job_id": job_id,
        "workflow_id": workflow_id,
        "workflow_run_id": handle.result_run_id,
    }


async def get_workflow_status(workflow_id: str) -> dict[str, Any]:
    """Get the status of a Temporal workflow.

    Args:
        workflow_id: The workflow ID

    Returns:
        dict with status, current activity, and result if completed
    """
    from src.platform.temporal.client import get_temporal_client

    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)

    try:
        desc = await handle.describe()
        status = desc.status.name if desc.status else "UNKNOWN"

        result = None
        if status == "COMPLETED":
            result = await handle.result()

        return {
            "workflow_id": workflow_id,
            "status": status,
            "start_time": desc.start_time.isoformat() if desc.start_time else None,
            "close_time": desc.close_time.isoformat() if desc.close_time else None,
            "result": result,
        }
    except Exception as e:
        return {
            "workflow_id": workflow_id,
            "status": "ERROR",
            "error": str(e),
        }


async def cancel_workflow(workflow_id: str) -> dict[str, Any]:
    """Cancel a running Temporal workflow.

    Args:
        workflow_id: The workflow ID to cancel

    Returns:
        dict with cancellation result
    """
    from src.platform.temporal.client import get_temporal_client

    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)

    try:
        await handle.cancel()
        return {
            "workflow_id": workflow_id,
            "status": "cancelled",
        }
    except Exception as e:
        return {
            "workflow_id": workflow_id,
            "status": "error",
            "error": str(e),
        }


def is_temporal_enabled() -> bool:
    """Check if Temporal is enabled."""
    config = get_temporal_config()
    return config.use_temporal or USE_TEMPORAL
