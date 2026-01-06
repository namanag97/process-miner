"""Temporal Workflows Package.

Exports all workflows for worker registration.

Ingestion Workflows:
    - DatasetIngestionWorkflow: Full dataset ingestion lifecycle
    - DatasetValidationWorkflow: Validation and column detection

Analysis Workflows:
    - ProcessDiscoveryWorkflow: Process model discovery
    - ConformanceCheckWorkflow: Conformance checking
"""

from src.platform.temporal.workflows.analysis import (
    ConformanceCheckWorkflow,
    ProcessDiscoveryWorkflow,
)
from src.platform.temporal.workflows.ingestion import (
    DatasetIngestionWorkflow,
    DatasetValidationWorkflow,
)

# All ingestion workflows
INGESTION_WORKFLOWS = [
    DatasetIngestionWorkflow,
    DatasetValidationWorkflow,
]

# All analysis workflows
ANALYSIS_WORKFLOWS = [
    ProcessDiscoveryWorkflow,
    ConformanceCheckWorkflow,
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
]
