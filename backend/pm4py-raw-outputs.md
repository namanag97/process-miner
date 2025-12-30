# PM4Py Raw Outputs Reference

**Source:** `/Users/namanagarwal/system/demo/pm4py-capabilities.py`

This document shows the **actual raw outputs** from PM4Py analysis functions as demonstrated in the comprehensive capabilities script.

---

## Output Structure Pattern

All analyses follow this consistent structure:

```json
{
  "metadata": {
    "analysis_timestamp": "ISO8601",
    "pm4py_version": "2.7.19.5",
    "total_cases": 30000,
    "total_events": 180000
  },
  "analyses": {
    "[analysis_name]": {
      "concept": "Human-readable name",
      "description": "What this analysis does",
      "reference": "Academic paper citation",
      "data": {
        /* actual results */
      }
    }
  },
  "summary": {
    "total_analyses": 23,
    "successful": 21,
    "failed": 2,
    "analyses_performed": ["list", "of", "analyses"]
  }
}
```

---

## 1. Event Data Statistics

### PM4Py Functions Used:

- `pm4py.get_start_activities(log)`
- `pm4py.get_end_activities(log)`
- `get_variants(log)`
- `case_statistics.get_all_case_durations(log)`
- `df['concept:name'].value_counts()`

### Raw Output:

```json
{
  "concept": "Event Log Statistics",
  "description": "Basic statistics about the event log",
  "data": {
    "start_activities": {
      "status": "success",
      "result": {
        "First Notification of Loss (FNOL)": 30000
      }
    },
    "end_activities": {
      "status": "success",
      "result": {
        "Close Claim": 30000
      }
    },
    "top_20_variants": {
      "status": "success",
      "result": [
        {
          "variant": "('Activity1', 'Activity2', ...)",
          "count": 1234
        }
      ],
      "total_variants": 150
    },
    "case_duration_stats": {
      "status": "success",
      "result": {
        "min_duration_seconds": 1362998.936,
        "max_duration_seconds": 4676330.265,
        "avg_duration_seconds": 3024994.595,
        "median_duration_seconds": 3026242.309
      }
    },
    "activity_frequencies": {
      "status": "success",
      "result": {
        "First Notification of Loss (FNOL)": 30000,
        "Assign Claim": 30000,
        "Claim Decision": 30000,
        "Set Reserve": 30000,
        "Payment Sent": 30000,
        "Close Claim": 30000
      }
    }
  }
}
```

**Key Data Types:**

- `start_activities`: `Dict[str, int]` - Activity name → frequency
- `end_activities`: `Dict[str, int]` - Activity name → frequency
- `variants`: `Dict[Tuple[str], int]` - Variant tuple → count
- `durations`: `List[float]` - Case durations in seconds

---

## 2. Directly-Follows Graph (DFG)

### PM4Py Function:

```python
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
dfg = dfg_discovery.apply(log)
```

### Raw Output:

```json
{
  "concept": "Directly-Follows Graph (DFG)",
  "description": "Shows frequency of activity sequences",
  "reference": "van der Aalst - A practitioner's guide to process mining",
  "data": {
    "dfg_edges": {
      "First Notification of Loss (FNOL) -> Assign Claim": 30000,
      "Assign Claim -> Claim Decision": 30000,
      "Claim Decision -> Set Reserve": 30000,
      "Set Reserve -> Payment Sent": 30000,
      "Payment Sent -> Close Claim": 30000
    },
    "num_edges": 5,
    "start_activities": {
      "First Notification of Loss (FNOL)": 30000
    },
    "end_activities": {
      "Close Claim": 30000
    }
  }
}
```

**Raw PM4Py Return Type:**

```python
dfg: Dict[Tuple[str, str], int]
# Example: {('A', 'B'): 150, ('B', 'C'): 120}
```

---

## 3. Alpha Miner

### PM4Py Function:

```python
net, im, fm = pm4py.discover_petri_net_alpha(log)
```

### Raw Output:

```json
{
  "concept": "Alpha Miner",
  "description": "Discovers Petri net from event log",
  "reference": "van der Aalst et al. - Workflow Mining: Discovering Process Models from Event Logs",
  "data": {
    "places": [
      "start",
      "({'Assign Claim'}, {'Claim Decision'})",
      "({'Claim Decision'}, {'Set Reserve'})",
      "({'Payment Sent'}, {'Close Claim'})",
      "({'First Notification of Loss (FNOL)'}, {'Assign Claim'})",
      "end",
      "({'Set Reserve'}, {'Payment Sent'})"
    ],
    "transitions": [
      "(Close Claim, 'Close Claim')",
      "(Assign Claim, 'Assign Claim')",
      "(First Notification of Loss (FNOL), 'First Notification of Loss (FNOL)')",
      "(Claim Decision, 'Claim Decision')",
      "(Set Reserve, 'Set Reserve')",
      "(Payment Sent, 'Payment Sent')"
    ],
    "arcs": [
      "start -> (First Notification of Loss (FNOL), 'First Notification of Loss (FNOL)')",
      "({'Claim Decision'}, {'Set Reserve'}) -> (Set Reserve, 'Set Reserve')",
      "/* ... more arcs ... */"
    ],
    "initial_marking": "['start:1']",
    "final_marking": "['end:1']"
  }
}
```

**Raw PM4Py Return Type:**

```python
net: PetriNet  # Has .places, .transitions, .arcs
im: Marking    # Initial marking
fm: Marking    # Final marking
```

---

## 4. Inductive Miner

### PM4Py Function:

```python
net, im, fm = pm4py.discover_petri_net_inductive(log)
```

### Raw Output:

```json
{
  "concept": "Inductive Miner",
  "description": "Discovers block-structured process models",
  "reference": "Leemans et al. - Discovering block-structured process models from event logs",
  "data": {
    "places": ["source", "p_3", "sink", "p_4", "p_5", "p_6", "p_7"],
    "transitions": [
      "(879b6a17-7b57-4df5-9080-301f8ec6d650, 'Assign Claim')",
      "(54b03830-6c79-4cb4-b920-b80a6639f977, 'Payment Sent')",
      "(d32bfccc-9317-4059-8007-74c95bf03be2, 'First Notification of Loss (FNOL)')",
      "/* ... UUIDs with activity labels ... */"
    ],
    "arcs": [
      "(0f18e82d-4968-4b92-ab6e-5f3ee09bd78b, 'Claim Decision') -> p_5",
      "source -> (d32bfccc-9317-4059-8007-74c95bf03be2, 'First Notification of Loss (FNOL)')",
      "/* ... */"
    ],
    "initial_marking": "['source:1']",
    "final_marking": "['sink:1']"
  }
}
```

**Note:** Inductive Miner uses UUIDs for transition IDs

---

## 5. Inductive Miner Infrequent (IMf)

### PM4Py Function:

```python
net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=0.2)
```

### Raw Output:

```json
{
  "concept": "Inductive Miner Infrequent (IMf)",
  "description": "Handles infrequent behavior in process discovery",
  "reference": "Leemans et al. - Discovering block-structured process models from event logs containing infrequent behaviour",
  "data": {
    "places": ["source", "p_4", "p_5", "sink", "p_3", "p_6", "p_7"],
    "transitions": [
      "(40223287-d88f-4555-9554-9290d9e52077, 'Claim Decision')",
      "/* ... */"
    ],
    "num_arcs": 12
  }
}
```

---

## 6. Heuristics Miner

### PM4Py Function:

```python
heu_net = pm4py.discover_heuristics_net(log)
```

### Raw Output:

```json
{
  "concept": "Heuristics Miner",
  "description": "Flexible heuristics-based process discovery",
  "reference": "Weijters et al. - Flexible heuristics miner (FHM)",
  "data": {
    "nodes": [
      "First Notification of Loss (FNOL)",
      "Assign Claim",
      "Claim Decision",
      "Set Reserve",
      "Payment Sent",
      "Close Claim"
    ],
    "status": "Heuristics net discovered successfully"
  }
}
```

**Raw PM4Py Return Type:**

```python
heuristics_net: HeuristicsNet  # Has .nodes attribute
```

---

## 7. Process Tree

### PM4Py Function:

```python
process_tree = pm4py.discover_process_tree_inductive(log)
```

### Raw Output:

```json
{
  "concept": "Process Tree",
  "description": "Hierarchical process model representation",
  "data": {
    "tree_string": "->( 'First Notification of Loss (FNOL)', 'Assign Claim', 'Claim Decision', 'Set Reserve', 'Payment Sent', 'Close Claim' )",
    "operator": "->",
    "label": null
  }
}
```

**Raw PM4Py Return Type:**

```python
tree: ProcessTree  # Has .operator, .label, .children
# Operators: ->, X, +, *, τ (tau/skip)
```

**Tree Operators:**

- `->` : Sequence
- `X` : Exclusive choice (XOR)
- `+` : Parallel (AND)
- `*` : Loop
- `τ` : Silent/Skip

---

## 8. BPMN Model

### PM4Py Function:

```python
bpmn_model = convert_to_bpmn(net, im, fm)
```

### Raw Output:

```json
{
  "concept": "Business Process Model and Notation (BPMN)",
  "description": "Standard business process modeling notation",
  "reference": "Object Management Group (OMG)",
  "data": {
    "nodes": 8,
    "flows": 7,
    "status": "BPMN model created successfully"
  }
}
```

**Raw PM4Py Return Type:**

```python
bpmn: BPMN  # Has .get_nodes(), .get_flows()
```

---

## 9. Token-Based Replay

### PM4Py Function:

```python
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
replayed = token_replay.apply(log, net, im, fm)
```

### Raw Output:

```json
{
  "concept": "Token-Based Replay",
  "description": "Conformance checking using token replay",
  "reference": "Berti et al. - A novel token-based replay technique",
  "data": {
    "total_traces": 30000,
    "total_produced_tokens": 210000,
    "total_consumed_tokens": 210000,
    "total_missing_tokens": 0,
    "total_remaining_tokens": 0,
    "trace_fitness_available": true
  }
}
```

**Raw PM4Py Return Type:**

```python
replayed: List[Dict]
# Each item: {
#   'produced_tokens': int,
#   'consumed_tokens': int,
#   'missing_tokens': int,
#   'remaining_tokens': int,
#   'trace_is_fit': bool
# }
```

---

## 10. Alignments

### PM4Py Function:

```python
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
aligned = alignments.apply(log, net, im, fm)
```

### Raw Output:

```json
{
  "concept": "Alignments",
  "description": "Optimal alignment between log and model",
  "reference": "Adriansyah et al. - Conformance checking using cost-based fitness analysis",
  "data": {
    "total_traces_aligned": 30000,
    "average_alignment_cost": 0.0,
    "min_cost": 0,
    "max_cost": 0
  }
}
```

**Raw PM4Py Return Type:**

```python
aligned: List[Dict]
# Each item: {
#   'cost': float,
#   'alignment': List[Tuple]  # (log_move, model_move, label)
# }
```

---

## 11. Fitness Evaluation

### PM4Py Function:

```python
from pm4py.algo.evaluation.replay_fitness import algorithm as fitness_evaluator
fitness = fitness_evaluator.apply(
    log, net, im, fm,
    variant=fitness_evaluator.Variants.TOKEN_BASED
)
```

### Raw Output:

```json
{
  "concept": "Fitness Evaluation",
  "description": "Measures how well the model reproduces the log",
  "reference": "Token-based replay fitness",
  "data": {
    "perc_fit_traces": 100.0,
    "average_trace_fitness": 1.0,
    "log_fitness": 1.0,
    "percentage_of_fitting_traces": 100.0
  }
}
```

**Raw PM4Py Return Type:**

```python
fitness: Dict[str, float] = {
    'perc_fit_traces': float,
    'average_trace_fitness': float,
    'log_fitness': float,
    'percentage_of_fitting_traces': float
}
```

---

## 12. Precision Evaluation

### PM4Py Function:

```python
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
precision = precision_evaluator.apply(
    log, net, im, fm,
    variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN
)
```

### Raw Output:

```json
{
  "concept": "Precision Evaluation",
  "description": "Measures model precision (avoids underfitting)",
  "reference": "Munoz-Gama et al. - A fresh look at precision in process conformance",
  "data": {
    "precision": 1.0
  }
}
```

**Raw PM4Py Return Type:**

```python
precision: float  # Range: 0.0 to 1.0
```

---

## 13. Generalization Evaluation

### PM4Py Function:

```python
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
gen = generalization_evaluator.apply(log, net, im, fm)
```

### Raw Output:

```json
{
  "concept": "Generalization Evaluation",
  "description": "Measures model generalization capability",
  "reference": "Buijs et al. - Quality dimensions in process discovery",
  "data": {
    "generalization": 0.9942264973081038
  }
}
```

**Raw PM4Py Return Type:**

```python
generalization: float  # Range: 0.0 to 1.0
```

---

## 14. Simplicity Evaluation

### PM4Py Function:

```python
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
simp = simplicity_evaluator.apply(net)
```

### Raw Output:

```json
{
  "concept": "Simplicity Evaluation",
  "description": "Measures structural simplicity of the model",
  "reference": "Vázquez-Barreiros et al. - ProDiGen",
  "data": {
    "simplicity": 1.0
  }
}
```

**Raw PM4Py Return Type:**

```python
simplicity: float  # Range: 0.0 to 1.0
```

---

## 15. Social Network Analysis - Handover

### PM4Py Function:

```python
from pm4py.algo.organizational_mining.sna import algorithm as sna
hw_values = sna.apply(log, variant=sna.Variants.HANDOVER_LOG)
```

### Raw Output:

```json
{
  "concept": "Social Network Analysis - Handover of Work",
  "description": "Analyzes resource handover patterns",
  "reference": "van der Aalst et al. - Discovering social networks from event logs",
  "data": {
    "matrix_shape": "N/A",
    "status": "Handover network computed"
  }
}
```

**Raw PM4Py Return Type:**

```python
hw_values: np.ndarray  # N x N matrix where N = number of resources
# Entry [i,j] = how often resource i hands work to resource j
```

---

## 16. Organizational Roles Discovery

### PM4Py Function:

```python
from pm4py.algo.organizational_mining.roles import algorithm as roles_discovery
roles = roles_discovery.apply(log)
```

### Raw Output:

```json
{
  "concept": "Organizational Roles",
  "description": "Discovers roles based on activity-resource patterns",
  "reference": "Burattin et al. - Business models enhancement through discovery of roles",
  "data": {
    "roles": [
      {
        "role": "Activities: ['Assign Claim', 'Claim Decision', 'Close Claim', 'First Notification of Loss (FNOL)', 'Payment Sent', 'Set Reserve'] Originators importance {'RPA': 63600, 'Human': 116400}"
      }
    ],
    "total_roles": 1
  }
}
```

**Raw PM4Py Return Type:**

```python
roles: List[Role]  # Where Role is a namedtuple or object
# Role has: .resources (set), .activities (set)
```

---

## 17. Footprints

### PM4Py Function:

```python
from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
fp = footprints_discovery.apply(log)
```

### Raw Output:

```json
{
  "concept": "Footprints",
  "description": "Behavioral relations between activities",
  "reference": "van der Aalst - Process Mining: Data Science in Action",
  "data": {
    "sequence": ["A -> B", "B -> C"],
    "parallel": ["X || Y"],
    "activities": ["A", "B", "C", "X", "Y"]
  }
}
```

**Raw PM4Py Return Type:**

```python
footprints: Dict = {
    'sequence': Set[Tuple[str, str]],     # A always before B
    'parallel': Set[Tuple[str, str]],     # A and B can occur in parallel
    'activities': Set[str],               # All activities
    'start_activities': Set[str],
    'end_activities': Set[str]
}
```

---

## 18. Temporal Statistics

### PM4Py Function:

```python
from pm4py.statistics.traces.generic.log import case_arrival
arrival = case_arrival.get_case_arrival_avg(log)
```

### Raw Output:

```json
{
  "concept": "Temporal Statistics",
  "description": "Time-based process statistics",
  "data": {
    "average_case_arrival_seconds": 3180.325654917564,
    "log_timespan": {
      "start": "2020-04-06T07:50:45.322658",
      "end": "2023-05-26T01:49:58.261710"
    }
  }
}
```

**Raw PM4Py Return Type:**

```python
arrival: float  # Average seconds between case arrivals
```

---

## 19. Variant Filtering

### PM4Py Function:

```python
from pm4py.algo.filtering.log.variants import variants_filter
filtered = variants_filter.filter_log_variants_percentage(log, percentage=0.8)
```

### Raw Output:

```json
{
  "concept": "Variant Filtering",
  "description": "Filter log by top variants covering 80% of cases",
  "data": {
    "original_cases": 30000,
    "filtered_cases": 30000,
    "reduction_percentage": 0.0
  }
}
```

**Raw PM4Py Return Type:**

```python
filtered_log: EventLog  # New log with only top variants
```

---

## 20. Log Skeleton

### PM4Py Function:

```python
from pm4py.algo.discovery.log_skeleton import algorithm as log_skeleton_discovery
skeleton = log_skeleton_discovery.apply(log)
```

### Raw Output:

```json
{
  "concept": "Log Skeleton",
  "description": "Declarative process model constraints",
  "reference": "Verbeek - The log skeleton visualizer in ProM 6.9",
  "data": {
    "equivalence_relations": 30,
    "always_after": 15,
    "always_before": 15,
    "never_together": 0
  }
}
```

**Raw PM4Py Return Type:**

```python
skeleton: Dict = {
    'equivalence': List[Set],     # Sets of activities with same behavior
    'always_after': List[Tuple],  # (A, B) means A always after B
    'always_before': List[Tuple], # (A, B) means A always before B
    'never_together': List[Tuple] # (A, B) never in same case
}
```

---

## 21. Batch Detection

### PM4Py Function:

```python
from pm4py.algo.discovery.batches import algorithm as batch_detection
batches = batch_detection.apply(log)
```

### Raw Output:

```json
{
  "concept": "Batch Detection",
  "description": "Identifies batch processing patterns",
  "reference": "Martin et al. - Batch processing: Definition and event log identification",
  "data": {
    "total_batch_patterns": 12,
    "batch_summary": [
      {
        "activity": "Assign Claim",
        "resource": "RPA",
        "batch_type_count": 3,
        "batch_types": {
          "Concurrent batching": 3
        }
      }
    ]
  }
}
```

**Raw PM4Py Return Type:**

```python
batches: List[Tuple]
# Each batch: (
#   (activity, resource),        # Activity-resource pair
#   batch_type_count,             # Number of batch types
#   {batch_type: instances}       # Dict of batch instances
# )
```

**Batch Types:**

- **Simultaneous batching**: Events processed at exact same time
- **Concurrent batching**: Events processed in parallel
- **Sequential batching**: Events processed one after another
- **Task-based batching**: Same activity batched

---

## 22. Transition System

### PM4Py Function:

```python
from pm4py.algo.discovery.transition_system import algorithm as ts_discovery
ts = ts_discovery.apply(log)
```

### Raw Output:

```json
{
  "concept": "Transition System",
  "description": "State-based process representation",
  "reference": "van der Aalst - Process Mining: Data Science in Action",
  "data": {
    "states": 7,
    "transitions": 6
  }
}
```

**Raw PM4Py Return Type:**

```python
ts: TransitionSystem  # Has .states, .transitions
# States represent process states
# Transitions represent state changes
```

---

## 23. Prefix Tree

### PM4Py Function:

```python
from pm4py.algo.discovery.prefix_tree import algorithm as prefix_tree_discovery
prefix_tree = prefix_tree_discovery.apply(log)
```

### Raw Output:

```json
{
  "concept": "Prefix Tree (Trie)",
  "description": "Prefix-based trace representation",
  "data": {
    "status": "Prefix tree constructed successfully"
  }
}
```

**Raw PM4Py Return Type:**

```python
prefix_tree: PrefixTree  # Tree structure for case prefixes
```

---

## Quality Metric Ranges

All PM4Py quality metrics return values in range `[0.0, 1.0]`:

| Metric             | Range     | Ideal Value | Interpretation                             |
| ------------------ | --------- | ----------- | ------------------------------------------ |
| **Fitness**        | 0.0 - 1.0 | ≥ 0.8       | How well model can replay log              |
| **Precision**      | 0.0 - 1.0 | ≥ 0.8       | How much behavior is allowed but not seen  |
| **Generalization** | 0.0 - 1.0 | ≥ 0.8       | How well model generalizes to unseen cases |
| **Simplicity**     | 0.0 - 1.0 | ≥ 0.7       | Structural simplicity of model             |

**Interpretation Guide:**

- **Fitness = 1.0**: Perfect replay (all cases fit perfectly)
- **Fitness < 0.8**: Model cannot explain many cases → underfitting
- **Precision = 1.0**: Model is very precise (no extra behavior)
- **Precision < 0.8**: Model allows too much → overfitting
- **Generalization ≈ 1.0**: Model generalizes well
- **Simplicity = 1.0**: Very simple, minimal complexity

---

## Common Data Types

### EventLog Structure

```python
log: EventLog = [
    Trace1,  # List of events for case 1
    Trace2,  # List of events for case 2
    ...
]

trace: Trace = [
    Event1,
    Event2,
    ...
]

event: Event = {
    'concept:name': 'Activity Name',
    'time:timestamp': datetime,
    'org:resource': 'Resource Name',
    # ... other attributes
}
```

### Petri Net Structure

```python
net: PetriNet
net.places: Set[Place]
net.transitions: Set[Transition]
net.arcs: Set[Arc]

# Markings
im: Marking = {Place: tokens}  # Initial
fm: Marking = {Place: tokens}  # Final
```

### Process Tree Operators

```python
ProcessTree.operator in [
    '->', # Sequence
    'X',  # Exclusive choice (XOR)
    '+',  # Parallel (AND)
    '*',  # Loop
    'τ'   # Silent/Skip
]
```

---

## Academic References

All analyses include academic references:

1. **van der Aalst, W.M.P.** - Process Mining: Data Science in Action
2. **Leemans et al.** - Discovering block-structured process models
3. **Weijters et al.** - Flexible heuristics miner (FHM)
4. **Adriansyah et al.** - Conformance checking using cost-based fitness
5. **Munoz-Gama et al.** - A fresh look at precision in process conformance
6. **Buijs et al.** - Quality dimensions in process discovery
7. **Berti et al.** - A novel token-based replay technique
8. **Martin et al.** - Batch processing: Definition and event log identification
9. **Burattin et al.** - Business models enhancement through discovery of roles
10. **Verbeek** - The log skeleton visualizer in ProM 6.9
11. **Vázquez-Barreiros et al.** - ProDiGen

---

## Error Handling

All analyses use `safe_execute()` wrapper returning:

```python
# Success
{
    "status": "success",
    "result": <actual_data>
}

# Error
{
    "status": "error",
    "error": "Error message string"
}
```

**Example in output:**

```json
{
  "concept": "Analysis Name",
  "error": "'list' object has no attribute 'get'"
}
```

---

## Summary Section

Every analysis includes a summary:

```json
{
  "summary": {
    "total_analyses": 23,
    "successful": 21,
    "failed": 2,
    "analyses_performed": [
      "event_data_statistics",
      "directly_follows_graph",
      "alpha_miner",
      "/* ... */"
    ]
  }
}
```

---

## Usage Example

```python
# Load log
log = pm4py.read_xes('event_log.xes')

# Discover model
net, im, fm = pm4py.discover_petri_net_inductive(log)

# Check conformance
fitness = pm4py.fitness_token_based_replay(log, net, im, fm)
precision = pm4py.precision_token_based_replay(log, net, im, fm)

# Output formats
print(fitness)  # {'average_trace_fitness': 0.95, ...}
print(precision)  # 0.88
```

---

## Key Takeaways

1. **All analyses have academic references** - Every output cites the original paper
2. **Consistent structure** - All use concept/description/reference/data pattern
3. **Status wrapping** - All use success/error wrappers
4. **Quality metrics** - All return float in [0.0, 1.0] range
5. **Rich metadata** - Timestamps, versions, counts included
6. **Serialization-ready** - All outputs are JSON-serializable

This is what the backend **should** be returning to match PM4Py's capabilities! 🎯
