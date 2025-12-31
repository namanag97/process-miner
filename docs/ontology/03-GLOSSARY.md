# Glossary — Business Definitions for Domain Terms

> **ATLAS Ontological Analysis**  
> Generated: 2025-12-31  
> System: Process Mining SaaS Platform

---

## Core Domain Concepts

### Event Log

```yaml
business_definition: |
  A chronological record of activities that occurred during the execution of 
  business processes. Each event log captures "what happened, when, by whom, 
  and in what context" across multiple process instances (cases).

technical_definition: |
  A structured dataset containing events grouped by case identifiers. Stored 
  in the `event_logs` table with computed statistics. Can be ingested from 
  CSV or XES files. Supports filtering to create derived logs.

examples:
  - "Order-to-Cash process log with 10,000 orders over 6 months"
  - "IT Incident Management log from ServiceNow export"
  - "Patient journey log from hospital information system"

anti_patterns:
  - "Not a document or file — it's processed data from a file"
  - "Not a single trace — contains multiple process instances"

synonyms:
  - "Process Log"
  - "Activity Log"
  - "Transaction Log"
  - "Audit Trail"
```

### Process Case

```yaml
business_definition: |
  A single instance of a business process from start to finish. Represents 
  one complete journey through the process (e.g., one customer order, one 
  patient visit, one IT ticket).

technical_definition: |
  A record in `process_cases` table that groups related events by their 
  `case_id`. Contains computed fields for `start_time`, `end_time`, and 
  `variant_key` (activity sequence hash).

examples:
  - "Order #12345 from placement to delivery"
  - "Loan application APP-2024-001 from submission to decision"
  - "Support ticket INC-999 from creation to resolution"

anti_patterns:
  - "Not an individual event — a case contains multiple events"
  - "Not a customer — cases are process instances, not actors"

synonyms:
  - "Trace"
  - "Process Instance"
  - "Case"
  - "Transaction"
```

### Process Event

```yaml
business_definition: |
  A single activity occurrence within a process instance. Records what 
  happened, when it happened, and optionally who performed it.

technical_definition: |
  A row in `process_events` table with required `activity`, `timestamp`, 
  and optional `resource`. Linked to a `ProcessCase` via `case_ref_id`. 
  Additional attributes stored in `attributes_json`.

examples:
  - "Create Order at 2024-01-15 09:23:45 by John Smith"
  - "Approve Invoice at 2024-03-20 14:00:00 by System"
  - "Send Notification at 2024-02-28 11:15:30"

anti_patterns:
  - "Not a scheduled task — it's a recorded occurrence"
  - "Not a state — it's an action that occurred"

synonyms:
  - "Activity Instance"
  - "Log Entry"
  - "Action"
```

### Activity

```yaml
business_definition: |
  A distinct type of work or task that can occur in a process. Represents 
  "what" happens, independent of when or by whom.

technical_definition: |
  A unique string value in the `ProcessEvent.activity` column. Aggregated 
  into `EventLog.activities_json` for quick access. Used for DFG nodes 
  and variant analysis.

examples:
  - "Create Order"
  - "Send Invoice"
  - "Approve Request"
  - "Close Ticket"

anti_patterns:
  - "Not an event — activities are types, events are instances"
  - "Not a role — activities are tasks, not job functions"

synonyms:
  - "Task"
  - "Step"
  - "Action Type"
```

### Variant

```yaml
business_definition: |
  A unique sequence of activities that cases follow through the process.
  Cases with the same activity sequence belong to the same variant,
  regardless of timing or resources.

technical_definition: |
  Identified by `variant_key` (hash of activity sequence). Computed by
  PM4Py's `get_variants` function. Displayed as "A → B → C" activity
  trace format.

examples:
  - "Create Order → Pick Items → Ship → Close" (happy path)
  - "Create Order → Cancel Order" (early termination)
  - "Create Order → Pick Items → Return Items → Pick Items → Ship → Close" (rework)

anti_patterns:
  - "Not a version — variants are execution paths, not releases"
  - "Not configurable — variants are discovered from data"

synonyms:
  - "Trace Variant"
  - "Execution Path"
  - "Process Path"
```

---

## Process Discovery Concepts

### Process Model

```yaml
business_definition: |
  A formal representation of how a business process works, discovered 
  from event log data. Shows the flow of activities, decision points, 
  and parallelism.

technical_definition: |
  Stored in `process_models` table with `serialized_model` (pickled PM4Py 
  object). Format determined by `model_format` enum. Quality measured by 
  `fitness` and `precision` scores.

examples:
  - Petri Net discovered from Order-to-Cash log
  - BPMN model generated from Inductive Miner
  - Process Tree from Inductive Miner Infrequent

anti_patterns:
  - "Not a manual specification — it's discovered from data"
  - "Not the 'true' process — it's an approximation based on observed behavior"

synonyms:
  - "Discovered Model"
  - "Process Map"
  - "Workflow Model"
```

### Directly-Follows Graph (DFG)

```yaml
business_definition: |
  A visual representation showing which activities directly follow each 
  other in the process. The simplest form of process visualization, 
  showing frequency and flow patterns.

technical_definition: |
  Computed by PM4Py's DFG discovery. Returns nodes (activities) and 
  edges (transitions) with frequency counts. Optionally includes 
  performance metrics (avg/min/max duration per edge).

examples:
  - DFG showing "Create Order" is followed by "Pick Items" 8,500 times
  - Performance DFG showing average time between activities

anti_patterns:
  - "Not a formal model — DFGs don't guarantee soundness"
  - "Not a control flow — parallel activities may appear sequential"

synonyms:
  - "Frequency Graph"
  - "Process Graph"
  - "Activity Flow"
```

### Petri Net

```yaml
business_definition: |
  A formal mathematical model representing process flow using places 
  (states), transitions (activities), and tokens (process instances). 
  Enables rigorous analysis of process behavior.

technical_definition: |
  PM4Py object with `PetriNet`, `initial_marking`, and `final_marking`. 
  Discovered by Alpha, Inductive, or Heuristics miners. Visualized as 
  SVG with places (circles), transitions (rectangles), and arcs.

examples:
  - Sound Petri net from Inductive Miner
  - Petri net with deadlock from Alpha Miner on noisy data

anti_patterns:
  - "Not a flowchart — Petri nets have formal semantics"
  - "Not human-designed — discovered automatically"

synonyms:
  - "Place/Transition Net"
  - "Workflow Net"
```

### Mining Algorithm

```yaml
business_definition: |
  A computational method for discovering process models from event logs. 
  Different algorithms have different strengths for handling noise, 
  complexity, and specific process patterns.

technical_definition: |
  Enumerated in `MinerType`: alpha, alpha_plus, inductive, inductive_infrequent, 
  heuristics, dfg. Implemented in `MiningService` using PM4Py library functions.

examples:
  - "Alpha Miner — classic, struggles with noise"
  - "Inductive Miner — recommended, produces sound models"
  - "Heuristics Miner — handles noise well, may produce unsound models"

anti_patterns:
  - "Not a data mining algorithm — specifically for process mining"
  - "Not supervised learning — discovers structure without labels"

synonyms:
  - "Discovery Algorithm"
  - "Process Discovery Method"
```

---

## Conformance & Quality Concepts

### Fitness

```yaml
business_definition: |
  A measure of how well the observed behavior in the event log 
  can be replayed by the process model. High fitness means the 
  model allows most of the observed traces.

technical_definition: |
  Computed via token replay or alignment. Stored in `ProcessModel.fitness` 
  and `ConformanceResult.fitness`. Range 0.0-1.0 where 1.0 is perfect fit.

examples:
  - "Fitness of 0.95 — 95% of tokens successfully replayed"
  - "Fitness of 0.70 — significant deviations from model"

anti_patterns:
  - "High fitness doesn't mean good model — overfitting is possible"
  - "Not accuracy — it's about behavior coverage"

synonyms:
  - "Replay Fitness"
  - "Log Fitness"
```

### Precision

```yaml
business_definition: |
  A measure of how precisely the model describes the observed behavior. 
  High precision means the model doesn't allow much behavior that wasn't 
  observed in the log.

technical_definition: |
  Computed using escaping edges or alignments. Stored in `ProcessModel.precision` 
  and `ConformanceResult.precision`. Range 0.0-1.0. Requires more computation 
  than fitness.

examples:
  - "Precision of 0.90 — model is specific to observed behavior"
  - "Precision of 0.50 — model allows many unobserved paths"

anti_patterns:
  - "High precision doesn't mean good model — underfitting is possible"
  - "Trade-off with fitness — improving one may hurt the other"

synonyms:
  - "Behavioral Precision"
  - "Model Precision"
```

### Deviation

```yaml
business_definition: |
  A discrepancy between the expected process behavior (model) and the 
  actual observed behavior (event log). Indicates where reality differs 
  from the design.

technical_definition: |
  Detected by `ConformanceService.detect_deviations()`. Types include 
  `missing_activity`, `wrong_order`, `extra_activity`. Returned with 
  case_id, activity, expected_after, frequency, and impact severity.

examples:
  - "Activity 'Credit Check' missing in 15% of cases"
  - "Activity 'Ship' occurred before 'Pack' in 200 cases"
  - "Unexpected activity 'Manual Override' in 50 cases"

anti_patterns:
  - "Not always bad — deviations may be valid exceptions"
  - "Not root cause — deviations are symptoms"

synonyms:
  - "Non-Conformance"
  - "Violation"
  - "Exception"
```

---

## Analytics Concepts

### Bottleneck

```yaml
business_definition: |
  An activity or transition in the process that causes delays, limiting 
  overall process throughput. Characterized by high waiting times relative 
  to service times.

technical_definition: |
  Detected by `AnalyticsService.detect_bottlenecks()`. Bottleneck if 
  waiting_time > service_time * threshold. Returns severity (low/medium/high), 
  impact_score, preceding/following activities.

examples:
  - "Manager Approval — avg wait 5 days, high impact score"
  - "Quality Check — creates queue of 50 items"

anti_patterns:
  - "Not the slowest activity — bottleneck is about flow, not duration"
  - "Not always fixable — may be a resource constraint"

synonyms:
  - "Constraint"
  - "Delay Point"
  - "Queue Point"
```

### Rework

```yaml
business_definition: |
  When an activity is executed multiple times within the same case, 
  indicating repetition, correction, or loop in the process. Often 
  signals quality issues or process inefficiencies.

technical_definition: |
  Detected by `AnalyticsService.analyze_rework()`. Counts activities 
  appearing more than once per case. Reports rework_count, cases_with_rework, 
  rework_percentage.

examples:
  - "Review Document — appears 3 times in 20% of cases"
  - "Data Entry — repeated due to validation failures"

anti_patterns:
  - "Not always bad — some loops are intentional (approval cycles)"
  - "Not same as variant — rework is within a case"

synonyms:
  - "Loop"
  - "Repeat"
  - "Iteration"
```

### Cycle Time

```yaml
business_definition: |
  The total elapsed time from start to finish of a process case. 
  Measures how long it takes to complete the entire process, 
  including waiting and processing time.

technical_definition: |
  Computed by `AnalyticsService.get_cycle_time()` as difference 
  between max and min timestamps per case. Returns min, max, avg, 
  median, and percentiles (25th, 75th, 95th).

examples:
  - "Average cycle time: 12 days"
  - "95th percentile: 45 days (5% of cases take longer)"

anti_patterns:
  - "Not processing time — includes waiting"
  - "Not lead time — typically same in process mining context"

synonyms:
  - "Case Duration"
  - "End-to-End Time"
  - "Throughput Time"
```

### Throughput

```yaml
business_definition: |
  The rate at which cases are completed through the process. 
  Measures process capacity and productivity over time.

technical_definition: |
  Computed by `AnalyticsService.get_throughput()`. Returns 
  cases_per_day, cases_per_week, cases_per_month based on 
  event log time range.

examples:
  - "150 orders processed per day"
  - "Weekly throughput increased by 20% after optimization"

anti_patterns:
  - "Not same as arrivals — throughput is completed cases"
  - "High throughput with low quality defeats the purpose"

synonyms:
  - "Volume"
  - "Capacity"
  - "Processing Rate"
```

---

## Organizational Concepts

### Resource

```yaml
business_definition: |
  A person, system, or entity that performs activities in the process. 
  Resources are the "who" or "what" that executes work.

technical_definition: |
  Optional field in `ProcessEvent.resource`. Extracted from event log 
  column mapping. Used for organizational mining and resource analytics.

examples:
  - "John Smith (employee)"
  - "API Gateway (system)"
  - "Customer Service Team (group)"

anti_patterns:
  - "Not a role — resources are specific entities"
  - "Not required — many logs don't have resource data"

synonyms:
  - "Actor"
  - "Performer"
  - "Agent"
```

### Handover

```yaml
business_definition: |
  When work transfers from one resource to another within the same case. 
  Handovers represent collaboration and potential communication points.

technical_definition: |
  Discovered by `OrganizationalService.discover_handover_network()`. 
  Counts consecutive events with different resources. Returns directed 
  graph with resources as nodes and handover frequency as edge weights.

examples:
  - "Sales → Operations handover occurs 500 times"
  - "High handover frequency may indicate silos"

anti_patterns:
  - "Not same as delegation — handovers are discovered, not assigned"
  - "More handovers isn't always bad — collaboration is needed"

synonyms:
  - "Work Transfer"
  - "Hand-off"
  - "Transition"
```

---

## Prediction Concepts

### Predictor

```yaml
business_definition: |
  A machine learning model trained on historical process data to 
  predict future outcomes for in-progress cases.

technical_definition: |
  Stored in `prediction_models` table. Trained by `PredictionService` 
  using scikit-learn/XGBoost. Supports `next_activity` and `remaining_time` 
  prediction targets.

examples:
  - "Next Activity Predictor with 85% accuracy"
  - "Remaining Time Predictor with MAE of 2 days"

anti_patterns:
  - "Not process model — predictors are ML models, not process models"
  - "Not prescriptive — predictors don't recommend actions"

synonyms:
  - "Prediction Model"
  - "ML Model"
```

### Case Prefix

```yaml
business_definition: |
  The sequence of activities that have already occurred in an in-progress 
  case. Used as input for predicting what happens next.

technical_definition: |
  List of activity strings passed to `PredictionService.predict_*()` 
  methods. One-hot encoded into feature vector for ML model input.

examples:
  - "['Create Order', 'Pick Items']"
  - "['Submit Application', 'Credit Check', 'Request Documents']"

anti_patterns:
  - "Not a variant — prefix is partial, variant is complete"
  - "Not fixed length — prefixes grow as case progresses"

synonyms:
  - "Partial Trace"
  - "Activity History"
```

---

## Infrastructure Concepts

### Project

```yaml
business_definition: |
  An organizational container for grouping related event logs, 
  models, and analyses. Helps users organize their process mining 
  work by business domain or initiative.

technical_definition: |
  Aggregate root in `projects` table. Contains `event_logs` via 
  optional foreign key. Tracks `total_files` and `total_analyses` 
  for quick statistics.

examples:
  - "Q1 2024 Order Process Analysis"
  - "IT Service Management Improvement"

anti_patterns:
  - "Not a workspace — projects are data containers"
  - "Not required — event logs can exist without projects"

synonyms:
  - "Analysis Project"
  - "Workspace"
  - "Folder"
```

### Workflow (Pipeline)

```yaml
business_definition: |
  An automated sequence of process mining operations that can be 
  executed on event logs. Enables repeatable, scheduled analysis.

technical_definition: |
  Stored in `workflows` table with `steps_json` defining the pipeline. 
  Executions tracked in `workflow_runs`. Supports cron-based scheduling.

examples:
  - "Daily Discovery Pipeline — upload → discover → check conformance"
  - "Weekly Performance Report — analyze bottlenecks → export"

anti_patterns:
  - "Not a process model — workflows automate analysis, not business processes"
  - "Not real-time — workflows run on-demand or scheduled"

synonyms:
  - "Pipeline"
  - "Automation"
  - "Analysis Workflow"
```
