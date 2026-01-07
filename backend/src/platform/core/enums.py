"""Platform layer enums.

This file contains:
1. Platform-only enums (JobStatus, JobType, EntityType, WorkflowStatus)
2. Re-exports from layer-specific locations for backward compatibility

New code should import directly from:
- src.datasets.enums for SourceFormat
- src.analysis.enums for MinerType, ModelFormat, ConformanceMethod
"""

from enum import Enum

# =============================================================================
# Re-exports for backward compatibility
# New code should import from the layer-specific modules directly
# =============================================================================
# Domain layer enums
from src.features.process_mining.enums import (
    ConformanceMethod,
    MinerType,
    ModelFormat,
    SourceFormat,
)

# =============================================================================
# Platform-only enums (these stay here)
# =============================================================================


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Job-Centric Architecture Enums
# =============================================================================


class JobType(str, Enum):
    """Types of async jobs for unified tracking."""

    INGESTION = "ingestion"  # Dataset parsing and ingestion
    VALIDATION = "validation"  # File validation and column detection
    DISCOVERY = "discovery"  # Process model discovery
    CONFORMANCE = "conformance"  # Conformance checking
    PREDICTION_TRAINING = "prediction_training"  # ML model training
    OCEL_IMPORT = "ocel_import"  # OCEL file import
    SIMULATION = "simulation"  # Process simulation
    FILTERING = "filtering"  # Dataset filtering
    FLATTEN = "flatten"  # OCEL flattening to traditional log
    ANALYSIS = "analysis"  # General analysis (bottleneck, etc.)


class JobStatus(str, Enum):
    """Job lifecycle states."""

    # Primary status values
    QUEUED = "queued"  # Job created, waiting to start
    RUNNING = "running"  # Job in progress
    COMPLETED = "completed"  # Job finished successfully
    FAILED = "failed"  # Job failed with error
    CANCELLED = "cancelled"  # Job cancelled by user

    # Legacy alias (for backward compatibility with existing code/data)
    PENDING = "pending"  # Legacy: prefer QUEUED for new code


class EntityType(str, Enum):
    """Types of entities created by jobs."""

    DATASET = "dataset"
    MODEL = "model"
    ANALYSIS = "analysis"
    PREDICTOR = "predictor"
    OCEL_LOG = "ocel_log"
    CONFORMANCE_RESULT = "conformance_result"


__all__ = [
    "ConformanceMethod",
    "EntityType",
    "JobStatus",
    "JobType",
    # Re-exports (backward compat)
    "MinerType",
    "ModelFormat",
    "SourceFormat",
    # Platform enums
    "WorkflowStatus",
]
