# Process Mining Platform - User Tools by Business Use Case

---

## 🚀 Getting Started

| Tool                    | What It Does                                   | SDK Method                     |
| ----------------------- | ---------------------------------------------- | ------------------------------ |
| **Upload Event Log**    | Import CSV/XES process data                    | `sdk.logs.ingest(file)`        |
| **Auto-Detect Columns** | Smart column mapping for CSV                   | `sdk.logs.detectColumns(file)` |
| **View Log Statistics** | Cases, events, activities, variants, durations | `sdk.logs.analyze(logId)`      |

---

## 📊 Process Discovery & Understanding

> _"What does our process actually look like?"_

| Tool                       | What It Does                            | When To Use                    | SDK Method                                   |
| -------------------------- | --------------------------------------- | ------------------------------ | -------------------------------------------- |
| **Discover Process Model** | Mine process model from data            | First analysis of any process  | `sdk.discovery.discover({logId, minerType})` |
| **Get Process Variants**   | Unique execution paths with frequencies | Understand process variations  | `sdk.logs.listVariants(logId)`               |
| **Visualize DFG**          | Directly-Follows Graph for UI rendering | Build interactive process maps | `sdk.visualization.getDFG(logId)`            |
| **Visualize Petri Net**    | Formal process model structure          | Advanced process modeling      | `sdk.visualization.getPetriNet(modelId)`     |
| **Export SVG**             | Render model as image                   | Reports, presentations         | `sdk.visualization.getModelSVG(modelId)`     |

**Mining Algorithms:**

- `inductive` - Best quality, handles complex processes
- `heuristics` - Good with noisy data
- `alpha` - Fast, simple processes only
- `dfg` - Fastest, frequency-based

---

## ✅ Compliance & Conformance

> _"Are we following the process correctly?"_

| Tool                  | What It Does                    | When To Use         | SDK Method                                         |
| --------------------- | ------------------------------- | ------------------- | -------------------------------------------------- |
| **Check Conformance** | Measure log-to-model fitness    | Compliance audits   | `sdk.conformance.check({logId, modelId})`          |
| **Get Diagnostics**   | Trace-level conformance details | Root cause analysis | `sdk.conformance.getDiagnostics(logId, modelId)`   |
| **Detect Deviations** | Find specific rule violations   | Exception reporting | `sdk.conformance.detectDeviations(logId, modelId)` |

**Key Metrics:**

- **Fitness** ≥ 0.8 = Conformant process
- **Token Replay** = Fast check
- **Alignment** = Precise check (slower)

---

## ⚡ Performance Optimization

> _"Where are the bottlenecks? How can we improve?"_

| Tool                      | What It Does                      | When To Use           | SDK Method                                     |
| ------------------------- | --------------------------------- | --------------------- | ---------------------------------------------- |
| **Detect Bottlenecks**    | Find high waiting-time activities | Process improvement   | `sdk.analytics.getBottlenecks(logId)`          |
| **Analyze Rework**        | Identify repeated activities      | Quality issues        | `sdk.analytics.getRework(logId)`               |
| **Get Cycle Time**        | End-to-end case durations         | SLA monitoring        | `sdk.analytics.getCycleTime(logId)`            |
| **Get Throughput**        | Cases per day/week/month          | Capacity planning     | `sdk.analytics.getThroughput(logId)`           |
| **Service Times**         | Per-activity duration stats       | Activity optimization | `sdk.analytics.getServiceTimes(logId)`         |
| **Performance Dashboard** | All-in-one performance summary    | Management reporting  | `sdk.analytics.getPerformanceDashboard(logId)` |

> ⚡ **Performance Note:** Analytics endpoints are **cached for 1 hour**.

---

## 🔮 Predictive Analytics

> _"What will happen next? How long will this take?"_

| Tool                       | What It Does                        | When To Use                 | SDK Method                                           |
| -------------------------- | ----------------------------------- | --------------------------- | ---------------------------------------------------- |
| **Train Predictor**        | Build ML model from historical data | Setup (one-time per target) | `sdk.predictions.trainPredictor(logId, request)`     |
| **Predict Next Activity**  | Forecast next step in process       | Real-time case monitoring   | `sdk.predictions.predict(predictorId, {casePrefix})` |
| **Predict Remaining Time** | Estimate time to completion         | SLA predictions             | `sdk.predictions.predict(predictorId, {casePrefix})` |
| **Batch Predict**          | Bulk predictions for efficiency     | Batch processing            | `sdk.predictions.predictBatch(predictorId, request)` |

**ML Details:**

- **Algorithms:** Random Forest (default), XGBoost
- **Targets:** `next_activity`, `remaining_time`
- **Training:** Can run async via `asyncMode=true`

---

## 🧪 What-If Analysis & Simulation

> _"What if we changed the process?"_

| Tool                  | What It Does                      | When To Use         | SDK Method                                             |
| --------------------- | --------------------------------- | ------------------- | ------------------------------------------------------ |
| **Simulate Scenario** | Model process changes             | Impact assessment   | `sdk.simulation.simulate(logId, {modifications})`      |
| **Capacity Planning** | Estimate resources for throughput | Resource planning   | `sdk.simulation.capacityPlan(logId, targetThroughput)` |
| **Model Play-Out**    | Generate synthetic traces         | Testing, validation | `sdk.simulation.playOut(modelId, {numTraces})`         |

---

## 🔍 Data Segmentation & Filtering

> _"Analyze specific subsets of process data"_

| Tool                 | What It Does                | When To Use       | SDK Method                                      |
| -------------------- | --------------------------- | ----------------- | ----------------------------------------------- |
| **Apply Filters**    | Create filtered log subset  | Focused analysis  | `sdk.filtering.applyFilter(logId, {filters})`   |
| **Preview Filter**   | See impact before applying  | Filter validation | `sdk.filtering.previewFilter(logId, {filters})` |
| **Filter Options**   | Get available filter values | Build filter UI   | `sdk.filtering.getFilterOptions(logId)`         |
| **Filter Templates** | Pre-built filter configs    | Quick start       | `sdk.filtering.getTemplates()`                  |

**Filter Types:**

- `time_range` - Date/time window
- `variant_top_k` - Top K variants only
- `activity_include/exclude` - Activity filtering
- `duration_min/max` - Case duration bounds

---

## 👥 Organizational Analysis

> _"Who does what? How do teams collaborate?"_

| Tool                      | What It Does                 | When To Use             | SDK Method                                     |
| ------------------------- | ---------------------------- | ----------------------- | ---------------------------------------------- |
| **Handover Network**      | Work handoff patterns        | Identify handoff delays | `sdk.org.buildHandoverNetwork(logId)`          |
| **Collaboration Network** | Who works together           | Team analysis           | `sdk.org.buildCollaborationNetwork(logId)`     |
| **Discover Roles**        | Group resources by behavior  | Org structure           | `sdk.org.discoverRoles(logId)`                 |
| **Resource Profile**      | Individual performance stats | Performance reviews     | `sdk.org.profileResource(logId, resourceName)` |
| **Workload Distribution** | Balance across resources     | Capacity issues         | `sdk.org.getWorkloadDistribution(logId)`       |

---

## 🔗 Object-Centric Process Mining (OCPM)

> _"Analyze multi-object processes (orders, items, deliveries)"_

| Tool                      | What It Does               | When To Use               | SDK Method                       |
| ------------------------- | -------------------------- | ------------------------- | -------------------------------- |
| **Upload OCEL**           | Import OCEL 2.0 data       | Object-centric analysis   | `sdk.ocpm.ingest(file)`          |
| **Get Object Types**      | List object types & counts | Understand data structure | `sdk.ocpm.getObjectTypes(logId)` |
| **Discover OC Petri Net** | Multi-object process model | Complex process discovery | `sdk.ocpm.discoverOCPN({logId})` |

**Formats:** `.jsonocel`, `.sqlite`, `.xmlocel`

---

## 🔄 Workflow Automation

> _"Automate recurring analysis pipelines"_

| Tool                | What It Does               | When To Use              | SDK Method                               |
| ------------------- | -------------------------- | ------------------------ | ---------------------------------------- |
| **Create Workflow** | Define multi-step pipeline | Automate analysis        | `sdk.workflows.create(request)`          |
| **Run Workflow**    | Execute pipeline on log    | Scheduled/triggered runs | `sdk.workflows.run(workflowId, {logId})` |
| **List Templates**  | Pre-built workflow configs | Quick start              | `sdk.workflows.getTemplates()`           |

---

## Technical Quick Reference

### Sync vs Async

| Feature      | Mode                | Notes                             |
| ------------ | ------------------- | --------------------------------- |
| File uploads | Sync                | Blocks until parsed               |
| Discovery    | Sync                | 1-30s depending on algorithm      |
| Conformance  | Sync                | Token replay fast, alignment slow |
| Analytics    | Sync (cached)       | 1-hour cache TTL                  |
| ML Training  | **Async available** | Use `asyncMode=true`              |
| Predictions  | Sync                | <100ms per prediction             |

### Error Handling

| Code | Meaning                |
| ---- | ---------------------- |
| 404  | Resource not found     |
| 400  | Invalid request/config |
| 422  | Validation error       |
| 500  | Server/algorithm error |

---

## SDK Setup

```typescript
import { ProcessMiningSdk } from "process-mining-sdk";

const sdk = new ProcessMiningSdk({
  baseUrl: "http://localhost:8001",
});

// Example: Full analysis pipeline
const log = await sdk.logs.ingest(file);
const model = await sdk.discovery.discover({
  logId: log.id,
  minerType: "inductive",
});
const conformance = await sdk.conformance.check({
  logId: log.id,
  modelId: model.id,
});
const dashboard = await sdk.analytics.getPerformanceDashboard(log.id);
```

---

_Concise reference - see `usertools.md` for complete technical details_
