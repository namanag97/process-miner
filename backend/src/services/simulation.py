"""Simulation Service - Process Simulation using PM4Py.

Provides model play-out, what-if simulation, and capacity planning.
"""

import time
from collections import defaultdict
from datetime import timedelta
from typing import Any

import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class SimulationService:
    """Process simulation service."""

    def play_out(self, model_data: Any, model_format: str, num_traces: int = 100) -> PM4PyLog:
        """Generate synthetic event log from a process model."""
        logger.info("playing_out_model", format=model_format, num_traces=num_traces)
        start = time.perf_counter()

        try:
            if model_format == "process_tree":
                log = pm4py.play_out(model_data, variant="basic", no_traces=num_traces)
            elif model_format == "petri_net":
                net, im, fm = model_data
                log = pm4py.play_out(net, im, fm, variant="basic", no_traces=num_traces)
            else:
                log = PM4PyLog()
        except Exception as e:
            logger.warning("play_out_failed", error=str(e))
            log = PM4PyLog()

        duration = (time.perf_counter() - start) * 1000
        logger.info("play_out_completed", traces=len(log), duration_ms=round(duration, 2))
        return log

    def simulate_scenario(self, pm4py_log: PM4PyLog, modifications: list[dict]) -> dict[str, Any]:
        """Simulate what-if scenario with modifications."""
        logger.info("simulating_scenario", traces=len(pm4py_log), modifications=len(modifications))
        start = time.perf_counter()

        original_metrics = self._compute_metrics(pm4py_log)

        simulated_log = self._apply_modifications(pm4py_log, modifications)
        simulated_metrics = self._compute_metrics(simulated_log)

        impact = {}
        for key in original_metrics:
            if isinstance(original_metrics[key], (int, float)) and isinstance(simulated_metrics[key], (int, float)):
                original_val = original_metrics[key]
                simulated_val = simulated_metrics[key]
                if original_val != 0:
                    impact[key] = round((simulated_val - original_val) / original_val * 100, 2)
                else:
                    impact[key] = 0

        duration = (time.perf_counter() - start) * 1000
        logger.info("simulation_completed", duration_ms=round(duration, 2))

        return {
            "scenario": "custom",
            "original_metrics": original_metrics,
            "simulated_metrics": simulated_metrics,
            "impact": impact,
        }

    def estimate_capacity(self, pm4py_log: PM4PyLog, target_throughput: float) -> dict[str, Any]:
        """Estimate resource requirements for target throughput."""
        logger.info("estimating_capacity", traces=len(pm4py_log), target_throughput=target_throughput)
        start = time.perf_counter()

        resource_events = defaultdict(int)
        resource_time = defaultdict(float)

        for trace in pm4py_log:
            for i, event in enumerate(trace):
                resource = event.get("org:resource", "default")
                resource_events[resource] += 1
                if i < len(trace) - 1 and "time:timestamp" in event and "time:timestamp" in trace[i + 1]:
                    duration = (trace[i + 1]["time:timestamp"] - event["time:timestamp"]).total_seconds()
                    resource_time[resource] += duration

        all_timestamps = []
        for trace in pm4py_log:
            for event in trace:
                if "time:timestamp" in event:
                    all_timestamps.append(event["time:timestamp"])

        if all_timestamps:
            time_range_days = (max(all_timestamps) - min(all_timestamps)).total_seconds() / 86400
            current_throughput = len(pm4py_log) / time_range_days if time_range_days > 0 else 0
        else:
            current_throughput = 0

        scaling_factor = target_throughput / current_throughput if current_throughput > 0 else 1

        current_resources = len(resource_events)
        estimated_resources = int(current_resources * scaling_factor + 0.5)

        duration = (time.perf_counter() - start) * 1000
        logger.info("capacity_estimated", duration_ms=round(duration, 2))

        return {
            "current_throughput_per_day": round(current_throughput, 2),
            "target_throughput_per_day": target_throughput,
            "scaling_factor": round(scaling_factor, 2),
            "current_resources": current_resources,
            "estimated_resources_needed": estimated_resources,
            "resource_utilization": {r: round(t / 3600, 2) for r, t in resource_time.items()},
        }

    def _compute_metrics(self, pm4py_log: PM4PyLog) -> dict[str, float]:
        """Compute basic metrics for a log."""
        durations = []
        for trace in pm4py_log:
            timestamps = [e.get("time:timestamp") for e in trace if "time:timestamp" in e]
            if len(timestamps) >= 2:
                durations.append((max(timestamps) - min(timestamps)).total_seconds())

        return {
            "total_cases": len(pm4py_log),
            "total_events": sum(len(t) for t in pm4py_log),
            "avg_duration_seconds": round(sum(durations) / len(durations), 2) if durations else 0,
            "min_duration_seconds": round(min(durations), 2) if durations else 0,
            "max_duration_seconds": round(max(durations), 2) if durations else 0,
        }

    def _apply_modifications(self, pm4py_log: PM4PyLog, modifications: list[dict]) -> PM4PyLog:
        """Apply modifications to create simulated log."""
        from pm4py.objects.log.obj import Event, EventLog, Trace

        new_log = EventLog()

        for trace in pm4py_log:
            new_trace = Trace()
            new_trace.attributes = dict(trace.attributes)

            for event in trace:
                new_event = Event()
                for k, v in event.items():
                    new_event[k] = v

                for mod in modifications:
                    if mod.get("type") == "reduce_duration":
                        factor = mod.get("factor", 0.8)
                        if "time:timestamp" in new_event and len(new_trace) > 0:
                            prev_ts = new_trace[-1].get("time:timestamp")
                            if prev_ts:
                                diff = (new_event["time:timestamp"] - prev_ts).total_seconds()
                                new_diff = diff * factor
                                new_event["time:timestamp"] = prev_ts + timedelta(seconds=new_diff)

                new_trace.append(new_event)
            new_log.append(new_trace)

        return new_log


simulation_service = SimulationService()
