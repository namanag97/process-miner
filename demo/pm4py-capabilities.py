"""
PM4Py Comprehensive Capabilities Demo
======================================
This script demonstrates all major PM4Py features and outputs results to JSON.
Supports both CSV and XES event log files.

Usage: python pm4py_capabilities.py <input_file.csv|input_file.xes> [output.json]
"""

import json
import sys
import os
from datetime import datetime
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# PM4Py imports
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.algo.evaluation.replay_fitness import algorithm as fitness_evaluator
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
from pm4py.statistics.traces.generic.log import case_statistics
# Use pm4py high-level functions for start/end activities
# pm4py.get_start_activities(log) and pm4py.get_end_activities(log)
from pm4py.statistics.variants.log import get as get_variants
from pm4py.algo.organizational_mining.sna import algorithm as sna
from pm4py.algo.organizational_mining.roles import algorithm as roles_discovery
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter
from pm4py.convert import convert_to_bpmn, convert_to_process_tree
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.statistics.traces.generic.log import case_arrival
from pm4py.util import constants
import pandas as pd
import numpy as np


class PM4PyEncoder(json.JSONEncoder):
    """Custom JSON encoder for PM4Py objects and numpy types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, tuple):
            return list(obj)
        if hasattr(obj, '__dict__'):
            return str(obj)
        return str(obj)


def load_event_log(file_path):
    """Load event log from CSV or XES file."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.csv':
        df = pd.read_csv(file_path)
        # Auto-detect common column names
        col_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'case' in col_lower and 'id' in col_lower:
                col_mapping[col] = 'case:concept:name'
            elif col_lower in ['activity', 'event', 'action', 'activity_name']:
                col_mapping[col] = 'concept:name'
            elif 'time' in col_lower or 'date' in col_lower:
                col_mapping[col] = 'time:timestamp'
            elif 'resource' in col_lower or 'user' in col_lower:
                col_mapping[col] = 'org:resource'
        
        df = df.rename(columns=col_mapping)
        
        # Convert timestamp
        if 'time:timestamp' in df.columns:
            df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
        
        log = pm4py.convert_to_event_log(df)
        return log, df
    
    elif ext == '.xes':
        log = xes_importer.apply(file_path)
        df = pm4py.convert_to_dataframe(log)
        return log, df
    
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def safe_execute(func, *args, **kwargs):
    """Safely execute a function and return result or error message."""
    try:
        return {"status": "success", "result": func(*args, **kwargs)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def analyze_event_log(log, df):
    """Perform comprehensive analysis on the event log."""
    results = {
        "metadata": {
            "analysis_timestamp": datetime.now().isoformat(),
            "pm4py_version": pm4py.__version__,
            "total_cases": len(log),
            "total_events": len(df)
        },
        "analyses": {}
    }
    
    # =========================================================================
    # 1. EVENT DATA STATISTICS
    # =========================================================================
    print("📊 Analyzing Event Data Statistics...")
    
    # Basic statistics
    results["analyses"]["event_data_statistics"] = {
        "concept": "Event Log Statistics",
        "description": "Basic statistics about the event log",
        "data": {}
    }
    
    # Start activities
    start_acts = safe_execute(pm4py.get_start_activities, log)
    results["analyses"]["event_data_statistics"]["data"]["start_activities"] = start_acts
    
    # End activities
    end_acts = safe_execute(pm4py.get_end_activities, log)
    results["analyses"]["event_data_statistics"]["data"]["end_activities"] = end_acts
    
    # Variants
    variants = safe_execute(get_variants, log)
    if variants["status"] == "success":
        variant_list = [{"variant": str(k), "count": v} for k, v in 
                       sorted(variants["result"].items(), key=lambda x: -x[1])[:20]]
        results["analyses"]["event_data_statistics"]["data"]["top_20_variants"] = {
            "status": "success",
            "result": variant_list,
            "total_variants": len(variants["result"])
        }
    
    # Case duration statistics
    case_durations = safe_execute(case_statistics.get_all_case_durations, log)
    if case_durations["status"] == "success":
        durations = case_durations["result"]
        results["analyses"]["event_data_statistics"]["data"]["case_duration_stats"] = {
            "status": "success",
            "result": {
                "min_duration_seconds": min(durations) if durations else 0,
                "max_duration_seconds": max(durations) if durations else 0,
                "avg_duration_seconds": sum(durations)/len(durations) if durations else 0,
                "median_duration_seconds": sorted(durations)[len(durations)//2] if durations else 0
            }
        }
    
    # Activity frequencies
    activities = df['concept:name'].value_counts().to_dict() if 'concept:name' in df.columns else {}
    results["analyses"]["event_data_statistics"]["data"]["activity_frequencies"] = {
        "status": "success",
        "result": activities
    }
    
    # =========================================================================
    # 2. DIRECTLY-FOLLOWS GRAPH (DFG)
    # =========================================================================
    print("🔗 Discovering Directly-Follows Graph...")
    
    dfg_result = safe_execute(dfg_discovery.apply, log)
    if dfg_result["status"] == "success":
        dfg = dfg_result["result"]
        dfg_serializable = {f"{k[0]} -> {k[1]}": v for k, v in dfg.items()}
        results["analyses"]["directly_follows_graph"] = {
            "concept": "Directly-Follows Graph (DFG)",
            "description": "Shows frequency of activity sequences",
            "reference": "van der Aalst - A practitioner's guide to process mining",
            "data": {
                "dfg_edges": dfg_serializable,
                "num_edges": len(dfg),
                "start_activities": dict(pm4py.get_start_activities(log)),
                "end_activities": dict(pm4py.get_end_activities(log))
            }
        }
    
    # =========================================================================
    # 3. PROCESS DISCOVERY - ALPHA MINER
    # =========================================================================
    print("⚗️  Running Alpha Miner...")
    
    # Use high-level API which returns (net, im, fm) directly
    alpha_result = safe_execute(pm4py.discover_petri_net_alpha, log)
    if alpha_result["status"] == "success":
        net, im, fm = alpha_result["result"]
        results["analyses"]["alpha_miner"] = {
            "concept": "Alpha Miner",
            "description": "Discovers Petri net from event log",
            "reference": "van der Aalst et al. - Workflow Mining: Discovering Process Models from Event Logs",
            "data": {
                "places": [str(p) for p in net.places],
                "transitions": [str(t) for t in net.transitions],
                "arcs": [f"{a.source} -> {a.target}" for a in net.arcs],
                "initial_marking": str(im),
                "final_marking": str(fm)
            }
        }
        alpha_net, alpha_im, alpha_fm = net, im, fm
    else:
        alpha_net = None
        results["analyses"]["alpha_miner"] = {
            "concept": "Alpha Miner",
            "error": alpha_result["error"]
        }
    
    # =========================================================================
    # 4. PROCESS DISCOVERY - INDUCTIVE MINER
    # =========================================================================
    print("🔧 Running Inductive Miner...")
    
    # Use high-level API which returns (net, im, fm) directly
    inductive_result = safe_execute(pm4py.discover_petri_net_inductive, log)
    if inductive_result["status"] == "success":
        net, im, fm = inductive_result["result"]
        results["analyses"]["inductive_miner"] = {
            "concept": "Inductive Miner",
            "description": "Discovers block-structured process models",
            "reference": "Leemans et al. - Discovering block-structured process models from event logs",
            "data": {
                "places": [str(p) for p in net.places],
                "transitions": [str(t) for t in net.transitions],
                "arcs": [f"{a.source} -> {a.target}" for a in net.arcs],
                "initial_marking": str(im),
                "final_marking": str(fm)
            }
        }
        inductive_net, inductive_im, inductive_fm = net, im, fm
    else:
        inductive_net = None
        results["analyses"]["inductive_miner"] = {
            "concept": "Inductive Miner",
            "error": inductive_result["error"]
        }
    
    # =========================================================================
    # 5. PROCESS DISCOVERY - INDUCTIVE MINER INFREQUENT
    # =========================================================================
    print("🔧 Running Inductive Miner Infrequent...")
    
    # Use high-level API with noise_threshold for infrequent behavior filtering
    imf_result = safe_execute(pm4py.discover_petri_net_inductive, log, noise_threshold=0.2)
    if imf_result["status"] == "success":
        net, im, fm = imf_result["result"]
        results["analyses"]["inductive_miner_infrequent"] = {
            "concept": "Inductive Miner Infrequent (IMf)",
            "description": "Handles infrequent behavior in process discovery",
            "reference": "Leemans et al. - Discovering block-structured process models from event logs containing infrequent behaviour",
            "data": {
                "places": [str(p) for p in net.places],
                "transitions": [str(t) for t in net.transitions],
                "num_arcs": len(net.arcs)
            }
        }
    
    # =========================================================================
    # 6. PROCESS DISCOVERY - HEURISTICS MINER
    # =========================================================================
    print("🎯 Running Heuristics Miner...")
    
    # Use high-level API
    heuristics_result = safe_execute(pm4py.discover_heuristics_net, log)
    if heuristics_result["status"] == "success":
        heu_net = heuristics_result["result"]
        results["analyses"]["heuristics_miner"] = {
            "concept": "Heuristics Miner",
            "description": "Flexible heuristics-based process discovery",
            "reference": "Weijters et al. - Flexible heuristics miner (FHM)",
            "data": {
                "nodes": list(heu_net.nodes) if hasattr(heu_net, 'nodes') else [],
                "status": "Heuristics net discovered successfully"
            }
        }
    else:
        results["analyses"]["heuristics_miner"] = {
            "concept": "Heuristics Miner",
            "error": heuristics_result["error"]
        }
    
    # =========================================================================
    # 7. PROCESS TREE DISCOVERY
    # =========================================================================
    print("🌳 Discovering Process Tree...")
    
    try:
        process_tree = pm4py.discover_process_tree_inductive(log)
        results["analyses"]["process_tree"] = {
            "concept": "Process Tree",
            "description": "Hierarchical process model representation",
            "data": {
                "tree_string": str(process_tree),
                "operator": str(process_tree.operator) if process_tree.operator else "leaf",
                "label": process_tree.label if process_tree.label else None
            }
        }
    except Exception as e:
        results["analyses"]["process_tree"] = {
            "concept": "Process Tree",
            "error": str(e)
        }
    
    # =========================================================================
    # 8. BPMN CONVERSION
    # =========================================================================
    print("📋 Converting to BPMN...")
    
    try:
        if inductive_net:
            bpmn_model = convert_to_bpmn(inductive_net, inductive_im, inductive_fm)
            results["analyses"]["bpmn_model"] = {
                "concept": "Business Process Model and Notation (BPMN)",
                "description": "Standard business process modeling notation",
                "reference": "Object Management Group (OMG)",
                "data": {
                    "nodes": len(bpmn_model.get_nodes()) if hasattr(bpmn_model, 'get_nodes') else "N/A",
                    "flows": len(bpmn_model.get_flows()) if hasattr(bpmn_model, 'get_flows') else "N/A",
                    "status": "BPMN model created successfully"
                }
            }
    except Exception as e:
        results["analyses"]["bpmn_model"] = {
            "concept": "BPMN Model",
            "error": str(e)
        }
    
    # =========================================================================
    # 9. CONFORMANCE CHECKING - TOKEN REPLAY
    # =========================================================================
    print("🔄 Running Token-Based Replay...")
    
    if inductive_net:
        tbr_result = safe_execute(
            token_replay.apply, log, inductive_net, inductive_im, inductive_fm
        )
        if tbr_result["status"] == "success":
            replayed = tbr_result["result"]
            # Aggregate results
            total_produced = sum(r.get('produced_tokens', 0) for r in replayed)
            total_consumed = sum(r.get('consumed_tokens', 0) for r in replayed)
            total_missing = sum(r.get('missing_tokens', 0) for r in replayed)
            total_remaining = sum(r.get('remaining_tokens', 0) for r in replayed)
            
            results["analyses"]["token_based_replay"] = {
                "concept": "Token-Based Replay",
                "description": "Conformance checking using token replay",
                "reference": "Berti et al. - A novel token-based replay technique",
                "data": {
                    "total_traces": len(replayed),
                    "total_produced_tokens": total_produced,
                    "total_consumed_tokens": total_consumed,
                    "total_missing_tokens": total_missing,
                    "total_remaining_tokens": total_remaining,
                    "trace_fitness_available": True
                }
            }
    
    # =========================================================================
    # 10. CONFORMANCE CHECKING - ALIGNMENTS
    # =========================================================================
    print("📐 Computing Alignments...")
    
    if inductive_net:
        try:
            aligned = alignments.apply(log, inductive_net, inductive_im, inductive_fm)
            # Compute average fitness from alignments
            costs = [a['cost'] for a in aligned if 'cost' in a]
            results["analyses"]["alignments"] = {
                "concept": "Alignments",
                "description": "Optimal alignment between log and model",
                "reference": "Adriansyah et al. - Conformance checking using cost-based fitness analysis",
                "data": {
                    "total_traces_aligned": len(aligned),
                    "average_alignment_cost": sum(costs)/len(costs) if costs else 0,
                    "min_cost": min(costs) if costs else 0,
                    "max_cost": max(costs) if costs else 0
                }
            }
        except Exception as e:
            results["analyses"]["alignments"] = {
                "concept": "Alignments",
                "error": str(e)
            }
    
    # =========================================================================
    # 11. FITNESS EVALUATION
    # =========================================================================
    print("💪 Evaluating Fitness...")
    
    if inductive_net:
        fitness_result = safe_execute(
            fitness_evaluator.apply, log, inductive_net, inductive_im, inductive_fm,
            variant=fitness_evaluator.Variants.TOKEN_BASED
        )
        if fitness_result["status"] == "success":
            results["analyses"]["fitness_evaluation"] = {
                "concept": "Fitness Evaluation",
                "description": "Measures how well the model reproduces the log",
                "reference": "Token-based replay fitness",
                "data": fitness_result["result"]
            }
    
    # =========================================================================
    # 12. PRECISION EVALUATION
    # =========================================================================
    print("🎯 Evaluating Precision...")
    
    if inductive_net:
        precision_result = safe_execute(
            precision_evaluator.apply, log, inductive_net, inductive_im, inductive_fm,
            variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN
        )
        if precision_result["status"] == "success":
            results["analyses"]["precision_evaluation"] = {
                "concept": "Precision Evaluation",
                "description": "Measures model precision (avoids underfitting)",
                "reference": "Munoz-Gama et al. - A fresh look at precision in process conformance",
                "data": {"precision": precision_result["result"]}
            }
    
    # =========================================================================
    # 13. GENERALIZATION EVALUATION
    # =========================================================================
    print("🌐 Evaluating Generalization...")
    
    if inductive_net:
        gen_result = safe_execute(
            generalization_evaluator.apply, log, inductive_net, inductive_im, inductive_fm
        )
        if gen_result["status"] == "success":
            results["analyses"]["generalization_evaluation"] = {
                "concept": "Generalization Evaluation",
                "description": "Measures model generalization capability",
                "reference": "Buijs et al. - Quality dimensions in process discovery",
                "data": {"generalization": gen_result["result"]}
            }
    
    # =========================================================================
    # 14. SIMPLICITY EVALUATION
    # =========================================================================
    print("✨ Evaluating Simplicity...")
    
    if inductive_net:
        simp_result = safe_execute(
            simplicity_evaluator.apply, inductive_net
        )
        if simp_result["status"] == "success":
            results["analyses"]["simplicity_evaluation"] = {
                "concept": "Simplicity Evaluation",
                "description": "Measures structural simplicity of the model",
                "reference": "Vázquez-Barreiros et al. - ProDiGen",
                "data": {"simplicity": simp_result["result"]}
            }
    
    # =========================================================================
    # 15. SOCIAL NETWORK ANALYSIS
    # =========================================================================
    print("👥 Running Social Network Analysis...")
    
    if 'org:resource' in df.columns:
        # Handover of work
        try:
            hw_values = sna.apply(log, variant=sna.Variants.HANDOVER_LOG)
            results["analyses"]["social_network_handover"] = {
                "concept": "Social Network Analysis - Handover of Work",
                "description": "Analyzes resource handover patterns",
                "reference": "van der Aalst et al. - Discovering social networks from event logs",
                "data": {
                    "matrix_shape": hw_values.shape if hasattr(hw_values, 'shape') else "N/A",
                    "status": "Handover network computed"
                }
            }
        except Exception as e:
            results["analyses"]["social_network_handover"] = {
                "concept": "Social Network Analysis - Handover of Work",
                "error": str(e)
            }
        
        # Working together
        try:
            wt_values = sna.apply(log, variant=sna.Variants.WORKING_TOGETHER_LOG)
            results["analyses"]["social_network_working_together"] = {
                "concept": "Social Network Analysis - Working Together",
                "description": "Analyzes collaboration patterns",
                "reference": "van der Aalst et al. - Discovering social networks from event logs",
                "data": {
                    "status": "Working together network computed"
                }
            }
        except Exception as e:
            pass
    else:
        results["analyses"]["social_network_analysis"] = {
            "concept": "Social Network Analysis",
            "note": "No resource column found in event log"
        }
    
    # =========================================================================
    # 16. ORGANIZATIONAL ROLES DISCOVERY
    # =========================================================================
    print("🎭 Discovering Organizational Roles...")
    
    if 'org:resource' in df.columns:
        roles_result = safe_execute(roles_discovery.apply, log)
        if roles_result["status"] == "success":
            roles = roles_result["result"]
            roles_data = []
            for role in roles:
                # Handle both old tuple format and new Role object format
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
            results["analyses"]["organizational_roles"] = {
                "concept": "Organizational Roles",
                "description": "Discovers roles based on activity-resource patterns",
                "reference": "Burattin et al. - Business models enhancement through discovery of roles",
                "data": {
                    "roles": roles_data[:10],  # Top 10 roles
                    "total_roles": len(roles)
                }
            }
    
    # =========================================================================
    # 17. FOOTPRINTS
    # =========================================================================
    print("👣 Computing Footprints...")
    
    try:
        from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
        fp_log = footprints_discovery.apply(log)
        results["analyses"]["footprints"] = {
            "concept": "Footprints",
            "description": "Behavioral relations between activities",
            "reference": "van der Aalst - Process Mining: Data Science in Action",
            "data": {
                "sequence": [f"{k[0]} -> {k[1]}" for k in list(fp_log.get('sequence', set()))[:20]],
                "parallel": [f"{k[0]} || {k[1]}" for k in list(fp_log.get('parallel', set()))[:20]],
                "activities": list(fp_log.get('activities', set()))
            }
        }
    except Exception as e:
        results["analyses"]["footprints"] = {
            "concept": "Footprints",
            "error": str(e)
        }
    
    # =========================================================================
    # 18. TEMPORAL STATISTICS
    # =========================================================================
    print("⏱️  Computing Temporal Statistics...")
    
    if 'time:timestamp' in df.columns:
        try:
            # Case arrival rate
            arrival_stats = case_arrival.get_case_arrival_avg(log)
            results["analyses"]["temporal_statistics"] = {
                "concept": "Temporal Statistics",
                "description": "Time-based process statistics",
                "data": {
                    "average_case_arrival_seconds": arrival_stats,
                    "log_timespan": {
                        "start": df['time:timestamp'].min().isoformat() if pd.notna(df['time:timestamp'].min()) else None,
                        "end": df['time:timestamp'].max().isoformat() if pd.notna(df['time:timestamp'].max()) else None
                    }
                }
            }
        except Exception as e:
            results["analyses"]["temporal_statistics"] = {
                "concept": "Temporal Statistics",
                "error": str(e)
            }
    
    # =========================================================================
    # 19. FILTERING EXAMPLES
    # =========================================================================
    print("🔍 Demonstrating Filtering Capabilities...")
    
    # Filter by top variants
    try:
        filtered_log = variants_filter.filter_log_variants_percentage(log, percentage=0.8)
        results["analyses"]["filtering_variants"] = {
            "concept": "Variant Filtering",
            "description": "Filter log by top variants covering 80% of cases",
            "data": {
                "original_cases": len(log),
                "filtered_cases": len(filtered_log),
                "reduction_percentage": round((1 - len(filtered_log)/len(log)) * 100, 2)
            }
        }
    except Exception as e:
        pass
    
    # =========================================================================
    # 20. DECLARATIVE PROCESS MODELS / LOG SKELETON
    # =========================================================================
    print("📜 Computing Log Skeleton...")
    
    try:
        from pm4py.algo.discovery.log_skeleton import algorithm as log_skeleton_discovery
        skeleton = log_skeleton_discovery.apply(log)
        results["analyses"]["log_skeleton"] = {
            "concept": "Log Skeleton",
            "description": "Declarative process model constraints",
            "reference": "Verbeek - The log skeleton visualizer in ProM 6.9",
            "data": {
                "equivalence_relations": len(skeleton.get('equivalence', [])),
                "always_after": len(skeleton.get('always_after', [])),
                "always_before": len(skeleton.get('always_before', [])),
                "never_together": len(skeleton.get('never_together', []))
            }
        }
    except Exception as e:
        results["analyses"]["log_skeleton"] = {
            "concept": "Log Skeleton",
            "error": str(e)
        }
    
    # =========================================================================
    # 21. BATCH DETECTION
    # =========================================================================
    print("📦 Detecting Batches...")
    
    try:
        from pm4py.algo.discovery.batches import algorithm as batch_detection
        batches = batch_detection.apply(log)
        
        # Summarize batches instead of dumping raw data
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
        
        results["analyses"]["batch_detection"] = {
            "concept": "Batch Detection",
            "description": "Identifies batch processing patterns",
            "reference": "Martin et al. - Batch processing: Definition and event log identification",
            "data": {
                "total_batch_patterns": len(batches) if batches else 0,
                "batch_summary": batch_summary
            }
        }
    except Exception as e:
        results["analyses"]["batch_detection"] = {
            "concept": "Batch Detection",
            "error": str(e)
        }
    
    # =========================================================================
    # 22. TRANSITION SYSTEM
    # =========================================================================
    print("🔀 Building Transition System...")
    
    try:
        from pm4py.algo.discovery.transition_system import algorithm as ts_discovery
        ts = ts_discovery.apply(log)
        results["analyses"]["transition_system"] = {
            "concept": "Transition System",
            "description": "State-based process representation",
            "reference": "van der Aalst - Process Mining: Data Science in Action",
            "data": {
                "states": len(ts.states),
                "transitions": len(ts.transitions)
            }
        }
    except Exception as e:
        results["analyses"]["transition_system"] = {
            "concept": "Transition System",
            "error": str(e)
        }
    
    # =========================================================================
    # 23. PREFIX TREE
    # =========================================================================
    print("🌲 Building Prefix Tree...")
    
    try:
        from pm4py.algo.discovery.prefix_tree import algorithm as prefix_tree_discovery
        prefix_tree = prefix_tree_discovery.apply(log)
        results["analyses"]["prefix_tree"] = {
            "concept": "Prefix Tree (Trie)",
            "description": "Prefix-based trace representation",
            "data": {
                "status": "Prefix tree constructed successfully"
            }
        }
    except Exception as e:
        results["analyses"]["prefix_tree"] = {
            "concept": "Prefix Tree",
            "error": str(e)
        }
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*60)
    print("✅ Analysis Complete!")
    print("="*60)
    
    # Add summary
    successful = sum(1 for a in results["analyses"].values() 
                    if isinstance(a, dict) and a.get("data") is not None)
    failed = sum(1 for a in results["analyses"].values() 
                if isinstance(a, dict) and "error" in a)
    
    results["summary"] = {
        "total_analyses": len(results["analyses"]),
        "successful": successful,
        "failed": failed,
        "analyses_performed": list(results["analyses"].keys())
    }
    
    return results


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python pm4py_capabilities.py <input_file.csv|input_file.xes> [output.json]")
        print("\nExample:")
        print("  python pm4py_capabilities.py event_log.csv results.json")
        print("  python pm4py_capabilities.py event_log.xes")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "pm4py_analysis_results.json"
    
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' not found.")
        sys.exit(1)
    
    print("="*60)
    print("🔬 PM4Py Comprehensive Process Mining Analysis")
    print("="*60)
    print(f"📂 Input file: {input_file}")
    print(f"💾 Output file: {output_file}")
    print("="*60 + "\n")
    
    # Load event log
    print("📥 Loading event log...")
    log, df = load_event_log(input_file)
    print(f"   ✓ Loaded {len(log)} cases with {len(df)} events\n")
    
    # Run analysis
    results = analyze_event_log(log, df)
    
    # Save results
    print(f"\n💾 Saving results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=PM4PyEncoder)
    
    print(f"   ✓ Results saved successfully!")
    print(f"\n📊 Summary: {results['summary']['successful']} successful, "
          f"{results['summary']['failed']} failed out of "
          f"{results['summary']['total_analyses']} analyses")


if __name__ == "__main__":
    main()
