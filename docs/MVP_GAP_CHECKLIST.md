# Process Mining MVP — Data Flow Gap Analysis

> **Perspective**: CTO — How does data actually flow through the system?

---

## The Core Question

```
CSV File → ??? → User sees a process visualization with metrics
```

What happens in the `???` is the real complexity.

---

## Data Flow 1: Ingestion

### Current Path (What Exists)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌───────────────┐
│ User Upload │────▶│ Local FS     │────▶│ DuckDB Parse    │────▶│ SQLite Insert │
│ (Multipart) │     │ /data/storage│     │ (in-memory)     │     │ process_events│
└─────────────┘     └──────────────┘     └─────────────────┘     └───────────────┘
                           │                     │                       │
                           ▼                     ▼                       ▼
                    File copied to       Entire file loaded      Row-by-row or
                    temp location        into memory             bulk insert?
```

### Gap Analysis

| Stage | Have | Missing | Risk |
|-------|------|---------|------|
| **Upload** | Presigned URL flow | Large file chunking | >100MB uploads may timeout |
| **Storage** | Local FS | S3 abstraction tested | Works for MVP |
| **Parse** | DuckDB reads CSV | Streaming for large files | Memory explosion on 1GB files |
| **Transform** | Basic column mapping | Timestamp format inference | Edge cases fail silently |
| **Load** | Bulk insert exists | Transaction boundaries | Partial ingestion on failure |
| **Validate** | Schema validation | Data quality checks | Bad data propagates |

### State Machine (Dataset Lifecycle)

```
                    ┌─────────────────────────────────────────────────┐
                    ▼                                                 │
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐    ┌─────┴────┐
│ pending │───▶│ uploaded │───▶│ validated│───▶│ mapped    │───▶│ ingesting│
└─────────┘    └──────────┘    └──────────┘    └───────────┘    └──────────┘
     │              │               │               │                 │
     ▼              ▼               ▼               ▼                 ▼
 [timeout]     [file corrupt]  [bad schema]   [user abandons]    ┌────┴────┐
     │              │               │               │             │         │
     └──────────────┴───────────────┴───────────────┴────────────▶│  ERROR  │
                                                                  └─────────┘
                                                                       │
                                                        ┌──────────────┴──────────────┐
                                                        ▼                             ▼
                                                   [retryable]                   [terminal]
                                                   Can re-ingest                 Need re-upload
```

**Missing**: Error recovery paths. What happens when ingestion fails at step 3 of 5?

---

## Data Flow 2: Discovery

### Current Path

```
┌────────────┐     ┌──────────────────┐     ┌───────────┐     ┌────────────┐
│ Dataset ID │────▶│ Load events from │────▶│ PM4PY     │────▶│ Serialize  │
│            │     │ SQLite into RAM  │     │ Algorithm │     │ to DB      │
└────────────┘     └──────────────────┘     └───────────┘     └────────────┘
                           │                      │                  │
                           ▼                      ▼                  ▼
                   SELECT * FROM           Algorithm runs        joblib bytes
                   process_events          in single thread      stored in BLOB
                   WHERE dataset_id=X      (blocking)
```

### Gap Analysis

| Stage | Have | Missing | Risk |
|-------|------|---------|------|
| **Load** | SQL → PM4PY DataFrame | Streaming/chunked load | OOM on 500K+ events |
| **Algorithm Selection** | 17 algorithms | Auto-recommendation | User picks wrong algorithm |
| **Execution** | Sync execution works | Timeout enforcement | Alpha miner can hang forever |
| **Soundness Check** | pm4py.check_soundness | Not always called | User gets unsound model |
| **Quality Metrics** | Fitness/precision exist | Not computed by default | User has no quality signal |
| **Serialization** | joblib serialize | Large model storage | BLOB size limits |

### Algorithm Selection Logic (Spec vs Current)

**Spec says:**
```
variant_explosion = variant_count / case_count

< 0.10  → All algorithms available
0.10-0.30 → Warn on Alpha, default Inductive
0.30-0.50 → Hide Alpha, default IM-Infrequent
> 0.50  → Only DFG and IM-Infrequent
```

**Current**: No variant_explosion computed. No recommendations. User picks blindly.

---

## Data Flow 3: Visualization

### Current Path

```
┌────────────┐     ┌───────────────┐     ┌──────────────┐     ┌───────────┐
│ Model ID   │────▶│ Deserialize   │────▶│ Convert to   │────▶│ JSON over │
│            │     │ from BLOB     │     │ nodes/edges  │     │ HTTP      │
└────────────┘     └───────────────┘     └──────────────┘     └───────────┘
                          │                     │                   │
                          ▼                     ▼                   ▼
                    joblib.load()         Different logic      Frontend renders
                    in memory             per model type        with D3/Cytoscape
```

### Gap Analysis

| Stage | Have | Missing | Risk |
|-------|------|---------|------|
| **Model Retrieval** | Load from DB | Model not found handling | 404 with no context |
| **Deserialization** | joblib works | Version compatibility | Old models may break |
| **Graph Conversion** | Per-type logic | Unified contract | Frontend breaks on new types |
| **Metrics Attachment** | Frequency in nodes | Duration/performance | Incomplete insight |
| **Filtering** | None | Edge threshold slider | Frontend overwhelmed |
| **Caching** | None | Pre-computed viz | Slow repeated views |

### Visualization Contract (Spec vs Current)

**Spec requires:**
```json
{
  "nodes": [{"id", "label", "type", "metrics": {"frequency", "avg_duration_sec"}}],
  "edges": [{"source", "target", "metrics": {"frequency", "avg_wait_sec"}}],
  "summary": {"total_cases", "is_sound", "fitness", "precision"}
}
```

**Current**: Format varies by model type. No guaranteed `summary` block.

---

## Data Flow 4: Temporal Orchestration

### Target Path (From Spec)

```
┌──────────────┐    ┌─────────────────┐    ┌──────────────┐    ┌───────────┐
│ API Request  │───▶│ Temporal Server │───▶│ Worker picks │───▶│ Activities│
│ dispatch()   │    │ queues workflow │    │ up workflow  │    │ execute   │
└──────────────┘    └─────────────────┘    └──────────────┘    └───────────┘
                           │                      │                   │
                           ▼                      ▼                   ▼
                    Durable state          Heartbeat every       Each activity
                    persisted              10 seconds            can retry
```

### Gap Analysis

| Stage | Have | Missing | Risk |
|-------|------|---------|------|
| **Dispatch** | `dispatch_workflow()` | Temporal not running | Workflows never start |
| **Workflow Definition** | 3 workflows defined | Analysis workflow incomplete | Can't run discovery async |
| **Activities** | 5 activities defined | Progress reporting | User sees no progress |
| **Heartbeat** | Configured 60s | Actual heartbeat calls | Silent timeout |
| **Error Handling** | Retry policy defined | Dead letter queue | Failed jobs disappear |
| **Cancellation** | Not implemented | Cancel button | User stuck waiting |

---

## Edge Cases (From Research Doc)

| # | Edge Case | Current Handling | Required Handling |
|---|-----------|------------------|-------------------|
| 1 | Empty log (0 events) | Unknown | Return error before discovery |
| 2 | Single-trace log | Unknown | Warn user about overfitting |
| 3 | 100% unique variants | Unknown | Force DFG, warn user |
| 4 | Loops in process | Unknown | Disable Alpha automatically |
| 5 | >100 activities | Unknown | Suggest abstraction |
| 6 | >100K events | Unknown | Warn on slow algorithms |
| 7 | Concurrent activities | Unknown | Don't recommend Alpha |
| 8 | Timestamp collisions | Unknown | Detect and handle |
| 9 | PM4PY algorithm hangs | No timeout | Need activity-level timeout |
| 10 | Memory overflow | Crashes worker | Need memory limit per job |

---

## Missing Layers

### 1. Profile Layer (Between Ingest and Discovery)

```
┌─────────────┐     ┌───────────────────────────────────────────────┐     ┌───────────┐
│ Ingestion   │────▶│ PROFILE COMPUTATION                           │────▶│ Discovery │
│ Complete    │     │ • event_count, case_count, variant_count      │     │           │
└─────────────┘     │ • variant_explosion = variants / cases        │     └───────────┘
                    │ • has_loops (detect from DFG cycles)          │
                    │ • has_concurrent (timestamp collisions)       │
                    │ • noise_estimate (variant distribution)       │
                    └───────────────────────────────────────────────┘
```

**Gap**: This layer doesn't exist. No `dataset_profiles` table. No computation.

### 2. Cache Layer (Between Discovery and Visualization)

```
┌─────────────┐     ┌───────────────────────────────────────────────┐     ┌───────────────┐
│ Ingestion   │────▶│ DFG CACHE                                     │────▶│ Instant viz   │
│ Complete    │     │ • Pre-compute frequency DFG                   │     │ (no discovery)│
└─────────────┘     │ • Pre-compute performance DFG                 │     └───────────────┘
                    │ • Store in dfg_cache table                    │
                    └───────────────────────────────────────────────┘
```

**Gap**: This layer doesn't exist. Every DFG view hits the full pipeline.

### 3. Intelligence Layer (Discovery UX)

```
┌─────────────────────────────────────────────────────────────────────┐
│ RECOMMENDATION ENGINE                                               │
│                                                                     │
│ INPUT: dataset_profile                                              │
│ OUTPUT: {                                                           │
│   recommended: "inductive_infrequent",                             │
│   reason: "High variant explosion (56%)",                          │
│   available: ["dfg", "inductive_infrequent"],                      │
│   disabled: [{id: "alpha", reason: "Loops detected"}],             │
│   warnings: [{id: "inductive", msg: "May be slow"}]                │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

**Gap**: No recommendation engine. No UI to show recommendations.

---

## Summary: What Does "Done" Look Like?

### Minimal Viable Flow

1. User uploads CSV
2. System validates format, detects columns
3. User confirms/adjusts column mapping
4. System ingests events into database
5. **System computes profile** (NEW)
6. **System caches DFG** (NEW)
7. User sees instant DFG visualization
8. User selects algorithm **with recommendations** (NEW)
9. System discovers model (with timeout, progress)
10. User sees model visualization with metrics

### Data Integrity Checks Needed

- [ ] Uploaded file → stored file (checksum match)
- [ ] Stored file → parsed events (row count match)
- [ ] Parsed events → database events (count match)
- [ ] Database events → PM4PY log (event count match)
- [ ] Discovery input → output (model serializes correctly)
- [ ] Serialized model → deserialized (round-trip works)
- [ ] Model → visualization JSON (contract compliance)

---

*This document maps the actual complexity. Each arrow is potential failure.*

---

## Data Flow 5: Frontend → Backend Communication

### Upload Flow

```
┌──────────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ File Picker  │───▶│ Client-side │───▶│ Get presign │───▶│ Direct PUT  │───▶│ Confirm      │
│ (input type) │    │ validation  │    │ URL from API│    │ to storage  │    │ upload done  │
└──────────────┘    └─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
       │                  │                  │                   │                  │
       ▼                  ▼                  ▼                   ▼                  ▼
   File object       Check size         POST /presign       Upload bypasses   POST /uploaded
   in browser        Check type         Returns URL+key     API server        Triggers validation
```

| Stage | Have | Missing | Edge Case |
|-------|------|---------|-----------|
| File selection | Basic input | Drag-drop, multi-file | User selects wrong format |
| Client validation | Size check | Format deep check | User renames .exe to .csv |
| Presign request | Endpoint exists | Error handling | API down, no feedback |
| Direct upload | Works for small | Progress bar, chunking | 100MB+ timeouts |
| Confirmation | Endpoint exists | Retry on failure | Race condition: double upload |

### Discovery Flow (Frontend)

```
┌─────────────┐    ┌────────────────┐    ┌──────────────┐    ┌────────────┐    ┌────────────┐
│ Dataset     │───▶│ Show algorithm │───▶│ User selects │───▶│ POST       │───▶│ Poll job   │
│ selected    │    │ picker         │    │ + params     │    │ /discover  │    │ status     │
└─────────────┘    └────────────────┘    └──────────────┘    └────────────┘    └────────────┘
       │                  │                    │                  │                 │
       ▼                  ▼                    ▼                  ▼                 ▼
   Load profile      No recommendations    Raw params         202 + job_id     GET /jobs/{id}
   (doesn't exist)   shown currently       exposed            returned         every 2 seconds
```

| Stage | Have | Missing | Edge Case |
|-------|------|---------|-----------|
| Dataset context | Passed via state | Profile data | User has no context about data |
| Algorithm list | Fetched from API | Recommendations | User picks wrong algorithm |
| Parameter form | Basic inputs | Complexity slider | User sets bad params |
| Submit | POST works | Validation feedback | Submit while already running |
| Polling | Interval-based | WebSocket, cancel button | Tab closed, zombie jobs |
| Completion | Model ID returned | Auto-navigate to viz | User confused what to do next |

### Visualization Flow (Frontend)

```
┌─────────────┐    ┌────────────────┐    ┌──────────────┐    ┌────────────┐    ┌────────────┐
│ Model/      │───▶│ GET /viz/dfg   │───▶│ Parse JSON   │───▶│ Build      │───▶│ Render     │
│ Dataset ID  │    │ or /viz/model  │    │ nodes/edges  │    │ D3/Cyto    │    │ to canvas  │
└─────────────┘    └────────────────┘    └──────────────┘    └────────────┘    └────────────┘
       │                  │                    │                  │                 │
       ▼                  ▼                    ▼                  ▼                 ▼
   From URL params   Which endpoint?      Schema varies      Memory allocation   Performance
   or app state      Model vs dataset?    by model type      for large graph     with 1000 nodes
```

| Stage | Have | Missing | Edge Case |
|-------|------|---------|-----------|
| Entry point | Route exists | Deep link to specific model | URL expires, model deleted |
| Fetch | API call | Loading state, error state | Timeout, CORS error |
| Parse | JSON parse | Schema validation | Backend changes format |
| Graph build | Library configured | Memory management | 10K nodes crashes browser |
| Render | Basic render | Zoom, pan, filter | Long labels overflow |
| Interaction | Hover exists? | Click node → details | Touch support, mobile |

---

## Data Flow 6: Error Handling

### Error Propagation Path

```
┌─────────────┐    ┌────────────────┐    ┌──────────────┐    ┌────────────────────┐
│ Activity    │───▶│ Temporal       │───▶│ API Response │───▶│ Frontend displays  │
│ throws      │    │ retry/fail     │    │ (error JSON) │    │ to user            │
└─────────────┘    └────────────────┘    └──────────────┘    └────────────────────┘
       │                  │                    │                       │
       ▼                  ▼                    ▼                       ▼
   Exception type    Retry 3x,            RFC 7807 format        Toast/modal?
   not consistent    then mark failed     {"type", "title",      User action?
                                          "status", "detail"}
```

### Error Taxonomy (From Spec)

| Code | Stage | User Message | Recovery |
|------|-------|--------------|----------|
| `E_FILE_FORMAT` | Upload | "File format not supported" | Re-upload |
| `E_FILE_SIZE` | Upload | "File exceeds 500MB limit" | Chunk or downsample |
| `E_COLUMN_MISSING` | Mapping | "Required column X not found" | Re-map |
| `E_TIMESTAMP_INVALID` | Ingestion | "Cannot parse timestamps in column X" | Fix data |
| `E_ALGO_TIMEOUT` | Discovery | "Algorithm timed out after 5 min" | Try simpler algo |
| `E_ALGO_OOM` | Discovery | "Not enough memory for this log" | Use DFG |
| `E_MODEL_UNSOUND` | Discovery | "Model may have deadlocks" | Informational |

**Gap**: No consistent error codes. Errors are raw Python exceptions.

### Current Error Handling

| Layer | Have | Missing |
|-------|------|---------|
| Activity | try/except → return error dict | Typed error classes |
| Workflow | Catches activity failure | DLQ for poison jobs |
| API | RFC 7807 wrapper | Specific error codes |
| Frontend | console.log | Toast notifications, retry CTA |
| Logging | Structured logs | Correlation IDs across layers |
| Alerting | None | PagerDuty/Slack on critical |

---

## Data Flow 7: Multi-Tenancy & Authorization

### Current Path

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌─────────────┐
│ Request with │───▶│ Mock user    │───▶│ Dataset fetched  │───▶│ No workspace│
│ no auth      │    │ returned     │    │ by ID only       │    │ filter      │
└──────────────┘    └──────────────┘    └──────────────────┘    └─────────────┘
       │                  │                      │                     │
       ▼                  ▼                      ▼                     ▼
   Auth disabled     mvp-user-001          SELECT * FROM         Any dataset
   in dev            hardcoded             datasets               accessible
                                           WHERE id = ?
```

### Required Path

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐    ┌─────────────┐
│ JWT Token    │───▶│ Validate,    │───▶│ Check workspace  │───▶│ Row-level   │
│ in header    │    │ extract user │    │ membership       │    │ filtering   │
└──────────────┘    └──────────────┘    └──────────────────┘    └─────────────┘
       │                  │                      │                     │
       ▼                  ▼                      ▼                     ▼
   Bearer token      User object            Permission enum       workspace_id
   from login        with org_id            (READ/WRITE/ADMIN)    in every query
```

| Check | Have | Missing |
|-------|------|---------|
| Token validation | JWT decode exists | Not enforced (auth_enabled=false) |
| User lookup | Works | Token refresh flow |
| Workspace membership | Table exists | Checked in all endpoints? |
| Dataset ownership | `workspace_id` FK exists | Included in all queries? |
| Cross-tenant access | Unknown | Explicit tests with 2 workspaces |

---

## Data Flow 8: Performance Hot Paths

### Ingestion Critical Path

```
Time ──────────────────────────────────────────────────────────────────────────▶

│ File copy │   │ DuckDB read │   │ Transform │   │ Bulk insert │   │ Stats │
│   100ms   │   │    500ms    │   │   300ms   │   │   1000ms    │   │ 200ms │
└───────────┘   └─────────────┘   └───────────┘   └─────────────┘   └───────┘

                          For 100K rows ≈ 2.1 seconds
                          For 1M rows  ≈ 21 seconds (linear? sublinear?)
```

**Unknowns**:
- Is DuckDB streaming or loading entire file?
- Is bulk insert actually bulk or row-by-row?
- What's the memory ceiling?

### Discovery Critical Path

```
Time ──────────────────────────────────────────────────────────────────────────▶

│ Load log │   │ PM4PY convert │   │ Algorithm │   │ Serialize │   │ Save │
│   300ms  │   │     200ms     │   │  100-∞    │   │   100ms   │   │ 50ms │
└──────────┘   └───────────────┘   └───────────┘   └───────────┘   └──────┘

                    Algorithm time varies wildly:
                    - DFG: O(events)
                    - Alpha: O(activities² × events) 
                    - ILP: NP-hard, can be hours
```

**Unknowns**:
- No timeout enforcement per algorithm
- No memory limit per worker
- No automatic fallback to simpler algorithm

### Visualization Critical Path

```
Time ──────────────────────────────────────────────────────────────────────────▶

│ DB query │   │ Deserialize │   │ Graph JSON │   │ Network │   │ Render │
│   50ms   │   │    100ms    │   │    50ms    │   │  200ms  │   │ 500ms+ │
└──────────┘   └─────────────┘   └────────────┘   └─────────┘   └────────┘

                    Network + Render dominate
                    Large graphs (1000+ nodes): 5+ seconds
```

**Unknowns**:
- Is serialized model cached?
- Can we pre-compute viz JSON at discovery time?
- Frontend virtual scrolling for large graphs?

---

## What "MVP Done" Actually Means

### Happy Path Verified

```
[ ] 1. New user can upload 10MB CSV
[ ] 2. System detects case/activity/timestamp columns
[ ] 3. User confirms mapping in UI
[ ] 4. Ingestion completes in <30 seconds
[ ] 5. Events appear in database (count matches)
[ ] 6. DFG generates in <5 seconds
[ ] 7. Frontend shows DFG with correct node count
[ ] 8. User runs Inductive Miner
[ ] 9. Model completes in <2 minutes
[ ] 10. Model visualization renders in UI
[ ] 11. Fitness score displayed correctly
```

### Error Paths Verified

```
[ ] 1. Upload wrong file type → helpful error
[ ] 2. Upload 500MB file → graceful rejection
[ ] 3. Bad timestamp format → specific error message
[ ] 4. Run Alpha on looping log → warning or block
[ ] 5. Algorithm timeout → job marked failed with message
[ ] 6. Browser close during discovery → job continues
[ ] 7. Two users same workspace → correct isolation
[ ] 8. Two users different workspaces → zero cross-access
```

### Performance Verified

```
[ ] 1. 100K events ingests in <60 seconds
[ ] 2. DFG on 100K events in <10 seconds
[ ] 3. Inductive on 50K events in <60 seconds
[ ] 4. 500-node DFG renders in <3 seconds
[ ] 5. Memory usage stays under 4GB per worker
```

---

*Each unchecked box is work. Each arrow in a diagram is a potential bug.*

