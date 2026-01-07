"""Activity v2 Type Definitions.

Dataclasses for activity inputs and outputs.
Using dataclasses for Temporal serialization compatibility.
"""

from dataclasses import dataclass, field

# =============================================================================
# Ingestion Types
# =============================================================================


@dataclass
class ChunkInfo:
    """Information about a file chunk for parallel processing."""

    chunk_id: str
    start_offset: int
    end_offset: int
    row_count: int = 0


@dataclass
class ColumnMapping:
    """Column mapping for dataset ingestion."""

    case_id: str
    activity: str
    timestamp: str
    resource: str | None = None

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "activity": self.activity,
            "timestamp": self.timestamp,
            "resource": self.resource,
        }


@dataclass
class ValidationResult:
    """Result of file validation activity."""

    is_valid: bool
    file_format: str | None = None
    file_size_bytes: int = 0
    error_message: str | None = None


@dataclass
class ColumnDetectionResult:
    """Result of column detection activity."""

    columns: list[str] = field(default_factory=list)
    suggestions: dict = field(default_factory=dict)
    row_count: int = 0
    can_auto_map: bool = False


@dataclass
class ChunkProcessResult:
    """Result of processing a single chunk."""

    chunk_id: str
    events_processed: int = 0
    cases_processed: int = 0
    success: bool = True
    error_message: str | None = None


@dataclass
class IngestionResult:
    """Final result of ingestion workflow."""

    total_cases: int = 0
    total_events: int = 0
    total_activities: int = 0
    duration_ms: float = 0


# =============================================================================
# Analysis Types
# =============================================================================


@dataclass
class EventLogInfo:
    """Information about an event log."""

    is_ready: bool
    total_cases: int = 0
    total_events: int = 0
    total_activities: int = 0


@dataclass
class DiscoveryResult:
    """Result of process model discovery."""

    model_data: bytes  # Serialized PNML or BPMN
    model_format: str = "pnml"
    fitness: float | None = None
    precision: float | None = None


@dataclass
class ConformanceResult:
    """Result of conformance checking."""

    fitness: float
    precision: float
    is_conformant: bool
    fitting_traces: int
    total_traces: int
    deviations: list[dict] = field(default_factory=list)


@dataclass
class ModelMetrics:
    """Quality metrics for a process model."""

    fitness: float | None = None
    precision: float | None = None
    generalization: float | None = None
    simplicity: float | None = None
