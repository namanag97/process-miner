# Frontend Integration Guide - Real-Time Operations API

## Overview

The Operations API provides real-time workflow progress tracking via Server-Sent Events (SSE).
This replaces the legacy DAG system with Temporal-powered workflows.

## Quick Start

### 1. Start a Long-Running Operation

```typescript
// Start dataset ingestion
const response = await fetch('/api/v1/datasets/ingest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    dataset_id: datasetId,
    column_mapping: { case_id: 'CaseID', activity: 'Activity', timestamp: 'Timestamp' }
  })
});

const { workflow_id } = await response.json();
// workflow_id = "ingest-dataset-abc123-def456"
```

### 2. Subscribe to Real-Time Progress

```typescript
function subscribeToProgress(workflowId: string, onProgress: (data: ProgressEvent) => void) {
  const eventSource = new EventSource(`/api/v1/operations/${workflowId}/stream`);

  // Initial state
  eventSource.addEventListener('workflow:progress', (event) => {
    const data = JSON.parse(event.data);
    onProgress(data);
  });

  // Step progress updates
  eventSource.addEventListener('step:progress', (event) => {
    const data = JSON.parse(event.data);
    onProgress(data);
  });

  // Completion
  eventSource.addEventListener('workflow:completed', (event) => {
    const data = JSON.parse(event.data);
    onProgress({ ...data, status: 'completed' });
    eventSource.close();
  });

  // Failure
  eventSource.addEventListener('workflow:failed', (event) => {
    const data = JSON.parse(event.data);
    onProgress({ ...data, status: 'failed' });
    eventSource.close();
  });

  // Error handling
  eventSource.onerror = () => {
    // Reconnect after 3 seconds
    setTimeout(() => subscribeToProgress(workflowId, onProgress), 3000);
  };

  return () => eventSource.close();
}
```

### 3. React Hook Example

```typescript
import { useEffect, useState } from 'react';

interface ProgressState {
  progress: number;
  currentStep: string;
  status: 'running' | 'completed' | 'failed';
  details?: Record<string, any>;
  error?: string;
}

export function useWorkflowProgress(workflowId: string | null): ProgressState | null {
  const [progress, setProgress] = useState<ProgressState | null>(null);

  useEffect(() => {
    if (!workflowId) return;

    const eventSource = new EventSource(`/api/v1/operations/${workflowId}/stream`);

    const handleProgress = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      setProgress({
        progress: data.progress,
        currentStep: data.step,
        status: 'running',
        details: data.details,
      });
    };

    const handleCompleted = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      setProgress(prev => prev ? { ...prev, status: 'completed', progress: 100 } : null);
      eventSource.close();
    };

    const handleFailed = (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      setProgress(prev => prev ? {
        ...prev,
        status: 'failed',
        error: data.details?.error || data.error
      } : null);
      eventSource.close();
    };

    eventSource.addEventListener('workflow:progress', handleProgress);
    eventSource.addEventListener('step:progress', handleProgress);
    eventSource.addEventListener('step:started', handleProgress);
    eventSource.addEventListener('step:completed', handleProgress);
    eventSource.addEventListener('workflow:completed', handleCompleted);
    eventSource.addEventListener('workflow:failed', handleFailed);

    return () => eventSource.close();
  }, [workflowId]);

  return progress;
}

// Usage:
function IngestionProgress({ workflowId }: { workflowId: string }) {
  const progress = useWorkflowProgress(workflowId);

  if (!progress) return <Spinner />;

  return (
    <div>
      <Progress percent={progress.progress} />
      <div>Step: {progress.currentStep}</div>
      {progress.status === 'failed' && <Alert type="error" message={progress.error} />}
      {progress.status === 'completed' && <Alert type="success" message="Complete!" />}
    </div>
  );
}
```

---

## API Reference

### GET /api/v1/operations/{workflow_id}/stream

Subscribe to real-time progress updates for a workflow.

**Response**: `text/event-stream` (Server-Sent Events)

#### Event Types

| Event | Description | When |
|-------|-------------|------|
| `workflow:progress` | Overall workflow progress | On connect, periodically |
| `step:started` | Activity step started | When step begins |
| `step:progress` | Progress within a step | During long steps |
| `step:completed` | Activity step completed | When step finishes |
| `step:failed` | Activity step failed | On step error |
| `workflow:completed` | Workflow finished | On success (stream closes) |
| `workflow:failed` | Workflow failed | On error (stream closes) |

#### Event Data Schema

```typescript
interface ProgressEvent {
  workflow_id: string;        // e.g., "ingest-dataset-abc123"
  event: string;              // Event type
  step: string;               // Current step name
  progress: number;           // 0-100 percentage
  timestamp: string;          // ISO 8601 timestamp
  details: {
    status?: string;          // Temporal status (RUNNING, COMPLETED, etc.)
    started_at?: string;      // Workflow start time
    phase?: string;           // Sub-step within activity
    total_events?: number;    // Events processed (ingestion)
    total_cases?: number;     // Cases processed (ingestion)
    error?: string;           // Error message (on failure)
    [key: string]: any;       // Additional step-specific data
  };
}
```

### GET /api/v1/operations/{workflow_id}

Get current workflow status (polling alternative).

**Response**:
```json
{
  "workflow_id": "ingest-dataset-abc123",
  "status": "RUNNING",
  "started_at": "2024-01-15T10:30:00Z",
  "progress": {
    "progress": 45,
    "current_step": "parse_to_parquet",
    "total_events": 5000,
    "total_cases": 100
  }
}
```

### POST /api/v1/operations/{workflow_id}/cancel

Cancel a running workflow.

**Response**:
```json
{
  "workflow_id": "ingest-dataset-abc123",
  "status": "cancellation_requested"
}
```

---

## Workflow ID Patterns

| Operation | Workflow ID Pattern | Example |
|-----------|---------------------|---------|
| Dataset Ingestion | `ingest-dataset-{dataset_id}` | `ingest-dataset-abc123` |
| Dataset Validation | `validate-dataset-{dataset_id}` | `validate-dataset-abc123` |
| Process Discovery | `discover-{dataset_id}-{miner}` | `discover-abc123-inductive` |
| Conformance Check | `conformance-{dataset_id}-{model_id}` | `conformance-abc123-model456` |
| Quality Evaluation | `quality-{model_id}-{dataset_id}` | `quality-model456-abc123` |

---

## Step Names Reference

### Dataset Ingestion Steps

| Step | Progress Range | Description |
|------|----------------|-------------|
| `validate_file` | 5-15% | Checking file format |
| `parse_to_parquet` | 15-80% | Converting to Parquet |
| `compute_statistics` | 80-100% | Computing metadata |
| `completed` | 100% | Success |
| `failed` | - | Error occurred |

### Process Discovery Steps

| Step | Progress Range | Description |
|------|----------------|-------------|
| `load_event_log` | 10-20% | Loading dataset |
| `mine_model` | 20-70% | Running discovery algorithm |
| `compute_metrics` | 70-100% | Computing fitness/precision |
| `completed` | 100% | Success |

### Conformance Check Steps

| Step | Progress Range | Description |
|------|----------------|-------------|
| `load_event_log` | 10-30% | Loading dataset |
| `check_conformance` | 30-100% | Running conformance check |
| `completed` | 100% | Success |

---

## Error Handling

### Connection Errors

```typescript
eventSource.onerror = (error) => {
  console.error('SSE connection error:', error);

  // Check if stream ended normally or due to error
  if (eventSource.readyState === EventSource.CLOSED) {
    // Stream closed - check final status via REST API
    fetch(`/api/v1/operations/${workflowId}`)
      .then(res => res.json())
      .then(data => {
        if (data.status !== 'COMPLETED') {
          // Reconnect if still running
          setTimeout(() => reconnect(), 3000);
        }
      });
  }
};
```

### Workflow Failures

```typescript
eventSource.addEventListener('workflow:failed', (event) => {
  const { error, details } = JSON.parse(event.data);

  // Show user-friendly error
  notification.error({
    message: 'Operation Failed',
    description: error || 'An unexpected error occurred',
  });

  // Log details for debugging
  console.error('Workflow failed:', details);

  eventSource.close();
});
```

---

## TypeScript Types

```typescript
// Event types
type ProgressEventType =
  | 'workflow:progress'
  | 'step:started'
  | 'step:progress'
  | 'step:completed'
  | 'step:failed'
  | 'workflow:completed'
  | 'workflow:failed';

// Status types
type WorkflowStatus =
  | 'RUNNING'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED'
  | 'TERMINATED'
  | 'TIMED_OUT';

// Step names
type IngestionStep =
  | 'initializing'
  | 'validate_file'
  | 'parse_to_parquet'
  | 'compute_statistics'
  | 'completed'
  | 'failed';

type DiscoveryStep =
  | 'initializing'
  | 'load_event_log'
  | 'mine_model'
  | 'compute_metrics'
  | 'completed'
  | 'failed';

type ConformanceStep =
  | 'initializing'
  | 'load_event_log'
  | 'check_conformance'
  | 'completed'
  | 'failed';

// Full event interface
interface WorkflowProgressEvent {
  workflow_id: string;
  event: ProgressEventType;
  step: string;
  progress: number;
  timestamp: string;
  details: {
    status?: WorkflowStatus;
    started_at?: string;
    phase?: string;
    total_events?: number;
    total_cases?: number;
    total_activities?: number;
    parquet_s3_key?: string;
    error?: string;
    poll_mode?: boolean;
  };
}
```

---

## Migration from Legacy DAG API

If you were using the `/api/v1/dags` endpoints:

| Old Endpoint | New Endpoint | Notes |
|--------------|--------------|-------|
| `POST /dags/run` | `POST /datasets/ingest` | Returns `workflow_id` |
| `GET /dags/runs/{id}` | `GET /operations/{workflow_id}` | Use workflow_id |
| `GET /dags/runs/{id}/status` | `GET /operations/{workflow_id}/stream` | SSE streaming |
| `POST /dags/runs/{id}/cancel` | `POST /operations/{workflow_id}/cancel` | Same behavior |

---

## Best Practices

1. **Always close EventSource** when component unmounts
2. **Implement reconnection logic** for network interruptions
3. **Use debouncing** for progress bar updates (avoid excessive re-renders)
4. **Cache workflow_id** in localStorage for page refreshes
5. **Poll REST API** as fallback if SSE fails

```typescript
// Debounced progress updates
const [progress, setProgress] = useState(0);
const debouncedSetProgress = useMemo(
  () => debounce((value: number) => setProgress(value), 100),
  []
);

eventSource.addEventListener('step:progress', (event) => {
  const data = JSON.parse(event.data);
  debouncedSetProgress(data.progress);
});
```
