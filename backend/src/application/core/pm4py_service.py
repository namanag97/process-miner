"""PM4Py Service - Comprehensive Process Mining Integration.

This service provides a centralized interface to PM4Py capabilities including:
- Social Network Analysis (SNA)
- Organizational roles discovery
- Footprints analysis
- Log skeleton (declarative constraints)
- Batch detection
- Transition systems
- Model quality evaluation
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.organizational_mining.sna import algorithm as sna
from pm4py.algo.organizational_mining.roles import algorithm as roles_discovery
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
from pm4py.statistics.traces.generic.log import case_statistics, case_arrival
from pm4py.statistics.variants.log import get as get_variants

from src.domain.entities import EventLog
from src.application.core.discovery_service import discovery_service


@dataclass
class SNAResult:
    """Social Network Analysis result."""
    matrix_shape: Tuple[int, int]
    resources: List[str]
    network_type: str


class PM4PyService:
    """
    Comprehensive PM4Py Service.
    Provides access to advanced PM4Py process mining capabilities.
    """
    
    def get_start_activities(self, event_log: EventLog) -> Dict[str, int]:
        """Get start activities with their frequencies."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        return dict(pm4py.get_start_activities(pm4py_log))
    
    def get_end_activities(self, event_log: EventLog) -> Dict[str, int]:
        """Get end activities with their frequencies."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        return dict(pm4py.get_end_activities(pm4py_log))
    
    def get_variants(self, event_log: EventLog, top_n: int = 20) -> Dict[str, Any]:
        """Get process variants with counts."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        variants = get_variants(pm4py_log)
        
        variant_list = [
            {"variant": str(k), "count": v}
            for k, v in sorted(variants.items(), key=lambda x: -x[1])[:top_n]
        ]
        
        return {
            "top_variants": variant_list,
            "total_variants": len(variants),
        }
    
    def discover_dfg(self, event_log: EventLog) -> Dict[str, Any]:
        """Discover Directly-Follows Graph."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        dfg, start_activities, end_activities = pm4py.discover_dfg(pm4py_log)
        
        # Convert to serializable format
        edges = [
            {"source": edge[0], "target": edge[1], "frequency": freq}
            for edge, freq in dfg.items()
        ]
        
        return {
            "edges": edges,
            "num_edges": len(dfg),
            "start_activities": dict(start_activities),
            "end_activities": dict(end_activities),
        }
    
    def discover_footprints(self, event_log: EventLog) -> Dict[str, Any]:
        """Compute footprints (behavioral relations between activities)."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        try:
            from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
            fp_log = footprints_discovery.apply(pm4py_log)
            
            return {
                "sequence": [f"{k[0]} -> {k[1]}" for k in list(fp_log.get('sequence', set()))[:50]],
                "parallel": [f"{k[0]} || {k[1]}" for k in list(fp_log.get('parallel', set()))[:50]],
                "activities": list(fp_log.get('activities', set())),
                "start_activities": list(fp_log.get('start_activities', set())),
                "end_activities": list(fp_log.get('end_activities', set())),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def discover_log_skeleton(self, event_log: EventLog) -> Dict[str, Any]:
        """Discover log skeleton (declarative process model constraints)."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        try:
            from pm4py.algo.discovery.log_skeleton import algorithm as log_skeleton_discovery
            skeleton = log_skeleton_discovery.apply(pm4py_log)
            
            return {
                "equivalence_count": len(skeleton.get('equivalence', [])),
                "always_after_count": len(skeleton.get('always_after', [])),
                "always_before_count": len(skeleton.get('always_before', [])),
                "never_together_count": len(skeleton.get('never_together', [])),
                "equivalence": list(skeleton.get('equivalence', []))[:20],
                "always_after": [f"{k[0]} after {k[1]}" for k in list(skeleton.get('always_after', []))[:20]],
                "always_before": [f"{k[0]} before {k[1]}" for k in list(skeleton.get('always_before', []))[:20]],
                "never_together": [f"{k[0]} never with {k[1]}" for k in list(skeleton.get('never_together', []))[:20]],
            }
        except Exception as e:
            return {"error": str(e)}
    
    def discover_organizational_roles(self, event_log: EventLog) -> Dict[str, Any]:
        """Discover organizational roles based on activity-resource patterns."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        # Check if resource column exists
        has_resources = any(
            'org:resource' in event 
            for trace in pm4py_log 
            for event in trace
        )
        
        if not has_resources:
            return {"note": "No resource column found in event log", "roles": []}
        
        try:
            roles = roles_discovery.apply(pm4py_log)
            roles_data = []
            
            for role in roles:
                try:
                    if hasattr(role, 'resources') and hasattr(role, 'activities'):
                        # New Role namedtuple format
                        roles_data.append({
                            "resources": list(role.resources) if isinstance(role.resources, (set, list)) else [role.resources],
                            "activities": list(role.activities) if isinstance(role.activities, (set, list)) else [role.activities]
                        })
                    else:
                        # Old tuple format
                        roles_data.append({
                            "resources": list(role[0]) if isinstance(role[0], (set, list)) else [role[0]],
                            "activities": list(role[1]) if isinstance(role[1], (set, list)) else [role[1]]
                        })
                except Exception:
                    roles_data.append({"role": str(role)})
            
            return {
                "roles": roles_data[:20],  # Limit to top 20 roles
                "total_roles": len(roles),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_sna_handover(self, event_log: EventLog) -> Dict[str, Any]:
        """Calculate Social Network Analysis - Handover of Work."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        # Check if resource column exists
        has_resources = any(
            'org:resource' in event 
            for trace in pm4py_log 
            for event in trace
        )
        
        if not has_resources:
            return {"note": "No resource column found in event log"}
        
        try:
            hw_values = sna.apply(pm4py_log, variant=sna.Variants.HANDOVER_LOG)
            
            return {
                "network_type": "handover_of_work",
                "matrix_shape": list(hw_values.shape) if hasattr(hw_values, 'shape') else "N/A",
                "status": "Handover network computed successfully",
            }
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_sna_working_together(self, event_log: EventLog) -> Dict[str, Any]:
        """Calculate Social Network Analysis - Working Together."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        # Check if resource column exists
        has_resources = any(
            'org:resource' in event 
            for trace in pm4py_log 
            for event in trace
        )
        
        if not has_resources:
            return {"note": "No resource column found in event log"}
        
        try:
            wt_values = sna.apply(pm4py_log, variant=sna.Variants.WORKING_TOGETHER_LOG)
            
            return {
                "network_type": "working_together",
                "matrix_shape": list(wt_values.shape) if hasattr(wt_values, 'shape') else "N/A",
                "status": "Working together network computed successfully",
            }
        except Exception as e:
            return {"error": str(e)}
    
    def detect_batches(self, event_log: EventLog) -> Dict[str, Any]:
        """Detect batch processing patterns."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        try:
            from pm4py.algo.discovery.batches import algorithm as batch_detection
            batches = batch_detection.apply(pm4py_log)
            
            batch_summary = []
            if batches:
                for batch in batches[:10]:  # Limit to first 10 batch types
                    try:
                        activity_resource = batch[0] if len(batch) > 0 else None
                        batch_type_count = batch[1] if len(batch) > 1 else 0
                        batch_types = batch[2] if len(batch) > 2 else {}
                        
                        # Count events per batch type
                        type_counts = {}
                        for batch_type, instances in batch_types.items():
                            type_counts[batch_type] = len(instances) if isinstance(instances, list) else 1
                        
                        batch_summary.append({
                            "activity": activity_resource[0] if isinstance(activity_resource, (list, tuple)) else str(activity_resource),
                            "resource": activity_resource[1] if isinstance(activity_resource, (list, tuple)) and len(activity_resource) > 1 else "N/A",
                            "batch_type_count": batch_type_count,
                            "batch_types": type_counts
                        })
                    except Exception:
                        batch_summary.append({"raw": str(batch)[:200]})
            
            return {
                "total_batch_patterns": len(batches) if batches else 0,
                "batch_summary": batch_summary,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def build_transition_system(self, event_log: EventLog) -> Dict[str, Any]:
        """Build transition system from event log."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        try:
            from pm4py.algo.discovery.transition_system import algorithm as ts_discovery
            ts = ts_discovery.apply(pm4py_log)
            
            return {
                "states_count": len(ts.states),
                "transitions_count": len(ts.transitions),
                "status": "Transition system built successfully",
            }
        except Exception as e:
            return {"error": str(e)}
    
    def discover_process_tree(self, event_log: EventLog) -> Dict[str, Any]:
        """Discover process tree using inductive miner."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        try:
            process_tree = pm4py.discover_process_tree_inductive(pm4py_log)
            
            return {
                "tree_string": str(process_tree),
                "operator": str(process_tree.operator) if process_tree.operator else "leaf",
                "label": process_tree.label if process_tree.label else None,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_case_duration_statistics(self, event_log: EventLog) -> Dict[str, Any]:
        """Get case duration statistics."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        try:
            durations = case_statistics.get_all_case_durations(pm4py_log)
            
            if not durations:
                return {"note": "No case durations available"}
            
            return {
                "min_duration_seconds": min(durations),
                "max_duration_seconds": max(durations),
                "avg_duration_seconds": sum(durations) / len(durations),
                "median_duration_seconds": sorted(durations)[len(durations) // 2],
                "total_cases": len(durations),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_case_arrival_rate(self, event_log: EventLog) -> Dict[str, Any]:
        """Get average case arrival rate."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        try:
            arrival_avg = case_arrival.get_case_arrival_avg(pm4py_log)
            
            return {
                "average_arrival_seconds": arrival_avg,
                "average_arrival_minutes": arrival_avg / 60 if arrival_avg else 0,
                "average_arrival_hours": arrival_avg / 3600 if arrival_avg else 0,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def evaluate_generalization(
        self,
        event_log: EventLog,
        net: PetriNet,
        im: Marking,
        fm: Marking,
    ) -> float:
        """Evaluate model generalization."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        
        try:
            gen = generalization_evaluator.apply(pm4py_log, net, im, fm)
            return gen
        except Exception:
            return 0.0
    
    def evaluate_simplicity(self, net: PetriNet) -> float:
        """Evaluate model simplicity."""
        try:
            simp = simplicity_evaluator.apply(net)
            return simp
        except Exception:
            return 0.0
    
    def get_comprehensive_analysis(self, event_log: EventLog) -> Dict[str, Any]:
        """Run comprehensive PM4Py analysis (similar to demo file)."""
        results = {
            "metadata": {
                "total_cases": event_log.total_cases,
                "total_events": event_log.total_events,
            },
            "analyses": {}
        }
        
        # Start/End activities
        results["analyses"]["start_activities"] = self.get_start_activities(event_log)
        results["analyses"]["end_activities"] = self.get_end_activities(event_log)
        
        # Variants
        results["analyses"]["variants"] = self.get_variants(event_log)
        
        # DFG
        results["analyses"]["dfg"] = self.discover_dfg(event_log)
        
        # Footprints
        results["analyses"]["footprints"] = self.discover_footprints(event_log)
        
        # Log skeleton
        results["analyses"]["log_skeleton"] = self.discover_log_skeleton(event_log)
        
        # Organizational roles
        results["analyses"]["organizational_roles"] = self.discover_organizational_roles(event_log)
        
        # SNA
        results["analyses"]["sna_handover"] = self.calculate_sna_handover(event_log)
        results["analyses"]["sna_working_together"] = self.calculate_sna_working_together(event_log)
        
        # Batches
        results["analyses"]["batches"] = self.detect_batches(event_log)
        
        # Transition system
        results["analyses"]["transition_system"] = self.build_transition_system(event_log)
        
        # Process tree
        results["analyses"]["process_tree"] = self.discover_process_tree(event_log)
        
        # Case duration stats
        results["analyses"]["case_duration_statistics"] = self.get_case_duration_statistics(event_log)
        
        # Case arrival rate
        results["analyses"]["case_arrival_rate"] = self.get_case_arrival_rate(event_log)
        
        # Summary
        successful = sum(1 for a in results["analyses"].values() 
                        if isinstance(a, dict) and "error" not in a)
        failed = sum(1 for a in results["analyses"].values() 
                    if isinstance(a, dict) and "error" in a)
        
        results["summary"] = {
            "total_analyses": len(results["analyses"]),
            "successful": successful,
            "failed": failed,
        }
        
        return results


# Singleton instance
pm4py_service = PM4PyService()
