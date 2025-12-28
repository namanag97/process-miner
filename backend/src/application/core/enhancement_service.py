"""Process Enhancement Service - Performance Analysis."""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import timedelta
from statistics import mean, median

from src.domain.entities import EventLog, PerformanceMetrics
from src.domain.value_objects import Duration
from src.domain.aggregates import AnalysisAggregate


class EnhancementService:
    """
    Process Enhancement Service.
    Analyzes process performance, identifies bottlenecks, and measures KPIs.
    """
    
    def analyze_performance(
        self,
        event_log: EventLog,
    ) -> PerformanceMetrics:
        """
        Analyze performance of a process from event log.
        
        Returns:
            PerformanceMetrics with duration stats and bottleneck analysis
        """
        # Calculate case durations
        case_durations = []
        for case in event_log.cases:
            if case.duration:
                case_durations.append(case.duration.total_seconds)
        
        if not case_durations:
            # No durations available
            return PerformanceMetrics(
                id=uuid4(),
                log_id=event_log.id,
                avg_case_duration=Duration.from_seconds(0),
                median_case_duration=Duration.from_seconds(0),
                min_case_duration=Duration.from_seconds(0),
                max_case_duration=Duration.from_seconds(0),
            )
        
        # Calculate duration statistics
        avg_duration = mean(case_durations)
        median_duration = median(case_durations)
        min_duration = min(case_durations)
        max_duration = max(case_durations)
        
        # Analyze waiting times between activities
        waiting_times = self._calculate_waiting_times(event_log)
        
        # Identify bottlenecks (activities with highest waiting times)
        bottlenecks = self._identify_bottlenecks(waiting_times)
        
        # Calculate processing times per activity
        processing_times = self._calculate_processing_times(event_log)
        
        return PerformanceMetrics(
            id=uuid4(),
            log_id=event_log.id,
            avg_case_duration=Duration.from_seconds(avg_duration),
            median_case_duration=Duration.from_seconds(median_duration),
            min_case_duration=Duration.from_seconds(min_duration),
            max_case_duration=Duration.from_seconds(max_duration),
            bottleneck_activities=bottlenecks,
            waiting_times=waiting_times,
            processing_times=processing_times,
        )
    
    def get_kpis(self, event_log: EventLog) -> Dict[str, Any]:
        """
        Calculate key performance indicators for a process.
        """
        metrics = self.analyze_performance(event_log)
        
        # Throughput (cases per day)
        start, end = event_log.date_range
        if start and end:
            days = (end - start).days + 1
            throughput = event_log.total_cases / days if days > 0 else 0
        else:
            throughput = 0
        
        # Activity utilization
        activity_counts = {}
        for case in event_log.cases:
            for event in case.events:
                activity = str(event.activity)
                activity_counts[activity] = activity_counts.get(activity, 0) + 1
        
        # Calculate variant distribution
        variants = event_log.variants
        top_variants = variants[:5] if len(variants) >= 5 else variants
        variant_coverage = sum(v.case_count for v in top_variants) / event_log.total_cases if event_log.total_cases > 0 else 0
        
        return {
            "total_cases": event_log.total_cases,
            "total_events": event_log.total_events,
            "unique_activities": len(event_log.activities),
            "unique_variants": len(variants),
            "avg_case_duration_seconds": metrics.avg_case_duration.total_seconds,
            "median_case_duration_seconds": metrics.median_case_duration.total_seconds,
            "min_case_duration_seconds": metrics.min_case_duration.total_seconds,
            "max_case_duration_seconds": metrics.max_case_duration.total_seconds,
            "throughput_per_day": throughput,
            "top_5_variant_coverage": variant_coverage,
            "bottleneck_activities": metrics.bottleneck_activities,
            "activity_frequencies": activity_counts,
        }
    
    def get_activity_statistics(
        self,
        event_log: EventLog,
    ) -> List[Dict[str, Any]]:
        """Get statistics for each activity in the log."""
        activity_stats = {}
        
        for case in event_log.cases:
            for i, event in enumerate(case.events):
                activity = str(event.activity)
                
                if activity not in activity_stats:
                    activity_stats[activity] = {
                        "name": activity,
                        "count": 0,
                        "case_count": 0,
                        "durations": [],
                        "cases": set(),
                    }
                
                activity_stats[activity]["count"] += 1
                activity_stats[activity]["cases"].add(case.case_id)
                
                # Calculate duration to next activity
                if i < len(case.events) - 1:
                    next_event = case.events[i + 1]
                    duration = (next_event.timestamp.value - event.timestamp.value).total_seconds()
                    if duration > 0:
                        activity_stats[activity]["durations"].append(duration)
        
        # Convert to list and calculate statistics
        result = []
        for activity, stats in activity_stats.items():
            durations = stats["durations"]
            result.append({
                "activity": activity,
                "total_count": stats["count"],
                "case_count": len(stats["cases"]),
                "avg_duration_seconds": mean(durations) if durations else 0,
                "median_duration_seconds": median(durations) if durations else 0,
                "min_duration_seconds": min(durations) if durations else 0,
                "max_duration_seconds": max(durations) if durations else 0,
            })
        
        return sorted(result, key=lambda x: x["total_count"], reverse=True)
    
    def get_case_statistics(
        self,
        event_log: EventLog,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get statistics for individual cases."""
        result = []
        
        for case in event_log.cases[:limit]:
            duration = case.duration
            result.append({
                "case_id": case.case_id,
                "event_count": len(case.events),
                "variant": case.variant_key,
                "duration_seconds": duration.total_seconds if duration else 0,
                "start_time": case.start_time.to_iso() if case.start_time else None,
                "end_time": case.end_time.to_iso() if case.end_time else None,
            })
        
        return result
    
    def _calculate_waiting_times(
        self,
        event_log: EventLog,
    ) -> Dict[str, float]:
        """Calculate average waiting time before each activity."""
        waiting_times = {}
        
        for case in event_log.cases:
            for i, event in enumerate(case.events):
                if i > 0:
                    prev_event = case.events[i - 1]
                    wait_time = (event.timestamp.value - prev_event.timestamp.value).total_seconds()
                    
                    activity = str(event.activity)
                    if activity not in waiting_times:
                        waiting_times[activity] = []
                    waiting_times[activity].append(wait_time)
        
        # Calculate averages
        return {
            activity: mean(times) if times else 0
            for activity, times in waiting_times.items()
        }
    
    def _calculate_processing_times(
        self,
        event_log: EventLog,
    ) -> Dict[str, float]:
        """Calculate average processing time for each activity."""
        # For now, use waiting time as proxy for processing time
        # In real scenarios, this would need activity duration data
        return self._calculate_waiting_times(event_log)
    
    def _identify_bottlenecks(
        self,
        waiting_times: Dict[str, float],
        top_n: int = 5,
    ) -> List[str]:
        """Identify top bottleneck activities based on waiting times."""
        sorted_activities = sorted(
            waiting_times.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return [activity for activity, _ in sorted_activities[:top_n]]


# Singleton instance
enhancement_service = EnhancementService()
