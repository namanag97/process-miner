"""Temporal Workflows v2 - Temporal Native.

These workflows implement the correct Temporal patterns:
- Deterministic workflow IDs from business keys
- Query handlers for progress (survives replays)
- Chunk-based processing for long operations
- No AsyncJob creation - Temporal IS the job system

Usage:
    from src.infra.temporal.workflows_v2 import DatasetIngestionWorkflowV2

    # Start with deterministic ID
    workflow_id = f"ingest-dataset-{dataset_id}"
    handle = await client.start_workflow(
        DatasetIngestionWorkflowV2.run,
        args=[dataset_id, storage_key, mapping],
        id=workflow_id,
        task_queue="ingestion-queue",
        id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
    )
"""

from src.infra.temporal.workflows_v2.analysis import (
    ConformanceCheckWorkflowV2,
    ProcessDiscoveryWorkflowV2,
)
from src.infra.temporal.workflows_v2.ingestion import (
    DatasetIngestionWorkflowV2,
    DatasetValidationWorkflowV2,
)

__all__ = [
    "ConformanceCheckWorkflowV2",
    "DatasetIngestionWorkflowV2",
    "DatasetValidationWorkflowV2",
    "ProcessDiscoveryWorkflowV2",
]
