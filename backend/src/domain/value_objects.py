"""Domain Value Objects - Immutable, self-validating domain primitives.

Value objects are the building blocks of the domain model. They are:
- Immutable (frozen dataclasses)
- Self-validating (raise on invalid state)
- Equality by value (not identity)

Usage:
    case_id = CaseId("order-123")
    sequence = ActivitySequence.from_list(["Submit", "Approve", "Complete"])
    time_range = TimeRange(start=datetime(2024, 1, 1), end=datetime(2024, 1, 2))
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# =============================================================================
# Case & Activity Identifiers
# =============================================================================


@dataclass(frozen=True)
class CaseId:
    """Validated case identifier.

    Ensures case IDs are non-empty and normalized.
    """

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("CaseId cannot be empty")
        # Normalize whitespace
        object.__setattr__(self, "value", self.value.strip())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ActivityName:
    """Validated activity name.

    Ensures activity names are non-empty and normalized.
    """

    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("ActivityName cannot be empty")
        object.__setattr__(self, "value", self.value.strip())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ResourceId:
    """Optional resource/user identifier.

    Can be None for events without resource attribution.
    """

    value: str | None = None

    def __post_init__(self):
        if self.value is not None:
            object.__setattr__(self, "value", self.value.strip() or None)

    def __str__(self) -> str:
        return self.value or ""

    def __bool__(self) -> bool:
        return self.value is not None


# =============================================================================
# Activity Sequence (Variant)
# =============================================================================


@dataclass(frozen=True)
class ActivitySequence:
    """Immutable sequence of activities representing a process variant.

    This is one of the most important value objects in process mining.
    A variant is a unique sequence of activities that cases follow.

    Examples:
        >>> seq = ActivitySequence.from_list(["A", "B", "C"])
        >>> seq.to_trace_string()
        'A → B → C'
        >>> seq.has_rework
        False

        >>> seq_rework = ActivitySequence.from_list(["A", "B", "A", "C"])
        >>> seq_rework.has_rework
        True
        >>> seq_rework.rework_count
        1
    """

    activities: tuple[str, ...]

    def __post_init__(self):
        if not self.activities:
            raise ValueError("ActivitySequence cannot be empty")
        # Validate each activity
        for act in self.activities:
            if not act or not act.strip():
                raise ValueError("Activity name cannot be empty")

    @classmethod
    def from_list(cls, activities: list[str]) -> "ActivitySequence":
        """Create from a list of activity names."""
        return cls(tuple(activities))

    @classmethod
    def from_trace_string(cls, trace: str, separator: str = " → ") -> "ActivitySequence":
        """Parse from trace string format."""
        activities = [a.strip() for a in trace.split(separator) if a.strip()]
        return cls.from_list(activities)

    def to_trace_string(self, separator: str = " → ") -> str:
        """Convert to human-readable trace format."""
        return separator.join(self.activities)

    def to_list(self) -> list[str]:
        """Convert to mutable list."""
        return list(self.activities)

    @property
    def length(self) -> int:
        """Number of activities in the sequence."""
        return len(self.activities)

    @property
    def unique_activities(self) -> frozenset[str]:
        """Set of unique activities in the sequence."""
        return frozenset(self.activities)

    @property
    def unique_count(self) -> int:
        """Count of unique activities."""
        return len(self.unique_activities)

    @property
    def has_rework(self) -> bool:
        """True if any activity appears more than once."""
        return self.length != self.unique_count

    @property
    def rework_count(self) -> int:
        """Number of repeated activity occurrences."""
        return self.length - self.unique_count

    @property
    def rework_ratio(self) -> float:
        """Ratio of rework (0.0 = no rework, 1.0 = all rework)."""
        if self.length == 0:
            return 0.0
        return self.rework_count / self.length

    @property
    def first_activity(self) -> str:
        """First activity in the sequence."""
        return self.activities[0]

    @property
    def last_activity(self) -> str:
        """Last activity in the sequence."""
        return self.activities[-1]

    @property
    def variant_hash(self) -> str:
        """Stable hash for variant identification and grouping."""
        content = "|".join(self.activities)
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def contains(self, activity: str) -> bool:
        """Check if sequence contains an activity."""
        return activity in self.activities

    def count(self, activity: str) -> int:
        """Count occurrences of an activity."""
        return self.activities.count(activity)

    def get_prefix(self, length: int) -> "ActivitySequence":
        """Get first N activities as a new sequence."""
        if length <= 0:
            raise ValueError("Prefix length must be positive")
        return ActivitySequence(self.activities[:length])

    def get_suffix(self, length: int) -> "ActivitySequence":
        """Get last N activities as a new sequence."""
        if length <= 0:
            raise ValueError("Suffix length must be positive")
        return ActivitySequence(self.activities[-length:])

    def __len__(self) -> int:
        return self.length

    def __iter__(self):
        return iter(self.activities)

    def __getitem__(self, index: int) -> str:
        return self.activities[index]


# =============================================================================
# Time-Based Value Objects
# =============================================================================


@dataclass(frozen=True)
class TimeRange:
    """Time range value object with validation.

    Ensures end >= start and provides duration calculations.

    Examples:
        >>> tr = TimeRange(
        ...     start=datetime(2024, 1, 1, 9, 0),
        ...     end=datetime(2024, 1, 1, 17, 0)
        ... )
        >>> tr.duration_seconds
        28800.0  # 8 hours
        >>> tr.duration_hours
        8.0
    """

    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end < self.start:
            raise ValueError(f"End time ({self.end}) cannot be before start time ({self.start})")

    @classmethod
    def from_timestamps(
        cls, start_ts: datetime | None, end_ts: datetime | None
    ) -> Optional["TimeRange"]:
        """Create from optional timestamps, returns None if either is missing."""
        if start_ts is None or end_ts is None:
            return None
        return cls(start=start_ts, end=end_ts)

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        return (self.end - self.start).total_seconds()

    @property
    def duration_minutes(self) -> float:
        """Duration in minutes."""
        return self.duration_seconds / 60

    @property
    def duration_hours(self) -> float:
        """Duration in hours."""
        return self.duration_seconds / 3600

    @property
    def duration_days(self) -> float:
        """Duration in days."""
        return self.duration_seconds / 86400

    def contains(self, dt: datetime) -> bool:
        """Check if a datetime falls within this range."""
        return self.start <= dt <= self.end

    def overlaps(self, other: "TimeRange") -> bool:
        """Check if this range overlaps with another."""
        return self.start <= other.end and other.start <= self.end

    def __contains__(self, dt: datetime) -> bool:
        return self.contains(dt)


# =============================================================================
# Process Metrics Value Objects
# =============================================================================


@dataclass(frozen=True)
class QualityMetrics:
    """Process model quality metrics.

    Contains the four quality dimensions from PM4Py:
    - Fitness: How well the log fits the model (0.0-1.0)
    - Precision: How much the model allows behavior not in the log (0.0-1.0)
    - Generalization: How well the model generalizes beyond observed behavior (0.0-1.0)
    - Simplicity: How simple/understandable the model is (0.0-1.0)
    """

    fitness: float | None = None
    precision: float | None = None
    generalization: float | None = None
    simplicity: float | None = None

    def __post_init__(self):
        for metric_name in ["fitness", "precision", "generalization", "simplicity"]:
            value = getattr(self, metric_name)
            if value is not None and not (0.0 <= value <= 1.0):
                raise ValueError(f"{metric_name} must be between 0.0 and 1.0, got {value}")

    @property
    def f_score(self) -> float | None:
        """Harmonic mean of fitness and precision."""
        if self.fitness is None or self.precision is None:
            return None
        if self.fitness + self.precision == 0:
            return 0.0
        return 2 * (self.fitness * self.precision) / (self.fitness + self.precision)

    @property
    def is_conformant(self) -> bool:
        """True if fitness >= 0.8 (common threshold)."""
        return self.fitness is not None and self.fitness >= 0.8

    def to_dict(self) -> dict[str, float | None]:
        """Convert to dictionary."""
        return {
            "fitness": self.fitness,
            "precision": self.precision,
            "generalization": self.generalization,
            "simplicity": self.simplicity,
            "f_score": self.f_score,
        }


@dataclass(frozen=True)
class ProcessStatistics:
    """Aggregate statistics for an event log.

    Immutable summary of key process metrics.
    """

    total_events: int
    total_cases: int
    total_activities: int
    total_variants: int
    avg_case_duration_seconds: float | None = None
    min_case_duration_seconds: float | None = None
    max_case_duration_seconds: float | None = None

    def __post_init__(self):
        if self.total_events < 0:
            raise ValueError("total_events cannot be negative")
        if self.total_cases < 0:
            raise ValueError("total_cases cannot be negative")
        if self.total_activities < 0:
            raise ValueError("total_activities cannot be negative")

    @property
    def avg_events_per_case(self) -> float:
        """Average number of events per case."""
        if self.total_cases == 0:
            return 0.0
        return self.total_events / self.total_cases

    @property
    def avg_case_duration_hours(self) -> float | None:
        """Average case duration in hours."""
        if self.avg_case_duration_seconds is None:
            return None
        return self.avg_case_duration_seconds / 3600


# =============================================================================
# Variant Statistics
# =============================================================================


@dataclass(frozen=True)
class VariantStats:
    """Statistics for a single process variant.

    Combines the variant (activity sequence) with its frequency and performance data.
    """

    sequence: ActivitySequence
    case_count: int
    total_cases: int  # For calculating percentage
    avg_duration_seconds: float | None = None

    @property
    def frequency_percent(self) -> float:
        """Percentage of cases following this variant."""
        if self.total_cases == 0:
            return 0.0
        return (self.case_count / self.total_cases) * 100

    @property
    def complexity_score(self) -> float:
        """Complexity score based on length and rework (0.0-1.0).

        Formula:
        - Length component (30%): Normalized by 20 activities
        - Rework component (40%): Rework ratio
        - Repetition component (30%): 1 - unique ratio
        """
        length_score = min(self.sequence.length / 20, 1.0)
        rework_score = self.sequence.rework_ratio
        unique_ratio = self.sequence.unique_count / self.sequence.length
        repetition_score = 1 - unique_ratio

        return (length_score * 0.3) + (rework_score * 0.4) + (repetition_score * 0.3)
