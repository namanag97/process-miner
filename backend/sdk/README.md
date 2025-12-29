# @process-mining-saas/sdk

TypeScript SDK for the Process Mining API. Auto-generated from OpenAPI spec for full type safety.

## Installation

```bash
npm install @process-mining-saas/sdk
# or
yarn add @process-mining-saas/sdk
# or
pnpm add @process-mining-saas/sdk
```

## Quick Start

```typescript
import { ProcessesService, DiscoveryService, OpenAPI } from '@process-mining-saas/sdk';

// Configure the API base URL
OpenAPI.BASE = 'http://localhost:8001';

// List all processes
const processes = await ProcessesService.listProcesses();
console.log(processes.items);

// Upload a file
const formData = new FormData();
formData.append('file', file);
formData.append('name', 'My Event Log');

const uploaded = await ProcessesService.uploadProcess({ formData });
console.log(`Uploaded: ${uploaded.id}`);

// Discover a model
const model = await DiscoveryService.discoverModel({
  requestBody: {
    log_id: uploaded.id,
    miner_type: 'inductive',
  },
});
console.log(`Model fitness: ${model.fitness}`);
```

## Configuration

### Base URL

```typescript
import { OpenAPI } from '@process-mining-saas/sdk';

// Development
OpenAPI.BASE = 'http://localhost:8001';

// Production
OpenAPI.BASE = 'https://api.your-domain.com';
```

### Authentication (when enabled)

```typescript
import { OpenAPI } from '@process-mining-saas/sdk';

OpenAPI.TOKEN = 'your-jwt-token';
// or
OpenAPI.TOKEN = async () => {
  return await getTokenFromStorage();
};
```

### Request/Response Interceptors

```typescript
import { OpenAPI } from '@process-mining-saas/sdk';

// Add request headers
OpenAPI.HEADERS = {
  'X-Request-ID': crypto.randomUUID(),
};

// Custom error handling
OpenAPI.WITH_CREDENTIALS = true;
```

## Available Services

| Service | Description |
|---------|-------------|
| `ProcessesService` | Upload, list, manage event logs |
| `DiscoveryService` | Run mining algorithms, manage models |
| `VisualizationService` | Generate DFGs, Petri nets, SVGs |
| `ConformanceService` | Check conformance, get diagnostics |
| `OcpmService` | OCEL 2.0 support, object-centric mining |
| `WorkflowsService` | Pipeline automation |

## Type Exports

All Pydantic schemas are exported as TypeScript interfaces:

```typescript
import type {
  ProcessResponse,
  ProcessListResponse,
  ModelResponse,
  ConformanceResponse,
  DFGResponse,
  // ... 40+ more types
} from '@process-mining-saas/sdk';
```

## Examples

### List Processes with Pagination

```typescript
const { items, total, pages } = await ProcessesService.listProcesses({
  page: 1,
  pageSize: 10,
  sourceFormat: 'csv',
});
```

### Get Process Statistics

```typescript
const stats = await ProcessesService.getStatistics({
  processId: 'abc-123',
});

console.log(`Total events: ${stats.total_events}`);
console.log(`Variants: ${stats.total_variants}`);
console.log(`Activities: ${stats.activities.join(', ')}`);
```

### Discover and Visualize

```typescript
// Discover a model
const model = await DiscoveryService.discoverModel({
  requestBody: {
    log_id: processId,
    miner_type: 'inductive',
  },
});

// Get DFG visualization data
const dfg = await VisualizationService.generateDfg({
  logId: processId,
});

// Use dfg.nodes and dfg.edges for React Flow, D3, etc.
```

### Conformance Checking

```typescript
const result = await ConformanceService.checkConformance({
  requestBody: {
    log_id: processId,
    model_id: modelId,
    method: 'token_replay',
  },
});

if (result.is_conformant) {
  console.log(`Fitness: ${result.fitness}`);
} else {
  const diagnostics = await ConformanceService.getDiagnostics({
    resultId: result.id,
  });
  console.log(`Non-fitting traces: ${diagnostics.non_fitting_traces}`);
}
```

## Error Handling

```typescript
import { ApiError } from '@process-mining-saas/sdk';

try {
  await ProcessesService.getProcess({ processId: 'invalid' });
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`API Error ${error.status}: ${error.body?.detail}`);
  }
}
```

## Development

### Regenerate SDK

The SDK is auto-generated from the OpenAPI spec. To regenerate:

```bash
# Start the API server
cd .. && uvicorn src.api.main:app --port 8001

# Generate SDK
npm run generate
npm run build
```

### Local Development

```bash
# Link for local testing
npm link

# In your frontend project
npm link @process-mining-saas/sdk
```

## Integration Guide

See [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) for detailed React integration patterns, including:

- React Query hooks
- File upload components
- Error boundary integration
- State management patterns

## License

MIT
