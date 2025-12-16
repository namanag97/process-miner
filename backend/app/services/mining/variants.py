from collections import defaultdict
import pm4py
from pm4py.objects.log.obj import EventLog

from ...models import Deviation
from ...core import get_logger

log = get_logger(__name__)


class VariantExtractionError(Exception):
    """Raised when variant extraction fails."""

    def __init__(self, message: str, cause: Exception | None = None):
        self.message = message
        self.cause = cause
        super().__init__(message)


def get_variants(event_log: EventLog, top_k: int = 100) -> list[dict]:
    """
    Extract process variants from event log.

    Args:
        event_log: PM4Py EventLog
        top_k: Maximum number of variants to return (default 100)

    Returns:
        List of variant dictionaries

    Raises:
        VariantExtractionError: If variant extraction fails
    """
    log.info("Extracting variants...")

    if not event_log or len(event_log) == 0:
        raise VariantExtractionError("Cannot extract variants from empty event log")

    try:
        # Get variants with counts
        variants = pm4py.get_variants(event_log)

        if not variants:
            log.warning("No variants found in event log")
            return []

        # Sort by frequency
        sorted_variants = sorted(
            variants.items(),
            key=lambda x: len(x[1]) if isinstance(x[1], list) else x[1],
            reverse=True
        )[:top_k]

        if len(variants) > top_k:
            log.info(f"Truncated variants from {len(variants)} to {top_k}")

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

            # Truncate case_ids to limit response size
            truncated_case_ids = case_ids[:100]
            if len(case_ids) > 100:
                log.debug(f"Truncated case_ids for variant_{i+1} from {len(case_ids)} to 100")

            result.append({
                "id": f"variant_{i+1}",
                "sequence": sequence,
                "case_count": case_count,
                "percentage": (case_count / total_cases) * 100 if total_cases > 0 else 0,
                "avg_duration_ms": avg_duration * 1000,  # Convert to ms
                "case_ids": truncated_case_ids,
            })

        log.info(f"Found {len(result)} variants")
        return result

    except Exception as e:
        log.error(f"Variant extraction failed: {e}")
        raise VariantExtractionError(f"Failed to extract variants: {str(e)}", cause=e)


def detect_deviations(event_log: EventLog, variants: list[dict]) -> list[Deviation]:
    """
    Detect process deviations like rework and skips.

    Args:
        event_log: PM4Py EventLog
        variants: List of variant dictionaries

    Returns:
        List of Deviation objects (max 20)
    """
    if not event_log or len(event_log) == 0:
        log.warning("Cannot detect deviations from empty event log")
        return []

    deviations = []

    try:
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
                    affected_cases=cases[:100],  # Truncate to limit size
                    frequency=len(cases),
                ))

        # Detect unusual paths (variants with low frequency)
        for variant in variants:
            if variant["percentage"] < 1.0 and variant["case_count"] >= 3:
                sequence_preview = ' -> '.join(variant['sequence'][:5])
                if len(variant['sequence']) > 5:
                    sequence_preview += '...'
                deviations.append(Deviation(
                    type="unusual_path",
                    description=f"Unusual process path: {sequence_preview}",
                    affected_cases=variant["case_ids"][:100],
                    frequency=variant["case_count"],
                ))

        # Limit to top 20 deviations
        if len(deviations) > 20:
            log.info(f"Truncated deviations from {len(deviations)} to 20")
        return deviations[:20]

    except Exception as e:
        log.error(f"Deviation detection failed: {e}")
        # Return empty list instead of raising - deviations are optional
        return []
