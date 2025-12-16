from typing import Any
import pm4py
from pm4py.objects.log.obj import EventLog

from ...core import get_logger

log = get_logger(__name__)

def discover_dfg(event_log: EventLog) -> dict[str, Any]:
    """
    Discover Directly-Follows Graph using PM4Py.
    """
    log.info("Discovering DFG...")
    
    # Basic DFG
    dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)
    
    # Performance DFG (for durations)
    try:
        perf_dfg, _, _ = pm4py.discover_performance_dfg(event_log)
    except Exception as e:
        log.warning(f"Could not get performance DFG: {e}")
        perf_dfg = {}
    
    log.info(f"DFG discovered: {len(dfg)} edges")
    
    return {
        "dfg": dfg,
        "start_activities": start_activities,
        "end_activities": end_activities,
        "performance_dfg": perf_dfg,
    }
