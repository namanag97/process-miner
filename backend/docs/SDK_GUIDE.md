# SDK Guide

> **Package:** `process-mining-sdk`  
> **Source:** `/sdk/src/`  
> **TypeScript:** 5.x with ESM

---

## Installation

```bash
npm install process-mining-sdk
```

---

## Quick Start

```typescript
import { ProcessMiningSdk } from "process-mining-sdk";

const sdk = new ProcessMiningSdk({
  baseUrl: "http://localhost:8001",
  timeout: 30000, // optional, default 30s
});

// Upload and analyze
const log = await sdk.logs.ingest(file, { name: "My Process" });
const stats = await sdk.logs.analyze(log.id);
const bottlenecks = await sdk.analytics.getBottlenecks(log.id);
```

---

## SDK Structure

```
sdk.auth          → Authentication
sdk.logs          → Event log operations
sdk.discovery     → Process model discovery
sdk.conformance   → Conformance checking
sdk.performance   → Performance analysis
sdk.analytics     → Analytics & bottlenecks
sdk.filtering     → Event log filtering
sdk.predictions   → ML predictions
sdk.visualization → Graph data for rendering
sdk.ocpm          → Object-centric process mining
sdk.org           → Organizational mining
sdk.simulation    → What-if simulation
sdk.models        → Process model management
sdk.workflows     → Workflow automation
sdk.notifications → Notifications
sdk.integrations  → External integrations
sdk.processMining → PM4Py advanced features
```

---

## Clients Reference

### `sdk.logs` — Event Log Operations

| Method                        | Endpoint                         | Return Type        |
| ----------------------------- | -------------------------------- | ------------------ |
| `ingest(file, options?)`      | `POST /processes/upload`         | `IngestionResult`  |
| `detectColumns(file)`         | `POST /processes/detect-columns` | `ColumnDetection`  |
| `list(options?)`              | `GET /processes`                 | `PaginatedLogs`    |
| `get(logId)`                  | `GET /processes/{id}`            | `EventLogDetails`  |
| `analyze(logId)`              | `GET /processes/{id}/statistics` | `LogStatistics`    |
| `listVariants(logId, limit?)` | `GET /processes/{id}/variants`   | `ProcessVariant[]` |
| `listActivities(logId)`       | `GET /processes/{id}/activities` | `string[]`         |
| `remove(logId)`               | `DELETE /processes/{id}`         | `void`             |

```typescript
// Upload with column mapping
const result = await sdk.logs.ingest(file, {
  name: "Q4 2024 Orders",
  caseIdColumn: "order_id",
  activityColumn: "step",
  timestampColumn: "timestamp",
  resourceColumn: "handler",
});

// List with pagination
const logs = await sdk.logs.list({
  page: 1,
  pageSize: 20,
  sortBy: "created_at",
  sortOrder: "desc",
});

// Get statistics
const stats = await sdk.logs.analyze(logId);
console.log(`${stats.caseCount} cases, ${stats.variantCount} variants`);
```

**Error Handling:**

```typescript
try {
  await sdk.logs.ingest(file);
} catch (error) {
  if (error instanceof ApiError) {
    if (error.status === 422) {
      console.error("Column mapping failed:", error.detail);
    }
  }
}
```

---

### `sdk.discovery` — Process Discovery

| Method                 | Endpoint                        | Return Type       |
| ---------------------- | ------------------------------- | ----------------- |
| `discover(options)`    | `POST /discovery/discover`      | `ModelResponse`   |
| `listMiners()`         | `GET /discovery/miners`         | `MinerInfo[]`     |
| `listModels(options?)` | `GET /discovery/models`         | `PaginatedModels` |
| `getModel(modelId)`    | `GET /discovery/models/{id}`    | `ModelResponse`   |
| `deleteModel(modelId)` | `DELETE /discovery/models/{id}` | `void`            |

```typescript
// Discover with inductive miner
const model = await sdk.discovery.discover({
  logId: "log_abc123",
  minerType: "inductive",
  modelName: "Main Process Model",
});

console.log(`Fitness: ${model.fitness}, Precision: ${model.precision}`);

// List available miners
const miners = await sdk.discovery.listMiners();
// [{id: 'alpha', name: 'Alpha Miner', ...}, ...]
```

---

### `sdk.conformance` — Conformance Checking

| Method                                       | Endpoint                       | Return Type              |
| -------------------------------------------- | ------------------------------ | ------------------------ |
| `check(options)`                             | `POST /conformance/check`      | `ConformanceResult`      |
| `measureFitness(logId, modelId)`             | `GET /conformance/fitness`     | `number`                 |
| `measurePrecision(logId, modelId)`           | `GET /conformance/precision`   | `number`                 |
| `diagnose(logId, modelId)`                   | `GET /conformance/diagnostics` | `ConformanceDiagnostics` |
| `findDeviations(logId, modelId, threshold?)` | `GET /conformance/deviations`  | `Deviation[]`            |
| `computeAlignments(logId, modelId, limit?)`  | `GET /conformance/alignments`  | `AlignmentAnalysis`      |

```typescript
// Quick conformance check
const result = await sdk.conformance.check({
  logId: "log_abc123",
  modelId: "model_xyz789",
  method: "token_replay", // or 'alignment' for more accuracy
});

if (result.isConformant) {
  console.log(`Fitness: ${result.fitness}`);
} else {
  const deviations = await sdk.conformance.findDeviations(logId, modelId);
  console.log(`${deviations.length} deviations found`);
}
```

---

### `sdk.analytics` — Performance Analytics

| Method                            | Endpoint                                 | Return Type                    |
| --------------------------------- | ---------------------------------------- | ------------------------------ |
| `getBottlenecks(logId)`           | `GET /analytics/logs/{id}/bottlenecks`   | `BottleneckListResponse`       |
| `getRework(logId)`                | `GET /analytics/logs/{id}/rework`        | `ReworkListResponse`           |
| `getServiceTimes(logId)`          | `GET /analytics/logs/{id}/service-times` | `ServiceTimeResponse[]`        |
| `getCycleTime(logId)`             | `GET /analytics/logs/{id}/cycle-time`    | `CycleTimeResponse`            |
| `getThroughput(logId)`            | `GET /analytics/logs/{id}/throughput`    | `ThroughputResponse`           |
| `getPatterns(logId, minSupport?)` | `GET /analytics/logs/{id}/patterns`      | `PatternResponse[]`            |
| `getPerformanceDashboard(logId)`  | `GET /analytics/logs/{id}/performance`   | `PerformanceDashboardResponse` |

```typescript
// Get all performance metrics in one call
const dashboard = await sdk.analytics.getPerformanceDashboard(logId);
console.log(`Avg cycle time: ${dashboard.cycleTime.avgSeconds}s`);
console.log(`Top bottleneck: ${dashboard.topBottlenecks[0]?.activity}`);

// Detailed bottleneck analysis
const bottlenecks = await sdk.analytics.getBottlenecks(logId);
for (const b of bottlenecks.bottlenecks) {
  if (b.isBottleneck) {
    console.log(`${b.activity}: ${b.avgWaitingTimeSeconds}s average wait`);
  }
}
```

---

### `sdk.filtering` — Event Log Filtering

| Method                          | Endpoint                            | Return Type                  |
| ------------------------------- | ----------------------------------- | ---------------------------- |
| `applyFilter(logId, request)`   | `POST /filtering/logs/{id}/apply`   | `FilteredLogResponse`        |
| `previewFilter(logId, request)` | `POST /filtering/logs/{id}/preview` | `FilterPreviewResponse`      |
| `getFilterOptions(logId)`       | `GET /filtering/logs/{id}/options`  | `FilterOptionsResponse`      |
| `getTemplates()`                | `GET /filtering/templates`          | `FilterTemplateListResponse` |

```typescript
// Preview filter impact
const preview = await sdk.filtering.previewFilter(logId, {
  filters: [
    { type: "time_range", params: { start: "2024-10-01", end: "2024-12-31" } },
    { type: "variants_top_k", params: { k: 10 } },
  ],
});

console.log(
  `Would retain ${preview.wouldRetainCases} of ${preview.statistics.originalCases} cases`
);

// Apply and create new log
const filtered = await sdk.filtering.applyFilter(logId, {
  name: "Q4 Happy Path",
  filters: [{ type: "variants_top_k", params: { k: 5 } }],
  saveResult: true,
});

// Use filtered log for analysis
const bottlenecks = await sdk.analytics.getBottlenecks(filtered.id);
```

---

### `sdk.predictions` — ML Predictions

| Method                                   | Endpoint                                          | Return Type                              |
| ---------------------------------------- | ------------------------------------------------- | ---------------------------------------- |
| `trainPredictor(logId, request, async?)` | `POST /predictions/logs/{id}/train`               | `PredictorResponse \| JobStatusResponse` |
| `getTrainingJob(jobId)`                  | `GET /predictions/jobs/{id}`                      | `JobStatusResponse`                      |
| `listPredictors(logId)`                  | `GET /predictions/logs/{id}/predictors`           | `PredictorListResponse`                  |
| `getPredictor(predictorId)`              | `GET /predictions/predictors/{id}`                | `PredictorResponse`                      |
| `predict(predictorId, request)`          | `POST /predictions/predictors/{id}/predict`       | `PredictionResponse`                     |
| `predictBatch(predictorId, request)`     | `POST /predictions/predictors/{id}/predict-batch` | `BatchPredictionResponse`                |
| `deletePredictor(predictorId)`           | `DELETE /predictions/predictors/{id}`             | `void`                                   |

```typescript
// Train async (default)
const job = await sdk.predictions.trainPredictor(logId, {
  targetType: "next_activity",
  algorithm: "random_forest",
});

// Poll for completion
let status = await sdk.predictions.getTrainingJob(job.id);
while (status.status === "running") {
  await new Promise((r) => setTimeout(r, 2000));
  status = await sdk.predictions.getTrainingJob(job.id);
}

const predictorId = status.result?.predictorId;

// Make prediction
const prediction = await sdk.predictions.predict(predictorId, {
  casePrefix: ["Create Order", "Approve"],
});

console.log(
  `Next: ${prediction.prediction} (${prediction.confidence * 100}% confidence)`
);
```

---

### `sdk.visualization` — Graph Data

| Method                               | Endpoint                                | Return Type                   |
| ------------------------------------ | --------------------------------------- | ----------------------------- |
| `getDFG(logId, includePerformance?)` | `GET /visualization/{id}/dfg`           | `DFGResponse`                 |
| `getExplorerData(logId, options?)`   | `GET /visualization/{id}/explorer-data` | `ProcessExplorerDataResponse` |
| `getPetriNet(modelId)`               | `GET /visualization/{id}/petri-net`     | `PetriNetResponse`            |
| `getModelSVG(modelId)`               | `GET /visualization/{id}/svg`           | `string`                      |
| `getDFGSVG(logId)`                   | `GET /visualization/{id}/dfg/svg`       | `string`                      |

```typescript
// Get all data for Process Explorer in one call
const data = await sdk.visualization.getExplorerData(logId, {
  includePerformance: true,
  includeComplexity: true,
  topVariants: 20,
});

// Use with React Flow
const nodes = data.dfg.nodes.map((n) => ({
  id: n.id,
  data: { label: n.name, frequency: n.frequency },
  position: { x: 0, y: 0 }, // layout needed
}));

const edges = data.dfg.edges.map((e) => ({
  id: `${e.source}-${e.target}`,
  source: e.source,
  target: e.target,
  label: `${e.frequency} (${(e.probability * 100).toFixed(0)}%)`,
}));
```

---

### `sdk.ocpm` — Object-Centric Process Mining

| Method                    | Endpoint                           | Return Type                |
| ------------------------- | ---------------------------------- | -------------------------- |
| `uploadOCEL(file, name?)` | `POST /ocpm/upload`                | `OCELLogResponse`          |
| `listLogs()`              | `GET /ocpm/logs`                   | `OCELLogListResponse`      |
| `getLog(logId)`           | `GET /ocpm/logs/{id}`              | `OCELLogResponse`          |
| `getObjectTypes(logId)`   | `GET /ocpm/logs/{id}/object-types` | `OCELObjectTypeResponse[]` |
| `getStatistics(logId)`    | `GET /ocpm/logs/{id}/statistics`   | `OCELStatisticsResponse`   |
| `discoverOCPN(request)`   | `POST /ocpm/discover`              | `OCPetriNetResponse`       |
| `getOCDFG(logId)`         | `GET /ocpm/logs/{id}/oc-dfg`       | `OCDFGResponse`            |

```typescript
const ocel = await sdk.ocpm.uploadOCEL(file, "Order Fulfillment");
const ocdfg = await sdk.ocpm.getOCDFG(ocel.id);

// Render separate DFG per object type
for (const [objType, graph] of Object.entries(ocdfg.graphsByType)) {
  console.log(`${objType}: ${graph.nodes.length} activities`);
}
```

---

### `sdk.org` — Organizational Mining

| Method                                | Endpoint                                              | Return Type                |
| ------------------------------------- | ----------------------------------------------------- | -------------------------- |
| `getHandoverNetwork(logId)`           | `GET /organizational/logs/{id}/handover-network`      | `SocialNetworkResponse`    |
| `getCollaborationNetwork(logId)`      | `GET /organizational/logs/{id}/collaboration-network` | `SocialNetworkResponse`    |
| `getResourceSimilarity(logId)`        | `GET /organizational/logs/{id}/resource-similarity`   | `SocialNetworkResponse`    |
| `discoverRoles(logId)`                | `GET /organizational/logs/{id}/roles`                 | `ResourceRoleResponse[]`   |
| `getResourceProfile(logId, resource)` | `GET /organizational/logs/{id}/resources/{r}/profile` | `ResourceProfileResponse`  |
| `getWorkload(logId)`                  | `GET /organizational/logs/{id}/workload`              | `ResourceWorkloadResponse` |

```typescript
const handover = await sdk.org.getHandoverNetwork(logId);

// Visualize with force-directed graph
const nodes = handover.nodes.map((n) => ({ id: n.id, label: n.label }));
const edges = handover.edges.map((e) => ({
  from: e.source,
  to: e.target,
  value: e.weight,
}));
```

---

### `sdk.simulation` — What-If Analysis

| Method                                  | Endpoint                                   | Return Type            |
| --------------------------------------- | ------------------------------------------ | ---------------------- |
| `playOut(modelId, request)`             | `POST /simulation/models/{id}/play-out`    | `PlayOutResponse`      |
| `simulate(logId, request)`              | `POST /simulation/logs/{id}/simulate`      | `SimulationResponse`   |
| `capacityPlan(logId, targetThroughput)` | `POST /simulation/logs/{id}/capacity-plan` | `CapacityPlanResponse` |

```typescript
// What-if: remove a bottleneck activity
const result = await sdk.simulation.simulate(logId, {
  modifications: [
    { type: "remove_activity", activity: "Manual Review" },
    { type: "speed_up", activity: "Approval", factor: 2.0 },
  ],
});

console.log(`Cycle time reduction: ${result.impact.cycleTimeReductionPct}%`);
```

---

## Error Handling

```typescript
import { ApiError } from "process-mining-sdk";

try {
  await sdk.logs.get("nonexistent");
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`${error.status}: ${error.problem.title}`);
    console.error(`Detail: ${error.problem.detail}`);
  }
}
```

### ApiError Properties

| Property           | Type           | Description            |
| ------------------ | -------------- | ---------------------- |
| `status`           | number         | HTTP status code       |
| `problem`          | ProblemDetails | RFC 7807 error details |
| `problem.title`    | string         | Error title            |
| `problem.detail`   | string         | Specific error message |
| `problem.instance` | string         | Request path           |

---

## Authentication

```typescript
// Sign in
await sdk.auth.signIn({ email: "user@example.com", password: "secret" });

// Check auth status
if (sdk.isAuthenticated()) {
  const user = await sdk.auth.whoAmI();
}

// Sign out
await sdk.auth.signOut();
```

**Note:** Auth is optional for development. Set `AUTH_ENABLED=false` in backend.

---

## Configuration

```typescript
interface SdkConfig {
  baseUrl: string; // Required: API base URL
  apiPrefix?: string; // Default: '/api/v1'
  timeout?: number; // Default: 30000ms
  onAuthError?: () => void; // Called on 401
}

const sdk = new ProcessMiningSdk({
  baseUrl: process.env.API_URL,
  timeout: 60000,
  onAuthError: () => {
    router.push("/login");
  },
});
```

---

## TypeScript Types

All types are exported from the package:

```typescript
import {
  EventLog,
  ProcessVariant,
  BottleneckResponse,
  DFGNode,
  DFGEdge,
  // ... all types
} from "process-mining-sdk";
```

---

## React Query Integration

```typescript
import { useQuery, useMutation } from "@tanstack/react-query";
import { ProcessMiningSdk } from "process-mining-sdk";

const sdk = new ProcessMiningSdk({ baseUrl: "/api" });

// Query hook
export function useLogStatistics(logId: string) {
  return useQuery({
    queryKey: ["logs", logId, "statistics"],
    queryFn: () => sdk.logs.analyze(logId),
    staleTime: 5 * 60 * 1000, // 5 min
  });
}

// Mutation hook
export function useDiscoverModel() {
  return useMutation({
    mutationFn: (options: DiscoverOptions) => sdk.discovery.discover(options),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["models"] }),
  });
}
```

---

## Common Patterns

### Polling Async Jobs

```typescript
async function waitForJob(jobId: string, maxWaitMs = 300000) {
  const startTime = Date.now();

  while (Date.now() - startTime < maxWaitMs) {
    const status = await sdk.predictions.getTrainingJob(jobId);

    if (status.status === "completed") return status;
    if (status.status === "failed") throw new Error(status.error);

    await new Promise((r) => setTimeout(r, 2000));
  }

  throw new Error("Job timeout");
}
```

### Paginating Results

```typescript
async function* getAllLogs() {
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const result = await sdk.logs.list({ page, pageSize: 100 });
    yield* result.items;

    hasMore = page < result.pages;
    page++;
  }
}

// Usage
for await (const log of getAllLogs()) {
  console.log(log.name);
}
```

### Caching Considerations

Analytics endpoints are cached server-side for 1 hour:

- `getBottlenecks`
- `getRework`
- `getServiceTimes`

For real-time data, use `logs.analyze()` which is not cached.
