"""Analytics Service - KPIs and Dashboards."""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
from statistics import mean

from src.domain.entities import EventLog
from src.application.core.enhancement_service import enhancement_service


class AnalyticsService:
    """
    Analytics Service.
    Provides dashboard data, KPIs, and statistics.
    """
    
    def get_dashboard_data(
        self,
        event_log: EventLog,
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for an event log.
        """
        # Get KPIs from enhancement service
        kpis = enhancement_service.get_kpis(event_log)
        
        # Get activity statistics
        activity_stats = enhancement_service.get_activity_statistics(event_log)
        
        # Get variant distribution
        variants = event_log.variants
        variant_data = [
            {
                "key": v.key[:50] + "..." if len(v.key) > 50 else v.key,
                "count": v.case_count,
                "percentage": v.case_count / event_log.total_cases * 100 if event_log.total_cases > 0 else 0,
                "length": v.length,
            }
            for v in variants[:10]
        ]
        
        # Time series data
        time_series = self._get_time_series(event_log)
        
        return {
            "summary": {
                "total_cases": event_log.total_cases,
                "total_events": event_log.total_events,
                "unique_activities": len(event_log.activities),
                "unique_variants": len(variants),
                "unique_resources": len(event_log.resources),
            },
            "kpis": kpis,
            "top_activities": activity_stats[:10],
            "top_variants": variant_data,
            "time_series": time_series,
        }
    
    def get_variant_statistics(
        self,
        event_log: EventLog,
        top_n: int = 20,
    ) -> Dict[str, Any]:
        """
        Get detailed variant statistics.
        """
        variants = event_log.variants
        
        # Pareto analysis
        total_cases = event_log.total_cases
        cumulative = 0
        pareto_data = []
        
        for i, v in enumerate(variants[:top_n]):
            cumulative += v.case_count
            pareto_data.append({
                "rank": i + 1,
                "variant": v.key[:100],
                "count": v.case_count,
                "percentage": v.case_count / total_cases * 100 if total_cases > 0 else 0,
                "cumulative_percentage": cumulative / total_cases * 100 if total_cases > 0 else 0,
            })
        
        return {
            "total_variants": len(variants),
            "top_variants": pareto_data,
            "variants_needed_for_80": self._find_pareto_threshold(variants, total_cases, 0.8),
        }
    
    def get_resource_statistics(
        self,
        event_log: EventLog,
    ) -> Dict[str, Any]:
        """
        Get resource/user statistics.
        """
        resource_data = {}
        
        for case in event_log.cases:
            for event in case.events:
                resource = str(event.resource) if event.resource else "unknown"
                
                if resource not in resource_data:
                    resource_data[resource] = {
                        "resource": resource,
                        "event_count": 0,
                        "activities": set(),
                        "cases": set(),
                    }
                
                resource_data[resource]["event_count"] += 1
                resource_data[resource]["activities"].add(str(event.activity))
                resource_data[resource]["cases"].add(event.case_id)
        
        # Convert to serializable format
        result = []
        for resource, data in resource_data.items():
            result.append({
                "resource": resource,
                "event_count": data["event_count"],
                "activity_count": len(data["activities"]),
                "case_count": len(data["cases"]),
                "top_activities": list(data["activities"])[:5],
            })
        
        return {
            "total_resources": len(resource_data),
            "resources": sorted(result, key=lambda x: x["event_count"], reverse=True)[:20],
        }
    
    def get_time_analysis(
        self,
        event_log: EventLog,
        granularity: str = "day",
    ) -> Dict[str, Any]:
        """
        Get time-based analysis of the process.
        """
        time_series = self._get_time_series(event_log, granularity)
        
        # Weekday distribution
        weekday_counts = [0] * 7
        hour_counts = [0] * 24
        
        for case in event_log.cases:
            for event in case.events:
                ts = event.timestamp.value
                weekday_counts[ts.weekday()] += 1
                hour_counts[ts.hour] += 1
        
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        return {
            "time_series": time_series,
            "weekday_distribution": [
                {"day": weekday_names[i], "count": count}
                for i, count in enumerate(weekday_counts)
            ],
            "hourly_distribution": [
                {"hour": f"{i:02d}:00", "count": count}
                for i, count in enumerate(hour_counts)
            ],
        }
    
    def get_comparison(
        self,
        log1: EventLog,
        log2: EventLog,
    ) -> Dict[str, Any]:
        """
        Compare two event logs.
        """
        kpis1 = enhancement_service.get_kpis(log1)
        kpis2 = enhancement_service.get_kpis(log2)
        
        return {
            "log1": {
                "id": str(log1.id),
                "name": log1.name,
                "kpis": kpis1,
            },
            "log2": {
                "id": str(log2.id),
                "name": log2.name,
                "kpis": kpis2,
            },
            "comparison": {
                "case_count_diff": log2.total_cases - log1.total_cases,
                "event_count_diff": log2.total_events - log1.total_events,
                "avg_duration_diff_seconds": (
                    kpis2["avg_case_duration_seconds"] - kpis1["avg_case_duration_seconds"]
                ),
                "throughput_diff": kpis2["throughput_per_day"] - kpis1["throughput_per_day"],
            },
        }
    
    def _get_time_series(
        self,
        event_log: EventLog,
        granularity: str = "day",
    ) -> List[Dict[str, Any]]:
        """Generate time series data for events."""
        if granularity == "hour":
            format_str = "%Y-%m-%d %H:00"
        elif granularity == "day":
            format_str = "%Y-%m-%d"
        elif granularity == "week":
            format_str = "%Y-W%W"
        elif granularity == "month":
            format_str = "%Y-%m"
        else:
            format_str = "%Y-%m-%d"
        
        time_buckets = {}
        
        for case in event_log.cases:
            for event in case.events:
                bucket = event.timestamp.value.strftime(format_str)
                time_buckets[bucket] = time_buckets.get(bucket, 0) + 1
        
        return [
            {"period": period, "count": count}
            for period, count in sorted(time_buckets.items())
        ]
    
    def _find_pareto_threshold(
        self,
        variants: list,
        total_cases: int,
        threshold: float,
    ) -> int:
        """Find how many variants needed to cover threshold % of cases."""
        if total_cases == 0:
            return 0
        
        cumulative = 0
        for i, v in enumerate(variants):
            cumulative += v.case_count
            if cumulative / total_cases >= threshold:
                return i + 1
        
        return len(variants)


# Singleton instance
analytics_service = AnalyticsService()
