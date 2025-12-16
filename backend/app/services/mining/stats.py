from typing import Any
import pm4py
from pm4py.objects.log.obj import EventLog

from ...core import get_logger

log = get_logger(__name__)


class StatisticsError(Exception):
    """Raised when statistics calculation fails."""

    def __init__(self, message: str, cause: Exception | None = None):
        self.message = message
        self.cause = cause
        super().__init__(message)


def get_statistics(event_log: EventLog) -> dict[str, Any]:
    """
    Calculate overall process statistics.

    Raises:
        StatisticsError: If statistics calculation fails
    """
    log.info("Calculating statistics...")

    if not event_log or len(event_log) == 0:
        raise StatisticsError("Cannot calculate statistics from empty event log")

    try:
        # Basic counts
        total_cases = len(event_log)
        total_events = sum(len(trace) for trace in event_log)

        # Activities
        activities = pm4py.get_event_attribute_values(event_log, "concept:name")
        total_activities = len(activities) if activities else 0

        # Variants
        variants = pm4py.get_variants(event_log)
        total_variants = len(variants) if variants else 0

        # Case durations - handle empty case
        case_durations = pm4py.get_all_case_durations(event_log)
        if case_durations and len(case_durations) > 0:
            avg_duration = sum(case_durations) / len(case_durations)
            sorted_durations = sorted(case_durations)
            median_duration = sorted_durations[len(sorted_durations) // 2]
        else:
            avg_duration = 0
            median_duration = 0
            log.warning("No case durations available")

        # Start/end activities
        start_activities = list(pm4py.get_start_activities(event_log).keys())
        end_activities = list(pm4py.get_end_activities(event_log).keys())

        return {
            "total_cases": total_cases,
            "total_events": total_events,
            "total_activities": total_activities,
            "total_variants": total_variants,
            "avg_case_duration_ms": avg_duration * 1000,
            "median_case_duration_ms": median_duration * 1000,
            "start_activities": start_activities,
            "end_activities": end_activities,
        }
    except Exception as e:
        log.error(f"Statistics calculation failed: {e}")
        raise StatisticsError(f"Failed to calculate statistics: {str(e)}", cause=e)


def get_activity_stats(event_log: EventLog) -> list[dict]:
    """
    Get per-activity statistics.

    Raises:
        StatisticsError: If activity stats calculation fails
    """
    if not event_log or len(event_log) == 0:
        raise StatisticsError("Cannot calculate activity stats from empty event log")

    try:
        activities = pm4py.get_event_attribute_values(event_log, "concept:name")
        start_activities = set(pm4py.get_start_activities(event_log).keys())
        end_activities = set(pm4py.get_end_activities(event_log).keys())

        total_events = sum(activities.values()) if activities else 0

        if total_events == 0:
            log.warning("No activities found in event log")
            return []

        return [
            {
                "name": name,
                "frequency": freq,
                "frequency_pct": (freq / total_events * 100) if total_events > 0 else 0,
                "is_start": name in start_activities,
                "is_end": name in end_activities,
                "avg_duration_ms": 0,  # Would need performance analysis
            }
            for name, freq in sorted(activities.items(), key=lambda x: -x[1])
        ]
    except Exception as e:
        log.error(f"Activity stats calculation failed: {e}")
        raise StatisticsError(f"Failed to calculate activity stats: {str(e)}", cause=e)
