"""Temporal Compatibility Layer.

Provides a compatibility layer for transitioning from Celery to Temporal.
This module stubs out Temporal functions when Temporal is not available.
"""

from typing import Any


def is_temporal_enabled() -> bool:
    """Check if Temporal is enabled and available.

    Returns:
        False for MVP - Temporal not yet integrated
    """
    return False


async def dispatch_workflow(
    workflow_type: str,
    args: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    """Dispatch workflow (compatibility stub).

    For MVP, this is a placeholder. Actual workflow dispatch
    should use Celery or direct function calls.

    Args:
        workflow_type: Type of workflow to dispatch
        args: Workflow arguments
        **kwargs: Additional options

    Returns:
        Dict with status (stub returns not_implemented)

    Raises:
        NotImplementedError: Temporal not yet integrated in MVP
    """
    raise NotImplementedError(
        "Temporal workflows not yet implemented. "
        f"Use Celery tasks or direct calls for {workflow_type}"
    )


async def get_workflow_status(workflow_id: str) -> dict[str, Any]:
    """Get workflow execution status (compatibility stub).

    Args:
        workflow_id: Workflow instance ID

    Returns:
        Status dict (stub returns unknown)

    Raises:
        NotImplementedError: Temporal not yet integrated in MVP
    """
    raise NotImplementedError(
        "Temporal workflow status not yet implemented. "
        f"Cannot get status for workflow {workflow_id}"
    )


async def cancel_workflow(workflow_id: str) -> bool:
    """Cancel running workflow (compatibility stub).

    Args:
        workflow_id: Workflow instance ID

    Returns:
        False (stub - cannot cancel non-existent workflow)

    Raises:
        NotImplementedError: Temporal not yet integrated in MVP
    """
    raise NotImplementedError(
        "Temporal workflow cancellation not yet implemented. "
        f"Cannot cancel workflow {workflow_id}"
    )
