"""Workflows Module - Automated workflow execution.

Components:
- router.py: API router for workflow endpoints
- service.py: WorkflowService for workflow execution
"""

from .router import router
from .service import WorkflowService, workflow_service

__all__ = [
    "router",
    "WorkflowService",
    "workflow_service",
]
