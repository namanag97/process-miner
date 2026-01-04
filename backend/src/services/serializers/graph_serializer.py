"""Graph Structure Serializer.

Generates standardized JSON representations of process models for frontend visualization.
Supports DFG, Petri nets, and multi-level abstraction.
"""

from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from pm4py.objects.petri_net.obj import Marking, PetriNet

logger = structlog.get_logger(__name__)


class GraphStructureSerializer:
    """Generate standardized JSON for frontend consumption."""

    def serialize_dfg(
        self,
        dfg: dict[tuple[str, str], int],
        start_activities: dict[str, int],
        end_activities: dict[str, int],
        activities_count: dict[str, int] | None = None
    ) -> dict[str, Any]:
        """Convert DFG to visualization-ready JSON.

        Args:
            dfg: Directly-Follows Graph as dict of (source, target) -> frequency
            start_activities: Dict of activity -> count for start activities
            end_activities: Dict of activity -> count for end activities
            activities_count: Optional dict of activity -> total occurrences

        Returns:
            Visualization-ready JSON with nodes and edges
        """
        # Collect all unique activities
        all_activities = set()
        for (source, target) in dfg:
            all_activities.add(source)
            all_activities.add(target)
        all_activities.update(start_activities.keys())
        all_activities.update(end_activities.keys())

        # Build nodes
        nodes = []
        for activity in sorted(all_activities):
            node = {
                'id': activity,
                'label': activity,
                'frequency': activities_count.get(activity, 0) if activities_count else 0,
                'isStart': activity in start_activities,
                'isEnd': activity in end_activities
            }
            nodes.append(node)

        # Build edges
        edges = []
        total_frequency = sum(dfg.values())

        for (source, target), frequency in dfg.items():
            edge = {
                'id': f'edge-{source}-{target}',
                'source': source,
                'target': target,
                'frequency': frequency,
                'probability': frequency / total_frequency if total_frequency > 0 else 0
            }
            edges.append(edge)

        result = {
            'nodes': nodes,
            'edges': edges,
            'startActivities': start_activities,
            'endActivities': end_activities,
            'totalFrequency': total_frequency,
            'metadata': {
                'nodeCount': len(nodes),
                'edgeCount': len(edges),
                'type': 'dfg'
            }
        }

        logger.info(
            "dfg_serialization_success",
            nodes=len(nodes),
            edges=len(edges),
            total_freq=total_frequency
        )

        return result

    def serialize_petri_net(
        self,
        net: 'PetriNet',
        im: 'Marking',
        fm: 'Marking'
    ) -> dict[str, Any]:
        """Convert Petri net to visualization JSON.

        Args:
            net: PM4Py Petri net
            im: Initial marking
            fm: Final marking

        Returns:
            Visualization-ready JSON with places, transitions, and arcs
        """
        # Build places
        places = []
        for place in net.places:
            place_data = {
                'id': place.name or str(id(place)),
                'name': place.name or '',
                'tokens': im.get(place, 0) if im else 0,
                'isInitial': place in im if im else False,
                'isFinal': place in fm if fm else False
            }
            places.append(place_data)

        # Build transitions
        transitions = []
        for trans in net.transitions:
            trans_data = {
                'id': trans.name or str(id(trans)),
                'label': trans.label or trans.name or '',
                'isInvisible': trans.label is None
            }
            transitions.append(trans_data)

        # Build arcs
        arcs = []
        for arc_id, arc in enumerate(net.arcs):
            arc_data = {
                'id': f'arc-{arc_id}',
                'source': arc.source.name or str(id(arc.source)),
                'target': arc.target.name or str(id(arc.target)),
                'weight': arc.weight if hasattr(arc, 'weight') else 1
            }
            arcs.append(arc_data)

        result = {
            'places': places,
            'transitions': transitions,
            'arcs': arcs,
            'metadata': {
                'placeCount': len(places),
                'transitionCount': len(transitions),
                'arcCount': len(arcs),
                'type': 'petri_net',
                'netName': getattr(net, 'name', 'unnamed')
            }
        }

        logger.info(
            "petri_net_serialization_success",
            places=len(places),
            transitions=len(transitions),
            arcs=len(arcs)
        )

        return result

    def precompute_abstraction_levels(
        self,
        dfg: dict[tuple[str, str], int],
        start_activities: dict[str, int],
        end_activities: dict[str, int],
        levels: list[int] | None = None
    ) -> dict[int, dict[str, Any]]:
        """Pre-compute multiple abstraction levels for a DFG.

        Args:
            dfg: Base DFG
            start_activities: Start activities
            end_activities: End activities
            levels: Percentiles to compute (e.g., [100, 75, 50, 25])

        Returns:
            Dict mapping abstraction level -> serialized graph
        """
        import copy

        if levels is None:
            levels = [100, 75, 50, 25]

        results = {}

        # Sort edges by frequency
        sorted_edges = sorted(dfg.items(), key=lambda x: x[1], reverse=True)

        for level in levels:
            # Calculate how many edges to keep
            num_edges = max(1, int(len(sorted_edges) * level / 100))

            # Create filtered DFG
            filtered_dfg = dict(sorted_edges[:num_edges])

            # Serialize filtered DFG
            serialized = self.serialize_dfg(
                filtered_dfg,
                copy.deepcopy(start_activities),
                copy.deepcopy(end_activities)
            )

            results[level] = serialized

        logger.info(
            "abstraction_levels_computed",
            levels=levels,
            original_edges=len(dfg)
        )

        return results

    def add_layout_hints(
        self,
        graph_json: dict[str, Any],
        layout_algorithm: str = 'dagre'
    ) -> dict[str, Any]:
        """Add layout algorithm hints to graph JSON.

        Args:
            graph_json: Serialized graph JSON
            layout_algorithm: Layout algorithm name (dagre, force, hierarchical)

        Returns:
            Graph JSON with layout hints added
        """
        if 'metadata' not in graph_json:
            graph_json['metadata'] = {}

        graph_json['metadata']['layoutHint'] = layout_algorithm
        graph_json['metadata']['autoLayout'] = True

        return graph_json
