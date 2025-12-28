"""Domain Value Objects - Immutable types representing domain concepts."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class ProcessMiningError(Exception):
    """Base exception for domain errors."""
    pass


class ValidationError(ProcessMiningError):
    """Validation error in domain."""
    pass


class ActivityName(str):
    """Value object representing an activity name."""
    
    def __new__(cls, value: str):
        if not value or not value.strip():
            raise ValidationError("Activity name cannot be empty")
        instance = super().__new__(cls, value.strip())
        return instance


class ResourceId(str):
    """Value object representing a resource/user identifier."""
    
    def __new__(cls, value: str):
        instance = super().__new__(cls, value.strip() if value else "unknown")
        return instance


@dataclass(frozen=True)
class Timestamp:
    """Value object representing an event timestamp."""
    value: datetime
    
    def __post_init__(self):
        if self.value is None:
            raise ValidationError("Timestamp cannot be None")
    
    @classmethod
    def now(cls) -> "Timestamp":
        return cls(datetime.utcnow())
    
    @classmethod
    def from_string(cls, date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> "Timestamp":
        return cls(datetime.strptime(date_str, fmt))
    
    def to_iso(self) -> str:
        return self.value.isoformat()


@dataclass(frozen=True)
class Duration:
    """Value object representing a time duration."""
    value: timedelta
    
    @property
    def total_seconds(self) -> float:
        return self.value.total_seconds()
    
    @property
    def total_minutes(self) -> float:
        return self.value.total_seconds() / 60
    
    @property
    def total_hours(self) -> float:
        return self.value.total_seconds() / 3600
    
    @property
    def total_days(self) -> float:
        return self.value.days + self.value.seconds / 86400
    
    @classmethod
    def from_seconds(cls, seconds: float) -> "Duration":
        return cls(timedelta(seconds=seconds))
    
    @classmethod
    def between(cls, start: Timestamp, end: Timestamp) -> "Duration":
        return cls(end.value - start.value)
    
    def __str__(self) -> str:
        total = int(self.total_seconds)
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@dataclass(frozen=True)
class FitnessScore:
    """Value object representing conformance fitness (0.0 - 1.0)."""
    value: float
    
    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise ValidationError(f"Fitness score must be between 0 and 1, got {self.value}")
    
    @property
    def percentage(self) -> float:
        return self.value * 100
    
    @property
    def is_perfect(self) -> bool:
        return self.value == 1.0
    
    def __str__(self) -> str:
        return f"{self.percentage:.1f}%"


@dataclass(frozen=True)
class PrecisionScore:
    """Value object representing conformance precision (0.0 - 1.0)."""
    value: float
    
    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise ValidationError(f"Precision score must be between 0 and 1, got {self.value}")


@dataclass(frozen=True)
class GeneralizationScore:
    """Value object representing conformance generalization (0.0 - 1.0)."""
    value: float


@dataclass(frozen=True)
class SimplicityScore:
    """Value object representing model simplicity (0.0 - 1.0)."""
    value: float


class MinerType(str, Enum):
    """Types of process discovery miners."""
    ALPHA = "alpha"
    ALPHA_PLUS = "alpha_plus"
    INDUCTIVE = "inductive"
    INDUCTIVE_INFREQUENT = "inductive_infrequent"
    HEURISTICS = "heuristics"
    DFG = "dfg"


class ModelFormat(str, Enum):
    """Process model output formats."""
    PETRI_NET = "petri_net"
    BPMN = "bpmn"
    PROCESS_TREE = "process_tree"
    DFG = "dfg"


class ConformanceMethod(str, Enum):
    """Conformance checking methods."""
    TOKEN_REPLAY = "token_replay"
    ALIGNMENT = "alignment"


class LogFormat(str, Enum):
    """Supported event log formats."""
    CSV = "csv"
    XES = "xes"
    PARQUET = "parquet"


@dataclass(frozen=True)
class ColumnMapping:
    """Mapping of CSV columns to event log fields."""
    case_id: str = "case:concept:name"
    activity: str = "concept:name"
    timestamp: str = "time:timestamp"
    resource: Optional[str] = None
    cost: Optional[str] = None
    transformation: Optional[str] = None  # Optional transformation rule
    
    def to_dict(self) -> dict:
        return {
            "case:concept:name": self.case_id,
            "concept:name": self.activity,
            "time:timestamp": self.timestamp,
            **({"org:resource": self.resource} if self.resource else {}),
        }


# =============================================================================
# STATE ENUMS (Phase 2 Enhancement)
# =============================================================================

class EventLogState(str, Enum):
    """State machine for EventLog aggregate."""
    DRAFT = "draft"
    PARSING = "parsing"
    VALIDATING = "validating"
    READY = "ready"
    FAILED = "failed"
    ARCHIVED = "archived"


class ProcessModelState(str, Enum):
    """State machine for ProcessModel aggregate."""
    DISCOVERING = "discovering"
    DISCOVERED = "discovered"
    ANNOTATED = "annotated"
    SAVED = "saved"
    FAILED = "failed"


class ConformanceResultState(str, Enum):
    """State machine for ConformanceResult aggregate."""
    REQUESTED = "requested"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DeviationType(str, Enum):
    """Types of conformance deviations."""
    MISSING = "missing"           # Expected activity not found
    UNEXPECTED = "unexpected"     # Activity not in model
    WRONG_ORDER = "wrong_order"   # Activity in wrong sequence
    WRONG_RESOURCE = "wrong_resource"  # Wrong resource performed activity


class Severity(str, Enum):
    """Severity levels for issues and deviations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SourceType(str, Enum):
    """Source types for event logs."""
    UPLOAD = "upload"
    CONNECTOR = "connector"
    API = "api"


# =============================================================================
# NEW VALUE OBJECTS (Phase 2 Enhancement)
# =============================================================================

@dataclass(frozen=True)
class LogStatistics:
    """Statistics for an event log."""
    event_count: int
    case_count: int
    activity_count: int
    variant_count: int
    resource_count: int = 0
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    avg_case_duration_seconds: Optional[float] = None
    
    @classmethod
    def empty(cls) -> "LogStatistics":
        return cls(
            event_count=0,
            case_count=0,
            activity_count=0,
            variant_count=0,
        )


@dataclass(frozen=True)
class QualityIssue:
    """A single quality issue detected during validation."""
    issue_type: str
    message: str
    severity: Severity
    affected_rows: int = 0
    column: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "issue_type": self.issue_type,
            "message": self.message,
            "severity": self.severity.value,
            "affected_rows": self.affected_rows,
            "column": self.column,
        }


@dataclass(frozen=True)
class QualityReport:
    """Quality assessment report for an event log."""
    completeness_score: float  # 0.0 - 1.0
    validity_score: float      # 0.0 - 1.0
    issues: tuple[QualityIssue, ...] = ()
    
    @property
    def overall_score(self) -> float:
        """Calculate overall quality score."""
        return (self.completeness_score + self.validity_score) / 2
    
    @property
    def is_valid(self) -> bool:
        """Check if log passes minimum quality threshold."""
        return self.overall_score >= 0.7 and not any(
            issue.severity == Severity.CRITICAL for issue in self.issues
        )
    
    def to_dict(self) -> dict:
        return {
            "completeness_score": self.completeness_score,
            "validity_score": self.validity_score,
            "overall_score": self.overall_score,
            "is_valid": self.is_valid,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True)
class Deviation:
    """A conformance deviation between log and model."""
    case_id: str
    deviation_type: DeviationType
    expected_activity: Optional[str] = None
    actual_activity: Optional[str] = None
    position: int = 0
    severity: Severity = Severity.MEDIUM
    
    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "deviation_type": self.deviation_type.value,
            "expected_activity": self.expected_activity,
            "actual_activity": self.actual_activity,
            "position": self.position,
            "severity": self.severity.value,
        }


@dataclass(frozen=True)
class DeviationSummary:
    """Summary of deviations from conformance checking."""
    total_deviations: int
    deviations_by_type: dict[str, int]
    deviations_by_activity: dict[str, int]
    deviation_rate: float  # 0.0 - 1.0
    most_deviating_cases: tuple[str, ...] = ()
    
    def to_dict(self) -> dict:
        return {
            "total_deviations": self.total_deviations,
            "deviations_by_type": self.deviations_by_type,
            "deviations_by_activity": self.deviations_by_activity,
            "deviation_rate": self.deviation_rate,
            "most_deviating_cases": list(self.most_deviating_cases),
        }


@dataclass(frozen=True)
class FilterConfig:
    """Configuration for filtering during process discovery."""
    variant_threshold: Optional[float] = None  # 0.0 - 1.0, filter rare variants
    activity_threshold: Optional[int] = None   # Min occurrences to include
    path_threshold: Optional[int] = None       # Min path occurrences
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "variant_threshold": self.variant_threshold,
            "activity_threshold": self.activity_threshold,
            "path_threshold": self.path_threshold,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }


# =============================================================================
# TRANSITION / DFG VALUE OBJECTS (Process Perspective)
# =============================================================================

@dataclass(frozen=True)
class Transition:
    """
    Represents an edge in the Directly-Follows Graph (DFG).
    Maps to the Transition concept in the Process Mining Ontology.
    """
    source_activity: str
    target_activity: str
    frequency: int
    probability: float  # 0.0 - 1.0
    avg_duration_seconds: float = 0.0
    min_duration_seconds: float = 0.0
    max_duration_seconds: float = 0.0
    
    @property
    def edge_key(self) -> str:
        """Unique key for this transition."""
        return f"{self.source_activity} -> {self.target_activity}"
    
    def to_dict(self) -> dict:
        return {
            "source_activity": self.source_activity,
            "target_activity": self.target_activity,
            "frequency": self.frequency,
            "probability": self.probability,
            "avg_duration_seconds": self.avg_duration_seconds,
            "min_duration_seconds": self.min_duration_seconds,
            "max_duration_seconds": self.max_duration_seconds,
        }


class GatewayType(str, Enum):
    """Types of process gateways (routing logic)."""
    XOR = "xor"      # Exclusive OR - one path
    AND = "and"      # Parallel - all paths
    OR = "or"        # Inclusive OR - one or more paths


class GatewayDirection(str, Enum):
    """Direction of gateway in process flow."""
    SPLIT = "split"  # One input, multiple outputs
    JOIN = "join"    # Multiple inputs, one output


@dataclass(frozen=True)
class Gateway:
    """
    Represents a routing point in the process.
    Maps to the Gateway concept in the Process Mining Ontology.
    """
    activity: str  # Activity at which split/join occurs
    gateway_type: GatewayType
    direction: GatewayDirection
    branches: tuple[str, ...] = ()  # Connected activities
    
    def to_dict(self) -> dict:
        return {
            "activity": self.activity,
            "gateway_type": self.gateway_type.value,
            "direction": self.direction.value,
            "branches": list(self.branches),
        }


class ActivityTypeEnum(str, Enum):
    """Types of process activities."""
    TASK = "task"
    DECISION = "decision"
    START = "start"
    END = "end"
    INTERMEDIATE = "intermediate"
    SUBPROCESS = "subprocess"


@dataclass(frozen=True)
class ActivityTypeInfo:
    """
    Rich activity type information.
    Maps to the ActivityType concept in the Process Mining Ontology.
    """
    name: str
    code: Optional[str] = None
    category: Optional[str] = None
    activity_type: ActivityTypeEnum = ActivityTypeEnum.TASK
    is_automated: bool = False
    is_value_adding: bool = True
    occurrence_count: int = 0
    avg_processing_time_seconds: float = 0.0
    avg_cost: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "code": self.code,
            "category": self.category,
            "activity_type": self.activity_type.value,
            "is_automated": self.is_automated,
            "is_value_adding": self.is_value_adding,
            "occurrence_count": self.occurrence_count,
            "avg_processing_time_seconds": self.avg_processing_time_seconds,
            "avg_cost": self.avg_cost,
        }


class VersionStatus(str, Enum):
    """Status of a version."""
    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class LogVersionInfo:
    """
    Event log version metadata.
    Enables versioning of event log datasets.
    """
    version_number: int
    label: Optional[str] = None
    notes: Optional[str] = None
    status: VersionStatus = VersionStatus.DRAFT
    observation_start: Optional[datetime] = None
    observation_end: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "version_number": self.version_number,
            "label": self.label,
            "notes": self.notes,
            "status": self.status.value,
            "observation_start": self.observation_start.isoformat() if self.observation_start else None,
            "observation_end": self.observation_end.isoformat() if self.observation_end else None,
        }


@dataclass(frozen=True)
class VariantInfo:
    """
    Enhanced variant information with performance metrics.
    Maps to the ProcessVariant concept in the ERD.
    """
    variant_hash: str
    activity_trace: str  # A->B->C->D format
    length: int
    case_count: int
    frequency_percent: float
    avg_duration_seconds: Optional[float] = None
    median_duration_seconds: Optional[float] = None
    min_duration_seconds: Optional[float] = None
    max_duration_seconds: Optional[float] = None
    avg_cost: Optional[float] = None
    is_happy_path: bool = False
    is_compliant: bool = True
    rank: int = 0
    
    @classmethod
    def from_activities(cls, activities: tuple[str, ...], case_count: int, total_cases: int, rank: int = 0) -> "VariantInfo":
        import hashlib
        trace = "->".join(activities)
        variant_hash = hashlib.md5(trace.encode()).hexdigest()
        return cls(
            variant_hash=variant_hash,
            activity_trace=trace,
            length=len(activities),
            case_count=case_count,
            frequency_percent=(case_count / total_cases * 100) if total_cases > 0 else 0.0,
            rank=rank,
        )
    
    def to_dict(self) -> dict:
        return {
            "variant_hash": self.variant_hash,
            "activity_trace": self.activity_trace,
            "length": self.length,
            "case_count": self.case_count,
            "frequency_percent": self.frequency_percent,
            "avg_duration_seconds": self.avg_duration_seconds,
            "median_duration_seconds": self.median_duration_seconds,
            "min_duration_seconds": self.min_duration_seconds,
            "max_duration_seconds": self.max_duration_seconds,
            "avg_cost": self.avg_cost,
            "is_happy_path": self.is_happy_path,
            "is_compliant": self.is_compliant,
            "rank": self.rank,
        }


# =============================================================================
# SLA VALUE OBJECTS (Time Perspective)
# =============================================================================

class SLAScope(str, Enum):
    """Scope of SLA application."""
    CASE = "case"           # Applies to entire case duration
    ACTIVITY = "activity"   # Applies to specific activity duration
    TRANSITION = "transition"  # Applies to time between activities


@dataclass(frozen=True)
class SLADefinition:
    """
    Service Level Agreement definition.
    Maps to the SLA concept in the Process Mining Ontology.
    """
    name: str
    target_duration_seconds: float
    warning_threshold_seconds: float
    scope: SLAScope
    activity_name: Optional[str] = None  # Required if scope is ACTIVITY
    source_activity: Optional[str] = None  # Required if scope is TRANSITION
    target_activity: Optional[str] = None  # Required if scope is TRANSITION
    
    def __post_init__(self):
        if self.scope == SLAScope.ACTIVITY and not self.activity_name:
            raise ValidationError("Activity name required for activity-scoped SLA")
        if self.scope == SLAScope.TRANSITION and not (self.source_activity and self.target_activity):
            raise ValidationError("Source and target activities required for transition-scoped SLA")
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "target_duration_seconds": self.target_duration_seconds,
            "warning_threshold_seconds": self.warning_threshold_seconds,
            "scope": self.scope.value,
            "activity_name": self.activity_name,
            "source_activity": self.source_activity,
            "target_activity": self.target_activity,
        }


@dataclass(frozen=True)
class SLAStatus(str, Enum):
    """Status of SLA compliance."""
    MET = "met"
    WARNING = "warning"
    BREACHED = "breached"


@dataclass(frozen=True)
class SLAResult:
    """Result of SLA check for a specific case."""
    case_id: str
    sla_name: str
    actual_duration_seconds: float
    target_duration_seconds: float
    status: str  # SLAStatus value
    exceeded_by_seconds: float = 0.0
    
    @property
    def compliance_percentage(self) -> float:
        """How close to target (100% = exactly at target)."""
        if self.target_duration_seconds == 0:
            return 0.0
        return min(100.0, (self.target_duration_seconds / max(self.actual_duration_seconds, 0.001)) * 100)
    
    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "sla_name": self.sla_name,
            "actual_duration_seconds": self.actual_duration_seconds,
            "target_duration_seconds": self.target_duration_seconds,
            "status": self.status,
            "exceeded_by_seconds": self.exceeded_by_seconds,
            "compliance_percentage": self.compliance_percentage,
        }


# =============================================================================
# RESOURCE PERSPECTIVE VALUE OBJECTS
# =============================================================================

@dataclass(frozen=True)
class ResourceProfile:
    """
    Profile of a resource/user in the process.
    Enhanced Resource concept from the Process Mining Ontology.
    """
    identifier: str
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    total_activities: int = 0
    total_cases: int = 0
    avg_activities_per_case: float = 0.0
    most_frequent_activities: tuple[str, ...] = ()
    
    def to_dict(self) -> dict:
        return {
            "identifier": self.identifier,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "total_activities": self.total_activities,
            "total_cases": self.total_cases,
            "avg_activities_per_case": self.avg_activities_per_case,
            "most_frequent_activities": list(self.most_frequent_activities),
        }


@dataclass(frozen=True)
class Handoff:
    """
    Represents a resource handoff in the process.
    Maps to the Handoff concept in the Process Mining Ontology.
    """
    from_resource: str
    to_resource: str
    activity: str  # Activity at which handoff occurs
    frequency: int
    avg_handoff_time_seconds: float = 0.0
    
    @property
    def handoff_key(self) -> str:
        """Unique key for this handoff."""
        return f"{self.from_resource} -> {self.to_resource} @ {self.activity}"
    
    def to_dict(self) -> dict:
        return {
            "from_resource": self.from_resource,
            "to_resource": self.to_resource,
            "activity": self.activity,
            "frequency": self.frequency,
            "avg_handoff_time_seconds": self.avg_handoff_time_seconds,
        }
