"""
PM4Py Service - Core process mining operations.

This is the heart of the backend. It wraps PM4Py functions and transforms
output into React Flow compatible format for the frontend.
"""

from typing import Any
from collections import defaultdict

import pandas as pd
import pm4py
from pm4py.objects.log.obj import EventLog

from ..models import (
    DFGNode,
    DFGEdge,
    DFGResponse,
    DFGSummary,
    ActivityNodeData,
    NodePosition,
    EdgeData,
    VariantItem,
    VariantsResponse,
    ActivityStat,
    ProcessStats,
    Deviation,
)
from ..core import get_logger

_log = get_logger(__name__)


class PM4PyService:
    """
    Wrapper around PM4Py for process mining operations.
    
    All process mining logic is delegated to PM4Py. This class handles:
    - Converting DataFrames to EventLogs
    - Calling PM4Py algorithms
    - Transforming outputs to React Flow format
    """
    
    def create_event_log(
        self,
        df: pd.DataFrame,
        case_id_col: str,
        activity_col: str,
        timestamp_col: str,
        resource_col: str | None = None,
        timestamp_format: str | None = None,
    ) -> EventLog:
        """
        Convert a pandas DataFrame to a PM4Py EventLog.
        
        Args:
            df: Source DataFrame
            case_id_col: Column name for case ID
            activity_col: Column name for activity
            timestamp_col: Column name for timestamp
            resource_col: Optional column name for resource
            timestamp_format: Optional datetime format string
            
        Returns:
            PM4Py EventLog object
        """
        __log.info(f"Creating event log from {len(df)} rows")
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Parse timestamps
        if timestamp_format and timestamp_format != "ISO8601":
            df[timestamp_col] = pd.to_datetime(
                df[timestamp_col], 
                format=timestamp_format,
                errors="coerce"
            )
        else:
            df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors="coerce")
        
        # Drop rows with null timestamps
        null_ts = df[timestamp_col].isna().sum()
        if null_ts > 0:
            _log.warning(f"Dropping {null_ts} rows with null timestamps")
            df = df.dropna(subset=[timestamp_col])
        
        # Format for PM4Py
        df = pm4py.format_dataframe(
            df,
            case_id=case_id_col,
            activity_key=activity_col,
            timestamp_key=timestamp_col,
        )
        
        # Add resource if provided
        if resource_col and resource_col in df.columns:
            df["org:resource"] = df[resource_col]
        
        # Convert to event log
        log = pm4py.convert_to_event_log(df)
        
        __log.info(f"Created event log with {len(log)} cases")
        return log
    
    def discover_dfg(self, log: EventLog) -> dict[str, Any]:
        """
        Discover Directly-Follows Graph using PM4Py.
        
        Args:
            log: PM4Py EventLog
            
        Returns:
            Dict with DFG data for transformation
        """
        __log.info("Discovering DFG...")
        
        # Basic DFG
        dfg, start_activities, end_activities = pm4py.discover_dfg(log)
        
        # Performance DFG (for durations)
        try:
            perf_dfg, _, _ = pm4py.discover_performance_dfg(log)
        except Exception as e:
            _log.warning(f"Could not get performance DFG: {e}")
            perf_dfg = {}
        
        __log.info(f"DFG discovered: {len(dfg)} edges")
        
        return {
            "dfg": dfg,
            "start_activities": start_activities,
            "end_activities": end_activities,
            "performance_dfg": perf_dfg,
        }
    
    def get_variants(self, log: EventLog, top_k: int = 100) -> list[dict]:
        """
        Extract process variants from event log.
        
        Args:
            log: PM4Py EventLog
            top_k: Maximum number of variants to return
            
        Returns:
            List of variant dictionaries
        """
        __log.info("Extracting variants...")
        
        # Get variants with counts
        variants = pm4py.get_variants(log)
        
        # Sort by frequency
        sorted_variants = sorted(
            variants.items(),
            key=lambda x: len(x[1]) if isinstance(x[1], list) else x[1],
            reverse=True
        )[:top_k]
        
        # Calculate total for percentages
        total_cases = len(log)
        
        # Get case durations for each variant
        case_durations = pm4py.get_all_case_durations(log)
        case_duration_map = dict(zip(
            [trace.attributes.get("concept:name", str(i)) for i, trace in enumerate(log)],
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
            
            result.append({
                "id": f"variant_{i+1}",
                "sequence": sequence,
                "case_count": case_count,
                "percentage": (case_count / total_cases) * 100 if total_cases > 0 else 0,
                "avg_duration_ms": avg_duration * 1000,  # Convert to ms
                "case_ids": case_ids[:100],  # Limit case IDs
            })
        
        __log.info(f"Found {len(result)} variants")
        return result
    
    def get_statistics(self, log: EventLog) -> dict[str, Any]:
        """
        Calculate overall process statistics.
        
        Args:
            log: PM4Py EventLog
            
        Returns:
            Dictionary of statistics
        """
        _log.info("Calculating statistics...")
        
        # Basic counts
        total_cases = len(log)
        total_events = sum(len(trace) for trace in log)
        
        # Activities
        activities = pm4py.get_event_attribute_values(log, "concept:name")
        total_activities = len(activities)
        
        # Variants
        variants = pm4py.get_variants(log)
        total_variants = len(variants)
        
        # Case durations
        case_durations = pm4py.get_all_case_durations(log)
        avg_duration = sum(case_durations) / len(case_durations) if case_durations else 0
        
        # Median duration
        sorted_durations = sorted(case_durations)
        median_duration = (
            sorted_durations[len(sorted_durations) // 2]
            if sorted_durations else 0
        )
        
        # Start/end activities
        start_activities = list(pm4py.get_start_activities(log).keys())
        end_activities = list(pm4py.get_end_activities(log).keys())
        
        return {
            "total_cases": total_cases,
            "total_events": total_events,
            "total_activities": total_activities,
            "total_variants": total_variants,
            "avg_case_duration_ms": avg_duration * 1000,
            "median_case_duration_ms": median_duration * 1000,
            "start_activities": start_activities,
            "end_activities": end_activities,
        }
    
    def get_activity_stats(self, log: EventLog) -> list[dict]:
        """
        Get per-activity statistics.
        
        Args:
            log: PM4Py EventLog
            
        Returns:
            List of activity statistics
        """
        activities = pm4py.get_event_attribute_values(log, "concept:name")
        start_activities = set(pm4py.get_start_activities(log).keys())
        end_activities = set(pm4py.get_end_activities(log).keys())
        
        total_events = sum(activities.values())
        
        return [
            {
                "name": name,
                "frequency": freq,
                "frequency_pct": (freq / total_events * 100) if total_events > 0 else 0,
                "is_start": name in start_activities,
                "is_end": name in end_activities,
                "avg_duration_ms": 0,  # Would need performance analysis
            }
            for name, freq in sorted(activities.items(), key=lambda x: -x[1])
        ]
    
    def detect_deviations(self, log: EventLog, variants: list[dict]) -> list[Deviation]:
        """
        Detect process deviations like rework and skips.
        
        Args:
            log: PM4Py EventLog
            variants: List of variant data
            
        Returns:
            List of detected deviations
        """
        deviations = []
        
        # Detect rework (same activity appears multiple times in a trace)
        rework_cases: dict[str, list[str]] = defaultdict(list)
        
        for trace in log:
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
                    affected_cases=cases[:100],
                    frequency=len(cases),
                ))
        
        # Detect unusual paths (variants with low frequency)
        for variant in variants:
            if variant["percentage"] < 1.0 and variant["case_count"] >= 3:
                deviations.append(Deviation(
                    type="unusual_path",
                    description=f"Unusual process path: {' → '.join(variant['sequence'][:5])}...",
                    affected_cases=variant["case_ids"][:100],
                    frequency=variant["case_count"],
                ))
        
        return deviations[:20]  # Limit to top 20 deviations
    
    def transform_dfg_for_react_flow(
        self,
        dfg_data: dict[str, Any],
        stats: dict[str, Any],
    ) -> DFGResponse:
        """
        Transform PM4Py DFG output to React Flow format.
        
        This is the key transformation that makes the backend output
        directly usable by the frontend's React Flow component.
        
        Args:
            dfg_data: Output from discover_dfg()
            stats: Output from get_statistics()
            
        Returns:
            DFGResponse ready for frontend
        """
        dfg = dfg_data["dfg"]
        start_activities = dfg_data["start_activities"]
        end_activities = dfg_data["end_activities"]
        performance_dfg = dfg_data.get("performance_dfg", {})
        
        # Collect all activity names
        activities: set[str] = set()
        for (source, target) in dfg.keys():
            activities.add(source)
            activities.add(target)
        for act in start_activities:
            activities.add(act)
        for act in end_activities:
            activities.add(act)
        
        # Calculate activity frequencies
        activity_freq: dict[str, int] = defaultdict(int)
        for (source, target), freq in dfg.items():
            activity_freq[source] += freq
            activity_freq[target] += freq
        
        max_frequency = max(activity_freq.values()) if activity_freq else 1
        
        # Simple layout: arrange activities in layers
        # Start activities on left, end on right, others in middle
        start_set = set(start_activities.keys())
        end_set = set(end_activities.keys())
        middle = activities - start_set - end_set
        
        # Position calculation
        x_spacing = 250
        y_spacing = 100
        
        positions: dict[str, tuple[float, float]] = {}
        
        # Position start activities
        start_list = sorted(start_set)
        for i, act in enumerate(start_list):
            positions[act] = (0, i * y_spacing)
        
        # Position middle activities
        middle_list = sorted(middle)
        for i, act in enumerate(middle_list):
            positions[act] = (x_spacing, i * y_spacing)
        
        # Position end activities
        end_list = sorted(end_set)
        for i, act in enumerate(end_list):
            positions[act] = (x_spacing * 2, i * y_spacing)
        
        # Create nodes
        nodes: list[DFGNode] = []
        for act in activities:
            x, y = positions.get(act, (x_spacing, 0))
            freq = activity_freq.get(act, 0)
            
            nodes.append(DFGNode(
                id=self._to_node_id(act),
                type="activityNode",
                position=NodePosition(x=x, y=y),
                data=ActivityNodeData(
                    label=act,
                    frequency=freq,
                    isStart=act in start_set,
                    isEnd=act in end_set,
                    avgDuration=0,  # Would need event-level timing
                    maxFrequency=max_frequency,
                ),
            ))
        
        # Create edges
        edges: list[DFGEdge] = []
        for (source, target), freq in dfg.items():
            # Get duration from performance DFG
            duration = 0
            perf_key = (source, target)
            if perf_key in performance_dfg:
                perf_data = performance_dfg[perf_key]
                # Performance DFG returns dict with 'mean' key
                if isinstance(perf_data, dict):
                    duration = perf_data.get("mean", 0) * 1000  # Convert to ms
                else:
                    duration = float(perf_data) * 1000
            
            edges.append(DFGEdge(
                id=f"e-{self._to_node_id(source)}-{self._to_node_id(target)}",
                source=self._to_node_id(source),
                target=self._to_node_id(target),
                type="processEdge",
                data=EdgeData(
                    frequency=freq,
                    avgDuration=duration,
                ),
            ))
        
        return DFGResponse(
            nodes=nodes,
            edges=edges,
            summary=DFGSummary(
                totalCases=stats["total_cases"],
                totalEvents=stats["total_events"],
                totalActivities=stats["total_activities"],
                totalVariants=stats["total_variants"],
            ),
        )
    
    def transform_variants(self, variants_data: list[dict]) -> VariantsResponse:
        """
        Transform variant data to response format.
        
        Args:
            variants_data: Output from get_variants()
            
        Returns:
            VariantsResponse
        """
        items = []
        happy_path_set = False
        
        for v in variants_data:
            is_happy = not happy_path_set and v["case_count"] > 0
            if is_happy:
                happy_path_set = True
            
            items.append(VariantItem(
                id=v["id"],
                sequence=v["sequence"],
                trace_display=" → ".join(v["sequence"]),
                case_count=v["case_count"],
                percentage=round(v["percentage"], 2),
                avg_duration_ms=v["avg_duration_ms"],
                is_happy_path=is_happy,
                case_ids=v["case_ids"],
            ))
        
        return VariantsResponse(
            total=len(items),
            variants=items,
        )
    
    def _to_node_id(self, activity_name: str) -> str:
        """Convert activity name to a valid React Flow node ID."""
        # Replace spaces and special chars with underscores
        return activity_name.lower().replace(" ", "_").replace("-", "_")


# Singleton instance
pm4py_service = PM4PyService()
