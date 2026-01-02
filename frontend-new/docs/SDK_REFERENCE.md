# Process Mining SDK Reference

> **Package**: `@lumina/design-system`  
> **Version**: 1.0.0

---

## Overview

The Process Mining SDK provides a type-safe, React-first interface to the backend API. It includes:

- **API Modules**: Typed methods for all backend endpoints
- **React Query Hooks**: Pre-built hooks with caching and invalidation
- **Hook Factories**: Utilities for creating new hooks
- **Query Keys**: Centralized cache key management

---

## Installation & Setup

```tsx
import { SDKProvider } from '@lumina/design-system';

function App() {
  return (
    <SDKProvider baseUrl="http://localhost:8001">
      <YourApp />
    </SDKProvider>
  );
}
```

### Configuration Options

| Prop           | Type                   | Default                 | Description                |
| -------------- | ---------------------- | ----------------------- | -------------------------- |
| `baseUrl`      | `string`               | `http://localhost:8001` | Backend API base URL       |
| `getAuthToken` | `() => string \| null` | localStorage lookup     | Function to get auth token |

---

## Quick Start

### Using Pre-built Hooks

```tsx
import {
  useProcesses,
  useProcess,
  useDeleteProcess,
} from '@lumina/design-system';

function ProcessList() {
  // List all processes with pagination
  const { data, isLoading, error } = useProcesses({ pageSize: 20 });

  // Delete mutation
  const { mutate: deleteProcess, isPending } = useDeleteProcess();

  if (isLoading) return <Spinner />;
  if (error) return <Error message={error.message} />;

  return (
    <ul>
      {data?.items.map((process) => (
        <li key={process.id}>
          {process.name}
          <button onClick={() => deleteProcess(process.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

### Using SDK Directly

```tsx
import { useSDK } from '@lumina/design-system';

function UploadButton() {
  const sdk = useSDK();
  const [progress, setProgress] = useState(0);

  const handleUpload = async (file: File) => {
    const { id } = await sdk.processes.ingestWithProgress(
      file,
      { name: file.name },
      setProgress,
    );
    console.log('Uploaded:', id);
  };

  return (
    <input type="file" onChange={(e) => handleUpload(e.target.files[0])} />
  );
}
```

---

## API Modules

### processes

Event log upload, management, and statistics.

| Method                                             | Description             | Returns              |
| -------------------------------------------------- | ----------------------- | -------------------- |
| `list(options?)`                                   | List all event logs     | `PaginatedEventLogs` |
| `get(id)`                                          | Get single log details  | `EventLog`           |
| `ingest(file, metadata?)`                          | Upload file             | `{ id: string }`     |
| `ingestWithProgress(file, metadata?, onProgress?)` | Upload with progress    | `{ id: string }`     |
| `delete(id)`                                       | Delete event log        | `void`               |
| `detectColumns(file)`                              | Auto-detect CSV columns | `ColumnDetection`    |
| `analyze(logId)`                                   | Get log statistics      | `Statistics`         |

### discovery

Process model discovery and visualization.

| Method                         | Description             | Returns       |
| ------------------------------ | ----------------------- | ------------- |
| `discover(options)`            | Run process discovery   | `Model`       |
| `buildDFG(logId, options?)`    | Generate DFG            | `DFGResponse` |
| `getVariants(logId, options?)` | List process variants   | `Variant[]`   |
| `getActivities(logId)`         | List activities         | `Activity[]`  |
| `extractPetriNet(modelId)`     | Get Petri net structure | `PetriNet`    |

### analytics

Performance analytics and KPIs.

| Method                            | Description           | Returns                |
| --------------------------------- | --------------------- | ---------------------- |
| `getPerformance(logId)`           | Performance dashboard | `PerformanceDashboard` |
| `getBottlenecks(logId)`           | Detect bottlenecks    | `Bottleneck[]`         |
| `getRework(logId)`                | Analyze rework        | `ReworkAnalysis`       |
| `getCycleTime(logId)`             | Cycle time statistics | `CycleTimeStats`       |
| `getThroughput(logId)`            | Throughput metrics    | `ThroughputMetrics`    |
| `getPatterns(logId, minSupport?)` | Frequent patterns     | `Pattern[]`            |

### conformance

Conformance checking and deviation analysis.

| Method                              | Description           | Returns             |
| ----------------------------------- | --------------------- | ------------------- |
| `check(request)`                    | Run conformance check | `ConformanceResult` |
| `getDiagnostics(logId, modelId?)`   | Get diagnostics       | `Diagnostics`       |
| `getDeviations(logId, modelId?)`    | List deviations       | `Deviation[]`       |
| `getQualityMetrics(logId, modelId)` | Full quality metrics  | `QualityMetrics`    |

### predictions

ML-based predictions.

| Method                             | Description       | Returns        |
| ---------------------------------- | ----------------- | -------------- |
| `trainPredictor(logId, request)`   | Train ML model    | `Predictor`    |
| `getPredictors(logId?)`            | List predictors   | `Predictor[]`  |
| `predict(predictorId, request)`    | Make prediction   | `Prediction`   |
| `predictBatch(predictorId, cases)` | Batch predictions | `Prediction[]` |
| `deletePredictor(id)`              | Delete predictor  | `void`         |

### simulation

Process simulation and what-if analysis.

| Method                        | Description            | Returns            |
| ----------------------------- | ---------------------- | ------------------ |
| `playOut(modelId, options)`   | Generate synthetic log | `SimulatedLog`     |
| `simulate(logId, scenario)`   | Run simulation         | `SimulationResult` |
| `capacityPlan(logId, target)` | Capacity planning      | `CapacityPlan`     |

### organizational

Organizational mining and resource analysis.

| Method                                | Description           | Returns           |
| ------------------------------------- | --------------------- | ----------------- |
| `getHandoverNetwork(logId)`           | Handover of work      | `Network`         |
| `getCollaborationNetwork(logId)`      | Working together      | `Network`         |
| `getSimilarityNetwork(logId)`         | Resource similarity   | `Network`         |
| `getRoles(logId)`                     | Discovered roles      | `Role[]`          |
| `getResourceProfile(logId, resource)` | Resource profile      | `ResourceProfile` |
| `getWorkload(logId)`                  | Workload distribution | `WorkloadMetrics` |

---

## React Query Hooks

### Available Hooks

#### Processes

- `useProcesses(options?)` - Paginated process list
- `useProcess(id)` - Single process details
- `useProjectProcesses(projectId)` - Processes in a project
- `useUploadProcess()` - Upload mutation
- `useDeleteProcess()` - Delete mutation
- `useDetectColumns()` - Column detection mutation
- `useProcessStatistics(logId)` - Process statistics

#### Discovery

- `useDFG(logId, options?)` - DFG data
- `useVariants(logId, options?)` - Variant list
- `useActivities(logId)` - Activity list
- `useDiscoverProcess()` - Discovery mutation
- `useExplorerData(logId)` - Combined explorer data

#### Analytics

- `usePerformance(logId)` - Performance metrics
- `useRework(logId)` - Rework analysis
- `useBottlenecks(logId)` - Bottleneck detection
- `useCycleTime(logId)` - Cycle time stats
- `useThroughput(logId)` - Throughput metrics
- `usePatterns(logId, minSupport?)` - Frequent patterns

#### Projects

- `useProjects(options?)` - Project list
- `useProject(id)` - Single project
- `useCreateProject()` - Create mutation
- `useUpdateProject()` - Update mutation
- `useDeleteProject()` - Delete mutation

---

## Hook Factories

Create custom hooks with consistent patterns:

### createQueryHook

```tsx
import { createQueryHook, queryKeys } from '@lumina/design-system';

export const useCustomData = createQueryHook({
  queryKey: (logId: string) => ['custom', logId],
  queryFn: (sdk, logId) => sdk.analytics.getPerformance(logId),
  defaultOptions: { staleTime: 5 * 60 * 1000 },
});

// Usage
const { data, isLoading } = useCustomData('log-123');
```

### createMutationHook

```tsx
import { createMutationHook, queryKeys } from '@lumina/design-system';

export const useCustomMutation = createMutationHook({
  mutationFn: (sdk, { id, data }: { id: string; data: unknown }) =>
    sdk.processes.update(id, data),
  invalidateKeys: ({ id }) => [
    queryKeys.processes.detail(id),
    queryKeys.processes.all(),
  ],
  successMessage: 'Updated successfully',
  errorMessage: (error) => `Failed: ${error.message}`,
});

// Usage
const { mutate, isPending } = useCustomMutation();
mutate({ id: '123', data: { name: 'New Name' } });
```

### createPrefetchFn

```tsx
import { createPrefetchFn, queryKeys, useSDK } from '@lumina/design-system';
import { useQueryClient } from '@tanstack/react-query';

const prefetchProcess = createPrefetchFn({
  queryKey: (id: string) => queryKeys.processes.detail(id),
  queryFn: (sdk, id) => sdk.processes.get(id),
});

function ProcessLink({ id }: { id: string }) {
  const queryClient = useQueryClient();
  const sdk = useSDK();

  return (
    <Link
      to={`/processes/${id}`}
      onMouseEnter={() => prefetchProcess(queryClient, sdk, id)}
    >
      View Process
    </Link>
  );
}
```

---

## Query Keys

All query keys are centralized for consistency:

```tsx
import { queryKeys } from '@lumina/design-system';

// Use in custom queries
const { data } = useQuery({
  queryKey: queryKeys.processes.detail('123'),
  queryFn: () => sdk.processes.get('123'),
});

// Invalidate queries
queryClient.invalidateQueries({
  queryKey: queryKeys.processes.all(),
});
```

### Available Key Factories

```tsx
queryKeys.processes.all(); // ['processes']
queryKeys.processes.list(filters); // ['processes', 'list', filters]
queryKeys.processes.detail(id); // ['processes', id]
queryKeys.processes.statistics(id); // ['processes', id, 'statistics']

queryKeys.dfg.data(logId, options); // ['dfg', logId, options]
queryKeys.variants.list(logId); // ['variants', logId]
queryKeys.activities.list(logId); // ['activities', logId]

queryKeys.analytics.performance(logId); // ['analytics', 'performance', logId]
queryKeys.analytics.bottlenecks(logId); // ['analytics', 'bottlenecks', logId]
queryKeys.analytics.rework(logId); // ['analytics', 'rework', logId]

queryKeys.conformance.check(logId, modelId); // ['conformance', logId, modelId]
queryKeys.conformance.diagnostics(logId); // ['conformance', 'diagnostics', logId]
```

---

## Error Handling

All SDK methods throw `APIError` on failure:

```tsx
import { APIError } from '@lumina/design-system';

try {
  await sdk.processes.get('invalid-id');
} catch (error) {
  if (error instanceof APIError) {
    console.log(error.status); // 404
    console.log(error.title); // "Not Found"
    console.log(error.detail); // "Process not found: invalid-id"

    if (error.isNotFound()) {
      // Handle 404
    }
    if (error.isServerError()) {
      // Handle 5xx
    }
  }
}
```

### Error Types

```tsx
interface APIError {
  status: number; // HTTP status code
  title: string; // Error title
  detail: string; // Detailed message
  instance?: string; // Request URL

  // Helper methods
  isNetworkError(): boolean; // status === 0
  isServerError(): boolean; // 5xx
  isClientError(): boolean; // 4xx
  isNotFound(): boolean; // 404
}
```

---

## Health Checking

```tsx
const sdk = useSDK();

// Check if backend is reachable
const isHealthy = await sdk.checkHealth();

// Get cached health status (no network call)
const cachedStatus = sdk.isHealthy();
```

---

## TypeScript Support

All SDK methods are fully typed. Import types as needed:

```tsx
import type {
  EventLog,
  ProcessResponse,
  Variant,
  DFGResponse,
  ConformanceResult,
  Predictor,
} from '@lumina/design-system';
```

---

## Migration Guide

### From Raw fetch to SDK

**Before:**

```tsx
const response = await fetch('/api/v1/processes');
const data = await response.json();
```

**After:**

```tsx
const { data } = useProcesses();
// or
const data = await sdk.processes.list();
```

### From useEffect to useQuery

**Before:**

```tsx
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  fetch(`/api/v1/processes/${id}`)
    .then((res) => res.json())
    .then(setData)
    .finally(() => setLoading(false));
}, [id]);
```

**After:**

```tsx
const { data, isLoading } = useProcess(id);
```

---

## Best Practices

1. **Use hooks for React components**, SDK directly for utilities
2. **Prefetch on hover** for instant navigation
3. **Invalidate related queries** after mutations
4. **Handle loading and error states** - hooks provide `isLoading`, `error`
5. **Use query keys factory** - never hardcode query keys
