"""Temporal Workflows Package.

Exports all workflows for worker registration.

All workflows implement:
- Query handlers for real-time progress tracking (get_progress)
- Deterministic workflow IDs for idempotent starts
- Progress state that survives worker restarts

Workflow ID Patterns:
    - Ingestion: f"ingest-dataset-{dataset_id}"
    - Validation: f"validate-dataset-{dataset_id}"
    - Discovery: f"discover-{dataset_id}-{miner_type}"
    - Conformance: f"conformance-{dataset_id}-{model_id}"
    - Quality: f"quality-{model_id}-{dataset_id}"

Ingestion Workflows:
    - DatasetIngestionWorkflow: Full dataset ingestion lifecycle
    - DatasetValidationWorkflow: Validation and column detection

Analysis Workflows:
    - ProcessDiscoveryWorkflow: Process model discovery
    - ConformanceCheckWorkflow: Conformance checking
    - QualityEvaluationWorkflow: Comprehensive quality metrics
"""

from src.platform.temporal.workflows.analysis import (
    ConformanceCheckWorkflow,
    ProcessDiscoveryWorkflow,
)
from src.platform.temporal.workflows.ingestion import (
    DatasetIngestionWorkflow,
    DatasetValidationWorkflow,
)
from src.platform.temporal.workflows.quality import QualityEvaluationWorkflow

# All ingestion workflows
INGESTION_WORKFLOWS = [
    DatasetIngestionWorkflow,
    DatasetValidationWorkflow,
]

# All analysis workflows
ANALYSIS_WORKFLOWS = [
    ProcessDiscoveryWorkflow,
    ConformanceCheckWorkflow,
    QualityEvaluationWorkflow,
]

# Combined list
ALL_WORKFLOWS = INGESTION_WORKFLOWS + ANALYSIS_WORKFLOWS

__all__ = [
    "ALL_WORKFLOWS",
    "ANALYSIS_WORKFLOWS",
    "INGESTION_WORKFLOWS",
    "ConformanceCheckWorkflow",
    "DatasetIngestionWorkflow",
    "DatasetValidationWorkflow",
    "ProcessDiscoveryWorkflow",
    "QualityEvaluationWorkflow",
]
