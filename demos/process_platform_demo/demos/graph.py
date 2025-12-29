"""
Process Graph Demo
Using NetworkX for process visualization and analysis
"""
import networkx as nx
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json


@dataclass
class ProcessMetrics:
    """Metrics for process graph analysis."""
    num_activities: int
    num_transitions: int
    start_activities: List[str]
    end_activities: List[str]
    most_frequent_path: List[str]
    bottleneck_activity: str
    avg_path_length: float
    variants_count: int
    loops_detected: List[Tuple[str, str]]


class ProcessGraph:
    """
    Build and analyze process graphs from event logs.
    
    Features:
    1. Directly-Follows Graph (DFG)
    2. Process metrics calculation
    3. Bottleneck detection
    4. Variant analysis
    5. Export to various formats
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.activity_counts = defaultdict(int)
        self.transition_counts = defaultdict(int)
        self.activity_durations = defaultdict(list)
        self.variants = defaultdict(int)
    
    def build_from_event_log(self, events: List[Dict]):
        """
        Build process graph from event log.
        
        Args:
            events: List of event dicts with case_id, activity, timestamp
        """
        # Group by case
        cases = defaultdict(list)
        for event in events:
            cases[event['case_id']].append(event)
        
        # Sort each case by timestamp
        for case_id in cases:
            cases[case_id].sort(key=lambda x: x['timestamp'])
        
        # Build graph
        for case_id, case_events in cases.items():
            # Track variant (path)
            path = tuple(e['activity'] for e in case_events)
            self.variants[path] += 1
            
            for i, event in enumerate(case_events):
                activity = event['activity']
                self.activity_counts[activity] += 1
                
                # Add node if not exists
                if not self.graph.has_node(activity):
                    self.graph.add_node(activity, count=0, avg_duration=0)
                
                self.graph.nodes[activity]['count'] = self.activity_counts[activity]
                
                # Calculate duration if next event exists in same case
                if i < len(case_events) - 1:
                    next_event = case_events[i + 1]
                    next_activity = next_event['activity']
                    
                    # Duration between this and next activity
                    if 'timestamp' in event and 'timestamp' in next_event:
                        duration = (next_event['timestamp'] - event['timestamp']).total_seconds() / 3600
                        self.activity_durations[activity].append(duration)
                    
                    # Add/update edge
                    self.transition_counts[(activity, next_activity)] += 1
                    
                    if self.graph.has_edge(activity, next_activity):
                        self.graph[activity][next_activity]['weight'] += 1
                    else:
                        self.graph.add_edge(activity, next_activity, weight=1)
        
        # Update average durations
        for activity, durations in self.activity_durations.items():
            if durations:
                self.graph.nodes[activity]['avg_duration'] = sum(durations) / len(durations)
    
    def get_start_activities(self) -> List[str]:
        """Get activities with no incoming edges."""
        return [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]
    
    def get_end_activities(self) -> List[str]:
        """Get activities with no outgoing edges."""
        return [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]
    
    def detect_bottleneck(self) -> str:
        """Find the bottleneck activity (highest average duration)."""
        if not self.activity_durations:
            return ""
        
        avg_durations = {
            act: sum(durs) / len(durs) 
            for act, durs in self.activity_durations.items()
            if durs
        }
        
        if avg_durations:
            return max(avg_durations, key=avg_durations.get)
        return ""
    
    def detect_loops(self) -> List[Tuple[str, str]]:
        """Detect loops in the process."""
        loops = []
        try:
            cycles = list(nx.simple_cycles(self.graph))
            for cycle in cycles:
                if len(cycle) >= 2:
                    loops.append((cycle[0], cycle[-1]))
        except:
            pass
        return loops[:5]  # Limit to 5 loops
    
    def get_most_frequent_variant(self) -> List[str]:
        """Get the most frequently occurring process path."""
        if not self.variants:
            return []
        
        most_common = max(self.variants.items(), key=lambda x: x[1])
        return list(most_common[0])
    
    def calculate_metrics(self) -> ProcessMetrics:
        """Calculate process metrics."""
        return ProcessMetrics(
            num_activities=self.graph.number_of_nodes(),
            num_transitions=self.graph.number_of_edges(),
            start_activities=self.get_start_activities(),
            end_activities=self.get_end_activities(),
            most_frequent_path=self.get_most_frequent_variant(),
            bottleneck_activity=self.detect_bottleneck(),
            avg_path_length=sum(len(v) for v in self.variants) / len(self.variants) if self.variants else 0,
            variants_count=len(self.variants),
            loops_detected=self.detect_loops()
        )
    
    def to_vis_format(self) -> Dict:
        """Export graph in visualization-friendly format."""
        nodes = []
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            nodes.append({
                'id': node,
                'label': node,
                'count': node_data.get('count', 0),
                'avg_duration': round(node_data.get('avg_duration', 0), 2),
                'is_start': self.graph.in_degree(node) == 0,
                'is_end': self.graph.out_degree(node) == 0
            })
        
        edges = []
        for source, target in self.graph.edges():
            edge_data = self.graph[source][target]
            edges.append({
                'source': source,
                'target': target,
                'weight': edge_data.get('weight', 1)
            })
        
        return {'nodes': nodes, 'edges': edges}
    
    def to_dot(self) -> str:
        """Export graph in DOT format for Graphviz."""
        lines = ['digraph ProcessModel {']
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box];')
        
        # Nodes
        for node in self.graph.nodes():
            count = self.graph.nodes[node].get('count', 0)
            lines.append(f'  "{node}" [label="{node}\\n({count})"];')
        
        # Edges
        for source, target in self.graph.edges():
            weight = self.graph[source][target].get('weight', 1)
            lines.append(f'  "{source}" -> "{target}" [label="{weight}"];')
        
        lines.append('}')
        return '\n'.join(lines)


def build_graph_from_dataframe(df) -> ProcessGraph:
    """Build process graph from pandas DataFrame."""
    events = df.to_dict('records')
    
    graph = ProcessGraph()
    graph.build_from_event_log(events)
    
    return graph


def run_demo(event_log_df) -> Dict:
    """Run the process graph demo."""
    
    graph = build_graph_from_dataframe(event_log_df)
    metrics = graph.calculate_metrics()
    vis_data = graph.to_vis_format()
    
    # Format activity statistics
    activity_stats = []
    for node in graph.graph.nodes():
        node_data = graph.graph.nodes[node]
        in_deg = graph.graph.in_degree(node)
        out_deg = graph.graph.out_degree(node)
        
        activity_stats.append({
            'activity': node,
            'frequency': node_data.get('count', 0),
            'avg_duration_hours': round(node_data.get('avg_duration', 0), 2),
            'incoming': in_deg,
            'outgoing': out_deg
        })
    
    # Sort by frequency
    activity_stats.sort(key=lambda x: x['frequency'], reverse=True)
    
    # Top transitions
    transitions = []
    for (src, tgt), count in sorted(graph.transition_counts.items(), key=lambda x: -x[1])[:10]:
        transitions.append({
            'from': src,
            'to': tgt,
            'frequency': count
        })
    
    # Top variants
    variants = []
    for path, count in sorted(graph.variants.items(), key=lambda x: -x[1])[:5]:
        variants.append({
            'path': ' → '.join(path),
            'frequency': count,
            'steps': len(path)
        })
    
    return {
        'metrics': {
            'total_activities': metrics.num_activities,
            'total_transitions': metrics.num_transitions,
            'unique_variants': metrics.variants_count,
            'avg_path_length': round(metrics.avg_path_length, 1),
            'start_activities': metrics.start_activities,
            'end_activities': metrics.end_activities,
            'bottleneck': metrics.bottleneck_activity,
            'loops_found': len(metrics.loops_detected)
        },
        'activity_statistics': activity_stats,
        'top_transitions': transitions,
        'top_variants': variants,
        'visualization_data': vis_data
    }
