# Temporal DAG & Real-Time Streaming Architecture Plan

## Executive Summary

You have **two parallel systems** that should be unified:
1. **Custom DAG Engine** (`src/platform/dag/`) - Not connected to anything
2. **Temporal Workflows** - Partially implemented (v1 vs v2)
3. **SSE Streaming** - Exists but not connected to Temporal

**Current State**: Temporal workflows run, but clients must poll `/operations/{id}` for status. Real-time streaming exists but isn't wired to Temporal.

---

## Current Architecture Analysis

### What You Have

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CURRENT STATE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐      ┌─────────────────┐      ┌───────────────────┐       │
│  │   Frontend   │─────▶│ /operations/{id}│─────▶│     Temporal      │       │
│  │   (Polling)  │      │    (REST API)   │      │    (Workflows)    │       │
│  └──────────────┘      └─────────────────┘      └───────────────────┘       │
│         │                                                │                   │
│         │              ┌─────────────────┐               │                   │
│         └─────────────▶│ /jobs/{id}/stream│              │ (NOT CONNECTED)  │
│         (SSE - unused) │    (SSE API)    │               │                   │
│                        └─────────────────┘               ▼                   │
│                               │                  ┌───────────────────┐       │
│                               │                  │   Redis Pub/Sub   │       │
│                               └─────────────────▶│  (EventStream)    │       │
│                                  (reads from)    └───────────────────┘       │
│                                                          ▲                   │
│                                                          │                   │
│                                                  (NOTHING PUBLISHES HERE)    │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    UNUSED: Custom DAG Engine                          │   │
│  │    src/platform/dag/ - Engine, Executor, Registry, Models            │   │
│  │    (Not connected to Temporal or any workflow orchestration)          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Files Analyzed

| Component | File | Status |
|-----------|------|--------|
| Temporal Workflows v1 | `src/platform/temporal/workflows/ingestion.py` | ❌ No query handlers |
| Temporal Workflows v2 | `src/platform/temporal/workflows_v2/ingestion.py` | ✅ Has `get_progress` query |
| Operations API | `src/api/routers/operations.py` | ✅ Queries Temporal |
| Jobs SSE Stream | `src/platform/jobs/router.py` | ⚠️ Reads Redis, but nothing publishes |
| Event Stream Manager | `src/features/process_mining/services/ingestion/stream.py` | ✅ Redis pub/sub ready |
| Custom DAG Engine | `src/platform/dag/engine.py` | ❌ Unused, not connected |
| DAG Executor | `src/platform/dag/executor.py` | ❌ Unused |

---

## Gap Analysis

### Critical Gaps

| # | Gap | Impact | Priority |
|---|-----|--------|----------|
| 1 | **v1 workflows lack progress query handlers** | Operations API fails to get progress | High |
| 2 | **Temporal activities don't publish to Redis** | SSE streaming is dead | High |
| 3 | **No WebSocket support** | Clients must poll or use one-way SSE | Medium |
| 4 | **DAG system disconnected** | Wasted code, confusing architecture | Medium |
| 5 | **Dual v1/v2 workflow systems** | Confusion about which to use | High |

### What's Working vs Not Working

| Feature | Status | Details |
|---------|--------|---------|
| Temporal workflow execution | ✅ Working | Workflows run and complete |
| Progress via query handlers | ⚠️ Partial | Only v2 workflows have them |
| Operations API status | ✅ Working | Polls Temporal directly |
| SSE job streaming | ❌ Dead | Nothing publishes to Redis |
| Custom DAG orchestration | ❌ Unused | Not connected to anything |
| Real-time frontend updates | ❌ Missing | Only polling works |

---

## Target Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TARGET STATE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐                                                           │
│  │   Frontend   │◀──────────────────────────────────────────────┐           │
│  └──────┬───────┘                                               │           │
│         │                                                       │           │
│         │  Option A: SSE (one-way, simpler)                    │           │
│         │  Option B: WebSocket (bi-directional)                │           │
│         ▼                                                       │           │
│  ┌──────────────────────────────────────────────────────────┐  │           │
│  │              API Layer                                    │  │           │
│  │  ┌────────────────┐  ┌─────────────────┐                 │  │           │
│  │  │ POST /ingest   │  │ GET /operations │                 │  │           │
│  │  │ (starts flow)  │  │ /{id}/stream    │◀────────────────┼──┘           │
│  │  └───────┬────────┘  └────────┬────────┘                 │              │
│  └──────────┼────────────────────┼──────────────────────────┘              │
│             │                    │                                          │
│             ▼                    ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Temporal                                      │  │
│  │  ┌──────────────────────────────────────────────────────────────┐    │  │
│  │  │  DatasetIngestionWorkflow (unified v2)                        │    │  │
│  │  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐       │    │  │
│  │  │  │Validate │──▶│ Chunk 1 │──▶│ Chunk N │──▶│Finalize │       │    │  │
│  │  │  └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘       │    │  │
│  │  │       │              │              │              │          │    │  │
│  │  │       └──────────────┴──────────────┴──────────────┘          │    │  │
│  │  │                         │                                      │    │  │
│  │  │                         ▼ (each activity publishes)            │    │  │
│  │  │              ┌─────────────────────┐                           │    │  │
│  │  │              │   @workflow.query   │◀── Operations API polls   │    │  │
│  │  │              │   get_progress()    │                           │    │  │
│  │  │              └─────────────────────┘                           │    │  │
│  │  └──────────────────────────────────────────────────────────────┘    │  │
│  │                              │                                        │  │
│  │                              ▼                                        │  │
│  │                    ┌─────────────────┐                               │  │
│  │                    │   Redis Pub/Sub │──────▶ SSE/WebSocket to FE   │  │
│  │                    │  (event_stream) │                               │  │
│  │                    └─────────────────┘                               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  REMOVED: Custom DAG Engine (replaced by Temporal's native DAG)      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Unify Workflows (High Priority)

**Goal**: Single workflow version with progress tracking

#### 1.1 Migrate all workflows to v2 pattern

```python
# BEFORE (v1 - no progress tracking)
@workflow.defn
class DatasetIngestionWorkflow:
    @workflow.run
    async def run(self, dataset_id: str, ...):
        # No state, no query handlers
        await workflow.execute_activity(validate_file, ...)
        await workflow.execute_activity(parse_to_parquet, ...)

# AFTER (v2 - with progress)
@workflow.defn
class DatasetIngestionWorkflow:
    def __init__(self):
        self._progress = IngestionProgress()

    @workflow.query
    def get_progress(self) -> dict:
        """Query handler - survives worker restarts."""
        return asdict(self._progress)

    @workflow.signal
    async def cancel_requested(self):
        """Signal handler - allows external cancellation."""
        self._cancel_requested = True

    @workflow.run
    async def run(self, dataset_id: str, ...):
        self._progress.current_step = "validating"
        self._progress.percent = 10
        # ...
```

**Files to modify**:
- Delete `src/platform/temporal/workflows/` (v1)
- Move `src/platform/temporal/workflows_v2/` to `src/platform/temporal/workflows/`
- Update all imports

#### 1.2 Add query handlers to ALL workflows

Every workflow must have:
```python
@workflow.query
def get_progress(self) -> dict:
    return {
        "progress": self._progress,
        "current_step": self._current_step,
        "total_steps": self._total_steps,
        "error": self._error,
        "started_at": self._started_at,
        "eta_seconds": self._compute_eta(),
    }
```

---

### Phase 2: Wire Activities to Redis Pub/Sub (High Priority)

**Goal**: Real-time updates flow from Temporal to clients

#### 2.1 Create activity progress publisher

```python
# src/platform/temporal/activities/progress.py

from src.features.process_mining.services.ingestion.stream import event_stream_manager

async def publish_activity_progress(
    user_id: str,
    workflow_id: str,
    step: str,
    progress: int,
    details: dict | None = None,
):
    """Publish progress from activity to Redis for SSE streaming."""
    await event_stream_manager.publish_event(
        user_id=user_id,
        job_id=workflow_id,  # Use workflow_id as job_id
        event_type=EventType.JOB_PROGRESS,
        data={
            "step": step,
            "progress": progress,
            "details": details or {},
        },
    )
```

#### 2.2 Update activities to publish progress

```python
# BEFORE
@activity.defn
async def parse_to_parquet_activity(input: ParseToParquetInput) -> ParseResult:
    # Just does work, no progress publishing
    for chunk in chunks:
        activity.heartbeat(f"Processing chunk {i}")
        process_chunk(chunk)
    return result

# AFTER
@activity.defn
async def parse_to_parquet_activity(input: ParseToParquetInput) -> ParseResult:
    for i, chunk in enumerate(chunks):
        # 1. Heartbeat to Temporal (prevents timeout)
        activity.heartbeat(f"chunk_{i}")

        # 2. Publish to Redis (real-time frontend updates)
        await publish_activity_progress(
            user_id=input.user_id,
            workflow_id=f"ingest-dataset-{input.dataset_id}",
            step="parsing",
            progress=int((i + 1) / len(chunks) * 100),
            details={"chunk": i + 1, "total_chunks": len(chunks)},
        )

        process_chunk(chunk)
    return result
```

---

### Phase 3: Unified Operations Streaming Endpoint (Medium Priority)

**Goal**: Single endpoint for real-time workflow status

#### 3.1 Create unified SSE endpoint

```python
# src/api/routers/operations.py

@router.get("/{workflow_id}/stream")
async def stream_operation_progress(
    request: Request,
    workflow_id: str,
    user: CurrentUser,
):
    """SSE stream for real-time workflow progress.

    Combines:
    1. Initial state from Temporal query
    2. Real-time updates from Redis pub/sub
    3. Final result when workflow completes
    """
    async def event_generator():
        # 1. Send initial state from Temporal
        try:
            client = await get_temporal_client()
            handle = client.get_workflow_handle(workflow_id)
            progress = await handle.query("get_progress")
            yield SSEEvent(EventType.JOB_PROGRESS, progress).to_sse_format()
        except Exception:
            pass

        # 2. Subscribe to Redis for real-time updates
        async for event in event_stream_manager.subscribe(user.id, workflow_id):
            if await request.is_disconnected():
                break
            yield event

            # Check if workflow completed
            if "completed" in event or "failed" in event:
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

#### 3.2 Frontend integration

```typescript
// Frontend: Real-time workflow tracking
function useWorkflowProgress(workflowId: string) {
  const [progress, setProgress] = useState<ProgressState | null>(null);

  useEffect(() => {
    const eventSource = new EventSource(
      `/api/v1/operations/${workflowId}/stream`
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data);
    };

    eventSource.addEventListener('job:completed', (event) => {
      setProgress({ ...JSON.parse(event.data), status: 'completed' });
      eventSource.close();
    });

    eventSource.addEventListener('job:failed', (event) => {
      setProgress({ ...JSON.parse(event.data), status: 'failed' });
      eventSource.close();
    });

    return () => eventSource.close();
  }, [workflowId]);

  return progress;
}
```

---

### Phase 4: Remove Custom DAG System (Medium Priority)

**Goal**: Clean architecture, no dead code

#### 4.1 Decision: Temporal IS the DAG engine

Temporal natively supports:
- Step dependencies (activity sequencing)
- Parallel execution (`asyncio.gather` in workflows)
- Failure handling and compensation
- Progress tracking via queries

**Your custom DAG engine duplicates this**.

#### 4.2 Migration path

```bash
# Files to remove
rm -rf src/platform/dag/

# Update any references (if any)
grep -r "from src.platform.dag" src/
```

If the DAG system is used somewhere, migrate to Temporal child workflows:

```python
# BEFORE: Custom DAG
dag_run = await dag_service.create_run(dag_definition, context)
await dag_executor.run_to_completion(dag_run.id)

# AFTER: Temporal child workflows
@workflow.defn
class PipelineWorkflow:
    @workflow.run
    async def run(self, pipeline_config: dict):
        # Temporal handles DAG natively
        results = await asyncio.gather(
            workflow.execute_child_workflow(StepAWorkflow.run, ...),
            workflow.execute_child_workflow(StepBWorkflow.run, ...),
        )
        # StepC depends on A and B
        await workflow.execute_child_workflow(StepCWorkflow.run, results)
```

---

### Phase 5: Optional - WebSocket for Bi-Directional (Low Priority)

**When to add WebSocket**:
- User needs to send commands during workflow (pause/resume/cancel)
- Real-time collaboration features
- Chat-like interactions

**SSE is sufficient for**:
- Progress updates (one-way)
- Status notifications
- Simple real-time dashboards

If needed, add WebSocket:

```python
# src/api/routers/ws.py
from fastapi import WebSocket

@router.websocket("/ws/operations/{workflow_id}")
async def websocket_operation(websocket: WebSocket, workflow_id: str):
    await websocket.accept()

    # Bi-directional communication
    async def send_progress():
        async for event in event_stream_manager.subscribe(user_id, workflow_id):
            await websocket.send_text(event)

    async def receive_commands():
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "cancel":
                await cancel_workflow(workflow_id)

    await asyncio.gather(send_progress(), receive_commands())
```

---

## Summary: Action Items

| Phase | Task | Files | Effort |
|-------|------|-------|--------|
| **1.1** | Migrate v1 → v2 workflows | `src/platform/temporal/workflows/` | 2 days |
| **1.2** | Add query handlers to all workflows | All workflow files | 1 day |
| **2.1** | Create activity progress publisher | New file | 0.5 day |
| **2.2** | Wire activities to publish progress | All activity files | 2 days |
| **3.1** | Create unified SSE endpoint | `operations.py` | 1 day |
| **3.2** | Frontend SSE integration | Frontend hooks | 1 day |
| **4.1** | Remove custom DAG system | Delete `src/platform/dag/` | 0.5 day |
| **5** | WebSocket (optional) | New router | 2 days |

**Total estimate**: ~10 days for full implementation

---

## Quick Wins (Can Do Today)

1. **Fix v1 workflows**: Add `@workflow.query get_progress()` to all v1 workflows
2. **Test SSE endpoint**: Verify `/jobs/{id}/stream` works when Redis publishes
3. **Publish from one activity**: Add Redis publish to `parse_to_parquet_activity` as POC

```python
# Quick fix for ingestion.py v1
@workflow.defn
class DatasetIngestionWorkflow:
    def __init__(self):
        self._progress = 0
        self._step = "initializing"

    @workflow.query
    def get_progress(self) -> dict:
        return {"progress": self._progress, "current_step": self._step}

    @workflow.run
    async def run(self, ...):
        self._step = "validating"
        self._progress = 10
        # ... rest of workflow
```

This immediately enables `/operations/{id}` to return progress!
