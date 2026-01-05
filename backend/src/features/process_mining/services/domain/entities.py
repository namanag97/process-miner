"""Domain Entities - Objects with identity and behavior.

Entities have:
- Unique identity (ID that persists across state changes)
- Mutable state (unlike value objects)
- Domain behavior (methods that encapsulate business logic)
- Invariant enforcement

The main aggregate root is DatasetAggregate, which owns ProcessCases and
provides PM4Py log caching for performance optimization.
"""

import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from src.features.process_mining.services.domain.value_objects import (
    ActivitySequence,
    CaseId,
    ProcessStatistics,
    TimeRange,
    VariantStats,
)
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

# Avoid circular imports - PM4Py types only for type hints
if TYPE_CHECKING:
    from pm4py.objects.log.obj import EventLog as PM4PyLog


# =============================================================================
# Process Event Entity
# =============================================================================


@dataclass
class ProcessEvent:
    """Single event in a process case.

    Events are the atomic units of process mining. Each event represents
    an activity occurrence at a specific time.
    """

    id: str
    activity: str
    timestamp: datetime
    resource: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.activity or not self.activity.strip():
            raise ValueError("Event activity cannot be empty")

    @property
    def has_resource(self) -> bool:
        """True if this event has resource attribution."""
        return self.resource is not None and self.resource.strip() != ""


# =============================================================================
# Process Case Entity
# =============================================================================


@dataclass
class ProcessCase:
    """A case/trace in an event log.

    A case is a sequence of events that belong to the same process instance.
    This entity provides computed properties for variant analysis, duration,
    and rework detection.

    Invariants:
    - Must have at least one event
    - Events must be ordered by timestamp
    """

    case_id: CaseId
    events: list[ProcessEvent] = field(default_factory=list)

    def __post_init__(self):
        # Sort events by timestamp on creation
        self.events = sorted(self.events, key=lambda e: e.timestamp)

    @classmethod
    def create(cls, case_id: str, events: list[ProcessEvent]) -> "ProcessCase":
        """Factory method for creating a case with validation."""
        return cls(case_id=CaseId(case_id), events=events)

    # --- Computed Properties ---

    @property
    def variant(self) -> ActivitySequence:
        """Get the activity sequence (variant) for this case."""
        if not self.events:
            raise ValueError("Cannot compute variant for empty case")
        return ActivitySequence.from_list([e.activity for e in self.events])

    @property
    def time_range(self) -> TimeRange | None:
        """Get the time range from first to last event."""
        if not self.events:
            return None
        return TimeRange(start=self.events[0].timestamp, end=self.events[-1].timestamp)

    @property
    def duration_seconds(self) -> float | None:
        """Duration from first to last event in seconds."""
        tr = self.time_range
        return tr.duration_seconds if tr else None

    @property
    def event_count(self) -> int:
        """Number of events in this case."""
        return len(self.events)

    @property
    def has_rework(self) -> bool:
        """True if any activity appears more than once."""
        return self.variant.has_rework if self.events else False

    @property
    def start_activity(self) -> str | None:
        """First activity in the case."""
        return self.events[0].activity if self.events else None

    @property
    def end_activity(self) -> str | None:
        """Last activity in the case."""
        return self.events[-1].activity if self.events else None

    @property
    def resources(self) -> set[str]:
        """Set of unique resources involved in this case."""
        return {e.resource for e in self.events if e.resource}

    # --- Domain Behavior ---

    def get_activity_frequency(self, activity: str) -> int:
        """Count occurrences of an activity in this case."""
        return sum(1 for e in self.events if e.activity == activity)

    def get_events_for_activity(self, activity: str) -> list[ProcessEvent]:
        """Get all events for a specific activity."""
        return [e for e in self.events if e.activity == activity]

    def contains_activity(self, activity: str) -> bool:
        """Check if case contains a specific activity."""
        return any(e.activity == activity for e in self.events)

    def get_prefix(self, length: int) -> list[ProcessEvent]:
        """Get first N events (prefix)."""
        return self.events[:length]

    def get_suffix(self, length: int) -> list[ProcessEvent]:
        """Get last N events (suffix)."""
        return self.events[-length:]


# =============================================================================
# Event Log Aggregate Root
# =============================================================================


class DatasetAggregate:
    """Aggregate root for event logs.

    This is the primary aggregate in the process mining domain. It owns:
    - ProcessCases (and their events)
    - PM4Py log cache for performance
    - DFG and variant caches

    The aggregate ensures consistency and provides domain behavior for
    filtering, analysis, and PM4Py integration.

    Key Features:
    - Lazy PM4Py log conversion with caching
    - Cached variant computation
    - Filtering operations that return new aggregates

    Usage:
        log = DatasetAggregate(id="log-1", name="Order Process", cases=cases)

        # PM4Py operations use cached log
        pm4py_log = log.to_pm4py_log()  # First call: converts
        pm4py_log = log.to_pm4py_log()  # Second call: cache hit

        # Filtering returns new aggregate
        filtered = log.filter_by_activities(include=["Submit", "Approve"])
    """

    def __init__(
        self,
        id: str,
        name: str,
        cases: list[ProcessCase],
        source_format: str = "csv",
        source_file: str | None = None,
        created_at: datetime | None = None,
    ):
        self._id = id
        self._name = name
        self._cases = cases
        self._source_format = source_format
        self._source_file = source_file
        self._created_at = created_at or datetime.utcnow()

        # Caches (lazy-loaded)
        self._pm4py_cache: PM4PyLog | None = None
        self._variants_cache: dict[ActivitySequence, list[ProcessCase]] | None = None
        self._statistics_cache: ProcessStatistics | None = None
        self._activities_cache: set[str] | None = None

    # --- Identity ---

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def source_format(self) -> str:
        return self._source_format

    @property
    def source_file(self) -> str | None:
        return self._source_file

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # --- Basic Metrics (O(1) after first computation) ---

    @property
    def cases(self) -> list[ProcessCase]:
        """Access to cases (readonly view encouraged)."""
        return self._cases

    @property
    def total_cases(self) -> int:
        return len(self._cases)

    @property
    def total_events(self) -> int:
        return sum(c.event_count for c in self._cases)

    @property
    def activities(self) -> set[str]:
        """Set of unique activities in the log."""
        if self._activities_cache is None:
            self._activities_cache = {e.activity for c in self._cases for e in c.events}
        return self._activities_cache

    @property
    def total_activities(self) -> int:
        return len(self.activities)

    @property
    def resources(self) -> set[str]:
        """Set of unique resources in the log."""
        return {e.resource for c in self._cases for e in c.events if e.resource}

    # --- Variant Analysis (Cached) ---

    @property
    def variants(self) -> dict[ActivitySequence, list[ProcessCase]]:
        """Get variants mapped to their cases (cached)."""
        if self._variants_cache is None:
            self._variants_cache = self._compute_variants()
        return self._variants_cache

    @property
    def total_variants(self) -> int:
        return len(self.variants)

    def _compute_variants(self) -> dict[ActivitySequence, list[ProcessCase]]:
        """Compute variant groupings."""
        result: dict[ActivitySequence, list[ProcessCase]] = defaultdict(list)
        for case in self._cases:
            if case.events:
                result[case.variant].append(case)
        return dict(result)

    def get_variant_stats(self, top_n: int | None = None) -> list[VariantStats]:
        """Get variant statistics sorted by frequency."""
        stats = []
        for sequence, cases in self.variants.items():
            durations = [c.duration_seconds for c in cases if c.duration_seconds]
            avg_duration = sum(durations) / len(durations) if durations else None

            stats.append(
                VariantStats(
                    sequence=sequence,
                    case_count=len(cases),
                    total_cases=self.total_cases,
                    avg_duration_seconds=avg_duration,
                )
            )

        # Sort by case count descending
        stats.sort(key=lambda v: v.case_count, reverse=True)

        if top_n:
            return stats[:top_n]
        return stats

    # --- Start/End Activity Analysis ---

    def get_start_activities(self) -> dict[str, int]:
        """Get start activities with frequencies."""
        counts: dict[str, int] = defaultdict(int)
        for case in self._cases:
            if case.start_activity:
                counts[case.start_activity] += 1
        return dict(counts)

    def get_end_activities(self) -> dict[str, int]:
        """Get end activities with frequencies."""
        counts: dict[str, int] = defaultdict(int)
        for case in self._cases:
            if case.end_activity:
                counts[case.end_activity] += 1
        return dict(counts)

    # --- Statistics (Cached) ---

    @property
    def statistics(self) -> ProcessStatistics:
        """Get aggregate statistics (cached)."""
        if self._statistics_cache is None:
            self._statistics_cache = self._compute_statistics()
        return self._statistics_cache

    def _compute_statistics(self) -> ProcessStatistics:
        """Compute aggregate statistics."""
        durations = [c.duration_seconds for c in self._cases if c.duration_seconds is not None]

        return ProcessStatistics(
            total_events=self.total_events,
            total_cases=self.total_cases,
            total_activities=self.total_activities,
            total_variants=self.total_variants,
            avg_case_duration_seconds=sum(durations) / len(durations) if durations else None,
            min_case_duration_seconds=min(durations) if durations else None,
            max_case_duration_seconds=max(durations) if durations else None,
        )

    # --- PM4Py Integration (Cached) ---

    def to_pm4py_log(self) -> "PM4PyLog":
        """Convert to PM4Py EventLog with caching.

        This is the KEY OPTIMIZATION - the PM4Py log is built once and reused
        for all subsequent operations (discovery, conformance, etc.).

        Returns:
            PM4Py EventLog object
        """
        if self._pm4py_cache is not None:
            logger.debug("pm4py_cache_hit", log_id=self._id)
            return self._pm4py_cache

        start_time = time.perf_counter()

        # Import here to avoid circular dependency
        from pm4py.objects.log.obj import Event as PM4PyEvent
        from pm4py.objects.log.obj import EventLog as PM4PyLog
        from pm4py.objects.log.obj import Trace

        pm4py_log = PM4PyLog()

        for case in self._cases:
            trace = Trace()
            trace.attributes["concept:name"] = case.case_id.value

            for event in case.events:
                pm4py_event = PM4PyEvent()
                pm4py_event["concept:name"] = event.activity
                pm4py_event["time:timestamp"] = event.timestamp

                if event.resource:
                    pm4py_event["org:resource"] = event.resource

                # Add additional attributes
                for key, value in event.attributes.items():
                    pm4py_event[key] = value

                trace.append(pm4py_event)

            pm4py_log.append(trace)

        self._pm4py_cache = pm4py_log

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "pm4py_log_built",
            log_id=self._id,
            cases=self.total_cases,
            events=self.total_events,
            duration_ms=round(duration_ms, 2),
        )

        return pm4py_log

    def invalidate_cache(self) -> None:
        """Invalidate all caches (call after mutations)."""
        self._pm4py_cache = None
        self._variants_cache = None
        self._statistics_cache = None
        self._activities_cache = None
        logger.debug("cache_invalidated", log_id=self._id)

    # --- Filtering (Returns New Aggregates) ---

    def filter(
        self, predicate: Callable[[ProcessCase], bool], suffix: str = "filtered"
    ) -> "DatasetAggregate":
        """Filter cases using a predicate function.

        Returns a NEW aggregate with only matching cases.
        The original aggregate is unchanged.
        """
        filtered_cases = [c for c in self._cases if predicate(c)]
        return DatasetAggregate(
            id=f"{self._id}_{suffix}",
            name=f"{self._name} ({suffix})",
            cases=filtered_cases,
            source_format=self._source_format,
        )

    def filter_by_time(self, time_range: TimeRange) -> "DatasetAggregate":
        """Filter to cases within a time range."""

        def in_range(case: ProcessCase) -> bool:
            if not case.events:
                return False
            first_event_time = case.events[0].timestamp
            return time_range.start <= first_event_time <= time_range.end

        return self.filter(in_range, suffix="time_filtered")

    def filter_by_variant(self, variant: ActivitySequence) -> "DatasetAggregate":
        """Filter to cases with a specific variant."""
        return self.filter(lambda c: c.events and c.variant == variant, suffix="variant_filtered")

    def filter_by_activities(
        self,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> "DatasetAggregate":
        """Filter cases containing/excluding specific activities."""

        def matches(case: ProcessCase) -> bool:
            case_activities = {e.activity for e in case.events}

            if include and not case_activities.issuperset(include):
                return False
            return not (exclude and case_activities.intersection(exclude))

        return self.filter(matches, suffix="activity_filtered")

    def filter_by_start_activity(self, activities: list[str]) -> "DatasetAggregate":
        """Filter to cases starting with specific activities."""
        return self.filter(lambda c: c.start_activity in activities, suffix="start_filtered")

    def filter_by_end_activity(self, activities: list[str]) -> "DatasetAggregate":
        """Filter to cases ending with specific activities."""
        return self.filter(lambda c: c.end_activity in activities, suffix="end_filtered")

    def filter_by_duration(
        self,
        min_seconds: float | None = None,
        max_seconds: float | None = None,
    ) -> "DatasetAggregate":
        """Filter cases by duration."""

        def in_range(case: ProcessCase) -> bool:
            duration = case.duration_seconds
            if duration is None:
                return False
            if min_seconds is not None and duration < min_seconds:
                return False
            return not (max_seconds is not None and duration > max_seconds)

        return self.filter(in_range, suffix="duration_filtered")

    def filter_top_variants(self, k: int) -> "DatasetAggregate":
        """Filter to cases belonging to top K variants by frequency."""
        top_variants = {v.sequence for v in self.get_variant_stats(top_n=k)}
        return self.filter(
            lambda c: c.events and c.variant in top_variants, suffix=f"top{k}_variants"
        )

    # --- Equality & Hashing ---

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DatasetAggregate):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return f"DatasetAggregate(id={self._id}, name={self._name}, cases={self.total_cases})"
