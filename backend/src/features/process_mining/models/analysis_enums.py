"""Analysis Domain Enums.

Status and type enumerations for process mining analyses.
"""

from enum import Enum


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
