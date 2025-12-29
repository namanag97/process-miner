"""Dependency Injection Container (Composition Root).

This module is the single place where infrastructure implementations
are wired to application service dependencies. This keeps the application
layer clean of any infrastructure knowledge.

Following the Composition Root pattern from Clean Architecture.
"""

from src.application.generic.workflow_service import WorkflowService
from src.application.support.ingestion_service import IngestionService
from src.infrastructure.messaging.event_bus import event_bus
from src.infrastructure.storage.file_storage import file_storage
from src.infrastructure.workers.task_queue import task_queue

# =============================================================================
# Service Instances (Singletons)
# =============================================================================

# Ingestion Service - with file storage and event bus
ingestion_service = IngestionService(
    file_storage=file_storage,
    event_bus=event_bus,
)

# Workflow Service - with task queue
workflow_service = WorkflowService(
    task_queue=task_queue,
)


# =============================================================================
# Factory Functions (for testing / custom configurations)
# =============================================================================


def create_ingestion_service(
    file_storage_override=None,
    event_bus_override=None,
) -> IngestionService:
    """Create an ingestion service with optional dependency overrides."""
    return IngestionService(
        file_storage=file_storage_override or file_storage,
        event_bus=event_bus_override or event_bus,
    )


def create_workflow_service(
    task_queue_override=None,
) -> WorkflowService:
    """Create a workflow service with optional dependency overrides."""
    return WorkflowService(
        task_queue=task_queue_override or task_queue,
    )
