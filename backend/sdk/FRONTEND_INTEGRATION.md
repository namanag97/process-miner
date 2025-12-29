# Frontend Integration Guide

Complete guide for integrating the Process Mining SDK with React applications.

## Table of Contents

1. [Setup](#setup)
2. [React Query Integration](#react-query-integration)
3. [File Upload Patterns](#file-upload-patterns)
4. [Error Handling](#error-handling)
5. [Type Safety](#type-safety)
6. [Common Patterns](#common-patterns)

---

## Setup

### Installation

```bash
npm install @process-mining-saas/sdk @tanstack/react-query axios
```

### Environment Configuration

Create `.env` or `.env.local`:

```env
VITE_API_URL=http://localhost:8001
VITE_API_VERSION=v1
```

### SDK Configuration

```typescript
// src/lib/api.ts
import { OpenAPI } from '@process-mining-saas/sdk';

export function configureApi() {
  OpenAPI.BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';

  // Optional: Add request ID for tracing
  OpenAPI.HEADERS = {
    'X-Request-ID': () => crypto.randomUUID(),
  };
}

// Call in main.tsx before rendering
configureApi();
```

### Query Client Setup

```typescript
// src/lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';
import { ApiError } from '@process-mining-saas/sdk';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors
        if (error instanceof ApiError && error.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
    },
    mutations: {
      retry: false,
    },
  },
});
```

---

## React Query Integration

### Query Keys

```typescript
// src/lib/queryKeys.ts
export const queryKeys = {
  // Processes
  processes: {
    all: ['processes'] as const,
    lists: () => [...queryKeys.processes.all, 'list'] as const,
    list: (filters: { page?: number; sourceFormat?: string }) =>
      [...queryKeys.processes.lists(), filters] as const,
    details: () => [...queryKeys.processes.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.processes.details(), id] as const,
    statistics: (id: string) => [...queryKeys.processes.detail(id), 'statistics'] as const,
    variants: (id: string) => [...queryKeys.processes.detail(id), 'variants'] as const,
    cases: (id: string, page: number) => [...queryKeys.processes.detail(id), 'cases', page] as const,
  },

  // Discovery
  discovery: {
    all: ['discovery'] as const,
    miners: () => [...queryKeys.discovery.all, 'miners'] as const,
    models: {
      all: () => [...queryKeys.discovery.all, 'models'] as const,
      list: (logId?: string) => [...queryKeys.discovery.models.all(), { logId }] as const,
      detail: (id: string) => [...queryKeys.discovery.models.all(), id] as const,
    },
  },

  // Conformance
  conformance: {
    all: ['conformance'] as const,
    results: {
      all: () => [...queryKeys.conformance.all, 'results'] as const,
      list: (logId?: string) => [...queryKeys.conformance.results.all(), { logId }] as const,
      detail: (id: string) => [...queryKeys.conformance.results.all(), id] as const,
      diagnostics: (id: string) => [...queryKeys.conformance.results.detail(id), 'diagnostics'] as const,
    },
  },

  // Visualization
  visualization: {
    dfg: (logId: string) => ['visualization', 'dfg', logId] as const,
    petriNet: (modelId: string) => ['visualization', 'petri-net', modelId] as const,
  },

  // OCEL
  ocel: {
    all: ['ocel'] as const,
    logs: () => [...queryKeys.ocel.all, 'logs'] as const,
    log: (id: string) => [...queryKeys.ocel.logs(), id] as const,
    statistics: (id: string) => [...queryKeys.ocel.log(id), 'statistics'] as const,
  },

  // Workflows
  workflows: {
    all: ['workflows'] as const,
    templates: () => [...queryKeys.workflows.all, 'templates'] as const,
    list: () => [...queryKeys.workflows.all, 'list'] as const,
    detail: (id: string) => [...queryKeys.workflows.list(), id] as const,
    runs: (id: string) => [...queryKeys.workflows.detail(id), 'runs'] as const,
  },
} as const;
```

### Hooks

See `examples/react-query-hooks.ts` for complete implementation.

---

## File Upload Patterns

### Basic Upload Component

```typescript
// src/components/ProcessUpload.tsx
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ProcessesService, ProcessResponse, ApiError } from '@process-mining-saas/sdk';
import { queryKeys } from '../lib/queryKeys';

interface UploadState {
  progress: number;
  status: 'idle' | 'uploading' | 'success' | 'error';
  error?: string;
}

export function ProcessUpload({ onSuccess }: { onSuccess?: (process: ProcessResponse) => void }) {
  const [state, setState] = useState<UploadState>({ progress: 0, status: 'idle' });
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      setState({ progress: 0, status: 'uploading' });

      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', file.name.replace(/\.[^/.]+$/, '')); // Remove extension

      return ProcessesService.uploadProcess({ formData });
    },
    onSuccess: (data) => {
      setState({ progress: 100, status: 'success' });
      queryClient.invalidateQueries({ queryKey: queryKeys.processes.lists() });
      onSuccess?.(data);
    },
    onError: (error: ApiError) => {
      setState({
        progress: 0,
        status: 'error',
        error: error.body?.detail || 'Upload failed',
      });
    },
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  return (
    <div className="upload-container">
      <input
        type="file"
        accept=".csv,.xes"
        onChange={handleFileChange}
        disabled={state.status === 'uploading'}
      />

      {state.status === 'uploading' && (
        <div className="progress-bar">
          <div style={{ width: `${state.progress}%` }} />
        </div>
      )}

      {state.status === 'error' && (
        <div className="error">{state.error}</div>
      )}

      {state.status === 'success' && (
        <div className="success">Upload complete!</div>
      )}
    </div>
  );
}
```

### Drag and Drop Upload

```typescript
// src/components/DropzoneUpload.tsx
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ProcessesService } from '@process-mining-saas/sdk';
import { queryKeys } from '../lib/queryKeys';

export function DropzoneUpload() {
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', file.name.replace(/\.[^/.]+$/, ''));
      return ProcessesService.uploadProcess({ formData });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.processes.lists() });
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach(file => uploadMutation.mutate(file));
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/xml': ['.xes'],
    },
    maxFiles: 1,
  });

  return (
    <div
      {...getRootProps()}
      className={`dropzone ${isDragActive ? 'active' : ''}`}
    >
      <input {...getInputProps()} />
      {isDragActive ? (
        <p>Drop the file here...</p>
      ) : (
        <p>Drag & drop a CSV or XES file, or click to select</p>
      )}
    </div>
  );
}
```

---

## Error Handling

### Error Boundary

```typescript
// src/components/ApiErrorBoundary.tsx
import { Component, ReactNode } from 'react';
import { ApiError } from '@process-mining-saas/sdk';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
}

interface State {
  error: Error | null;
}

export class ApiErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  reset = () => {
    this.setState({ error: null });
  };

  render() {
    if (this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.reset);
      }

      const isApiError = this.state.error instanceof ApiError;

      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          {isApiError && (
            <p>
              Error {(this.state.error as ApiError).status}:{' '}
              {(this.state.error as ApiError).body?.detail}
            </p>
          )}
          <button onClick={this.reset}>Try again</button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Error Hook

```typescript
// src/hooks/useApiError.ts
import { useState, useCallback } from 'react';
import { ApiError } from '@process-mining-saas/sdk';

interface ApiErrorState {
  message: string;
  status: number;
  details?: Record<string, unknown>;
}

export function useApiError() {
  const [error, setError] = useState<ApiErrorState | null>(null);

  const handleError = useCallback((err: unknown) => {
    if (err instanceof ApiError) {
      setError({
        message: err.body?.detail || err.message,
        status: err.status,
        details: err.body,
      });
    } else if (err instanceof Error) {
      setError({
        message: err.message,
        status: 0,
      });
    } else {
      setError({
        message: 'An unexpected error occurred',
        status: 0,
      });
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return { error, handleError, clearError };
}
```

---

## Type Safety

### Using Enums

```typescript
import { MinerType, ConformanceMethod, SourceFormat } from '@process-mining-saas/sdk';

// Type-safe miner selection
const minerOptions = [
  { value: 'alpha', label: 'Alpha Miner' },
  { value: 'inductive', label: 'Inductive Miner' },
  { value: 'heuristics', label: 'Heuristics Miner' },
  { value: 'dfg', label: 'DFG' },
] as const;

// Use in component
function MinerSelect({ value, onChange }: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <select value={value} onChange={e => onChange(e.target.value)}>
      {minerOptions.map(opt => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  );
}
```

### Response Type Inference

```typescript
import { ProcessesService } from '@process-mining-saas/sdk';

// Types are automatically inferred
async function example() {
  const list = await ProcessesService.listProcesses({ page: 1 });
  // list: ProcessListResponse
  // list.items: ProcessResponse[]

  const process = await ProcessesService.getProcess({ processId: 'abc' });
  // process: ProcessDetailResponse

  const stats = await ProcessesService.getStatistics({ processId: 'abc' });
  // stats: StatisticsResponse
  // stats.activities: string[]
  // stats.start_activities: Record<string, number>
}
```

---

## Common Patterns

### Optimistic Updates

```typescript
const deleteMutation = useMutation({
  mutationFn: (id: string) => ProcessesService.deleteProcess({ processId: id }),
  onMutate: async (id) => {
    await queryClient.cancelQueries({ queryKey: queryKeys.processes.lists() });

    const previous = queryClient.getQueryData(queryKeys.processes.list({}));

    queryClient.setQueryData(queryKeys.processes.list({}), (old: any) => ({
      ...old,
      items: old?.items?.filter((p: any) => p.id !== id) ?? [],
    }));

    return { previous };
  },
  onError: (err, id, context) => {
    queryClient.setQueryData(queryKeys.processes.list({}), context?.previous);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.processes.lists() });
  },
});
```

### Polling for Long Operations

```typescript
function useWorkflowRun(runId: string) {
  return useQuery({
    queryKey: ['workflow-run', runId],
    queryFn: () => WorkflowsService.getWorkflowRun({ runId }),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      // Poll every 2 seconds while running
      if (status === 'running' || status === 'pending') {
        return 2000;
      }
      return false; // Stop polling when complete
    },
  });
}
```

### Prefetching

```typescript
function ProcessList() {
  const queryClient = useQueryClient();
  const { data } = useProcesses();

  // Prefetch details on hover
  const prefetchProcess = (id: string) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.processes.detail(id),
      queryFn: () => ProcessesService.getProcess({ processId: id }),
      staleTime: 60 * 1000,
    });
  };

  return (
    <ul>
      {data?.items.map(process => (
        <li
          key={process.id}
          onMouseEnter={() => prefetchProcess(process.id)}
        >
          {process.name}
        </li>
      ))}
    </ul>
  );
}
```

### Infinite Scroll

```typescript
function useCasesInfinite(processId: string) {
  return useInfiniteQuery({
    queryKey: ['processes', processId, 'cases'],
    queryFn: ({ pageParam = 1 }) =>
      ProcessesService.listCases({
        processId,
        page: pageParam,
        pageSize: 50,
      }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.pages) {
        return lastPage.page + 1;
      }
      return undefined;
    },
  });
}
```

---

## Troubleshooting

### CORS Issues

If you see CORS errors in development:

1. Ensure the backend is running with correct origins:
   ```python
   # src/core/config.py
   allowed_origins: list[str] = [
       "http://localhost:3000",
       "http://localhost:5173",
   ]
   ```

2. Check that credentials are handled correctly:
   ```typescript
   OpenAPI.WITH_CREDENTIALS = true;
   ```

### Request ID Tracing

Add request IDs for debugging:

```typescript
OpenAPI.HEADERS = {
  'X-Request-ID': () => crypto.randomUUID(),
};

// In browser dev tools, match X-Request-ID header with backend logs
```

### Type Mismatches

If types don't match the API:

1. Regenerate the SDK: `npm run generate && npm run build`
2. Check API version matches SDK version
3. Clear node_modules and reinstall: `rm -rf node_modules && npm install`
