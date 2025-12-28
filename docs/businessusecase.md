# Process Mining SaaS - Web Application

## Complete Business Activities & Use Cases

---

# SECTION 1: USE CASE CATEGORIES

## 1.1 Core Process Mining Use Cases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROCESS MINING USE CASE TAXONOMY                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  DISCOVERY   │  │ CONFORMANCE  │  │ ENHANCEMENT  │  │  AUTOMATION  │    │
│  │              │  │              │  │              │  │              │    │
│  │ • Process    │  │ • Compliance │  │ • Performance│  │ • RPA        │    │
│  │   Discovery  │  │   Checking   │  │   Analysis   │  │   Discovery  │    │
│  │ • Variant    │  │ • Deviation  │  │ • Bottleneck │  │ • Workflow   │    │
│  │   Analysis   │  │   Detection  │  │   Detection  │  │   Automation │    │
│  │ • Path       │  │ • Audit      │  │ • Resource   │  │ • Intelligent│    │
│  │   Exploration│  │   Support    │  │   Optimization│  │   Routing   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  MONITORING  │  │  PREDICTION  │  │   SOCIAL/ORG │  │  OBJECT-     │    │
│  │              │  │              │  │              │  │  CENTRIC     │    │
│  │ • Real-time  │  │ • Outcome    │  │ • Org Mining │  │ • Multi-obj  │    │
│  │   Dashboards │  │   Prediction │  │ • Handover   │  │   Analysis   │    │
│  │ • KPI        │  │ • Duration   │  │   Analysis   │  │ • Object     │    │
│  │   Tracking   │  │   Forecast   │  │ • Role       │  │   Lifecycle  │    │
│  │ • Alerting   │  │ • Risk       │  │   Discovery  │  │ • Interaction│    │
│  │              │  │   Assessment │  │              │  │   Patterns   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# SECTION 2: COMPLETE BUSINESS ACTIVITIES BY USE CASE

## 2.1 PROCESS DISCOVERY USE CASE

### Purpose

Automatically discover how processes actually execute based on event data, revealing the real process rather than the documented one.

### Actor: Process Analyst

### Business Activities

| Activity ID | Business Activity                  | Description                         | Input                | Output               | PM4PY Mapping                  |
| ----------- | ---------------------------------- | ----------------------------------- | -------------------- | -------------------- | ------------------------------ |
| DIS-001     | **Upload Event Log**               | Import process execution data       | File (XES/CSV/OCEL)  | Parsed EventLog      | `read_xes()`, `read_csv()`     |
| DIS-002     | **Configure Column Mapping**       | Map CSV columns to event attributes | Column mappings      | Configured schema    | Manual mapping                 |
| DIS-003     | **Validate Data Quality**          | Check for missing/invalid data      | EventLog             | Quality report       | Custom validation              |
| DIS-004     | **Preview Event Data**             | View sample of imported events      | EventLog             | Data preview         | DataFrame preview              |
| DIS-005     | **Select Discovery Algorithm**     | Choose appropriate miner            | Algorithm choice     | Selected algorithm   | Algorithm selection            |
| DIS-006     | **Configure Algorithm Parameters** | Set thresholds and options          | Parameters           | Configured algorithm | Algorithm params               |
| DIS-007     | **Execute Discovery**              | Run discovery algorithm             | EventLog + Algorithm | Process Model        | `discover_*()`                 |
| DIS-008     | **View Process Model**             | Display discovered model            | Process Model        | Visualization        | `view_*()`                     |
| DIS-009     | **Adjust Model Complexity**        | Simplify/detail the model           | Thresholds           | Filtered model       | Filtering params               |
| DIS-010     | **Annotate with Frequency**        | Add frequency counts to model       | EventLog + Model     | Annotated model      | Frequency annotation           |
| DIS-011     | **Annotate with Performance**      | Add timing data to model            | EventLog + Model     | Annotated model      | Performance annotation         |
| DIS-012     | **Compare Discovery Results**      | Compare different algorithms        | Multiple models      | Comparison view      | Model comparison               |
| DIS-013     | **Export Process Model**           | Download model file                 | Process Model        | BPMN/PNML file       | `write_bpmn()`, `write_pnml()` |
| DIS-014     | **Save Discovery Session**         | Persist analysis state              | Session data         | Saved session        | Application state              |
| DIS-015     | **Share Discovery Results**        | Share with team members             | Model + permissions  | Shared access        | Sharing service                |

### User Journey Flow

```
Upload Log → Validate → Configure → Discover → View → Refine → Annotate → Export/Share
```

---

## 2.2 VARIANT ANALYSIS USE CASE

### Purpose

Identify and analyze different execution paths (variants) through a process to understand process behavior diversity.

### Actor: Process Analyst, Business Manager

### Business Activities

| Activity ID | Business Activity                | Description                        | Input                  | Output             | PM4PY Mapping          |
| ----------- | -------------------------------- | ---------------------------------- | ---------------------- | ------------------ | ---------------------- |
| VAR-001     | **Extract Variants**             | Identify unique execution paths    | EventLog               | Variant list       | `get_variants()`       |
| VAR-002     | **View Variant Distribution**    | See frequency of each variant      | Variants               | Distribution chart | Statistics viz         |
| VAR-003     | **Sort Variants by Frequency**   | Order by occurrence count          | Variants               | Sorted list        | Sorting                |
| VAR-004     | **Sort Variants by Performance** | Order by duration                  | Variants               | Sorted list        | Performance stats      |
| VAR-005     | **Filter Top Variants**          | Focus on most common paths         | Variants + threshold   | Filtered variants  | `filter_variants()`    |
| VAR-006     | **Compare Variant Paths**        | Side-by-side variant comparison    | Selected variants      | Comparison view    | Custom viz             |
| VAR-007     | **Visualize Single Variant**     | Show variant as process flow       | Single variant         | Flow visualization | DFG per variant        |
| VAR-008     | **Identify Happy Path**          | Find most efficient variant        | Variants + performance | Best variant       | Analysis               |
| VAR-009     | **Detect Deviation Variants**    | Find non-standard paths            | Variants + reference   | Deviation list     | Comparison             |
| VAR-010     | **Calculate Variant Statistics** | Compute duration, cost per variant | Variants               | Statistics table   | `get_case_durations()` |
| VAR-011     | **Group Variants by Pattern**    | Cluster similar variants           | Variants               | Grouped variants   | Clustering             |
| VAR-012     | **Export Variant Report**        | Download variant analysis          | Analysis results       | PDF/Excel report   | Report generation      |
| VAR-013     | **Create Variant Alert**         | Notify on new/unusual variants     | Alert config           | Active alert       | Alerting service       |
| VAR-014     | **Drill Down to Cases**          | View cases for specific variant    | Variant                | Case list          | Filtering              |
| VAR-015     | **Tag Variant Category**         | Label variants (happy, exception)  | Variant + tag          | Tagged variant     | Metadata               |

---

## 2.3 CONFORMANCE CHECKING USE CASE

### Purpose

Compare actual process execution against a reference model to identify deviations, ensure compliance, and measure alignment.

### Actor: Compliance Officer, Process Analyst, Auditor

### Business Activities

| Activity ID | Business Activity                 | Description                        | Input              | Output               | PM4PY Mapping                 |
| ----------- | --------------------------------- | ---------------------------------- | ------------------ | -------------------- | ----------------------------- |
| CON-001     | **Select Reference Model**        | Choose model to check against      | Model list         | Selected model       | Model selection               |
| CON-002     | **Import Reference Model**        | Upload external reference model    | BPMN/PNML file     | Imported model       | `read_bpmn()`, `read_pnml()`  |
| CON-003     | **Select Event Log**              | Choose log to analyze              | Log list           | Selected log         | Log selection                 |
| CON-004     | **Choose Conformance Method**     | Select checking algorithm          | Method options     | Selected method      | Algorithm choice              |
| CON-005     | **Configure Check Parameters**    | Set cost functions, thresholds     | Parameters         | Configured check     | Parameter config              |
| CON-006     | **Execute Conformance Check**     | Run conformance analysis           | Log + Model        | Conformance result   | `conformance_diagnostics_*()` |
| CON-007     | **View Fitness Score**            | Display overall fitness metric     | Result             | Fitness value        | `fitness_*()`                 |
| CON-008     | **View Precision Score**          | Display precision metric           | Result             | Precision value      | `precision_*()`               |
| CON-009     | **View Generalization Score**     | Display generalization metric      | Result             | Generalization value | Generalization calc           |
| CON-010     | **View Simplicity Score**         | Display model simplicity           | Model              | Simplicity value     | Simplicity calc               |
| CON-011     | **Identify Deviations**           | List all non-conforming activities | Result             | Deviation list       | Deviation extraction          |
| CON-012     | **Classify Deviation Types**      | Categorize deviations              | Deviations         | Classified list      | Classification                |
| CON-013     | **View Deviation Heatmap**        | Highlight deviations on model      | Model + deviations | Annotated model      | Heatmap viz                   |
| CON-014     | **Drill Down to Violations**      | See specific violation cases       | Deviation          | Case list            | Filtering                     |
| CON-015     | **Calculate Deviation Cost**      | Quantify impact of deviations      | Deviations + costs | Cost analysis        | Cost calculation              |
| CON-016     | **View Alignment Details**        | See move-by-move alignment         | Trace alignment    | Alignment viz        | `view_alignments()`           |
| CON-017     | **Compare Conformance Over Time** | Track conformance trends           | Historical results | Trend chart          | Time series                   |
| CON-018     | **Generate Compliance Report**    | Create audit documentation         | Results            | Compliance report    | Report generation             |
| CON-019     | **Set Conformance Threshold**     | Define acceptable deviation level  | Threshold value    | Active threshold     | Configuration                 |
| CON-020     | **Create Conformance Alert**      | Notify on threshold breach         | Alert config       | Active alert         | Alerting service              |
| CON-021     | **Export Conformance Evidence**   | Download for external audit        | Results            | Evidence package     | Export service                |
| CON-022     | **Schedule Regular Checks**       | Automate periodic conformance      | Schedule config    | Scheduled job        | Scheduler                     |

---

## 2.4 PERFORMANCE ANALYSIS USE CASE

### Purpose

Analyze timing, throughput, and efficiency of process execution to identify bottlenecks and optimization opportunities.

### Actor: Process Analyst, Operations Manager

### Business Activities

| Activity ID | Business Activity                | Description                       | Input                | Output           | PM4PY Mapping                 |
| ----------- | -------------------------------- | --------------------------------- | -------------------- | ---------------- | ----------------------------- |
| PER-001     | **Calculate Case Durations**     | Compute end-to-end times          | EventLog             | Duration list    | `get_case_durations()`        |
| PER-002     | **View Duration Distribution**   | Visualize timing spread           | Durations            | Histogram        | Duration viz                  |
| PER-003     | **Calculate Activity Durations** | Time per activity                 | EventLog             | Activity times   | `get_service_time()`          |
| PER-004     | **Calculate Waiting Times**      | Time between activities           | EventLog             | Wait times       | `get_sojourn_time()`          |
| PER-005     | **Identify Bottlenecks**         | Find slowest process points       | Performance data     | Bottleneck list  | Analysis                      |
| PER-006     | **View Performance Spectrum**    | Time-based activity visualization | EventLog             | Spectrum chart   | `view_performance_spectrum()` |
| PER-007     | **Annotate Model with Times**    | Add performance to process flow   | Model + times        | Annotated model  | Performance DFG               |
| PER-008     | **Compare Period Performance**   | Analyze across time periods       | EventLog + periods   | Comparison       | Time filtering                |
| PER-009     | **Calculate Throughput Rate**    | Cases per time unit               | EventLog             | Throughput value | `get_case_arrival_average()`  |
| PER-010     | **Identify Rework Loops**        | Find repetitive patterns          | EventLog             | Loop list        | Loop detection                |
| PER-011     | **Calculate Rework Cost**        | Quantify rework impact            | Loops + costs        | Cost value       | Calculation                   |
| PER-012     | **Filter by Performance**        | Focus on slow/fast cases          | EventLog + threshold | Filtered log     | `filter_case_performance()`   |
| PER-013     | **View Dotted Chart**            | Event distribution over time      | EventLog             | Dotted chart     | `view_dotted_chart()`         |
| PER-014     | **Detect Performance Drift**     | Identify timing changes           | EventLog             | Drift points     | Drift detection               |
| PER-015     | **Set Performance Baseline**     | Define target metrics             | Metrics              | Baseline config  | Configuration                 |
| PER-016     | **Compare to Baseline**          | Measure against targets           | Current + baseline   | Comparison       | Analysis                      |
| PER-017     | **Generate Performance Report**  | Create management summary         | Metrics              | Report           | Report generation             |
| PER-018     | **Create Performance Alert**     | Notify on SLA breach              | Alert config         | Active alert     | Alerting                      |
| PER-019     | **Calculate Path Performance**   | Time for specific paths           | Path + log           | Path duration    | `filter_paths_performance()`  |
| PER-020     | **Identify Fast Track Cases**    | Find expedited processes          | EventLog             | Fast cases       | Filtering                     |

---

## 2.5 BOTTLENECK DETECTION USE CASE

### Purpose

Identify process constraints, resource limitations, and flow restrictions that limit overall throughput.

### Actor: Operations Manager, Process Analyst

### Business Activities

| Activity ID | Business Activity                    | Description                        | Input               | Output            | PM4PY Mapping     |
| ----------- | ------------------------------------ | ---------------------------------- | ------------------- | ----------------- | ----------------- |
| BOT-001     | **Analyze Queue Times**              | Measure waiting between activities | EventLog            | Queue analysis    | Wait time calc    |
| BOT-002     | **Identify High-Wait Activities**    | Find activities with longest waits | Queue times         | Activity list     | Ranking           |
| BOT-003     | **Visualize Bottleneck Locations**   | Highlight constraints on model     | Model + analysis    | Annotated model   | Heatmap           |
| BOT-004     | **Calculate Resource Utilization**   | Measure resource load              | EventLog            | Utilization rates | Resource analysis |
| BOT-005     | **Identify Overloaded Resources**    | Find capacity constraints          | Utilization         | Resource list     | Filtering         |
| BOT-006     | **Analyze Batch Formation**          | Detect batching patterns           | EventLog            | Batch analysis    | Pattern detection |
| BOT-007     | **Calculate Throughput Impact**      | Quantify bottleneck effect         | Analysis            | Impact metrics    | Calculation       |
| BOT-008     | **Simulate Bottleneck Removal**      | What-if without constraint         | Simulation params   | Projected metrics | Simulation        |
| BOT-009     | **Prioritize Improvements**          | Rank bottlenecks by impact         | Bottleneck list     | Prioritized list  | Ranking           |
| BOT-010     | **Track Bottleneck Resolution**      | Monitor improvement progress       | Historical data     | Trend analysis    | Time series       |
| BOT-011     | **Compare Shift/Period Bottlenecks** | Analyze by time segment            | EventLog + segments | Comparison        | Segmentation      |
| BOT-012     | **Generate Bottleneck Report**       | Document constraints               | Analysis            | Report            | Report generation |

---

## 2.6 ROOT CAUSE ANALYSIS USE CASE

### Purpose

Investigate why deviations, delays, or issues occur by analyzing correlations and patterns in process data.

### Actor: Process Analyst, Quality Manager

### Business Activities

| Activity ID | Business Activity                | Description                     | Input                 | Output            | PM4PY Mapping        |
| ----------- | -------------------------------- | ------------------------------- | --------------------- | ----------------- | -------------------- |
| RCA-001     | **Define Investigation Scope**   | Select cases/issues to analyze  | Selection criteria    | Case subset       | Filtering            |
| RCA-002     | **Extract Case Attributes**      | Gather relevant case data       | Cases                 | Attribute table   | Attribute extraction |
| RCA-003     | **Correlate with Outcomes**      | Find attribute-outcome patterns | Attributes + outcomes | Correlations      | Statistical analysis |
| RCA-004     | **Identify Common Patterns**     | Find shared characteristics     | Problem cases         | Pattern list      | Pattern mining       |
| RCA-005     | **Compare Problem vs Normal**    | Contrast case populations       | Two case sets         | Comparison        | Comparative analysis |
| RCA-006     | **Analyze Resource Involvement** | Check resource correlation      | Cases + resources     | Resource analysis | SNA features         |
| RCA-007     | **Analyze Temporal Patterns**    | Check time-based correlations   | Cases + time          | Time patterns     | Temporal analysis    |
| RCA-008     | **Analyze Path Correlation**     | Check variant correlation       | Cases + variants      | Path analysis     | Variant analysis     |
| RCA-009     | **Build Decision Tree**          | ML-based cause identification   | Features + outcomes   | Decision rules    | ML features          |
| RCA-010     | **Validate Hypotheses**          | Test suspected causes           | Hypothesis + data     | Validation result | Statistical testing  |
| RCA-011     | **Document Root Causes**         | Record findings                 | Analysis results      | Documentation     | Note taking          |
| RCA-012     | **Generate RCA Report**          | Create formal analysis          | Findings              | Report            | Report generation    |
| RCA-013     | **Link to Improvement Actions**  | Connect causes to solutions     | Causes                | Action items      | Action tracking      |

---

## 2.7 ORGANIZATIONAL MINING USE CASE

### Purpose

Discover organizational structures, work patterns, handovers, and collaboration networks from process data.

### Actor: HR Manager, Process Analyst, Operations Manager

### Business Activities

| Activity ID | Business Activity                 | Description                      | Input            | Output                 | PM4PY Mapping                           |
| ----------- | --------------------------------- | -------------------------------- | ---------------- | ---------------------- | --------------------------------------- |
| ORG-001     | **Extract Resource List**         | Identify all participants        | EventLog         | Resource list          | Attribute extraction                    |
| ORG-002     | **Discover Handover Network**     | Find work transfer patterns      | EventLog         | Handover graph         | `discover_handover_of_work_network()`   |
| ORG-003     | **View Handover Visualization**   | Display handover network         | Network          | Interactive viz        | `view_sna()`                            |
| ORG-004     | **Discover Working Together**     | Find collaboration patterns      | EventLog         | Collaboration graph    | `discover_working_together_network()`   |
| ORG-005     | **Discover Subcontracting**       | Find delegation patterns         | EventLog         | Subcontracting graph   | `discover_subcontracting_network()`     |
| ORG-006     | **Discover Similar Activities**   | Find role similarities           | EventLog         | Similarity matrix      | `discover_similar_activities_network()` |
| ORG-007     | **Mine Organizational Roles**     | Identify functional groups       | EventLog         | Role clusters          | `discover_organizational_roles()`       |
| ORG-008     | **Calculate Resource Workload**   | Measure activity per resource    | EventLog         | Workload stats         | Activity counting                       |
| ORG-009     | **Identify Resource Bottlenecks** | Find overloaded resources        | Workload data    | Bottleneck list        | Analysis                                |
| ORG-010     | **Analyze Resource Performance**  | Compare resource efficiency      | EventLog         | Performance comparison | Performance stats                       |
| ORG-011     | **Detect Segregation of Duties**  | Check compliance rules           | EventLog + rules | Violations             | Rule checking                           |
| ORG-012     | **View Resource Timeline**        | Activity over time per resource  | EventLog         | Timeline chart         | Dotted chart variant                    |
| ORG-013     | **Compare Team Performance**      | Contrast team metrics            | Teams + metrics  | Comparison             | Comparative analysis                    |
| ORG-014     | **Identify Training Needs**       | Find skill gaps                  | Performance data | Recommendations        | Analysis                                |
| ORG-015     | **Generate Org Mining Report**    | Document organizational findings | Analysis         | Report                 | Report generation                       |

---

## 2.8 PREDICTIVE PROCESS MONITORING USE CASE

### Purpose

Predict future behavior of running cases including outcomes, remaining time, and next activities.

### Actor: Operations Manager, Process Analyst

### Business Activities

| Activity ID | Business Activity                | Description               | Input                 | Output              | PM4PY Mapping                  |
| ----------- | -------------------------------- | ------------------------- | --------------------- | ------------------- | ------------------------------ |
| PRD-001     | **Extract Training Features**    | Prepare ML dataset        | EventLog              | Feature matrix      | `extract_features_dataframe()` |
| PRD-002     | **Define Prediction Target**     | Specify what to predict   | Target choice         | Target column       | Configuration                  |
| PRD-003     | **Split Train/Test Data**        | Prepare model validation  | EventLog              | Train/test sets     | `split_train_test()`           |
| PRD-004     | **Train Prediction Model**       | Build ML model            | Training data         | Trained model       | ML training                    |
| PRD-005     | **Validate Model Accuracy**      | Test prediction quality   | Test data             | Accuracy metrics    | Model evaluation               |
| PRD-006     | **Predict Case Outcome**         | Forecast success/failure  | Running case          | Outcome prediction  | Model inference                |
| PRD-007     | **Predict Remaining Time**       | Forecast completion time  | Running case          | Time estimate       | Duration prediction            |
| PRD-008     | **Predict Next Activity**        | Forecast next step        | Running case          | Activity prediction | Sequence prediction            |
| PRD-009     | **Predict Risk Level**           | Assess case risk          | Running case          | Risk score          | Risk model                     |
| PRD-010     | **View Running Cases Dashboard** | Monitor active cases      | Live data             | Dashboard           | Real-time viz                  |
| PRD-011     | **Set Prediction Thresholds**    | Define alert triggers     | Threshold values      | Alert config        | Configuration                  |
| PRD-012     | **Create Prediction Alert**      | Notify on risk prediction | Alert config          | Active alert        | Alerting                       |
| PRD-013     | **Explain Prediction**           | Show prediction drivers   | Prediction            | Explanation         | Explainability                 |
| PRD-014     | **Update Model**                 | Retrain with new data     | New data              | Updated model       | Model retraining               |
| PRD-015     | **Track Prediction Accuracy**    | Monitor model performance | Predictions + actuals | Accuracy trend      | Model monitoring               |

---

## 2.9 CONCEPT DRIFT DETECTION USE CASE

### Purpose

Detect changes in process behavior over time, identifying when and how processes evolve.

### Actor: Process Analyst, Operations Manager

### Business Activities

| Activity ID | Business Activity                  | Description                   | Input              | Output             | PM4PY Mapping        |
| ----------- | ---------------------------------- | ----------------------------- | ------------------ | ------------------ | -------------------- |
| DRF-001     | **Define Time Windows**            | Set analysis periods          | Window config      | Configured windows | Time segmentation    |
| DRF-002     | **Extract Period Characteristics** | Compute per-period metrics    | EventLog + windows | Period features    | Feature extraction   |
| DRF-003     | **Detect Control-Flow Drift**      | Find activity pattern changes | EventLog           | Drift points       | Drift detection      |
| DRF-004     | **Detect Performance Drift**       | Find timing changes           | EventLog           | Drift points       | Performance drift    |
| DRF-005     | **Detect Resource Drift**          | Find organizational changes   | EventLog           | Drift points       | Resource analysis    |
| DRF-006     | **Visualize Drift Timeline**       | Show changes over time        | Drift points       | Timeline viz       | Visualization        |
| DRF-007     | **Compare Pre/Post Drift**         | Analyze before vs after       | Periods            | Comparison         | Comparative analysis |
| DRF-008     | **Quantify Drift Magnitude**       | Measure change severity       | Drift analysis     | Magnitude score    | Calculation          |
| DRF-009     | **Identify Drift Causes**          | Investigate change reasons    | Drift + context    | Cause analysis     | Root cause analysis  |
| DRF-010     | **Create Drift Alert**             | Notify on detected changes    | Alert config       | Active alert       | Alerting             |
| DRF-011     | **Track Process Evolution**        | Historical drift pattern      | Multiple periods   | Evolution chart    | Trend analysis       |
| DRF-012     | **Generate Drift Report**          | Document process changes      | Analysis           | Report             | Report generation    |

---

## 2.10 OBJECT-CENTRIC PROCESS MINING USE CASE

### Purpose

Analyze processes involving multiple interacting objects (orders, items, customers) with complex relationships.

### Actor: Process Analyst, Business Analyst

### Business Activities

| Activity ID | Business Activity                | Description                   | Input                | Output            | PM4PY Mapping                    |
| ----------- | -------------------------------- | ----------------------------- | -------------------- | ----------------- | -------------------------------- |
| OCE-001     | **Import OCEL Log**              | Load object-centric data      | OCEL file            | OCEL object       | `read_ocel*()`                   |
| OCE-002     | **View Object Types**            | Explore available types       | OCEL                 | Type list         | `ocel_get_object_types()`        |
| OCE-003     | **View Object Statistics**       | Summarize objects per type    | OCEL                 | Statistics        | `ocel_objects_summary()`         |
| OCE-004     | **Explore Object Relationships** | Understand type connections   | OCEL                 | Relationship viz  | Object graph                     |
| OCE-005     | **Discover OC-DFG**              | Multi-object directly-follows | OCEL                 | OC-DFG            | `discover_ocdfg()`               |
| OCE-006     | **Discover OC Petri Net**        | Object-centric process model  | OCEL                 | OC-PN             | `discover_oc_petri_net()`        |
| OCE-007     | **View OC-DFG Visualization**    | Display multi-object flow     | OC-DFG               | Visualization     | `view_ocdfg()`                   |
| OCE-008     | **View OC Petri Net**            | Display OC-PN                 | OC-PN                | Visualization     | `view_ocpn()`                    |
| OCE-009     | **Flatten to Single Type**       | Convert to traditional log    | OCEL + type          | EventLog          | `ocel_flattening()`              |
| OCE-010     | **Analyze Object Lifecycle**     | Track object state changes    | OCEL + type          | Lifecycle view    | Lifecycle analysis               |
| OCE-011     | **Discover Object Graph**        | Find object interactions      | OCEL                 | Object graph      | `discover_objects_graph()`       |
| OCE-012     | **Filter by Object Type**        | Focus on specific objects     | OCEL + types         | Filtered OCEL     | `filter_ocel_object_types()`     |
| OCE-013     | **Filter by Object Attribute**   | Filter by object properties   | OCEL + criteria      | Filtered OCEL     | `filter_ocel_object_attribute()` |
| OCE-014     | **View Temporal Summary**        | Time-based object activity    | OCEL                 | Temporal view     | `ocel_temporal_summary()`        |
| OCE-015     | **Analyze Object Cardinality**   | Events per object count       | OCEL                 | Cardinality stats | Statistics                       |
| OCE-016     | **Compare Object Type Behavior** | Contrast type patterns        | OCEL                 | Comparison        | Comparative analysis             |
| OCE-017     | **Extract OCEL Features**        | Prepare for ML                | OCEL                 | Feature matrix    | `extract_ocel_features()`        |
| OCE-018     | **Sample Large OCEL**            | Reduce for exploration        | OCEL + sample config | Sampled OCEL      | `sample_ocel()`                  |
| OCE-019     | **Export OCEL Analysis**         | Download results              | Analysis             | Export file       | Export service                   |

---

## 2.11 RPA DISCOVERY USE CASE

### Purpose

Identify automation opportunities by analyzing repetitive, rule-based activities suitable for robotic process automation.

### Actor: RPA Developer, Process Analyst, Automation Manager

### Business Activities

| Activity ID | Business Activity                    | Description                    | Input               | Output             | PM4PY Mapping        |
| ----------- | ------------------------------------ | ------------------------------ | ------------------- | ------------------ | -------------------- |
| RPA-001     | **Identify Repetitive Tasks**        | Find high-frequency activities | EventLog            | Activity ranking   | Frequency analysis   |
| RPA-002     | **Analyze Task Consistency**         | Measure execution variance     | EventLog            | Variance metrics   | Variant analysis     |
| RPA-003     | **Identify Rule-Based Tasks**        | Find deterministic flows       | EventLog            | Rule patterns      | Pattern detection    |
| RPA-004     | **Calculate Automation Potential**   | Score activities for RPA       | Analysis            | Potential scores   | Scoring model        |
| RPA-005     | **Estimate Time Savings**            | Project automation benefits    | Activity times      | Savings estimate   | Calculation          |
| RPA-006     | **Estimate Cost Savings**            | Project financial benefits     | Costs + potential   | ROI estimate       | Calculation          |
| RPA-007     | **Map Task Dependencies**            | Understand task relationships  | Process model       | Dependency map     | Model analysis       |
| RPA-008     | **Identify UI Interactions**         | Find screen-based tasks        | Activity attributes | UI task list       | Attribute filtering  |
| RPA-009     | **Prioritize Automation Candidates** | Rank by potential/effort       | Scores              | Prioritized list   | Ranking              |
| RPA-010     | **Document Task Steps**              | Detail automation requirements | Selected task       | Task specification | Documentation        |
| RPA-011     | **Identify Exception Handling**      | Find error patterns            | EventLog            | Exception flows    | Exception analysis   |
| RPA-012     | **Generate RPA Assessment**          | Create business case           | Analysis            | Assessment report  | Report generation    |
| RPA-013     | **Track Automation Progress**        | Monitor RPA implementation     | Project data        | Progress dashboard | Tracking             |
| RPA-014     | **Measure Post-RPA Performance**     | Compare before/after           | Historical data     | Impact analysis    | Comparative analysis |

---

## 2.12 COMPLIANCE MONITORING USE CASE

### Purpose

Continuously monitor processes against regulatory requirements, internal policies, and control objectives.

### Actor: Compliance Officer, Internal Auditor, Risk Manager

### Business Activities

| Activity ID | Business Activity               | Description                    | Input                | Output            | PM4PY Mapping        |
| ----------- | ------------------------------- | ------------------------------ | -------------------- | ----------------- | -------------------- |
| CMP-001     | **Define Compliance Rules**     | Specify required behaviors     | Rule definitions     | Rule set          | Rule configuration   |
| CMP-002     | **Import Regulatory Model**     | Load compliance process model  | Model file           | Reference model   | Model import         |
| CMP-003     | **Map Controls to Activities**  | Link controls to process       | Control definitions  | Control mapping   | Mapping              |
| CMP-004     | **Execute Compliance Check**    | Run rule validation            | EventLog + rules     | Violations        | Conformance checking |
| CMP-005     | **View Compliance Dashboard**   | Monitor overall status         | Check results        | Dashboard         | Visualization        |
| CMP-006     | **View Violation Details**      | Drill into specific issues     | Violations           | Violation list    | Detail view          |
| CMP-007     | **Classify Violation Severity** | Rate issue importance          | Violations           | Classified list   | Classification       |
| CMP-008     | **Calculate Compliance Rate**   | Measure overall conformance    | Check results        | Compliance %      | Calculation          |
| CMP-009     | **Track Compliance Trend**      | Monitor over time              | Historical data      | Trend chart       | Time series          |
| CMP-010     | **Generate Audit Evidence**     | Export for auditors            | Check results        | Evidence package  | Export               |
| CMP-011     | **Create Compliance Alert**     | Notify on violations           | Alert config         | Active alert      | Alerting             |
| CMP-012     | **Schedule Regular Checks**     | Automate monitoring            | Schedule config      | Scheduled job     | Scheduler            |
| CMP-013     | **Link to Remediation**         | Connect violations to actions  | Violations           | Action items      | Action tracking      |
| CMP-014     | **Check Segregation of Duties** | Validate SoD controls          | EventLog + SoD rules | SoD violations    | SoD checking         |
| CMP-015     | **Check Four-Eyes Principle**   | Validate approval requirements | EventLog + rules     | Violations        | Rule checking        |
| CMP-016     | **Generate Compliance Report**  | Create regulatory report       | All results          | Compliance report | Report generation    |
| CMP-017     | **Archive Compliance Records**  | Retain for audit trail         | Records              | Archived data     | Archival             |

---

## 2.13 SIMULATION & WHAT-IF ANALYSIS USE CASE

### Purpose

Test process changes virtually before implementation by simulating modified process behavior.

### Actor: Process Analyst, Operations Manager, Change Manager

### Business Activities

| Activity ID | Business Activity                | Description                  | Input                 | Output              | PM4PY Mapping                    |
| ----------- | -------------------------------- | ---------------------------- | --------------------- | ------------------- | -------------------------------- |
| SIM-001     | **Define Simulation Parameters** | Set resource, time configs   | Parameters            | Configuration       | Configuration                    |
| SIM-002     | **Generate Synthetic Log**       | Create log from model        | Process Model         | Synthetic EventLog  | `play_out()`                     |
| SIM-003     | **Run Stochastic Simulation**    | Probabilistic execution      | Model + distributions | Simulation result   | `simulate_stochastic_petrinet()` |
| SIM-004     | **Define What-If Scenario**      | Specify change parameters    | Scenario definition   | Configured scenario | Scenario config                  |
| SIM-005     | **Modify Activity Duration**     | Change timing assumptions    | Duration params       | Modified model      | Parameter change                 |
| SIM-006     | **Modify Resource Capacity**     | Change resource availability | Capacity params       | Modified model      | Parameter change                 |
| SIM-007     | **Modify Process Flow**          | Change activity routing      | Flow changes          | Modified model      | Model modification               |
| SIM-008     | **Execute What-If Simulation**   | Run modified scenario        | Modified model        | Simulation result   | Simulation engine                |
| SIM-009     | **Compare Scenarios**            | Contrast baseline vs changed | Multiple results      | Comparison          | Comparative analysis             |
| SIM-010     | **Visualize Simulation Results** | Display projected metrics    | Results               | Visualization       | Result viz                       |
| SIM-011     | **Calculate Projected Impact**   | Quantify expected changes    | Results               | Impact metrics      | Calculation                      |
| SIM-012     | **Sensitivity Analysis**         | Test parameter variations    | Parameter ranges      | Sensitivity chart   | Analysis                         |
| SIM-013     | **Generate Simulation Report**   | Document scenario analysis   | Results               | Report              | Report generation                |
| SIM-014     | **Save Scenario for Comparison** | Persist scenario results     | Results               | Saved scenario      | Storage                          |

---

## 2.14 DASHBOARD & REPORTING USE CASE

### Purpose

Create visualizations, dashboards, and reports to communicate process insights to stakeholders.

### Actor: All Users, Executives, Managers

### Business Activities

| Activity ID | Business Activity              | Description                 | Input            | Output             | PM4PY Mapping     |
| ----------- | ------------------------------ | --------------------------- | ---------------- | ------------------ | ----------------- |
| DSH-001     | **Create New Dashboard**       | Initialize dashboard canvas | Name + config    | Empty dashboard    | Dashboard service |
| DSH-002     | **Add KPI Widget**             | Display key metric          | KPI definition   | KPI widget         | Widget creation   |
| DSH-003     | **Add Chart Widget**           | Add visualization           | Chart config     | Chart widget       | Visualization     |
| DSH-004     | **Add Process Model Widget**   | Embed process visualization | Model selection  | Model widget       | Model embedding   |
| DSH-005     | **Add Table Widget**           | Display data table          | Data selection   | Table widget       | Table component   |
| DSH-006     | **Configure Widget Filters**   | Set data scope              | Filter criteria  | Configured widget  | Filter config     |
| DSH-007     | **Arrange Dashboard Layout**   | Position widgets            | Layout actions   | Arranged dashboard | Layout management |
| DSH-008     | **Set Dashboard Refresh**      | Configure auto-update       | Refresh interval | Auto-refresh       | Configuration     |
| DSH-009     | **Add Dashboard Filters**      | Create interactive filters  | Filter config    | Global filters     | Filter creation   |
| DSH-010     | **Share Dashboard**            | Grant access to others      | Sharing config   | Shared access      | Sharing service   |
| DSH-011     | **Schedule Dashboard Email**   | Auto-send dashboard         | Email config     | Scheduled job      | Email scheduler   |
| DSH-012     | **Export Dashboard as PDF**    | Download static version     | Dashboard        | PDF file           | PDF generation    |
| DSH-013     | **Create Report Template**     | Define report structure     | Template config  | Template           | Template creation |
| DSH-014     | **Generate Ad-hoc Report**     | Create one-time report      | Report config    | Report             | Report generation |
| DSH-015     | **Schedule Recurring Report**  | Automate report creation    | Schedule config  | Scheduled job      | Scheduler         |
| DSH-016     | **Customize Report Branding**  | Add logo, colors            | Brand config     | Branded template   | Branding          |
| DSH-017     | **Export Report Formats**      | Download in various formats | Format choice    | Export file        | Export service    |
| DSH-018     | **Embed Dashboard Externally** | Create embed code           | Embed config     | Embed code         | Embedding         |

---

## 2.15 ALERTING & MONITORING USE CASE

### Purpose

Set up automated alerts and continuous monitoring for process KPIs, deviations, and anomalies.

### Actor: Operations Manager, Process Owner, Analyst

### Business Activities

| Activity ID | Business Activity              | Description               | Input                 | Output            | PM4PY Mapping       |
| ----------- | ------------------------------ | ------------------------- | --------------------- | ----------------- | ------------------- |
| ALR-001     | **Define Alert Condition**     | Specify trigger criteria  | Condition config      | Alert definition  | Alert config        |
| ALR-002     | **Set KPI Threshold Alert**    | Alert on metric breach    | KPI + threshold       | KPI alert         | Threshold config    |
| ALR-003     | **Set Conformance Alert**      | Alert on violations       | Conformance threshold | Conformance alert | Alert config        |
| ALR-004     | **Set Anomaly Alert**          | Alert on unusual patterns | Anomaly detection     | Anomaly alert     | ML-based alerting   |
| ALR-005     | **Set SLA Breach Alert**       | Alert on deadline risk    | SLA definition        | SLA alert         | Time-based alert    |
| ALR-006     | **Set Drift Alert**            | Alert on process changes  | Drift threshold       | Drift alert       | Drift detection     |
| ALR-007     | **Configure Alert Recipients** | Specify who to notify     | User/channel list     | Recipient config  | Notification config |
| ALR-008     | **Configure Alert Channels**   | Set notification methods  | Channel config        | Email/Slack/etc.  | Channel config      |
| ALR-009     | **Configure Alert Frequency**  | Set notification timing   | Frequency config      | Throttling rules  | Frequency config    |
| ALR-010     | **View Alert History**         | Review past alerts        | Alert logs            | History view      | Alert history       |
| ALR-011     | **Acknowledge Alert**          | Mark as reviewed          | Alert ID              | Acknowledged      | Status update       |
| ALR-012     | **Snooze Alert**               | Temporarily disable       | Alert + duration      | Snoozed           | Status update       |
| ALR-013     | **Escalate Alert**             | Send to higher level      | Alert + escalation    | Escalated         | Escalation          |
| ALR-014     | **Link Alert to Action**       | Create followup task      | Alert                 | Action item       | Action tracking     |
| ALR-015     | **Analyze Alert Patterns**     | Review alert frequency    | Alert history         | Pattern analysis  | Analytics           |
| ALR-016     | **Tune Alert Thresholds**      | Optimize sensitivity      | Alert performance     | Updated config    | Optimization        |

---

# SECTION 3: BUSINESS ACTIVITY FLOWS BY PERSONA

## 3.1 Process Analyst Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROCESS ANALYST USER JOURNEY                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │ Import  │───▶│ Explore │───▶│ Discover│───▶│ Analyze │───▶│ Report  │  │
│  │ Data    │    │ Data    │    │ Process │    │ Insights│    │ Share   │  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│       │              │              │              │              │         │
│       ▼              ▼              ▼              ▼              ▼         │
│  • Upload log   • View stats   • Run miner   • Conformance  • Dashboard   │
│  • Map columns  • Check quality• View model  • Performance  • Export      │
│  • Validate     • Filter data  • Annotate    • Root cause   • Schedule    │
│                 • Preview      • Compare     • Prediction   • Share       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3.2 Compliance Officer Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMPLIANCE OFFICER USER JOURNEY                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │ Define  │───▶│ Check   │───▶│ Review  │───▶│ Remediate───▶│ Report  │  │
│  │ Rules   │    │ Compliance   │ Violations   │ Issues  │    │ Archive │  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│       │              │              │              │              │         │
│       ▼              ▼              ▼              ▼              ▼         │
│  • Import model • Run check   • View details• Create action• Generate    │
│  • Define rules • View score  • Classify    • Track progress • Export     │
│  • Map controls • Set alerts  • Investigate • Verify fix   • Archive     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3.3 Operations Manager Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      OPERATIONS MANAGER USER JOURNEY                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │ Monitor │───▶│ Identify│───▶│ Analyze │───▶│ Optimize│───▶│ Track   │  │
│  │ KPIs    │    │ Issues  │    │ Causes  │    │ Process │    │ Impact  │  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│       │              │              │              │              │         │
│       ▼              ▼              ▼              ▼              ▼         │
│  • View dashboard• Bottlenecks • Root cause • Simulate    • Compare      │
│  • Set alerts   • SLA breach  • Correlate  • What-if     • Report       │
│  • Track trends • Anomalies   • Investigate• Implement   • Document     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# SECTION 4: ACTIVITY TO UI SCREEN MAPPING

## 4.1 Web Application Screens

| Screen                    | Primary Activities                    | Secondary Activities         |
| ------------------------- | ------------------------------------- | ---------------------------- |
| **Home Dashboard**        | DSH-001 to DSH-010                    | ALR-010, Quick Stats         |
| **Data Import**           | DIS-001 to DIS-004                    | OCE-001, Connector Import    |
| **Log Explorer**          | VAR-001 to VAR-015, Filter Activities | Statistics, Preview          |
| **Process Discovery**     | DIS-005 to DIS-015                    | Algorithm Config, Comparison |
| **Model Viewer**          | DIS-008, DIS-010, DIS-011             | Export, Share, Annotate      |
| **Conformance Checker**   | CON-001 to CON-022                    | Deviation Analysis           |
| **Performance Analysis**  | PER-001 to PER-020                    | Bottleneck Detection         |
| **Variant Explorer**      | VAR-001 to VAR-015                    | Drill Down, Compare          |
| **Social Network**        | ORG-001 to ORG-015                    | Role Mining, Workload        |
| **OCEL Analysis**         | OCE-001 to OCE-019                    | Object Lifecycle             |
| **Predictive Monitoring** | PRD-001 to PRD-015                    | Live Case View               |
| **Simulation Studio**     | SIM-001 to SIM-014                    | Scenario Comparison          |
| **Alert Management**      | ALR-001 to ALR-016                    | History, Configuration       |
| **Report Builder**        | DSH-012 to DSH-018                    | Templates, Scheduling        |
| **Compliance Center**     | CMP-001 to CMP-017                    | Audit Trail                  |
| **Settings**              | User Config, Workspace Config         | Integrations, Team           |

---

# SECTION 5: ACTIVITY FREQUENCY & PRIORITY

## 5.1 High-Frequency Activities (Daily Use)

| Activity           | Frequency | User Type  |
| ------------------ | --------- | ---------- |
| View Dashboard     | Very High | All        |
| View Process Model | Very High | Analyst    |
| Filter Event Log   | Very High | Analyst    |
| View Variants      | High      | Analyst    |
| Check Conformance  | High      | Compliance |
| View Alerts        | High      | Operations |
| View Running Cases | High      | Operations |
| Export Reports     | High      | Manager    |

## 5.2 Medium-Frequency Activities (Weekly Use)

| Activity               | Frequency | User Type  |
| ---------------------- | --------- | ---------- |
| Upload Event Log       | Medium    | Analyst    |
| Execute Discovery      | Medium    | Analyst    |
| Run Conformance Check  | Medium    | Compliance |
| Create Dashboard       | Medium    | Analyst    |
| Configure Alerts       | Medium    | Operations |
| Generate Reports       | Medium    | Manager    |
| Train Prediction Model | Medium    | Analyst    |

## 5.3 Low-Frequency Activities (Monthly/Occasional)

| Activity                    | Frequency | User Type  |
| --------------------------- | --------- | ---------- |
| Configure Connectors        | Low       | Admin      |
| Define Compliance Rules     | Low       | Compliance |
| Create Report Templates     | Low       | Analyst    |
| Run Simulations             | Low       | Analyst    |
| Perform Root Cause Analysis | Low       | Analyst    |
| Update Prediction Models    | Low       | Analyst    |
| Archive Logs                | Low       | Admin      |

---

# SECTION 6: BUSINESS ACTIVITY MATRIX

## 6.1 Activity to PM4PY Function Mapping

| Activity Category | Total Activities | PM4PY Coverage | Custom Build  |
| ----------------- | ---------------- | -------------- | ------------- |
| Discovery         | 15               | 12             | 3             |
| Variant Analysis  | 15               | 10             | 5             |
| Conformance       | 22               | 15             | 7             |
| Performance       | 20               | 14             | 6             |
| Bottleneck        | 12               | 8              | 4             |
| Root Cause        | 13               | 6              | 7             |
| Organizational    | 15               | 10             | 5             |
| Prediction        | 15               | 8              | 7             |
| Drift Detection   | 12               | 6              | 6             |
| OCEL              | 19               | 16             | 3             |
| RPA Discovery     | 14               | 8              | 6             |
| Compliance        | 17               | 10             | 7             |
| Simulation        | 14               | 6              | 8             |
| Dashboard         | 18               | 4              | 14            |
| Alerting          | 16               | 2              | 14            |
| **TOTAL**         | **237**          | **135 (57%)**  | **102 (43%)** |

---

This document defines **237 business activities** across **15 major use cases** for your Process Mining SaaS web application, with complete mapping to PM4PY features and custom development needs.
