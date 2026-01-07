"""Value Objects for domain primitives.

Type-safe wrappers for domain identifiers and primitives that:
- Encapsulate validation rules
- Prevent primitive obsession
- Make invalid states unrepresentable
- Provide type safety across the codebase

Usage:
    process_id = ProcessId("550e8400-e29b-41d4-a716-446655440000")
    activity = ActivityName("Register Request")

    # Invalid values raise ValueError at construction time
    ProcessId("not-a-uuid")  # Raises ValueError
"""

import re
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

# =============================================================================
# Identifier Value Objects
# =============================================================================


@dataclass(frozen=True)
class ProcessId:
    """Unique identifier for an event log/process.

    Wraps a UUID string with validation.
    """

    value: str

    def __post_init__(self):
        if not self._is_valid_uuid(self.value):
            raise ValueError(f"Invalid ProcessId: {self.value}")

    @staticmethod
    def _is_valid_uuid(value: str) -> bool:
        try:
            UUID(value)
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    def generate(cls) -> "ProcessId":
        """Generate a new ProcessId."""
        from uuid import uuid4

        return cls(str(uuid4()))

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ProjectId:
    """Unique identifier for a project."""

    value: str

    def __post_init__(self):
        if not self._is_valid_uuid(self.value):
            raise ValueError(f"Invalid ProjectId: {self.value}")

    @staticmethod
    def _is_valid_uuid(value: str) -> bool:
        try:
            UUID(value)
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    def generate(cls) -> "ProjectId":
        from uuid import uuid4

        return cls(str(uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ModelId:
    """Unique identifier for a process model."""

    value: str

    def __post_init__(self):
        if not self._is_valid_uuid(self.value):
            raise ValueError(f"Invalid ModelId: {self.value}")

    @staticmethod
    def _is_valid_uuid(value: str) -> bool:
        try:
            UUID(value)
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    def generate(cls) -> "ModelId":
        from uuid import uuid4

        return cls(str(uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CaseId:
    """Business case identifier within an event log.

    Unlike ProcessId, this is the business-level case ID from the source data,
    not a system-generated UUID.
    """

    value: str
    MAX_LENGTH = 255

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("CaseId cannot be empty")
        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"CaseId exceeds max length of {self.MAX_LENGTH}")

    def __str__(self) -> str:
        return self.value


# =============================================================================
# Domain Value Objects
# =============================================================================


@dataclass(frozen=True)
class ActivityName:
    """Activity/event name in a process.

    Validated for length and content.
    """

    value: str
    MAX_LENGTH = 255

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("ActivityName cannot be empty")
        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"ActivityName exceeds max length of {self.MAX_LENGTH}")

    def normalized(self) -> "ActivityName":
        """Return normalized (trimmed, lowercase) activity name."""
        return ActivityName(self.value.strip().lower())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ResourceName:
    """Resource/actor name in a process event."""

    value: str
    MAX_LENGTH = 255

    def __post_init__(self):
        if self.value and len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"ResourceName exceeds max length of {self.MAX_LENGTH}")

    def __str__(self) -> str:
        return self.value or ""

    @classmethod
    def empty(cls) -> "ResourceName":
        return cls("")


@dataclass(frozen=True)
class VariantKey:
    """Unique identifier for a process variant (activity sequence).

    Format: Hash of activity sequence.
    """

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("VariantKey cannot be empty")

    @classmethod
    def from_activities(cls, activities: list[str]) -> "VariantKey":
        """Generate variant key from activity sequence."""
        import hashlib

        sequence = " -> ".join(activities)
        hash_value = hashlib.sha256(sequence.encode()).hexdigest()[:16]
        return cls(hash_value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ActivityTrace:
    """Ordered sequence of activities representing a process variant.

    Immutable list of activity names with string representation.
    """

    activities: tuple[str, ...]

    def __post_init__(self):
        if not self.activities:
            raise ValueError("ActivityTrace cannot be empty")

    @classmethod
    def from_list(cls, activities: list[str]) -> "ActivityTrace":
        return cls(tuple(activities))

    @classmethod
    def from_string(cls, trace: str, separator: str = " -> ") -> "ActivityTrace":
        """Parse from string format like 'A -> B -> C'."""
        activities = [a.strip() for a in trace.split(separator)]
        return cls(tuple(activities))

    def to_string(self, separator: str = " -> ") -> str:
        return separator.join(self.activities)

    def __len__(self) -> int:
        return len(self.activities)

    def __str__(self) -> str:
        return self.to_string()


# =============================================================================
# Time-related Value Objects
# =============================================================================


@dataclass(frozen=True)
class Duration:
    """Duration in seconds with convenience methods."""

    seconds: float

    def __post_init__(self):
        if self.seconds < 0:
            raise ValueError("Duration cannot be negative")

    @classmethod
    def from_timestamps(cls, start: datetime, end: datetime) -> "Duration":
        """Calculate duration between two timestamps."""
        delta = end - start
        return cls(delta.total_seconds())

    @classmethod
    def zero(cls) -> "Duration":
        return cls(0.0)

    @property
    def minutes(self) -> float:
        return self.seconds / 60

    @property
    def hours(self) -> float:
        return self.seconds / 3600

    @property
    def days(self) -> float:
        return self.seconds / 86400

    def __str__(self) -> str:
        if self.seconds < 60:
            return f"{self.seconds:.1f}s"
        if self.seconds < 3600:
            return f"{self.minutes:.1f}m"
        if self.seconds < 86400:
            return f"{self.hours:.1f}h"
        return f"{self.days:.1f}d"

    def __add__(self, other: "Duration") -> "Duration":
        return Duration(self.seconds + other.seconds)

    def __lt__(self, other: "Duration") -> bool:
        return self.seconds < other.seconds


@dataclass(frozen=True)
class Percentage:
    """Percentage value (0-100) with validation."""

    value: float

    def __post_init__(self):
        if not 0 <= self.value <= 100:
            raise ValueError(f"Percentage must be 0-100, got {self.value}")

    @classmethod
    def from_ratio(cls, ratio: float) -> "Percentage":
        """Create from ratio (0-1)."""
        return cls(ratio * 100)

    @property
    def ratio(self) -> float:
        """Get as ratio (0-1)."""
        return self.value / 100

    def __str__(self) -> str:
        return f"{self.value:.1f}%"


# =============================================================================
# Quality Metrics Value Objects
# =============================================================================


@dataclass(frozen=True)
class FitnessScore:
    """Process model fitness score (0-1)."""

    value: float

    def __post_init__(self):
        if not 0 <= self.value <= 1:
            raise ValueError(f"FitnessScore must be 0-1, got {self.value}")

    @property
    def percentage(self) -> Percentage:
        return Percentage.from_ratio(self.value)

    def is_acceptable(self, threshold: float = 0.8) -> bool:
        return self.value >= threshold

    def __str__(self) -> str:
        return f"{self.value:.2%}"


@dataclass(frozen=True)
class PrecisionScore:
    """Process model precision score (0-1)."""

    value: float

    def __post_init__(self):
        if not 0 <= self.value <= 1:
            raise ValueError(f"PrecisionScore must be 0-1, got {self.value}")

    @property
    def percentage(self) -> Percentage:
        return Percentage.from_ratio(self.value)

    def __str__(self) -> str:
        return f"{self.value:.2%}"


# =============================================================================
# Email Value Object
# =============================================================================


@dataclass(frozen=True)
class Email:
    """Validated email address."""

    value: str

    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def __post_init__(self):
        if not self.EMAIL_PATTERN.match(self.value):
            raise ValueError(f"Invalid email address: {self.value}")

    @property
    def domain(self) -> str:
        return self.value.split("@")[1]

    def __str__(self) -> str:
        return self.value


# =============================================================================
# Helper Functions
# =============================================================================


def parse_id(value: str, id_type: str = "process") -> ProcessId | ProjectId | ModelId:
    """Parse a string ID into the appropriate value object."""
    id_map: dict[str, type[ProcessId] | type[ProjectId] | type[ModelId]] = {
        "process": ProcessId,
        "project": ProjectId,
        "model": ModelId,
    }
    id_class = id_map.get(id_type, ProcessId)
    return id_class(value)  # type: ignore[return-value]
