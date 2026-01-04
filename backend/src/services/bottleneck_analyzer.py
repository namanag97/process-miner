"""Bottleneck Analysis Service.

Identifies congestion points in process models.
"""

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

import structlog
from pm4py.objects.log.obj import EventLog

logger = structlog.get_logger(__name__)


class BottleneckAnalyzer:
    """Analyze process bottlenecks and congestion."""

    def calculate_waiting_times(
        self,
        log: EventLog
    ) -> dict[str, dict[str, Any]]:
        """Calculate waiting times between activities.

        Args:
            log: Event log

        Returns:
            Dict mapping activity -> waiting time stats
        """
        waiting_times: dict[str, list[float]] = defaultdict(list)

        for trace in log:
            for i in range(len(trace) - 1):
                current_event = trace[i]
                next_event = trace[i + 1]

                current_time = current_event["time:timestamp"]
                next_time = next_event["time:timestamp"]
                next_activity = next_event["concept:name"]

                # Calculate waiting time in seconds
                if isinstance(current_time, datetime) and isinstance(next_time, datetime):
                    waiting_seconds = (next_time - current_time).total_seconds()
                    waiting_times[next_activity].append(waiting_seconds)

        # Calculate statistics
        stats = {}
        for activity, times in waiting_times.items():
            if times:
                stats[activity] = {
                    "mean": sum(times) / len(times),
                    "median": sorted(times)[len(times) // 2],
                    "max": max(times),
                    "min": min(times),
                    "p95": sorted(times)[int(len(times) * 0.95)] if len(times) > 0 else 0,
                    "count": len(times),
                }

        logger.info("waiting_times_calculated", activities=len(stats))
        return stats

    def identify_bottlenecks(
        self,
        log: EventLog,
        threshold_percentile: float = 0.9
    ) -> list[dict[str, Any]]:
        """Identify bottleneck activities.

        Args:
            log: Event log
            threshold_percentile: Activities above this percentile are bottlenecks

        Returns:
            List of bottleneck activities with metrics
        """
        waiting_stats = self.calculate_waiting_times(log)

        if not waiting_stats:
            return []

        # Calculate threshold
        all_means = [stats["mean"] for stats in waiting_stats.values()]
        all_means.sort()
        threshold_idx = int(len(all_means) * threshold_percentile)
        threshold = all_means[threshold_idx] if threshold_idx < len(all_means) else all_means[-1]

        # Find bottlenecks
        bottlenecks = []
        for activity, stats in waiting_stats.items():
            if stats["mean"] >= threshold:
                bottlenecks.append({
                    "activity": activity,
                    "avg_waiting_time": stats["mean"],
                    "max_waiting_time": stats["max"],
                    "p95_waiting_time": stats["p95"],
                    "occurrences": stats["count"],
                    "severity": "high" if stats["mean"] >= threshold * 1.5 else "medium",
                })

        # Sort by severity
        bottlenecks.sort(key=lambda x: x["avg_waiting_time"], reverse=True)

        logger.info(
            "bottlenecks_identified",
            total_activities=len(waiting_stats),
            bottlenecks=len(bottlenecks),
            threshold=threshold
        )

        return bottlenecks

    def calculate_throughput(
        self,
        log: EventLog,
        time_window_hours: int = 1
    ) -> dict[str, dict[datetime, int]]:
        """Calculate activity throughput over time.

        Args:
            log: Event log
            time_window_hours: Time window for aggregation

        Returns:
            Dict mapping activity -> {timestamp: count}
        """
        throughput: dict[str, Counter] = defaultdict(Counter)

        for trace in log:
            for event in trace:
                activity = event["concept:name"]
                timestamp = event["time:timestamp"]

                if isinstance(timestamp, datetime):
                    # Round to window
                    window_start = timestamp.replace(
                        minute=0,
                        second=0,
                        microsecond=0
                    )
                    throughput[activity][window_start] += 1

        logger.info(
            "throughput_calculated",
            activities=len(throughput),
            window_hours=time_window_hours
        )

        return {
            activity: dict(counter)
            for activity, counter in throughput.items()
        }

    def calculate_heat_map_data(
        self,
        log: EventLog
    ) -> dict[str, float]:
        """Calculate heat map intensity for each activity.

        Args:
            log: Event log

        Returns:
            Dict mapping activity -> heat intensity (0-1)
        """
        waiting_stats = self.calculate_waiting_times(log)

        if not waiting_stats:
            return {}

        # Normalize to 0-1 scale
        max_waiting = max(stats["mean"] for stats in waiting_stats.values())

        heat_map = {}
        for activity, stats in waiting_stats.items():
            intensity = stats["mean"] / max_waiting if max_waiting > 0 else 0
            heat_map[activity] = intensity

        logger.info("heat_map_calculated", activities=len(heat_map))
        return heat_map

    def calculate_queue_lengths(
        self,
        log: EventLog
    ) -> dict[str, dict[str, Any]]:
        """Calculate queue lengths at each activity.

        Args:
            log: Event log

        Returns:
            Dict mapping activity -> queue stats
        """
        # Track concurrent executions
        activity_timelines: dict[str, list[tuple[datetime, datetime]]] = defaultdict(list)

        for trace in log:
            for i, event in enumerate(trace):
                activity = event["concept:name"]
                start_time = event["time:timestamp"]

                # Estimate end time (use next event or add avg duration)
                if i + 1 < len(trace):
                    end_time = trace[i + 1]["time:timestamp"]
                else:
                    end_time = start_time

                if isinstance(start_time, datetime) and isinstance(end_time, datetime):
                    activity_timelines[activity].append((start_time, end_time))

        # Calculate max concurrent executions (queue length)
        queue_stats = {}
        for activity, timeline in activity_timelines.items():
            if not timeline:
                continue

            # Sort by start time
            timeline.sort()

            max_concurrent = 0
            current_concurrent = 0
            events = []

            # Create start/end events
            for start, end in timeline:
                events.append((start, 1))  # Start event
                events.append((end, -1))   # End event

            events.sort()

            # Sweep through events
            for _, delta in events:
                current_concurrent += delta
                max_concurrent = max(max_concurrent, current_concurrent)

            queue_stats[activity] = {
                "max_queue_length": max_concurrent,
                "total_executions": len(timeline),
                "avg_queue_length": max_concurrent / 2,  # Rough estimate
            }

        logger.info("queue_lengths_calculated", activities=len(queue_stats))
        return queue_stats
