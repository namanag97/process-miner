"""
State machine validator for dataset states.

Validates that state transitions follow the legal state machine:
PENDING → VALIDATING → VALIDATED → MAPPED → INGESTING → READY
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DatasetState(str, Enum):
    """Dataset state machine."""

    PENDING = "pending"
    VALIDATING = "validating"
    VALIDATED = "validated"
    AWAITING_MAPPING = "awaiting_mapping"  # Alternative name for VALIDATED
    MAPPED = "mapped"
    INGESTING = "ingesting"
    READY = "ready"
    FAILED = "failed"
    ERROR = "error"


# Valid state transitions
VALID_TRANSITIONS = {
    DatasetState.PENDING: [DatasetState.VALIDATING, DatasetState.FAILED],
    DatasetState.VALIDATING: [
        DatasetState.VALIDATED,
        DatasetState.AWAITING_MAPPING,
        DatasetState.FAILED,
    ],
    DatasetState.VALIDATED: [DatasetState.MAPPED, DatasetState.FAILED],
    DatasetState.AWAITING_MAPPING: [DatasetState.MAPPED, DatasetState.FAILED],
    DatasetState.MAPPED: [DatasetState.INGESTING, DatasetState.FAILED],
    DatasetState.INGESTING: [DatasetState.READY, DatasetState.FAILED],
    DatasetState.READY: [],  # Terminal state
    DatasetState.FAILED: [],  # Terminal state
    DatasetState.ERROR: [],  # Terminal state
}


@dataclass
class StateTransition:
    """Track a single state transition."""

    from_state: str
    to_state: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_seconds: float = 0.0

    def is_valid(self) -> bool:
        """Check if this transition is legal."""
        try:
            from_enum = DatasetState(self.from_state.lower())
            to_enum = DatasetState(self.to_state.lower())
            return to_enum in VALID_TRANSITIONS.get(from_enum, [])
        except (ValueError, KeyError):
            return False


class StateValidator:
    """Validates state transitions for datasets."""

    def __init__(self):
        self.transitions: list[StateTransition] = []
        self.last_state: str | None = None
        self.start_time: datetime | None = None

    def add_transition(self, from_state: str, to_state: str) -> bool:
        """
        Add and validate a state transition.

        Raises:
            ValueError: If transition is invalid
        """
        transition = StateTransition(from_state=from_state, to_state=to_state)

        if not transition.is_valid():
            valid_next = VALID_TRANSITIONS.get(DatasetState(from_state.lower()), [])
            raise ValueError(
                f"Invalid state transition: {from_state} → {to_state}. "
                f"Valid transitions from {from_state}: {[s.value for s in valid_next]}"
            )

        # Calculate duration since last transition
        if self.start_time:
            transition.duration_seconds = (datetime.utcnow() - self.start_time).total_seconds()

        self.transitions.append(transition)
        self.last_state = to_state
        self.start_time = datetime.utcnow()

        return True

    def get_summary(self) -> dict:
        """Get summary of all transitions."""
        total_duration = sum(t.duration_seconds for t in self.transitions)

        return {
            "total_transitions": len(self.transitions),
            "total_duration_seconds": round(total_duration, 2),
            "transitions": [
                {
                    "from": t.from_state,
                    "to": t.to_state,
                    "duration_seconds": round(t.duration_seconds, 2),
                }
                for t in self.transitions
            ],
            "current_state": self.last_state,
        }
