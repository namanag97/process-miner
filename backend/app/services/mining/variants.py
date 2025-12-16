from collections import defaultdict
import pm4py
from pm4py.objects.log.obj import EventLog

from ...models import Deviation
from ...core import get_logger

log = get_logger(__name__)

def get_variants(event_log: EventLog, top_k: int = 100) -> list[dict]:
    """
    Extract process variants from event log.
    """
    log.info("Extracting variants...")
    
    # Get variants with counts
    variants = pm4py.get_variants(event_log)
    
    # Sort by frequency
    sorted_variants = sorted(
        variants.items(),
        key=lambda x: len(x[1]) if isinstance(x[1], list) else x[1],
        reverse=True
    )[:top_k]
    
    # Calculate total for percentages
    total_cases = len(event_log)
    
    # Get case durations for each variant
    case_durations = pm4py.get_all_case_durations(event_log)
    case_duration_map = dict(zip(
        [trace.attributes.get("concept:name", str(i)) for i, trace in enumerate(event_log)],
        case_durations
    ))
    
    result = []
    for i, (trace, cases) in enumerate(sorted_variants):
        # Handle both new and old PM4Py API
        if isinstance(cases, list):
            case_count = len(cases)
            case_ids = [c.attributes.get("concept:name", str(j)) for j, c in enumerate(cases)]
        else:
            case_count = cases
            case_ids = []
        
        # Convert trace to list
        if isinstance(trace, tuple):
            sequence = list(trace)
        else:
            sequence = [str(trace)]
        
        # Calculate average duration for this variant
        variant_durations = [
            case_duration_map.get(cid, 0)
            for cid in case_ids
            if cid in case_duration_map
        ]
        avg_duration = sum(variant_durations) / len(variant_durations) if variant_durations else 0
        
        result.append({
            "id": f"variant_{i+1}",
            "sequence": sequence,
            "case_count": case_count,
            "percentage": (case_count / total_cases) * 100 if total_cases > 0 else 0,
            "avg_duration_ms": avg_duration * 1000,  # Convert to ms
            "case_ids": case_ids[:100],  # Limit case IDs
        })
    
    log.info(f"Found {len(result)} variants")
    return result


def detect_deviations(event_log: EventLog, variants: list[dict]) -> list[Deviation]:
    """
    Detect process deviations like rework and skips.
    """
    deviations = []
    
    # Detect rework (same activity appears multiple times in a trace)
    rework_cases: dict[str, list[str]] = defaultdict(list)
    
    for trace in event_log:
        case_id = trace.attributes.get("concept:name", "unknown")
        activity_counts: dict[str, int] = defaultdict(int)
        
        for event in trace:
            activity = event.get("concept:name", "unknown")
            activity_counts[activity] += 1
        
        for activity, count in activity_counts.items():
            if count > 1:
                rework_cases[activity].append(case_id)
    
    for activity, cases in rework_cases.items():
        if len(cases) >= 5:  # Only report if significant
            deviations.append(Deviation(
                type="rework",
                description=f"Activity '{activity}' is repeated in the same case",
                affected_cases=cases[:100],
                frequency=len(cases),
            ))
    
    # Detect unusual paths (variants with low frequency)
    for variant in variants:
        if variant["percentage"] < 1.0 and variant["case_count"] >= 3:
            deviations.append(Deviation(
                type="unusual_path",
                description=f"Unusual process path: {' -> '.join(variant['sequence'][:5])}...",
                affected_cases=variant["case_ids"][:100],
                frequency=variant["case_count"],
            ))
    
    return deviations[:20]  # Limit to top 20 deviations
