from typing import Any
import pm4py
from pm4py.objects.log.obj import EventLog

from ...core import get_logger

log = get_logger(__name__)

def get_statistics(event_log: EventLog) -> dict[str, Any]:
    """
    Calculate overall process statistics.
    """
    log.info("Calculating statistics...")
    
    # Basic counts
    total_cases = len(event_log)
    total_events = sum(len(trace) for trace in event_log)
    
    # Activities
    activities = pm4py.get_event_attribute_values(event_log, "concept:name")
    total_activities = len(activities)
    
    # Variants
    variants = pm4py.get_variants(event_log)
    total_variants = len(variants)
    
    # Case durations
    case_durations = pm4py.get_all_case_durations(event_log)
    avg_duration = sum(case_durations) / len(case_durations) if case_durations else 0
    
    # Median duration
    sorted_durations = sorted(case_durations)
    median_duration = (
        sorted_durations[len(sorted_durations) // 2]
        if sorted_durations else 0
    )
    
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


def get_activity_stats(event_log: EventLog) -> list[dict]:
    """
    Get per-activity statistics.
    """
    activities = pm4py.get_event_attribute_values(event_log, "concept:name")
    start_activities = set(pm4py.get_start_activities(event_log).keys())
    end_activities = set(pm4py.get_end_activities(event_log).keys())
    
    total_events = sum(activities.values())
    
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
