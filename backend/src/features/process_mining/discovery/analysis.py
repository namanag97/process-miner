"""Process Analysis - Statistics and analysis functions.

Contains DFG data extraction, variant analysis, activity statistics,
and case statistics using PM4Py.
"""

import time
from typing import Any

import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog
from pm4py.statistics.traces.generic.log import case_statistics

from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class ProcessAnalyzer:
    """Analyzes event logs for statistics and patterns."""

    def get_start_activities(self, pm4py_log: PM4PyLog) -> dict[str, int]:
        """Get start activities with frequencies."""
        return dict(pm4py.get_start_activities(pm4py_log))

    def get_end_activities(self, pm4py_log: PM4PyLog) -> dict[str, int]:
        """Get end activities with frequencies."""
        return dict(pm4py.get_end_activities(pm4py_log))

    def get_variants(self, pm4py_log: PM4PyLog, top_n: int = 20) -> dict[str, Any]:
        """Get process variants with counts."""
        variants = pm4py.get_variants(pm4py_log)

        def get_count(v):
            return len(v) if isinstance(v, (list, tuple)) else v

        # Use Unicode arrow to avoid delimiter collision
        variant_list = [
            {
                "variant": " → ".join(k) if isinstance(k, tuple) else str(k),
                "activities": list(k) if isinstance(k, tuple) else [str(k)],
                "count": get_count(v),
            }
            for k, v in sorted(variants.items(), key=lambda x: -get_count(x[1]))[:top_n]
        ]

        return {
            "top_variants": variant_list,
            "total_variants": len(variants),
        }

    def get_dfg_data(self, dfg: dict, start_activities: dict, end_activities: dict) -> dict[str, Any]:
        """Convert DFG to structured data for visualization."""
        all_activities = set()
        for (source, target), _ in dfg.items():
            all_activities.add(source)
            all_activities.add(target)

        activity_freq = {}
        for (source, target), freq in dfg.items():
            activity_freq[source] = activity_freq.get(source, 0) + freq
            activity_freq[target] = activity_freq.get(target, 0) + freq

        total_freq = sum(dfg.values())

        nodes = [
            {
                "id": act,
                "name": act,
                "frequency": activity_freq.get(act, 0),
                "is_start": act in start_activities,
                "is_end": act in end_activities,
            }
            for act in all_activities
        ]

        edges = [
            {
                "source": source,
                "target": target,
                "frequency": freq,
                "probability": round(freq / total_freq, 4) if total_freq > 0 else 0,
            }
            for (source, target), freq in dfg.items()
        ]

        return {
            "nodes": nodes,
            "edges": edges,
            "start_activities": dict(start_activities),
            "end_activities": dict(end_activities),
            "total_frequency": total_freq,
        }

    def get_dfg_with_performance(
        self, pm4py_log: PM4PyLog
    ) -> dict[str, Any]:
        """Get DFG with performance metrics (avg/min/max duration per edge)."""
        dfg, start_activities, end_activities = pm4py.discover_dfg(pm4py_log)
        perf_dfg, _, _ = pm4py.discover_performance_dfg(pm4py_log)

        all_activities = set()
        for (source, target), _ in dfg.items():
            all_activities.add(source)
            all_activities.add(target)

        activity_freq = {}
        for (source, target), freq in dfg.items():
            activity_freq[source] = activity_freq.get(source, 0) + freq
            activity_freq[target] = activity_freq.get(target, 0) + freq

        total_freq = sum(dfg.values())

        nodes = [
            {
                "id": act,
                "name": act,
                "frequency": activity_freq.get(act, 0),
                "is_start": act in start_activities,
                "is_end": act in end_activities,
            }
            for act in all_activities
        ]

        edges = []
        for (source, target), freq in dfg.items():
            edge_data = {
                "source": source,
                "target": target,
                "frequency": freq,
                "probability": round(freq / total_freq, 4) if total_freq > 0 else 0,
            }
            if (source, target) in perf_dfg:
                perf_data = perf_dfg[(source, target)]
                if isinstance(perf_data, dict):
                    edge_data["avg_duration_seconds"] = perf_data.get("mean")
                    edge_data["min_duration_seconds"] = perf_data.get("min")
                    edge_data["max_duration_seconds"] = perf_data.get("max")
                else:
                    edge_data["avg_duration_seconds"] = perf_data

            edges.append(edge_data)

        return {
            "nodes": nodes,
            "edges": edges,
            "start_activities": dict(start_activities),
            "end_activities": dict(end_activities),
            "total_frequency": total_freq,
        }

    def get_footprints(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Compute behavioral footprints (sequence/parallel relations)."""
        try:
            from pm4py.algo.discovery.footprints import algorithm as footprints_discovery

            fp_result = footprints_discovery.apply(pm4py_log)

            if isinstance(fp_result, list):
                sequence, parallel, activities = set(), set(), set()
                start_acts, end_acts = set(), set()

                for fp in fp_result:
                    if isinstance(fp, dict):
                        sequence.update(fp.get("sequence", set()))
                        parallel.update(fp.get("parallel", set()))
                        activities.update(fp.get("activities", set()))
                        start_acts.update(fp.get("start_activities", set()))
                        end_acts.update(fp.get("end_activities", set()))

                return {
                    "sequence": [f"{k[0]} -> {k[1]}" for k in list(sequence)[:50]],
                    "parallel": [f"{k[0]} || {k[1]}" for k in list(parallel)[:50]],
                    "activities": list(activities),
                    "start_activities": list(start_acts),
                    "end_activities": list(end_acts),
                }

            if isinstance(fp_result, dict):
                return {
                    "sequence": [
                        f"{k[0]} -> {k[1]}" for k in list(fp_result.get("sequence", set()))[:50]
                    ],
                    "parallel": [
                        f"{k[0]} || {k[1]}" for k in list(fp_result.get("parallel", set()))[:50]
                    ],
                    "activities": list(fp_result.get("activities", set())),
                    "start_activities": list(fp_result.get("start_activities", set())),
                    "end_activities": list(fp_result.get("end_activities", set())),
                }

            return {"error": f"Unexpected footprints result type: {type(fp_result)}"}
        except Exception as e:
            return {"error": str(e)}

    def get_activity_statistics(self, pm4py_log: PM4PyLog) -> list[dict[str, Any]]:
        """Get detailed statistics for each activity."""
        start_activities = dict(pm4py.get_start_activities(pm4py_log))
        end_activities = dict(pm4py.get_end_activities(pm4py_log))

        activity_freq: dict[str, int] = {}
        activity_positions: dict[str, list[float]] = {}
        activity_durations: dict[str, list[float]] = {}

        total_events = 0

        for trace in pm4py_log:
            trace_len = len(trace)
            for i, event in enumerate(trace):
                activity = event["concept:name"]

                activity_freq[activity] = activity_freq.get(activity, 0) + 1
                total_events += 1

                if trace_len > 1:
                    normalized_pos = i / (trace_len - 1)
                else:
                    normalized_pos = 0.5

                if activity not in activity_positions:
                    activity_positions[activity] = []
                activity_positions[activity].append(normalized_pos)

                if i < trace_len - 1:
                    next_event = trace[i + 1]
                    current_time = event.get("time:timestamp")
                    next_time = next_event.get("time:timestamp")
                    if current_time and next_time:
                        duration = (next_time - current_time).total_seconds()
                        if duration >= 0:
                            if activity not in activity_durations:
                                activity_durations[activity] = []
                            activity_durations[activity].append(duration)

        activities = []
        for activity, freq in sorted(activity_freq.items(), key=lambda x: -x[1]):
            positions = activity_positions.get(activity, [])
            durations = activity_durations.get(activity, [])

            activity_data = {
                "activity": activity,
                "frequency": freq,
                "frequency_percent": round(freq / total_events * 100, 2) if total_events > 0 else 0,
                "is_start_activity": activity in start_activities,
                "is_end_activity": activity in end_activities,
                "position_avg": round(sum(positions) / len(positions), 4) if positions else None,
            }

            if durations:
                activity_data["avg_duration_seconds"] = round(sum(durations) / len(durations), 2)
                activity_data["min_duration_seconds"] = round(min(durations), 2)
                activity_data["max_duration_seconds"] = round(max(durations), 2)

            activities.append(activity_data)

        return activities

    def get_case_statistics(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Get case duration statistics."""
        try:
            durations = case_statistics.get_all_case_durations(pm4py_log)

            if not durations:
                return {"note": "No case durations available"}

            sorted_durations = sorted(durations)
            return {
                "min_duration_seconds": min(durations),
                "max_duration_seconds": max(durations),
                "avg_duration_seconds": sum(durations) / len(durations),
                "median_duration_seconds": sorted_durations[len(durations) // 2],
                "total_cases": len(durations),
            }
        except Exception as e:
            return {"error": str(e)}

    def calculate_variant_complexity(self, activity_trace: str) -> dict[str, Any]:
        """Calculate complexity metrics for a variant.

        Args:
            activity_trace: Activity sequence in "A → B → C" format
        """
        if " → " in activity_trace:
            activities = [a.strip() for a in activity_trace.split(" → ")]
        else:
            activities = [a.strip() for a in activity_trace.split("->")]

        unique_activities = set(activities)
        unique_count = len(unique_activities)
        total_count = len(activities)

        rework_count = total_count - unique_count
        rework_ratio = rework_count / total_count if total_count > 0 else 0
        unique_ratio = unique_count / total_count if total_count > 0 else 1

        complexity_score = (
            min(total_count / 20, 1.0) * 0.3
            + rework_ratio * 0.4
            + (1 - unique_ratio) * 0.3
        )

        return {
            "complexity_score": round(complexity_score, 4),
            "rework_count": rework_count,
            "unique_activity_count": unique_count,
        }


# Singleton instance
process_analyzer = ProcessAnalyzer()
