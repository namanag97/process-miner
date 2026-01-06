"""Process Mining Enums.

Status and type enumerations for datasets and analyses.
"""

from enum import Enum


class DatasetStatus(str, Enum):
    """Dataset lifecycle states."""

    PENDING = "pending"
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    AWAITING_MAPPING = "awaiting_mapping"
    MAPPED = "mapped"
    INGESTING = "ingesting"
    READY = "ready"
    ERROR = "error"


class AnalysisType(str, Enum):
    """Types of process analyses."""

    DISCOVERY = "discovery"
    CONFORMANCE = "conformance"
    ENHANCEMENT = "enhancement"
    VARIANTS = "variants"
    BOTTLENECK = "bottleneck"


class AnalysisStatus(str, Enum):
    """Analysis job lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
