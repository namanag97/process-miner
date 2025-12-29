"""Domain Entities - Core business objects with identity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from src.domain.value_objects import (
    ActivityName,
    ConformanceResultState,
    Deviation,
    Duration,
    EventLogState,
    LogStatistics,
    MinerType,
    ModelFormat,
    ProcessModelState,
    ResourceId,
    Timestamp,
)


@dataclass
class ProcessEvent:
    """
    A single event in a process log.
    Represents one activity occurrence in a case.
    """

    id: UUID
    case_id: str
    activity: ActivityName
    timestamp: Timestamp
    resource: Optional[ResourceId] = None
    attributes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        case_id: str,
        activity: str,
        timestamp: datetime,
        resource: Optional[str] = None,
        **attributes,
    ) -> "ProcessEvent":
        return cls(
            id=uuid4(),
            case_id=case_id,
            activity=ActivityName(activity),
            timestamp=Timestamp(timestamp),
            resource=ResourceId(resource) if resource else None,
            attributes=attributes,
        )


@dataclass
class ProcessCase:
    """
    A single case/trace in a process log.
    Contains an ordered sequence of events.
    """

    id: UUID
    case_id: str
    events: list[ProcessEvent] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    @property
    def activities(self) -> list[str]:
        """Get ordered list of activity names."""
        return [str(e.activity) for e in self.events]

    @property
    def variant_key(self) -> str:
        """Get the variant key (comma-separated activities)."""
        return ",".join(self.activities)

    @property
    def duration(self) -> Optional[Duration]:
        """Get case duration from first to last event."""
        if len(self.events) < 2:
            return None
        sorted_events = sorted(self.events, key=lambda e: e.timestamp.value)
        return Duration.between(sorted_events[0].timestamp, sorted_events[-1].timestamp)

    @property
    def start_time(self) -> Optional[Timestamp]:
        if not self.events:
            return None
        return min(e.timestamp for e in self.events)

    @property
    def end_time(self) -> Optional[Timestamp]:
        if not self.events:
            return None
        return max(e.timestamp for e in self.events)

    @classmethod
    def create(cls, case_id: str, **attributes) -> "ProcessCase":
        return cls(id=uuid4(), case_id=case_id, attributes=attributes)

    def add_event(self, event: ProcessEvent) -> None:
        """Add an event to the case."""
        self.events.append(event)
        self.events.sort(key=lambda e: e.timestamp.value)


@dataclass
class Variant:
    """
    A unique sequence of activities observed in the log.
    """

    id: UUID
    activities: tuple[str, ...]
    case_count: int
    case_ids: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        return ",".join(self.activities)

    @property
    def length(self) -> int:
        return len(self.activities)

    @property
    def frequency(self) -> float:
        """Relative frequency (requires total cases to calculate properly)."""
        return self.case_count

    @classmethod
    def from_cases(cls, cases: list[ProcessCase]) -> list["Variant"]:
        """Extract variants from a list of cases."""
        variant_map: dict[str, list[str]] = {}

        for case in cases:
            key = case.variant_key
            if key not in variant_map:
                variant_map[key] = []
            variant_map[key].append(case.case_id)

        variants = []
        for key, case_ids in variant_map.items():
            activities = tuple(key.split(",")) if key else tuple()
            variants.append(
                cls(
                    id=uuid4(),
                    activities=activities,
                    case_count=len(case_ids),
                    case_ids=case_ids,
                )
            )

        return sorted(variants, key=lambda v: v.case_count, reverse=True)


@dataclass
class EventLog:
    """
    A collection of process cases representing an event log.
    This is the main input for process mining operations.
    """

    id: UUID
    name: str
    cases: list[ProcessCase] = field(default_factory=list)
    source_file: Optional[str] = None
    state: EventLogState = EventLogState.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_events(self) -> int:
        return sum(len(case.events) for case in self.cases)

    @property
    def total_cases(self) -> int:
        return len(self.cases)

    @property
    def activities(self) -> set[str]:
        """Get all unique activities in the log."""
        activities = set()
        for case in self.cases:
            activities.update(case.activities)
        return activities

    @property
    def variants(self) -> list[Variant]:
        """Extract all variants from the log."""
        return Variant.from_cases(self.cases)

    @property
    def resources(self) -> set[str]:
        """Get all unique resources in the log."""
        resources = set()
        for case in self.cases:
            for event in case.events:
                if event.resource:
                    resources.add(str(event.resource))
        return resources

    @property
    def date_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        """Get the time range of the log."""
        all_timestamps = []
        for case in self.cases:
            for event in case.events:
                all_timestamps.append(event.timestamp.value)

        if not all_timestamps:
            return None, None
        return min(all_timestamps), max(all_timestamps)

    @classmethod
    def create(cls, name: str, source_file: Optional[str] = None) -> "EventLog":
        return cls(id=uuid4(), name=name, source_file=source_file)

    def add_case(self, case: ProcessCase) -> None:
        """Add a case to the log."""
        self.cases.append(case)

    def get_case(self, case_id: str) -> Optional[ProcessCase]:
        """Get a case by its ID."""
        for case in self.cases:
            if case.case_id == case_id:
                return case
        return None

    def get_statistics(self) -> LogStatistics:
        """Compute and return log statistics."""
        start, end = self.date_range

        # Calculate average case duration
        durations = [c.duration.total_seconds for c in self.cases if c.duration]
        avg_duration = sum(durations) / len(durations) if durations else None

        return LogStatistics(
            event_count=self.total_events,
            case_count=self.total_cases,
            activity_count=len(self.activities),
            variant_count=len(self.variants),
            resource_count=len(self.resources),
            date_range_start=start,
            date_range_end=end,
            avg_case_duration_seconds=avg_duration,
        )

    def transition_to(self, new_state: EventLogState) -> None:
        """Transition log to a new state with validation."""
        valid_transitions = {
            EventLogState.DRAFT: [EventLogState.PARSING, EventLogState.FAILED],
            EventLogState.PARSING: [EventLogState.VALIDATING, EventLogState.FAILED],
            EventLogState.VALIDATING: [EventLogState.READY, EventLogState.FAILED],
            EventLogState.READY: [EventLogState.ARCHIVED],
            EventLogState.FAILED: [EventLogState.DRAFT],
            EventLogState.ARCHIVED: [],
        }
        if new_state not in valid_transitions.get(self.state, []):
            raise ValueError(f"Invalid state transition: {self.state} -> {new_state}")
        self.state = new_state


@dataclass
class ProcessModel:
    """
    A process model discovered from an event log.
    Can be Petri net, BPMN, Process Tree, or DFG.
    """

    id: UUID
    name: str
    format: ModelFormat
    source_log_id: Optional[UUID] = None
    miner_type: Optional[MinerType] = None
    state: ProcessModelState = ProcessModelState.DISCOVERING
    model_data: Optional[Any] = None  # PM4Py model object
    serialized: Optional[bytes] = None  # Serialized model for storage
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        name: str,
        format: ModelFormat,
        source_log_id: Optional[UUID] = None,
        miner_type: Optional[MinerType] = None,
    ) -> "ProcessModel":
        return cls(
            id=uuid4(),
            name=name,
            format=format,
            source_log_id=source_log_id,
            miner_type=miner_type,
        )


@dataclass
class ConformanceResult:
    """
    Result of conformance checking between a log and a model.
    """

    id: UUID
    log_id: UUID
    model_id: UUID
    fitness: float
    precision: Optional[float] = None
    generalization: Optional[float] = None
    simplicity: Optional[float] = None
    state: ConformanceResultState = ConformanceResultState.REQUESTED
    deviations: list[Deviation] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_conformant(self) -> bool:
        return self.fitness >= 0.95

    @classmethod
    def create(
        cls,
        log_id: UUID,
        model_id: UUID,
        fitness: float,
    ) -> "ConformanceResult":
        return cls(id=uuid4(), log_id=log_id, model_id=model_id, fitness=fitness)


@dataclass
class PerformanceMetrics:
    """
    Performance analysis results for a process.
    """

    id: UUID
    log_id: UUID
    avg_case_duration: Duration
    median_case_duration: Duration
    min_case_duration: Duration
    max_case_duration: Duration
    bottleneck_activities: list[str] = field(default_factory=list)
    waiting_times: dict[str, float] = field(default_factory=dict)
    processing_times: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
