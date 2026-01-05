"""Workflow Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.workflows.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.workflow import workflow_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.workflows import workflow_service
"""

from src.features.process_mining.workflows import (
    WorkflowService,
    workflow_service,
)

__all__ = [
    "WorkflowService",
    "workflow_service",
]
