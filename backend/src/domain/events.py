"""Domain Events - Events that occur in the domain."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    """Base class for domain events."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def event_type(self) -> str:
        return self.__class__.__name__


# =============================================================================
# EVENT LOG LIFECYCLE EVENTS
# =============================================================================


@dataclass
class LogUploadStarted(DomainEvent):
    """Event: Log upload has started."""

    log_id: UUID = field(default_factory=uuid4)
    log_name: str = ""
    source_type: str = "upload"
    file_size: int = 0


@dataclass
class LogUploadCompleted(DomainEvent):
    """Event: Log upload has completed."""

    log_id: UUID = field(default_factory=uuid4)
    storage_location: str = ""


@dataclass
class LogParsingStarted(DomainEvent):
    """Event: Log parsing has started."""

    log_id: UUID = field(default_factory=uuid4)


@dataclass
class LogParsingCompleted(DomainEvent):
    """Event: Log parsing has completed with statistics."""

    log_id: UUID = field(default_factory=uuid4)
    event_count: int = 0
    case_count: int = 0
    activity_count: int = 0
    variant_count: int = 0


@dataclass
class LogIngested(DomainEvent):
    """Event: An event log has been successfully ingested (legacy compatibility)."""

    log_id: UUID = field(default_factory=uuid4)
    log_name: str = ""
    total_cases: int = 0
    total_events: int = 0
    source_file: Optional[str] = None


@dataclass
class LogValidationCompleted(DomainEvent):
    """Event: Log validation has completed successfully."""

    log_id: UUID = field(default_factory=uuid4)
    completeness_score: float = 1.0
    validity_score: float = 1.0
    issue_count: int = 0


@dataclass
class LogValidationFailed(DomainEvent):
    """Event: Log validation has failed."""

    log_id: UUID = field(default_factory=uuid4)
    error_message: str = ""
    critical_issues: int = 0


@dataclass
class LogReady(DomainEvent):
    """Event: Log is ready for analysis."""

    log_id: UUID = field(default_factory=uuid4)
    log_name: str = ""
    event_count: int = 0
    case_count: int = 0


@dataclass
class LogArchived(DomainEvent):
    """Event: Log has been archived."""

    log_id: UUID = field(default_factory=uuid4)
    log_name: str = ""


@dataclass
class LogDeleted(DomainEvent):
    """Event: An event log has been deleted."""

    log_id: UUID = field(default_factory=uuid4)
    log_name: str = ""


# =============================================================================
# PROCESS DISCOVERY EVENTS
# =============================================================================


@dataclass
class DiscoveryRequested(DomainEvent):
    """Event: Process discovery has been requested."""

    log_id: UUID = field(default_factory=uuid4)
    algorithm: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscoveryStarted(DomainEvent):
    """Event: Process discovery has started."""

    model_id: UUID = field(default_factory=uuid4)
    log_id: UUID = field(default_factory=uuid4)
    algorithm: str = ""


@dataclass
class ModelDiscovered(DomainEvent):
    """Event: A process model has been discovered from a log."""

    model_id: UUID = field(default_factory=uuid4)
    model_name: str = ""
    source_log_id: UUID = field(default_factory=uuid4)
    miner_type: str = ""
    model_format: str = ""


@dataclass
class DiscoveryFailed(DomainEvent):
    """Event: Process discovery has failed."""

    model_id: UUID = field(default_factory=uuid4)
    log_id: UUID = field(default_factory=uuid4)
    error_message: str = ""


@dataclass
class ModelAnnotated(DomainEvent):
    """Event: Model has been annotated with frequency or performance data."""

    model_id: UUID = field(default_factory=uuid4)
    annotation_type: str = ""  # frequency, performance


@dataclass
class ModelImported(DomainEvent):
    """Event: A process model has been imported from a file."""

    model_id: UUID = field(default_factory=uuid4)
    model_name: str = ""
    model_format: str = ""
    source_file: Optional[str] = None


@dataclass
class ModelExported(DomainEvent):
    """Event: A process model has been exported."""

    model_id: UUID = field(default_factory=uuid4)
    export_format: str = ""
    location: str = ""


# =============================================================================
# CONFORMANCE CHECKING EVENTS
# =============================================================================


@dataclass
class ConformanceCheckRequested(DomainEvent):
    """Event: Conformance check has been requested."""

    log_id: UUID = field(default_factory=uuid4)
    model_id: UUID = field(default_factory=uuid4)
    method: str = "token_replay"


@dataclass
class ConformanceCheckStarted(DomainEvent):
    """Event: Conformance check has started."""

    result_id: UUID = field(default_factory=uuid4)


@dataclass
class ConformanceChecked(DomainEvent):
    """Event: Conformance checking has been completed."""

    result_id: UUID = field(default_factory=uuid4)
    log_id: UUID = field(default_factory=uuid4)
    model_id: UUID = field(default_factory=uuid4)
    fitness: float = 0.0
    is_conformant: bool = False


@dataclass
class ConformanceCheckFailed(DomainEvent):
    """Event: Conformance check has failed."""

    result_id: UUID = field(default_factory=uuid4)
    log_id: UUID = field(default_factory=uuid4)
    model_id: UUID = field(default_factory=uuid4)
    error_message: str = ""


@dataclass
class DeviationsIdentified(DomainEvent):
    """Event: Deviations have been identified from conformance checking."""

    result_id: UUID = field(default_factory=uuid4)
    log_id: UUID = field(default_factory=uuid4)
    model_id: UUID = field(default_factory=uuid4)
    total_deviations: int = 0
    deviation_rate: float = 0.0
    most_common_type: str = ""


@dataclass
class DeviationDetected(DomainEvent):
    """Event: A deviation from the model has been detected."""

    log_id: UUID = field(default_factory=uuid4)
    model_id: UUID = field(default_factory=uuid4)
    case_id: str = ""
    deviation_type: str = ""
    details: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# ANALYTICS EVENTS
# =============================================================================


@dataclass
class PerformanceAnalyzed(DomainEvent):
    """Event: Performance analysis has been completed."""

    log_id: UUID = field(default_factory=uuid4)
    avg_duration_seconds: float = 0.0
    bottleneck_count: int = 0


@dataclass
class BottlenecksIdentified(DomainEvent):
    """Event: Bottlenecks have been identified."""

    log_id: UUID = field(default_factory=uuid4)
    bottleneck_activities: list[str] = field(default_factory=list)
    most_severe: Optional[str] = None


@dataclass
class SLABreachDetected(DomainEvent):
    """Event: SLA breach has been detected."""

    log_id: UUID = field(default_factory=uuid4)
    case_id: str = ""
    sla_name: str = ""
    expected_duration: float = 0.0
    actual_duration: float = 0.0


@dataclass
class PredictionCompleted(DomainEvent):
    """Event: A prediction has been made."""

    log_id: UUID = field(default_factory=uuid4)
    prediction_type: str = ""
    case_id: Optional[str] = None
    predicted_value: Any = None
