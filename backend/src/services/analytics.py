"""Analytics Service - Performance Analytics using PM4Py.

Provides bottleneck detection, rework analysis, service times, cycle times,
throughput metrics, and frequent pattern discovery.
"""

import time
from collections import defaultdict
from datetime import datetime
from typing import Any

import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog
from pm4py.statistics.traces.generic.log import case_statistics

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Performance analytics service using PM4Py."""

    def detect_bottlenecks(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Detect bottlenecks based on waiting and service times."""
        logger.info("detecting_bottlenecks", traces=len(pm4py_log))
        start = time.perf_counter()

        activity_times = defaultdict(lambda: {"waiting": [], "service": [], "count": 0})

        for trace in pm4py_log:
            for i, event in enumerate(trace):
                activity = event.get("concept:name", "")
                activity_times[activity]["count"] += 1

                if i > 0 and "time:timestamp" in event and "time:timestamp" in trace[i - 1]:
                    prev_ts = trace[i - 1]["time:timestamp"]
                    curr_ts = event["time:timestamp"]
                    waiting = (curr_ts - prev_ts).total_seconds()
                    activity_times[activity]["waiting"].append(waiting)

        bottlenecks = []
        for activity, data in activity_times.items():
            avg_waiting = sum(data["waiting"]) / len(data["waiting"]) if data["waiting"] else 0
            avg_service = sum(data["service"]) / len(data["service"]) if data["service"] else 0

            is_bottleneck = avg_waiting > 3600
            severity = "high" if avg_waiting > 86400 else "medium" if avg_waiting > 3600 else "low"

            bottlenecks.append({
                "activity": activity,
                "avg_waiting_time_seconds": round(avg_waiting, 2),
                "avg_service_time_seconds": round(avg_service, 2),
                "frequency": data["count"],
                "is_bottleneck": is_bottleneck,
                "severity": severity,
            })

        bottlenecks.sort(key=lambda x: x["avg_waiting_time_seconds"], reverse=True)

        duration = (time.perf_counter() - start) * 1000
        logger.info("bottlenecks_detected", count=len([b for b in bottlenecks if b["is_bottleneck"]]), duration_ms=round(duration, 2))

        return {"bottlenecks": bottlenecks, "total_bottlenecks": len([b for b in bottlenecks if b["is_bottleneck"]])}

    def analyze_rework(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Analyze rework (repeated activities within cases)."""
        logger.info("analyzing_rework", traces=len(pm4py_log))
        start = time.perf_counter()

        activity_rework = defaultdict(lambda: {"rework_count": 0, "cases_with_rework": 0})
        cases_with_any_rework = 0

        for trace in pm4py_log:
            activity_counts = defaultdict(int)
            for event in trace:
                activity_counts[event.get("concept:name", "")] += 1

            has_rework = False
            for activity, count in activity_counts.items():
                if count > 1:
                    has_rework = True
                    activity_rework[activity]["rework_count"] += count - 1
                    activity_rework[activity]["cases_with_rework"] += 1

            if has_rework:
                cases_with_any_rework += 1

        total_cases = len(pm4py_log)
        rework_activities = [
            {
                "activity": activity,
                "rework_count": data["rework_count"],
                "cases_with_rework": data["cases_with_rework"],
                "rework_percentage": round(data["cases_with_rework"] / total_cases * 100, 2) if total_cases > 0 else 0,
            }
            for activity, data in activity_rework.items()
        ]
        rework_activities.sort(key=lambda x: x["rework_count"], reverse=True)

        duration = (time.perf_counter() - start) * 1000
        logger.info("rework_analyzed", activities_with_rework=len(rework_activities), duration_ms=round(duration, 2))

        return {
            "rework_activities": rework_activities,
            "total_rework_cases": cases_with_any_rework,
            "rework_percentage": round(cases_with_any_rework / total_cases * 100, 2) if total_cases > 0 else 0,
        }

    def get_service_times(self, pm4py_log: PM4PyLog) -> list[dict[str, Any]]:
        """Get service time statistics per activity."""
        logger.info("computing_service_times", traces=len(pm4py_log))
        start = time.perf_counter()

        activity_durations = defaultdict(list)

        for trace in pm4py_log:
            for i, event in enumerate(trace):
                if i < len(trace) - 1 and "time:timestamp" in event and "time:timestamp" in trace[i + 1]:
                    duration = (trace[i + 1]["time:timestamp"] - event["time:timestamp"]).total_seconds()
                    activity_durations[event.get("concept:name", "")].append(duration)

        result = []
        for activity, durations in activity_durations.items():
            if durations:
                sorted_durations = sorted(durations)
                n = len(sorted_durations)
                result.append({
                    "activity": activity,
                    "min_seconds": round(min(durations), 2),
                    "max_seconds": round(max(durations), 2),
                    "avg_seconds": round(sum(durations) / n, 2),
                    "median_seconds": round(sorted_durations[n // 2], 2),
                    "std_dev_seconds": round((sum((x - sum(durations) / n) ** 2 for x in durations) / n) ** 0.5, 2),
                })

        duration = (time.perf_counter() - start) * 1000
        logger.info("service_times_computed", activities=len(result), duration_ms=round(duration, 2))
        return result

    def get_cycle_time(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Get cycle time (case duration) statistics."""
        logger.info("computing_cycle_time", traces=len(pm4py_log))
        start = time.perf_counter()

        try:
            durations = case_statistics.get_all_case_durations(pm4py_log)
        except Exception:
            durations = []
            for trace in pm4py_log:
                timestamps = [e.get("time:timestamp") for e in trace if "time:timestamp" in e]
                if len(timestamps) >= 2:
                    durations.append((max(timestamps) - min(timestamps)).total_seconds())

        if not durations:
            return {"min_seconds": 0, "max_seconds": 0, "avg_seconds": 0, "median_seconds": 0,
                    "percentile_25_seconds": 0, "percentile_75_seconds": 0, "percentile_95_seconds": 0}

        sorted_d = sorted(durations)
        n = len(sorted_d)

        result = {
            "min_seconds": round(min(durations), 2),
            "max_seconds": round(max(durations), 2),
            "avg_seconds": round(sum(durations) / n, 2),
            "median_seconds": round(sorted_d[n // 2], 2),
            "percentile_25_seconds": round(sorted_d[int(n * 0.25)], 2),
            "percentile_75_seconds": round(sorted_d[int(n * 0.75)], 2),
            "percentile_95_seconds": round(sorted_d[int(n * 0.95)], 2),
        }

        duration = (time.perf_counter() - start) * 1000
        logger.info("cycle_time_computed", duration_ms=round(duration, 2))
        return result

    def get_throughput(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Get throughput metrics."""
        logger.info("computing_throughput", traces=len(pm4py_log))
        start = time.perf_counter()

        all_timestamps = []
        for trace in pm4py_log:
            for event in trace:
                if "time:timestamp" in event:
                    all_timestamps.append(event["time:timestamp"])

        if not all_timestamps:
            return {"total_cases": len(pm4py_log), "completed_cases": len(pm4py_log),
                    "cases_per_day": 0, "cases_per_week": 0, "cases_per_month": 0, "time_range_days": 0}

        min_ts, max_ts = min(all_timestamps), max(all_timestamps)
        time_range_days = (max_ts - min_ts).total_seconds() / 86400

        total_cases = len(pm4py_log)
        cases_per_day = total_cases / time_range_days if time_range_days > 0 else 0

        result = {
            "total_cases": total_cases,
            "completed_cases": total_cases,
            "cases_per_day": round(cases_per_day, 2),
            "cases_per_week": round(cases_per_day * 7, 2),
            "cases_per_month": round(cases_per_day * 30, 2),
            "time_range_days": round(time_range_days, 2),
        }

        duration = (time.perf_counter() - start) * 1000
        logger.info("throughput_computed", duration_ms=round(duration, 2))
        return result

    def get_frequent_patterns(self, pm4py_log: PM4PyLog, min_support: float = 0.1) -> list[dict[str, Any]]:
        """Get frequent activity patterns/subsequences."""
        logger.info("computing_patterns", traces=len(pm4py_log), min_support=min_support)
        start = time.perf_counter()

        pattern_counts = defaultdict(int)
        total_traces = len(pm4py_log)

        for trace in pm4py_log:
            activities = [e.get("concept:name", "") for e in trace]
            seen_patterns = set()
            for length in range(2, min(5, len(activities) + 1)):
                for i in range(len(activities) - length + 1):
                    pattern = tuple(activities[i:i + length])
                    if pattern not in seen_patterns:
                        seen_patterns.add(pattern)
                        pattern_counts[pattern] += 1

        patterns = []
        for pattern, count in pattern_counts.items():
            support = count / total_traces if total_traces > 0 else 0
            if support >= min_support:
                patterns.append({
                    "pattern": " -> ".join(pattern),
                    "frequency": count,
                    "support": round(support, 4),
                })

        patterns.sort(key=lambda x: x["frequency"], reverse=True)

        duration = (time.perf_counter() - start) * 1000
        logger.info("patterns_computed", count=len(patterns), duration_ms=round(duration, 2))
        return patterns[:50]

    def get_performance_dashboard(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Get comprehensive performance dashboard."""
        logger.info("computing_performance_dashboard", traces=len(pm4py_log))
        start = time.perf_counter()

        cycle_time = self.get_cycle_time(pm4py_log)
        throughput = self.get_throughput(pm4py_log)
        bottlenecks = self.detect_bottlenecks(pm4py_log)
        rework = self.analyze_rework(pm4py_log)

        result = {
            "cycle_time": cycle_time,
            "throughput": throughput,
            "top_bottlenecks": bottlenecks["bottlenecks"][:5],
            "rework_summary": {
                "total_rework_cases": rework["total_rework_cases"],
                "rework_percentage": rework["rework_percentage"],
                "top_rework_activities": rework["rework_activities"][:5],
            },
        }

        duration = (time.perf_counter() - start) * 1000
        logger.info("performance_dashboard_computed", duration_ms=round(duration, 2))
        return result


analytics_service = AnalyticsService()
