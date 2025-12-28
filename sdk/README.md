# Process Mining SDK

A TypeScript SDK for the Process Mining Platform API with business-focused method names following CodeOpinion guidance.

## Installation

```bash
npm install process-mining-sdk
```

## Quick Start

```typescript
import { ProcessMiningSdk } from "process-mining-sdk";

// Initialize SDK
const sdk = new ProcessMiningSdk({
  baseUrl: "http://localhost:8001",
});

// Sign in
await sdk.auth.signIn({ email: "user@example.com", password: "test" });

// Ingest event log
const log = await sdk.logs.ingest(file, { name: "Order Process" });

// Discover process model
const model = await sdk.discovery.discover({
  logId: log.id,
  minerType: "inductive",
});

// Check conformance
const result = await sdk.conformance.check({
  logId: log.id,
  modelId: model.modelId,
});

// Find bottlenecks
const bottlenecks = await sdk.performance.findBottlenecks(log.id);

// Get dashboard
const dashboard = await sdk.analytics.getDashboard(log.id);
```

## API Clients

The SDK provides 13 domain-specific clients with business-focused method names:

| Client          | Purpose               | Key Methods                                                                      |
| --------------- | --------------------- | -------------------------------------------------------------------------------- |
| `auth`          | Authentication        | `signIn()`, `signOut()`, `whoAmI()`                                              |
| `logs`          | Event Logs            | `ingest()`, `analyze()`, `assessQuality()`, `listVariants()`                     |
| `discovery`     | Process Discovery     | `discover()`, `buildDFG()`, `extractPetriNet()`, `evaluateQuality()`             |
| `conformance`   | Conformance Checking  | `check()`, `measureFitness()`, `computeAlignments()`, `findDeviations()`         |
| `performance`   | Performance Analysis  | `analyze()`, `findBottlenecks()`, `summarize()`, `measureActivityPerformance()`  |
| `analytics`     | Analytics             | `getDashboard()`, `discoverInsights()`, `detectAnomalies()`, `analyzeVariants()` |
| `ocpm`          | Object-Centric PM     | `ingest()`, `discoverOCPN()`, `listObjectTypes()`, `analyze()`                   |
| `org`           | Organizational Mining | `profileResources()`, `buildHandoverNetwork()`, `discoverRoles()`                |
| `models`        | Model Management      | `list()`, `get()`, `visualize()`, `remove()`                                     |
| `workflows`     | Workflows             | `start()`, `listPipelines()`, `getExecution()`, `cancel()`                       |
| `notifications` | Notifications         | `send()`, `subscribe()`, `configure()`                                           |
| `integrations`  | Integrations          | `createConnector()`, `sync()`, `fetchData()`                                     |
| `processMining` | PM4Py Features        | `analyzeFootprints()`, `extractLogSkeleton()`, `analyzeSNA()`                    |

## Business Verb Naming Convention

Following [CodeOpinion](https://codeopinion.com) guidance, method names use business verbs instead of CRUD operations:

| CRUD Style           | Business Verb Style |
| -------------------- | ------------------- |
| `createLog()`        | `ingest()`          |
| `getLogStatistics()` | `analyze()`         |
| `getQualityReport()` | `assessQuality()`   |
| `createModel()`      | `discover()`        |
| `getBottlenecks()`   | `findBottlenecks()` |
| `getFitness()`       | `measureFitness()`  |

## Error Handling

The SDK uses RFC 7807 Problem Details for errors:

```typescript
import { ApiError } from "process-mining-sdk";

try {
  await sdk.logs.get("invalid-id");
} catch (error) {
  if (error instanceof ApiError) {
    console.log(error.status); // 404
    console.log(error.problem.title); // "Event log not found"
    console.log(error.problem.type); // "about:blank"
  }
}
```

## Building

```bash
cd sdk
npm install
npm run build
```

## License

MIT
