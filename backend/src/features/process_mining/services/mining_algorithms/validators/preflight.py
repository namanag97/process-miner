"""Pre-flight Validation Service.

Validates event logs before expensive mining operations.
Fail fast with actionable error messages.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pm4py.objects.log.obj import EventLog as PM4PyLog

from src.features.process_mining.enums import MinerType
from src.infra.core.error_codes import DiscoveryErrorCode
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Pre-flight validation result.

    Attributes:
        errors: Blocking issues - mining SHOULD NOT proceed
        warnings: Non-blocking issues - mining CAN proceed with caution
        complexity: Estimated resource requirements
        is_valid: True if no blocking errors (warnings are OK)
    """

    errors: list[DiscoveryErrorCode] = field(default_factory=list)
    warnings: list[DiscoveryErrorCode] = field(default_factory=list)
    complexity: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """True if no blocking errors."""
        return len(self.errors) == 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API responses."""
        return {
            "is_valid": self.is_valid,
            "errors": [e.value for e in self.errors],
            "warnings": [w.value for w in self.warnings],
            "complexity": self.complexity,
        }


class PreflightValidator:
    """Validate event log before mining.

    Performs quick checks to fail fast before expensive operations.
    Business context: Enterprise customers upload GB-scale logs.
    We want to detect issues in seconds, not after 10 minutes of processing.
    """

    # Thresholds (configurable for enterprise customers)
    MAX_ACTIVITIES_WARNING = 500  # Warn above this
    MAX_ACTIVITIES_BLOCK = 2000  # Block above this
    MAX_EVENTS_FOR_SYNC = 50000  # Recommend async above this
    MAX_MEMORY_MB = 4096  # Block if estimated memory exceeds

    def validate(
        self,
        pm4py_log: PM4PyLog | None,
        miner_type: MinerType,
    ) -> ValidationResult:
        """Run all validation checks.

        Args:
            pm4py_log: PM4Py EventLog object (can be None)
            miner_type: Algorithm to use (some checks are algorithm-specific)

        Returns:
            ValidationResult with errors, warnings, and complexity estimate
        """
        result = ValidationResult()

        # Check 1: Empty log
        if not pm4py_log or len(pm4py_log) == 0:
            result.errors.append(DiscoveryErrorCode.EMPTY_EVENT_LOG)
            logger.warning("preflight_validation_failed", error="empty_event_log")
            return result  # Can't validate further

        # Gather statistics for validation
        stats = self._collect_statistics(pm4py_log)

        # Check 2: Required columns
        if not stats.get("has_activity_column"):
            result.errors.append(DiscoveryErrorCode.MISSING_ACTIVITY)

        # Check 3: Timestamps (required for some algorithms)
        timestamp_required = miner_type in [
            MinerType.PERFORMANCE_DFG,
            MinerType.TEMPORAL_PROFILE,
            MinerType.BATCHES,
        ]
        if timestamp_required and not stats.get("has_timestamp_column"):
            result.errors.append(DiscoveryErrorCode.MISSING_TIMESTAMPS)
        elif not stats.get("timestamps_valid", True):
            result.errors.append(DiscoveryErrorCode.INVALID_TIMESTAMPS)

        # Check 4: Activity count (warning vs blocking)
        unique_activities = stats.get("unique_activities", 0)
        if unique_activities > self.MAX_ACTIVITIES_BLOCK:
            result.errors.append(DiscoveryErrorCode.TOO_MANY_ACTIVITIES)
        elif unique_activities > self.MAX_ACTIVITIES_WARNING:
            result.warnings.append(DiscoveryErrorCode.TOO_MANY_ACTIVITIES)

        # Check 5: Memory estimation
        estimated_memory = self._estimate_memory(stats, miner_type)
        if estimated_memory > self.MAX_MEMORY_MB:
            result.errors.append(DiscoveryErrorCode.MEMORY_EXCEEDED)

        # Set complexity info
        result.complexity = {
            "unique_activities": unique_activities,
            "total_traces": stats.get("total_traces", 0),
            "total_events": stats.get("total_events", 0),
            "estimated_memory_mb": estimated_memory,
            "recommended_async": stats.get("total_events", 0) > self.MAX_EVENTS_FOR_SYNC,
        }

        logger.info(
            "preflight_validation_completed",
            is_valid=result.is_valid,
            errors=[e.value for e in result.errors],
            warnings=[w.value for w in result.warnings],
        )

        return result

    def _collect_statistics(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Collect statistics for validation (fast scan)."""
        stats: dict[str, Any] = {
            "total_traces": len(pm4py_log),
            "total_events": 0,
            "unique_activities": 0,
            "has_activity_column": False,
            "has_timestamp_column": False,
            "timestamps_valid": True,
        }

        activities: set[str] = set()
        sample_invalid_timestamps = 0

        for trace in pm4py_log:
            stats["total_events"] += len(trace)

            for event in trace:
                # Check for activity column
                activity = event.get("concept:name")
                if activity:
                    stats["has_activity_column"] = True
                    activities.add(str(activity))

                # Check for timestamp column
                timestamp = event.get("time:timestamp")
                if timestamp is not None:
                    stats["has_timestamp_column"] = True
                    # Quick validity check (sample first few)
                    if sample_invalid_timestamps < 10:
                        if not isinstance(timestamp, datetime):
                            sample_invalid_timestamps += 1
                            stats["timestamps_valid"] = False

        stats["unique_activities"] = len(activities)
        return stats

    def _estimate_memory(self, stats: dict[str, Any], miner_type: MinerType) -> int:
        """Estimate memory requirements in MB."""
        total_events = stats.get("total_events", 0)
        unique_activities = stats.get("unique_activities", 0)

        # Base memory estimation
        base_mb = 50  # PM4Py overhead
        event_mb = (total_events * 200) / (1024 * 1024)  # ~200 bytes per event

        # Algorithm-specific multipliers
        multiplier = 1.0
        if miner_type == MinerType.ILP:
            # ILP is exponential in activities
            multiplier = min(2**unique_activities / 1000, 100)
        elif miner_type in [MinerType.ALPHA, MinerType.HEURISTICS]:
            # Quadratic in activities
            multiplier = (unique_activities**2) / 1000

        return int(base_mb + event_mb * max(1, multiplier))
