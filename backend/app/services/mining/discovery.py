from typing import Any
import pm4py
from pm4py.objects.log.obj import EventLog

from ...core import get_logger

log = get_logger(__name__)


class DFGDiscoveryError(Exception):
    """Raised when DFG discovery fails."""

    def __init__(self, message: str, cause: Exception | None = None):
        self.message = message
        self.cause = cause
        super().__init__(message)


def discover_dfg(event_log: EventLog) -> dict[str, Any]:
    """
    Discover Directly-Follows Graph using PM4Py.

    Raises:
        DFGDiscoveryError: If DFG discovery fails
    """
    log.info("Discovering DFG...")

    if not event_log or len(event_log) == 0:
        raise DFGDiscoveryError("Cannot discover DFG from empty event log")

    try:
        # Basic DFG
        dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)
    except Exception as e:
        log.error(f"DFG discovery failed: {e}")
        raise DFGDiscoveryError(f"Failed to discover DFG: {str(e)}", cause=e)

    # Performance DFG (for durations) - optional, don't fail if unavailable
    perf_dfg = {}
    try:
        perf_dfg, _, _ = pm4py.discover_performance_dfg(event_log)
    except Exception as e:
        log.warning(f"Could not get performance DFG (continuing without): {e}")

    log.info(f"DFG discovered: {len(dfg)} edges")

    return {
        "dfg": dfg,
        "start_activities": start_activities,
        "end_activities": end_activities,
        "performance_dfg": perf_dfg,
    }
