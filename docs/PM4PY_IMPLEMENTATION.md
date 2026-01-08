# PM4PY IMPLEMENTATION GUIDE

## Complete Algorithm Reference for Backend

This document provides exact PM4Py code for implementing all discovery algorithms, conformance checking, and analytics in the backend.

---

## 1. DISCOVERY ALGORITHMS

### 1.1 DFG Discovery (Fastest - Use for Initial View)

```python
# src/domain/process_mining/discovery/dfg.py
import pm4py
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.statistics.attributes.log.get import get_attribute_values

def discover_dfg(log):
    """
    Discover Directly-Follows Graph - fastest algorithm.
    Use for: Quick visualization, large logs, initial exploration.
    """
    # Discover DFG
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    
    # Get activity frequencies
    activity_freq = get_attribute_values(log, "concept:name")
    
    # Build response structure for frontend
    nodes = []
    for activity, freq in activity_freq.items():
        nodes.append({
            "id": activity,
            "label": activity,
            "frequency": freq,
            "type": "start" if activity in start_activities else 
                    "end" if activity in end_activities else "activity"
        })
    
    edges = []
    for (source, target), count in dfg.items():
        edges.append({
            "source": source,
            "target": target,
            "value": count,
            "label": str(count)
        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "start_activities": dict(start_activities),
        "end_activities": dict(end_activities),
        "algorithm": "dfg",
        "model_type": "dfg"
    }
```

### 1.2 Alpha Miner (Educational/Simple Logs)

```python
# src/domain/process_mining/discovery/alpha.py
import pm4py
from pm4py.algo.discovery.alpha import algorithm as alpha_miner

def discover_alpha(log):
    """
    Alpha Miner - classic algorithm for clean logs.
    Use for: Simple processes, no noise, educational.
    Limitations: No noise handling, no loops of length 1-2.
    """
    net, initial_marking, final_marking = alpha_miner.apply(log)
    
    return net, initial_marking, final_marking

def discover_alpha_plus(log):
    """
    Alpha+ - handles loops of length 1-2.
    """
    net, im, fm = alpha_miner.apply(
        log,
        variant=alpha_miner.Variants.ALPHA_PLUS
    )
    return net, im, fm
```

### 1.3 Heuristics Miner (Best for Noisy Logs)

```python
# src/domain/process_mining/discovery/heuristics.py
import pm4py
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.objects.conversion.heuristics_net import converter as hn_converter

def discover_heuristics(log, dependency_threshold=0.5, and_threshold=0.65, 
                        loop_two_threshold=0.5, min_act_count=1):
    """
    Heuristics Miner - robust for noisy real-world logs.
    
    Parameters:
    - dependency_threshold (0.0-1.0): Higher = fewer edges, cleaner model
      - Low (0.1-0.3): Include weak relationships
      - Medium (0.5): Balanced (default)
      - High (0.8-0.95): Only strong relationships
    - and_threshold: For detecting parallel vs choice
    - loop_two_threshold: For length-2 loops
    - min_act_count: Minimum activity occurrences
    """
    parameters = {
        heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: dependency_threshold,
        heuristics_miner.Variants.CLASSIC.value.Parameters.AND_THRESHOLD: and_threshold,
        heuristics_miner.Variants.CLASSIC.value.Parameters.LOOP_LENGTH_TWO_THRESH: loop_two_threshold,
        heuristics_miner.Variants.CLASSIC.value.Parameters.MIN_ACT_COUNT: min_act_count,
    }
    
    # Returns HeuristicsNet object
    heu_net = heuristics_miner.apply(log, parameters=parameters)
    
    # Convert to Petri Net for standard handling
    net, im, fm = hn_converter.apply(heu_net)
    
    return net, im, fm, heu_net
```

### 1.4 Inductive Miner (Recommended - Guarantees Soundness)

```python
# src/domain/process_mining/discovery/inductive.py
import pm4py
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

def discover_inductive(log, noise_threshold=0.0, variant="imf"):
    """
    Inductive Miner - RECOMMENDED for production.
    Guarantees: Sound model (no deadlocks), always fits log.
    
    Variants:
    - "im": Basic (no noise handling)
    - "imf": Frequent (filters infrequent behavior) - RECOMMENDED
    - "imd": Directly-follows (fastest)
    
    Noise Threshold:
    - 0.0: No filtering
    - 0.1-0.2: Light filtering (recommended)
    - 0.3-0.5: Aggressive filtering
    """
    variant_map = {
        "im": inductive_miner.Variants.IM,
        "imf": inductive_miner.Variants.IMf,
        "imd": inductive_miner.Variants.IMd,
    }
    
    selected_variant = variant_map.get(variant, inductive_miner.Variants.IMf)
    
    # Get Process Tree first (native output)
    process_tree = inductive_miner.apply_tree(
        log,
        variant=selected_variant,
        parameters={
            selected_variant.value.Parameters.NOISE_THRESHOLD: noise_threshold
        }
    )
    
    # Convert to Petri Net
    from pm4py.objects.conversion.process_tree import converter as pt_converter
    net, im, fm = pt_converter.apply(process_tree)
    
    return net, im, fm, process_tree

def discover_inductive_dfg(log, noise_threshold=0.2):
    """
    Fastest Inductive Miner variant - uses DFG as input.
    5-10x faster than standard IM on large logs.
    """
    # First generate DFG
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    
    # Apply IMd variant
    net, im, fm = pm4py.discover_petri_net_inductive(
        log,
        noise_threshold=noise_threshold
    )
    
    return net, im, fm
```

### 1.5 ILP Miner (Optimal but Slow)

```python
# src/domain/process_mining/discovery/ilp.py
import pm4py
from pm4py.algo.discovery.ilp import algorithm as ilp_miner

def discover_ilp(log):
    """
    ILP Miner - optimal solution via Integer Linear Programming.
    Use for: Small critical processes where optimality matters.
    
    WARNING: 
    - < 5,000 events: Minutes
    - 5k-50k events: Hours
    - > 50k events: May not terminate
    """
    net, im, fm = ilp_miner.apply(log)
    return net, im, fm
```

### 1.6 BPMN Discovery

```python
# src/domain/process_mining/discovery/bpmn.py
import pm4py

def discover_bpmn(log, noise_threshold=0.2):
    """
    Discover BPMN model (via Inductive Miner conversion).
    """
    # Method 1: Direct BPMN discovery
    bpmn_graph = pm4py.discover_bpmn_inductive(log, noise_threshold=noise_threshold)
    
    return bpmn_graph

def petri_net_to_bpmn(net, im, fm):
    """
    Convert Petri Net to BPMN.
    """
    bpmn_graph = pm4py.convert_to_bpmn(net, im, fm)
    return bpmn_graph

def export_bpmn(bpmn_graph, filepath):
    """
    Export BPMN to XML file.
    """
    pm4py.write_bpmn(bpmn_graph, filepath)
```

---

## 2. MODEL SERIALIZATION

### 2.1 Petri Net to JSON

```python
# src/domain/process_mining/serialization/petri_net.py

def petri_net_to_json(net, im, fm):
    """
    Serialize Petri Net to JSON for storage/frontend.
    """
    places = []
    for place in net.places:
        places.append({
            "id": place.name,
            "name": place.name,
            "tokens": 1 if place in im else 0,
            "is_initial": place in im,
            "is_final": place in fm
        })
    
    transitions = []
    for trans in net.transitions:
        transitions.append({
            "id": trans.name,
            "name": trans.name,
            "label": trans.label if trans.label else trans.name,
            "is_silent": trans.label is None
        })
    
    arcs = []
    for arc in net.arcs:
        arcs.append({
            "id": f"{arc.source.name}->{arc.target.name}",
            "source": arc.source.name,
            "target": arc.target.name,
            "weight": arc.weight if hasattr(arc, 'weight') else 1
        })
    
    return {
        "places": places,
        "transitions": transitions,
        "arcs": arcs,
        "initial_marking": [p.name for p in im],
        "final_marking": [p.name for p in fm],
        "model_type": "petri_net"
    }

def json_to_petri_net(data):
    """
    Deserialize JSON back to PM4Py Petri Net.
    """
    from pm4py.objects.petri_net.obj import PetriNet, Marking
    from pm4py.objects.petri_net.utils import petri_utils
    
    net = PetriNet(name="imported_net")
    place_map = {}
    trans_map = {}
    
    # Create places
    for p_data in data["places"]:
        place = PetriNet.Place(p_data["id"])
        net.places.add(place)
        place_map[p_data["id"]] = place
    
    # Create transitions
    for t_data in data["transitions"]:
        label = None if t_data.get("is_silent") else t_data.get("label", t_data["name"])
        trans = PetriNet.Transition(t_data["id"], label)
        net.transitions.add(trans)
        trans_map[t_data["id"]] = trans
    
    # Create arcs
    for a_data in data["arcs"]:
        source_id = a_data["source"]
        target_id = a_data["target"]
        
        if source_id in place_map:
            source = place_map[source_id]
            target = trans_map[target_id]
        else:
            source = trans_map[source_id]
            target = place_map[target_id]
        
        petri_utils.add_arc_from_to(source, target, net)
    
    # Create markings
    im = Marking()
    for p_id in data.get("initial_marking", []):
        im[place_map[p_id]] = 1
    
    fm = Marking()
    for p_id in data.get("final_marking", []):
        fm[place_map[p_id]] = 1
    
    return net, im, fm
```

### 2.2 Process Tree to JSON

```python
# src/domain/process_mining/serialization/process_tree.py
from pm4py.objects.process_tree.obj import ProcessTree, Operator

def process_tree_to_json(tree):
    """
    Serialize Process Tree to JSON.
    """
    def node_to_dict(node):
        result = {
            "id": str(id(node)),
            "operator": node.operator.value if node.operator else None,
            "label": node.label,
            "children": [node_to_dict(child) for child in node.children]
        }
        return result
    
    return {
        "root": node_to_dict(tree),
        "model_type": "process_tree"
    }

# Operator meanings:
# -> : Sequence (A then B)
# X  : XOR/Choice (A or B)
# +  : AND/Parallel (A and B in any order)
# *  : Loop (repeat)
# τ  : Silent/invisible
```

---

## 3. VISUALIZATION GENERATION

### 3.1 SVG Generation

```python
# src/domain/process_mining/visualization/svg.py
import pm4py
from pm4py.visualization.petri_net import visualizer as pn_viz
from pm4py.visualization.dfg import visualizer as dfg_viz
from pm4py.visualization.bpmn import visualizer as bpmn_viz
from pm4py.visualization.process_tree import visualizer as pt_viz

def petri_net_to_svg(net, im, fm):
    """
    Generate SVG visualization of Petri Net.
    """
    gviz = pn_viz.apply(net, im, fm, parameters={
        pn_viz.Variants.WO_DECORATION.value.Parameters.FORMAT: "svg"
    })
    svg_bytes = pn_viz.serialize(gviz)
    return svg_bytes.decode('utf-8')

def dfg_to_svg(dfg, log=None, variant="frequency"):
    """
    Generate SVG visualization of DFG.
    
    Variants:
    - "frequency": Show edge counts
    - "performance": Show durations
    """
    from pm4py.statistics.attributes.log.get import get_attribute_values
    
    if variant == "frequency":
        viz_variant = dfg_viz.Variants.FREQUENCY
    else:
        viz_variant = dfg_viz.Variants.PERFORMANCE
    
    # Get activity counts if log provided
    activities_count = None
    if log:
        activities_count = get_attribute_values(log, "concept:name")
    
    gviz = dfg_viz.apply(
        dfg,
        activities_count=activities_count,
        variant=viz_variant,
        parameters={viz_variant.value.Parameters.FORMAT: "svg"}
    )
    
    svg_bytes = dfg_viz.serialize(gviz)
    return svg_bytes.decode('utf-8')

def bpmn_to_svg(bpmn_graph):
    """
    Generate SVG visualization of BPMN.
    """
    gviz = bpmn_viz.apply(bpmn_graph, parameters={
        bpmn_viz.Variants.CLASSIC.value.Parameters.FORMAT: "svg"
    })
    svg_bytes = bpmn_viz.serialize(gviz)
    return svg_bytes.decode('utf-8')

def process_tree_to_svg(tree):
    """
    Generate SVG visualization of Process Tree.
    """
    gviz = pt_viz.apply(tree, parameters={
        pt_viz.Variants.WO_DECORATION.value.Parameters.FORMAT: "svg"
    })
    svg_bytes = pt_viz.serialize(gviz)
    return svg_bytes.decode('utf-8')
```

---

## 4. CONFORMANCE CHECKING

### 4.1 Token Replay

```python
# src/domain/process_mining/conformance/token_replay.py
import pm4py
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay

def check_conformance_token_replay(log, net, im, fm):
    """
    Token-based replay conformance checking.
    Returns fitness score and diagnostics.
    """
    replayed_traces = token_replay.apply(log, net, im, fm)
    
    # Calculate fitness
    total_fitness = sum(r["trace_fitness"] for r in replayed_traces)
    avg_fitness = total_fitness / len(replayed_traces)
    
    # Find conforming vs deviating cases
    conforming = []
    deviating = []
    
    for i, result in enumerate(replayed_traces):
        case_id = log[i].attributes.get("concept:name", f"case_{i}")
        
        case_result = {
            "case_id": case_id,
            "fitness": result["trace_fitness"],
            "missing_tokens": result.get("missing_tokens", 0),
            "remaining_tokens": result.get("remaining_tokens", 0),
            "consumed_tokens": result.get("consumed_tokens", 0),
            "produced_tokens": result.get("produced_tokens", 0),
        }
        
        if result["trace_fitness"] == 1.0:
            conforming.append(case_result)
        else:
            deviating.append(case_result)
    
    return {
        "fitness": avg_fitness,
        "conforming_cases": len(conforming),
        "deviating_cases": len(deviating),
        "total_cases": len(replayed_traces),
        "conformance_rate": len(conforming) / len(replayed_traces),
        "conforming": conforming[:100],  # Limit for response size
        "deviating": sorted(deviating, key=lambda x: x["fitness"])[:100]
    }
```

### 4.2 Alignment-Based Conformance

```python
# src/domain/process_mining/conformance/alignments.py
import pm4py
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments

def check_conformance_alignments(log, net, im, fm):
    """
    Alignment-based conformance - more accurate but slower.
    """
    aligned_traces = alignments.apply(log, net, im, fm)
    
    results = []
    total_fitness = 0
    
    for i, alignment in enumerate(aligned_traces):
        case_id = log[i].attributes.get("concept:name", f"case_{i}")
        
        # Extract alignment details
        moves = alignment.get("alignment", [])
        
        log_moves = []  # Moves only in log (deviations)
        model_moves = []  # Moves only in model (skipped)
        sync_moves = []  # Synchronized moves (conforming)
        
        for move in moves:
            log_move, model_move = move
            if log_move == ">>" and model_move != ">>":
                model_moves.append(model_move)
            elif model_move == ">>" and log_move != ">>":
                log_moves.append(log_move)
            else:
                sync_moves.append(log_move)
        
        fitness = alignment.get("fitness", 0)
        total_fitness += fitness
        
        results.append({
            "case_id": case_id,
            "fitness": fitness,
            "cost": alignment.get("cost", 0),
            "sync_moves": len(sync_moves),
            "log_moves": log_moves,  # Activities in log but not model
            "model_moves": model_moves,  # Activities skipped
            "is_conforming": fitness == 1.0
        })
    
    avg_fitness = total_fitness / len(aligned_traces)
    
    return {
        "fitness": avg_fitness,
        "alignments": results[:100],
        "conforming_count": sum(1 for r in results if r["is_conforming"]),
        "total_cases": len(results)
    }
```

### 4.3 Precision & Generalization

```python
# src/domain/process_mining/conformance/quality.py
import pm4py
from pm4py.algo.evaluation.precision import algorithm as precision_eval
from pm4py.algo.evaluation.generalization import algorithm as generalization_eval
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_eval

def calculate_precision(log, net, im, fm):
    """
    Precision: How much of the model behavior is actually used?
    High precision = model doesn't allow too much extra behavior.
    """
    precision = precision_eval.apply(log, net, im, fm)
    return precision

def calculate_generalization(log, net, im, fm):
    """
    Generalization: Will model work on unseen cases?
    """
    generalization = generalization_eval.apply(log, net, im, fm)
    return generalization

def calculate_simplicity(net):
    """
    Simplicity: How complex is the model?
    """
    simplicity = simplicity_eval.apply(net)
    return simplicity

def evaluate_model_quality(log, net, im, fm):
    """
    Calculate all quality dimensions.
    """
    from pm4py.algo.evaluation.replay_fitness import algorithm as fitness_eval
    
    fitness_result = fitness_eval.apply(log, net, im, fm)
    
    return {
        "fitness": fitness_result.get("average_trace_fitness", 0),
        "precision": calculate_precision(log, net, im, fm),
        "generalization": calculate_generalization(log, net, im, fm),
        "simplicity": calculate_simplicity(net),
        "num_places": len(net.places),
        "num_transitions": len(net.transitions),
        "num_arcs": len(net.arcs)
    }
```

---

## 5. ANALYTICS

### 5.1 Variants Analysis

```python
# src/domain/analytics/variants.py
import pm4py
from pm4py.statistics.variants.log import get as variants_get

def get_variants(log, max_variants=100):
    """
    Extract all process variants (unique activity sequences).
    """
    variants = variants_get.get_variants(log)
    
    total_cases = len(log)
    result = []
    
    for variant_tuple, traces in variants.items():
        # variant_tuple is tuple of activities
        variant_list = list(variant_tuple) if isinstance(variant_tuple, tuple) else [variant_tuple]
        
        result.append({
            "variant": variant_list,
            "variant_string": " → ".join(variant_list),
            "count": len(traces),
            "percentage": len(traces) / total_cases * 100,
            "case_ids": [t.attributes.get("concept:name", "") for t in traces[:10]]
        })
    
    # Sort by frequency
    result.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "total_variants": len(variants),
        "total_cases": total_cases,
        "variant_explosion_ratio": len(variants) / total_cases,
        "variants": result[:max_variants]
    }
```

### 5.2 Bottleneck Detection

```python
# src/domain/analytics/bottlenecks.py
import pm4py
from pm4py.statistics.sojourn_time.log import get as sojourn_get
from pm4py.statistics.service_time.log import get as service_get

def detect_bottlenecks(log, top_n=10):
    """
    Identify bottlenecks by analyzing waiting/processing times.
    """
    # Sojourn time = waiting + processing
    sojourn_times = sojourn_get.apply(
        log, 
        parameters={"aggregation_measure": "mean"}
    )
    
    # Service time = just processing (if available)
    try:
        service_times = service_get.apply(
            log,
            parameters={"aggregation_measure": "mean"}
        )
    except:
        service_times = {}
    
    bottlenecks = []
    for activity, sojourn in sojourn_times.items():
        service = service_times.get(activity, 0)
        waiting = sojourn - service if service else sojourn
        
        # Classify severity
        if sojourn > 86400:  # > 1 day
            severity = "critical"
        elif sojourn > 3600:  # > 1 hour
            severity = "high"
        elif sojourn > 600:  # > 10 min
            severity = "medium"
        else:
            severity = "low"
        
        bottlenecks.append({
            "activity": activity,
            "avg_sojourn_time": sojourn,
            "avg_service_time": service,
            "avg_waiting_time": waiting,
            "severity": severity,
            "sojourn_time_formatted": format_duration(sojourn),
            "waiting_time_formatted": format_duration(waiting)
        })
    
    # Sort by sojourn time (worst first)
    bottlenecks.sort(key=lambda x: x["avg_sojourn_time"], reverse=True)
    
    return {
        "bottlenecks": bottlenecks[:top_n],
        "total_activities": len(bottlenecks)
    }

def format_duration(seconds):
    """Format seconds to human readable."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}h"
    else:
        return f"{seconds/86400:.1f}d"
```

### 5.3 Rework Detection

```python
# src/domain/analytics/rework.py

def detect_rework(log):
    """
    Identify cases with repeated activities (rework).
    """
    rework_cases = []
    total_rework_events = 0
    activity_rework_counts = {}
    
    for trace in log:
        case_id = trace.attributes.get("concept:name", "unknown")
        activities = [event["concept:name"] for event in trace]
        
        # Find repeated activities
        seen = set()
        repeated = []
        for act in activities:
            if act in seen:
                repeated.append(act)
                total_rework_events += 1
                activity_rework_counts[act] = activity_rework_counts.get(act, 0) + 1
            seen.add(act)
        
        if repeated:
            rework_cases.append({
                "case_id": case_id,
                "repeated_activities": list(set(repeated)),
                "rework_count": len(repeated),
                "trace_length": len(activities)
            })
    
    # Sort by rework count
    rework_cases.sort(key=lambda x: x["rework_count"], reverse=True)
    
    # Activity rework ranking
    activity_ranking = [
        {"activity": act, "rework_count": count}
        for act, count in sorted(activity_rework_counts.items(), 
                                  key=lambda x: x[1], reverse=True)
    ]
    
    return {
        "rework_rate": len(rework_cases) / len(log) * 100,
        "cases_with_rework": len(rework_cases),
        "total_cases": len(log),
        "total_rework_events": total_rework_events,
        "rework_cases": rework_cases[:50],
        "activity_rework_ranking": activity_ranking[:20]
    }
```

### 5.4 Cycle Time Analysis

```python
# src/domain/analytics/cycle_time.py
import pm4py
from pm4py.statistics.traces.generic.log import case_statistics
import statistics

def analyze_cycle_times(log):
    """
    Analyze case durations (cycle times).
    """
    # Get all case durations in seconds
    durations = case_statistics.get_all_case_durations(log)
    
    if not durations:
        return {"error": "No duration data available"}
    
    # Calculate statistics
    durations_sorted = sorted(durations)
    
    return {
        "count": len(durations),
        "mean": statistics.mean(durations),
        "median": statistics.median(durations),
        "min": min(durations),
        "max": max(durations),
        "std_dev": statistics.stdev(durations) if len(durations) > 1 else 0,
        "percentile_25": durations_sorted[len(durations)//4],
        "percentile_75": durations_sorted[3*len(durations)//4],
        "percentile_90": durations_sorted[int(len(durations)*0.9)],
        "percentile_95": durations_sorted[int(len(durations)*0.95)],
        # Formatted versions
        "mean_formatted": format_duration(statistics.mean(durations)),
        "median_formatted": format_duration(statistics.median(durations)),
        "min_formatted": format_duration(min(durations)),
        "max_formatted": format_duration(max(durations)),
    }
```

### 5.5 Throughput Analysis

```python
# src/domain/analytics/throughput.py
import pm4py
from pm4py.statistics.traces.generic.log import case_arrival
from datetime import datetime, timedelta
from collections import defaultdict

def analyze_throughput(log, time_unit="day"):
    """
    Analyze case throughput over time.
    """
    # Get case start times
    case_starts = []
    case_ends = []
    
    for trace in log:
        events = list(trace)
        if events:
            start_time = events[0]["time:timestamp"]
            end_time = events[-1]["time:timestamp"]
            case_starts.append(start_time)
            case_ends.append(end_time)
    
    if not case_starts:
        return {"error": "No timestamp data"}
    
    # Group by time unit
    def get_period(dt, unit):
        if unit == "hour":
            return dt.strftime("%Y-%m-%d %H:00")
        elif unit == "day":
            return dt.strftime("%Y-%m-%d")
        elif unit == "week":
            return dt.strftime("%Y-W%W")
        elif unit == "month":
            return dt.strftime("%Y-%m")
        return dt.strftime("%Y-%m-%d")
    
    arrivals = defaultdict(int)
    completions = defaultdict(int)
    
    for start in case_starts:
        arrivals[get_period(start, time_unit)] += 1
    
    for end in case_ends:
        completions[get_period(end, time_unit)] += 1
    
    # Build time series
    all_periods = sorted(set(arrivals.keys()) | set(completions.keys()))
    
    throughput_data = []
    for period in all_periods:
        throughput_data.append({
            "period": period,
            "arrivals": arrivals.get(period, 0),
            "completions": completions.get(period, 0)
        })
    
    return {
        "time_unit": time_unit,
        "total_arrivals": sum(arrivals.values()),
        "total_completions": sum(completions.values()),
        "avg_arrivals_per_period": sum(arrivals.values()) / len(all_periods),
        "avg_completions_per_period": sum(completions.values()) / len(all_periods),
        "data": throughput_data
    }
```

---

## 6. EVENT LOG LOADING

### 6.1 Load from Various Formats

```python
# src/domain/process_mining/log_utils.py
import pm4py
import pandas as pd
from pm4py.objects.conversion.log import converter as log_converter

def load_event_log_from_csv(filepath, case_col, activity_col, timestamp_col, 
                            resource_col=None, separator=","):
    """
    Load event log from CSV file.
    """
    df = pd.read_csv(filepath, sep=separator)
    
    # Rename columns to PM4Py standard names
    rename_map = {
        case_col: "case:concept:name",
        activity_col: "concept:name",
        timestamp_col: "time:timestamp"
    }
    if resource_col:
        rename_map[resource_col] = "org:resource"
    
    df = df.rename(columns=rename_map)
    
    # Parse timestamps
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
    
    # Sort by case and timestamp
    df = df.sort_values(["case:concept:name", "time:timestamp"])
    
    # Convert to EventLog
    log = log_converter.apply(df, variant=log_converter.Variants.TO_EVENT_LOG)
    
    return log

def load_event_log_from_xes(filepath):
    """
    Load event log from XES file.
    """
    log = pm4py.read_xes(filepath)
    return log

def load_event_log_from_dataframe(df, case_col, activity_col, timestamp_col):
    """
    Load event log from pandas DataFrame.
    """
    # Ensure proper column names
    df = df.rename(columns={
        case_col: "case:concept:name",
        activity_col: "concept:name",
        timestamp_col: "time:timestamp"
    })
    
    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["time:timestamp"]):
        df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
    
    # Convert to EventLog
    log = log_converter.apply(df, variant=log_converter.Variants.TO_EVENT_LOG)
    
    return log

def get_log_statistics(log):
    """
    Get basic statistics about an event log.
    """
    df = pm4py.convert_to_dataframe(log)
    
    return {
        "event_count": len(df),
        "case_count": df["case:concept:name"].nunique(),
        "activity_count": df["concept:name"].nunique(),
        "activities": df["concept:name"].unique().tolist(),
        "start_timestamp": df["time:timestamp"].min().isoformat(),
        "end_timestamp": df["time:timestamp"].max().isoformat(),
        "avg_events_per_case": len(df) / df["case:concept:name"].nunique()
    }
```

---

## 7. ALGORITHM SELECTION HELPER

```python
# src/domain/process_mining/algorithm_selector.py

def recommend_algorithm(log):
    """
    Automatically recommend best discovery algorithm based on log characteristics.
    """
    import pm4py
    from pm4py.statistics.variants.log import get as variants_get
    
    df = pm4py.convert_to_dataframe(log)
    
    # Calculate characteristics
    num_events = len(df)
    num_cases = df["case:concept:name"].nunique()
    num_activities = df["concept:name"].nunique()
    variants = variants_get.get_variants(log)
    num_variants = len(variants)
    
    variant_ratio = num_variants / num_cases
    avg_case_length = num_events / num_cases
    
    # Decision logic
    recommendations = []
    
    if num_events < 1000 and variant_ratio < 0.1:
        recommendations.append({
            "algorithm": "alpha",
            "reason": "Small, clean log with low variant explosion",
            "confidence": "high"
        })
    
    if variant_ratio > 0.5:
        recommendations.append({
            "algorithm": "inductive",
            "params": {"noise_threshold": 0.3},
            "reason": "High variant explosion - need aggressive noise filtering",
            "confidence": "high"
        })
    elif variant_ratio > 0.2:
        recommendations.append({
            "algorithm": "heuristic",
            "params": {"dependency_threshold": 0.7},
            "reason": "Moderate noise - heuristic miner handles this well",
            "confidence": "medium"
        })
    
    if num_activities > 50:
        recommendations.append({
            "algorithm": "dfg",
            "reason": "Many activities - DFG provides clearest overview",
            "confidence": "high"
        })
    
    if num_events > 1000000:
        recommendations.append({
            "algorithm": "inductive_dfg",
            "reason": "Very large log - need fastest variant",
            "confidence": "high"
        })
    
    # Default recommendation
    if not recommendations:
        recommendations.append({
            "algorithm": "inductive",
            "params": {"noise_threshold": 0.2},
            "reason": "General purpose, guarantees sound model",
            "confidence": "medium"
        })
    
    return {
        "log_characteristics": {
            "events": num_events,
            "cases": num_cases,
            "activities": num_activities,
            "variants": num_variants,
            "variant_ratio": variant_ratio,
            "avg_case_length": avg_case_length
        },
        "recommendations": recommendations,
        "primary_recommendation": recommendations[0]
    }
```

---

## 8. COMPLETE DISCOVERY SERVICE

```python
# src/services/discovery/discovery_service.py
from typing import Optional, Dict, Any
import pm4py

class DiscoveryService:
    """
    Unified discovery service supporting all algorithms.
    """
    
    ALGORITHMS = {
        "dfg": {"name": "Directly-Follows Graph", "output": "dfg"},
        "alpha": {"name": "Alpha Miner", "output": "petri_net"},
        "alpha_plus": {"name": "Alpha+ Miner", "output": "petri_net"},
        "heuristic": {"name": "Heuristics Miner", "output": "petri_net"},
        "inductive": {"name": "Inductive Miner", "output": "petri_net"},
        "inductive_imf": {"name": "Inductive Miner (Infrequent)", "output": "petri_net"},
        "inductive_imd": {"name": "Inductive Miner (DFG)", "output": "petri_net"},
        "ilp": {"name": "ILP Miner", "output": "petri_net"},
        "bpmn": {"name": "BPMN Discovery", "output": "bpmn"},
    }
    
    def list_algorithms(self):
        """List all available algorithms."""
        return [
            {"id": k, **v} 
            for k, v in self.ALGORITHMS.items()
        ]
    
    def discover(self, log, algorithm: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run discovery with specified algorithm.
        """
        params = parameters or {}
        
        if algorithm == "dfg":
            return self._discover_dfg(log)
        elif algorithm == "alpha":
            return self._discover_alpha(log)
        elif algorithm == "alpha_plus":
            return self._discover_alpha_plus(log)
        elif algorithm == "heuristic":
            return self._discover_heuristic(log, params)
        elif algorithm in ["inductive", "inductive_imf"]:
            return self._discover_inductive(log, params)
        elif algorithm == "inductive_imd":
            return self._discover_inductive_dfg(log, params)
        elif algorithm == "ilp":
            return self._discover_ilp(log)
        elif algorithm == "bpmn":
            return self._discover_bpmn(log, params)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    def _discover_dfg(self, log):
        dfg, start_acts, end_acts = pm4py.discover_dfg(log)
        # ... (use code from section 1.1)
        
    def _discover_inductive(self, log, params):
        noise = params.get("noise_threshold", 0.2)
        net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=noise)
        # ... serialize and return
        
    # ... other methods
```

---

## QUICK REFERENCE

| Algorithm | PM4Py Function | Best For |
|-----------|----------------|----------|
| DFG | `pm4py.discover_dfg()` | Quick viz, large logs |
| Alpha | `pm4py.discover_petri_net_alpha()` | Clean simple logs |
| Heuristic | `pm4py.discover_petri_net_heuristics()` | Noisy real-world logs |
| Inductive | `pm4py.discover_petri_net_inductive()` | Production (sound) |
| ILP | `pm4py.discover_petri_net_ilp()` | Small optimal models |
| BPMN | `pm4py.discover_bpmn_inductive()` | Business documentation |

**Conformance:**
| Check | Function |
|-------|----------|
| Token Replay | `pm4py.conformance_diagnostics_token_based_replay()` |
| Alignments | `pm4py.conformance_diagnostics_alignments()` |
| Fitness | `pm4py.fitness_token_based_replay()` |
| Precision | `pm4py.precision_token_based_replay()` |
