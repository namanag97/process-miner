"""Filtering Service - PM4Py Log Filtering Integration.

Provides comprehensive event log filtering capabilities using PM4Py's filtering module.
Supports time-based, variant-based, activity-based, and performance-based filtering.
"""

import time
from datetime import datetime
from typing import Any

import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog

from src.features.process_mining.models import Dataset
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class FilterType:
    """Filter type constants."""

    # Basic filters
    TIME_RANGE = "time_range"
    VARIANTS_TOP_K = "variants_top_k"
    VARIANTS_COVERAGE = "variants_coverage"
    ACTIVITIES = "activities"
    CASE_PERFORMANCE = "case_performance"
    CASE_SIZE = "case_size"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    ATTRIBUTE_VALUES = "attribute_values"

    # Advanced filters (Phase 4 PM4py integration)
    DIRECTLY_FOLLOWS = "directly_follows"  # Keep cases with A directly before B
    EVENTUALLY_FOLLOWS = "eventually_follows"  # Keep cases with A eventually before B
    BETWEEN = "between"  # Extract sub-cases between two activities
    FOUR_EYES = "four_eyes"  # Governance: different resources for A and B
    REWORK = "rework"  # Cases with activity repetition
    PREFIXES = "prefixes"  # Extract case prefixes
    SUFFIXES = "suffixes"  # Extract case suffixes
    PATH_PERFORMANCE = "path_performance"  # Filter by path duration


class FilteringService:
    """
    Event Log Filtering Service.

    Wraps PM4Py filtering functions to provide comprehensive log filtering.
    Supports chaining multiple filters and computing impact statistics.
    """

    # =========================================================================
    # Time-Based Filtering
    # =========================================================================

    def filter_time_range(
        self,
        pm4py_log: PM4PyLog,
        start_time: datetime,
        end_time: datetime,
    ) -> PM4PyLog:
        """
        Filter events within a time range.

        Args:
            pm4py_log: PM4Py event log
            start_time: Start of time range (inclusive)
            end_time: End of time range (inclusive)

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_time_range",
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_time_range(
            pm4py_log,
            start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time.strftime("%Y-%m-%d %H:%M:%S"),
            mode="events",
        )

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_time_range_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    # =========================================================================
    # Variant-Based Filtering
    # =========================================================================

    def filter_variants_top_k(
        self,
        pm4py_log: PM4PyLog,
        k: int = 10,
    ) -> PM4PyLog:
        """
        Keep only the top K most frequent variants.

        Args:
            pm4py_log: PM4Py event log
            k: Number of top variants to keep

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_variants_top_k",
            k=k,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_variants_top_k(pm4py_log, k=k)

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_variants_top_k_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_variants_coverage(
        self,
        pm4py_log: PM4PyLog,
        min_coverage_percentage: float = 0.8,
    ) -> PM4PyLog:
        """
        Keep variants that cover a minimum percentage of cases.

        Args:
            pm4py_log: PM4Py event log
            min_coverage_percentage: Minimum coverage (0.0 to 1.0)

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_variants_coverage",
            coverage=min_coverage_percentage,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_variants_by_coverage_percentage(
            pm4py_log,
            min_coverage_percentage=min_coverage_percentage,
        )

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_variants_coverage_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    # =========================================================================
    # Activity-Based Filtering
    # =========================================================================

    def filter_activities(
        self,
        pm4py_log: PM4PyLog,
        activities: list[str],
        mode: str = "keep",
        positive: bool = True,
    ) -> PM4PyLog:
        """
        Filter cases containing (or not containing) specific activities.

        Args:
            pm4py_log: PM4Py event log
            activities: List of activity names
            mode: 'keep' to keep cases with activities, 'remove' to remove
            positive: If True, keep matching cases; if False, exclude them

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_activities",
            activities=activities,
            mode=mode,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        retain = mode == "keep"
        filtered = pm4py.filter_event_attribute_values(
            pm4py_log,
            attribute_key="concept:name",
            values=activities,
            level="case",
            retain=retain,
        )

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_activities_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_start_activities(
        self,
        pm4py_log: PM4PyLog,
        activities: list[str],
    ) -> PM4PyLog:
        """
        Filter to cases starting with specific activities.

        Args:
            pm4py_log: PM4Py event log
            activities: Allowed start activities

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_start_activities",
            activities=activities,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_start_activities(pm4py_log, activities=activities)

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_start_activities_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_end_activities(
        self,
        pm4py_log: PM4PyLog,
        activities: list[str],
    ) -> PM4PyLog:
        """
        Filter to cases ending with specific activities.

        Args:
            pm4py_log: PM4Py event log
            activities: Allowed end activities

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_end_activities",
            activities=activities,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_end_activities(pm4py_log, activities=activities)

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_end_activities_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    # =========================================================================
    # Performance-Based Filtering
    # =========================================================================

    def filter_case_performance(
        self,
        pm4py_log: PM4PyLog,
        min_duration: float | None = None,
        max_duration: float | None = None,
    ) -> PM4PyLog:
        """
        Filter cases by duration (in seconds).

        Args:
            pm4py_log: PM4Py event log
            min_duration: Minimum case duration in seconds
            max_duration: Maximum case duration in seconds

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_case_performance",
            min_duration=min_duration,
            max_duration=max_duration,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_case_performance(
            pm4py_log,
            min_performance=min_duration or 0,
            max_performance=max_duration or float("inf"),
        )

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_case_performance_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_case_size(
        self,
        pm4py_log: PM4PyLog,
        min_size: int = 1,
        max_size: int | None = None,
    ) -> PM4PyLog:
        """
        Filter cases by number of events.

        Args:
            pm4py_log: PM4Py event log
            min_size: Minimum number of events per case
            max_size: Maximum number of events per case

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_case_size",
            min_size=min_size,
            max_size=max_size,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_case_size(
            pm4py_log,
            min_size=min_size,
            max_size=max_size or float("inf"),
        )

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_case_size_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    # =========================================================================
    # Attribute-Based Filtering
    # =========================================================================

    def filter_attribute_values(
        self,
        pm4py_log: PM4PyLog,
        attribute_key: str,
        values: list[str],
        retain: bool = True,
        level: str = "case",
    ) -> PM4PyLog:
        """
        Filter by event/case attribute values.

        Args:
            pm4py_log: PM4Py event log
            attribute_key: Attribute to filter on
            values: Values to match
            retain: If True, keep matching; if False, exclude
            level: 'case' or 'event'

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_attribute_values",
            attribute=attribute_key,
            values=values,
            retain=retain,
            level=level,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_event_attribute_values(
            pm4py_log,
            attribute_key=attribute_key,
            values=values,
            level=level,
            retain=retain,
        )

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_attribute_values_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    # =========================================================================
    # Advanced Filtering (Phase 4 PM4py Integration)
    # =========================================================================

    def filter_directly_follows(
        self,
        pm4py_log: PM4PyLog,
        activity_a: str,
        activity_b: str,
        retain: bool = True,
    ) -> PM4PyLog:
        """
        Filter cases where activity A directly precedes activity B.

        Args:
            pm4py_log: PM4Py event log
            activity_a: First activity
            activity_b: Second activity (must directly follow A)
            retain: If True, keep matching cases; if False, exclude

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_directly_follows",
            activity_a=activity_a,
            activity_b=activity_b,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_directly_follows_relation(
            pm4py_log,
            [activity_a, activity_b],
            retain=retain,
        )

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_directly_follows_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_eventually_follows(
        self,
        pm4py_log: PM4PyLog,
        activity_a: str,
        activity_b: str,
        retain: bool = True,
    ) -> PM4PyLog:
        """
        Filter cases where activity A eventually precedes activity B.

        Args:
            pm4py_log: PM4Py event log
            activity_a: First activity
            activity_b: Second activity (must eventually follow A)
            retain: If True, keep matching cases; if False, exclude

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "filtering_eventually_follows",
            activity_a=activity_a,
            activity_b=activity_b,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_eventually_follows_relation(
            pm4py_log,
            [activity_a, activity_b],
            retain=retain,
        )

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_eventually_follows_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_between(
        self,
        pm4py_log: PM4PyLog,
        activity_a: str,
        activity_b: str,
    ) -> PM4PyLog:
        """
        Extract sub-cases between two activities.

        Creates new traces containing only events between A and B (inclusive).

        Args:
            pm4py_log: PM4Py event log
            activity_a: Start activity
            activity_b: End activity

        Returns:
            Log with sub-traces between A and B
        """
        logger.info(
            "filtering_between",
            activity_a=activity_a,
            activity_b=activity_b,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_between(pm4py_log, activity_a, activity_b)

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_between_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_four_eyes_principle(
        self,
        pm4py_log: PM4PyLog,
        activity_a: str,
        activity_b: str,
    ) -> PM4PyLog:
        """
        Filter cases where activities A and B are done by different resources.

        Governance filter for separation of duties compliance.

        Args:
            pm4py_log: PM4Py event log
            activity_a: First activity
            activity_b: Second activity

        Returns:
            Cases where A and B have different resources
        """
        logger.info(
            "filtering_four_eyes_principle",
            activity_a=activity_a,
            activity_b=activity_b,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_four_eyes_principle(pm4py_log, activity_a, activity_b)

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_four_eyes_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_rework(
        self,
        pm4py_log: PM4PyLog,
        activity: str,
        min_occurrences: int = 2,
    ) -> PM4PyLog:
        """
        Filter cases with activity rework (repeated execution).

        Args:
            pm4py_log: PM4Py event log
            activity: Activity to check for repetition
            min_occurrences: Minimum number of occurrences to consider rework

        Returns:
            Cases where activity appears multiple times
        """
        logger.info(
            "filtering_rework",
            activity=activity,
            min_occurrences=min_occurrences,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        try:
            filtered = pm4py.filter_activities_rework(pm4py_log, activity, min_occurrences)
        except Exception:
            # Fallback: manual filtering
            result = PM4PyLog()
            for trace in pm4py_log:
                count = sum(1 for e in trace if e.get("concept:name") == activity)
                if count >= min_occurrences:
                    result.append(trace)
            filtered = result

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_rework_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_prefixes(
        self,
        pm4py_log: PM4PyLog,
        length: int = 5,
    ) -> PM4PyLog:
        """
        Extract prefix of each case up to specified length.

        Args:
            pm4py_log: PM4Py event log
            length: Maximum prefix length

        Returns:
            Log with truncated traces (prefixes only)
        """
        logger.info(
            "filtering_prefixes",
            length=length,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_prefixes(pm4py_log, length)

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_prefixes_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_suffixes(
        self,
        pm4py_log: PM4PyLog,
        length: int = 5,
    ) -> PM4PyLog:
        """
        Extract suffix of each case (last N events).

        Args:
            pm4py_log: PM4Py event log
            length: Maximum suffix length

        Returns:
            Log with truncated traces (suffixes only)
        """
        logger.info(
            "filtering_suffixes",
            length=length,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_suffixes(pm4py_log, length)

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_suffixes_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    def filter_paths_performance(
        self,
        pm4py_log: PM4PyLog,
        path: list[str],
        min_duration: float | None = None,
        max_duration: float | None = None,
    ) -> PM4PyLog:
        """
        Filter cases by performance (duration) along a specific path.

        Args:
            pm4py_log: PM4Py event log
            path: Activity sequence to measure
            min_duration: Minimum path duration in seconds
            max_duration: Maximum path duration in seconds

        Returns:
            Cases where path duration is within bounds
        """
        logger.info(
            "filtering_paths_performance",
            path=path,
            min_duration=min_duration,
            max_duration=max_duration,
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        filtered = pm4py.filter_paths_performance(
            pm4py_log,
            path,
            min_performance=min_duration or 0,
            max_performance=max_duration or float("inf"),
        )

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filtering_paths_performance_completed",
            filtered_traces=len(filtered),
            duration_ms=round(duration, 2),
        )
        return filtered

    # =========================================================================
    # Filter Chain Execution
    # =========================================================================

    def apply_filter_chain(
        self,
        pm4py_log: PM4PyLog,
        filters: list[dict[str, Any]],
    ) -> PM4PyLog:
        """
        Apply a chain of filters sequentially.

        Args:
            pm4py_log: PM4Py event log
            filters: List of filter configurations
                Each filter: {"type": "...", "params": {...}}

        Returns:
            Filtered PM4Py log
        """
        logger.info(
            "applying_filter_chain",
            filter_count=len(filters),
            original_traces=len(pm4py_log),
        )
        start = time.perf_counter()

        result = pm4py_log
        for i, filter_config in enumerate(filters):
            filter_type = filter_config.get("type")
            params = filter_config.get("params", {})

            logger.debug(
                "applying_filter",
                step=i + 1,
                filter_type=filter_type,
                current_traces=len(result),
            )

            result = self._apply_single_filter(result, filter_type, params)

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filter_chain_completed",
            filter_count=len(filters),
            final_traces=len(result),
            total_duration_ms=round(duration, 2),
        )
        return result

    def _apply_single_filter(
        self,
        pm4py_log: PM4PyLog,
        filter_type: str,
        params: dict[str, Any],
    ) -> PM4PyLog:
        """Apply a single filter based on type."""
        if filter_type == FilterType.TIME_RANGE:
            start_time = datetime.fromisoformat(params["start_time"])
            end_time = datetime.fromisoformat(params["end_time"])
            return self.filter_time_range(pm4py_log, start_time, end_time)

        if filter_type == FilterType.VARIANTS_TOP_K:
            return self.filter_variants_top_k(pm4py_log, k=params.get("k", 10))

        if filter_type == FilterType.VARIANTS_COVERAGE:
            return self.filter_variants_coverage(
                pm4py_log,
                min_coverage_percentage=params.get("coverage", 0.8),
            )

        if filter_type == FilterType.ACTIVITIES:
            return self.filter_activities(
                pm4py_log,
                activities=params["activities"],
                mode=params.get("mode", "keep"),
            )

        if filter_type == FilterType.CASE_PERFORMANCE:
            return self.filter_case_performance(
                pm4py_log,
                min_duration=params.get("min_duration"),
                max_duration=params.get("max_duration"),
            )

        if filter_type == FilterType.CASE_SIZE:
            return self.filter_case_size(
                pm4py_log,
                min_size=params.get("min_size", 1),
                max_size=params.get("max_size"),
            )

        if filter_type == FilterType.START_ACTIVITIES:
            return self.filter_start_activities(
                pm4py_log,
                activities=params["activities"],
            )

        if filter_type == FilterType.END_ACTIVITIES:
            return self.filter_end_activities(
                pm4py_log,
                activities=params["activities"],
            )

        if filter_type == FilterType.ATTRIBUTE_VALUES:
            return self.filter_attribute_values(
                pm4py_log,
                attribute_key=params["attribute"],
                values=params["values"],
                retain=params.get("retain", True),
                level=params.get("level", "case"),
            )

        raise ValueError(f"Unknown filter type: {filter_type}")

    # =========================================================================
    # Statistics & Analysis
    # =========================================================================

    def compute_filter_statistics(
        self,
        original: PM4PyLog,
        filtered: PM4PyLog,
    ) -> dict[str, Any]:
        """
        Compute statistics comparing original and filtered logs.

        Args:
            original: Original PM4Py log
            filtered: Filtered PM4Py log

        Returns:
            Dictionary with comparison statistics
        """
        original_cases = len(original)
        filtered_cases = len(filtered)
        original_events = sum(len(trace) for trace in original)
        filtered_events = sum(len(trace) for trace in filtered)

        # Get unique activities
        original_activities = set()
        filtered_activities = set()
        for trace in original:
            for event in trace:
                original_activities.add(event.get("concept:name", ""))
        for trace in filtered:
            for event in trace:
                filtered_activities.add(event.get("concept:name", ""))

        return {
            "original_cases": original_cases,
            "filtered_cases": filtered_cases,
            "cases_removed": original_cases - filtered_cases,
            "cases_retained_pct": round(
                filtered_cases / original_cases * 100 if original_cases > 0 else 0, 2
            ),
            "original_events": original_events,
            "filtered_events": filtered_events,
            "events_removed": original_events - filtered_events,
            "events_retained_pct": round(
                filtered_events / original_events * 100 if original_events > 0 else 0, 2
            ),
            "original_activities": len(original_activities),
            "filtered_activities": len(filtered_activities),
            "activities_removed": len(original_activities - filtered_activities),
        }

    def get_filter_options(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """
        Get available filter options based on log contents.

        Args:
            pm4py_log: PM4Py event log

        Returns:
            Dictionary with available filter values
        """
        logger.info("computing_filter_options", traces=len(pm4py_log))
        start = time.perf_counter()

        # Get activities
        activities = set()
        resources = set()
        timestamps = []

        for trace in pm4py_log:
            for event in trace:
                activities.add(event.get("concept:name", ""))
                if "org:resource" in event:
                    resources.add(event["org:resource"])
                if "time:timestamp" in event:
                    timestamps.append(event["time:timestamp"])

        # Get start/end activities
        start_activities = pm4py.get_start_activities(pm4py_log)
        end_activities = pm4py.get_end_activities(pm4py_log)

        # Get variants
        variants = pm4py.get_variants(pm4py_log)

        # Time range
        min_time = min(timestamps) if timestamps else None
        max_time = max(timestamps) if timestamps else None

        # Case sizes
        case_sizes = [len(trace) for trace in pm4py_log]

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "filter_options_computed",
            activities=len(activities),
            variants=len(variants),
            duration_ms=round(duration, 2),
        )

        return {
            "activities": sorted(activities),
            "resources": sorted(resources) if resources else [],
            "start_activities": dict(start_activities),
            "end_activities": dict(end_activities),
            "total_variants": len(variants),
            "time_range": {
                "min": min_time.isoformat() if min_time else None,
                "max": max_time.isoformat() if max_time else None,
            },
            "case_size_range": {
                "min": min(case_sizes) if case_sizes else 0,
                "max": max(case_sizes) if case_sizes else 0,
                "avg": round(sum(case_sizes) / len(case_sizes), 2) if case_sizes else 0,
            },
        }

    # =========================================================================
    # Pre-built Filter Templates
    # =========================================================================

    def get_filter_templates(self) -> list[dict[str, Any]]:
        """Get pre-built filter configurations."""
        return [
            {
                "id": "happy_path",
                "name": "Happy Path (Top 80%)",
                "description": "Keep variants covering 80% of cases",
                "filters": [{"type": FilterType.VARIANTS_COVERAGE, "params": {"coverage": 0.8}}],
            },
            {
                "id": "top_10_variants",
                "name": "Top 10 Variants",
                "description": "Keep only the 10 most common process variants",
                "filters": [{"type": FilterType.VARIANTS_TOP_K, "params": {"k": 10}}],
            },
            {
                "id": "remove_short_cases",
                "name": "Remove Short Cases",
                "description": "Remove cases with less than 3 events",
                "filters": [{"type": FilterType.CASE_SIZE, "params": {"min_size": 3}}],
            },
            {
                "id": "remove_outlier_duration",
                "name": "Remove Duration Outliers",
                "description": "Keep cases between 1 hour and 30 days",
                "filters": [
                    {
                        "type": FilterType.CASE_PERFORMANCE,
                        "params": {
                            "min_duration": 3600,
                            "max_duration": 2592000,
                        },
                    }
                ],
            },
            {
                "id": "completed_cases",
                "name": "Completed Cases Only",
                "description": "Filter to cases that reached an end activity",
                "filters": [],  # Requires dynamic end activities
            },
        ]

    # =========================================================================
    # Helpers
    # =========================================================================

    def to_pm4py_log(self, event_log: Dataset) -> PM4PyLog:
        """Convert ORM EventLog to PM4Py EventLog.

        DEPRECATED: This method triggers Object-Relational Impedance Mismatch.
        Use event_log_loader.load_as_pm4py_log(dataset_id) instead for 10x better performance.

        This method is kept only for backwards compatibility and will fail
        due to lazy="raise" on Dataset.cases relationship.
        """
        import warnings

        warnings.warn(
            "FilteringService.to_pm4py_log() is deprecated. "
            "Use event_log_loader.load_as_pm4py_log(dataset_id) instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Use fast path instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        return event_log_loader.load_as_pm4py_log(event_log.id)


