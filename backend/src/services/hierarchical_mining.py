"""Hierarchical Mining Service.

Implements recursive discovery with activity abstraction.
"""

from collections.abc import Iterator
from typing import Any

import structlog
from pm4py.objects.log.obj import EventLog

from src.services.mining import MiningService
from src.services.serializers.graph_serializer import GraphStructureSerializer

logger = structlog.get_logger(__name__)


class HierarchicalMiningService:
    """Recursive process discovery with abstraction levels."""

    def __init__(self):
        self.mining_service = MiningService()
        self.serializer = GraphStructureSerializer()

    def apply_activity_mapping(
        self,
        log: EventLog,
        mapping_rules: dict[str, str]
    ) -> EventLog:
        """Apply activity mapping to create abstracted log.

        Args:
            log: Original event log
            mapping_rules: Dict mapping low-level -> high-level activities

        Returns:
            New event log with mapped activities
        """
        from pm4py.objects.log.obj import Event, Trace

        mapped_log = EventLog()

        for trace in log:
            mapped_trace = Trace()
            # Copy trace attributes
            for key, value in trace.attributes.items():
                mapped_trace.attributes[key] = value

            for event in trace:
                mapped_event = Event()
                # Map activity name
                original_activity = event["concept:name"]
                mapped_activity = mapping_rules.get(original_activity, original_activity)

                # Copy event attributes
                for key, value in event.items():
                    if key == "concept:name":
                        mapped_event[key] = mapped_activity
                    else:
                        mapped_event[key] = value

                mapped_trace.append(mapped_event)

            mapped_log.append(mapped_trace)

        logger.info(
            "activity_mapping_applied",
            original_activities=len({e["concept:name"] for t in log for e in t}),
            mapped_activities=len({e["concept:name"] for t in mapped_log for e in t}),
            mapping_rules=len(mapping_rules)
        )

        return mapped_log

    def discover_hierarchical_models(
        self,
        log: EventLog,
        mapping_rules: dict[str, str],
        miner_type: str = "inductive"
    ) -> Iterator[tuple[int, dict[str, Any]]]:
        """Discover process models at multiple abstraction levels.

        Args:
            log: Base event log
            mapping_rules: Activity mappings for abstraction
            miner_type: Mining algorithm to use

        Yields:
            Tuples of (level, graph_json) for each abstraction level
        """
        # Level 0: Original model
        dfg, start_act, end_act, act_count = self.mining_service.discover_dfg(log)
        graph_json = self.serializer.serialize_dfg(dfg, start_act, end_act, act_count)

        yield 0, graph_json

        # Level 1+: Apply mappings recursively
        if mapping_rules:
            mapped_log = self.apply_activity_mapping(log, mapping_rules)
            dfg_mapped, start_mapped, end_mapped, act_count_mapped = self.mining_service.discover_dfg(mapped_log)
            graph_json_mapped = self.serializer.serialize_dfg(dfg_mapped, start_mapped, end_mapped, act_count_mapped)

            yield 1, graph_json_mapped

        logger.info("hierarchical_models_discovered", levels=2 if mapping_rules else 1)

    def suggest_activity_groupings(
        self,
        log: EventLog,
        num_groups: int = 5
    ) -> dict[str, str]:
        """Auto-suggest activity mappings using clustering.

        Args:
            log: Event log
            num_groups: Target number of high-level activities

        Returns:
            Suggested mapping rules
        """
        from collections import Counter

        # Get activity frequencies
        activities = [event["concept:name"] for trace in log for event in trace]
        activity_counts = Counter(activities)

        # Simple frequency-based grouping
        # Group low-frequency activities into "Other"
        sorted_activities = sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)

        mapping = {}
        if len(sorted_activities) > num_groups:
            # Keep top N activities, group rest as "Other"
            top_activities = {act for act, _ in sorted_activities[:num_groups - 1]}

            for activity, _ in sorted_activities:
                if activity in top_activities:
                    mapping[activity] = activity  # Keep as-is
                else:
                    mapping[activity] = "Other"

        logger.info(
            "activity_groupings_suggested",
            original_count=len(activity_counts),
            target_groups=num_groups,
            suggestions=len(mapping)
        )

        return mapping

    def calculate_drill_down_metadata(
        self,
        graph_json: dict[str, Any],
        mapping_rules: dict[str, str]
    ) -> dict[str, Any]:
        """Add drill-down metadata to graph nodes.

        Args:
            graph_json: High-level graph
            mapping_rules: Activity mappings

        Returns:
            Graph JSON with drill-down hints
        """
        # Invert mapping to get high-level -> [low-level activities]
        drill_down_map: dict[str, list[str]] = {}
        for low_level, high_level in mapping_rules.items():
            if high_level not in drill_down_map:
                drill_down_map[high_level] = []
            drill_down_map[high_level].append(low_level)

        # Add to nodes
        for node in graph_json.get("nodes", []):
            node_id = node["id"]
            if node_id in drill_down_map:
                node["drillDownActivities"] = drill_down_map[node_id]
                node["isDrillable"] = True
            else:
                node["isDrillable"] = False

        return graph_json
