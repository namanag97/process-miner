# API Reference

> **Base URL:** `http://localhost:8001/api/v1`  
> **Auth:** Bearer token (`Authorization: Bearer <token>`)  
> **Content-Type:** `application/json` (unless file upload)

---

## Quick Navigation

| Category                            | Endpoints                        |
| ----------------------------------- | -------------------------------- |
| [Projects](#projects)               | Organize logs into folders       |
| [Event Logs](#event-logs-processes) | Upload, list, analyze logs       |
| [Discovery](#discovery)             | Mine process models              |
| [Visualization](#visualization)     | DFG, Petri nets, SVG export      |
| [Conformance](#conformance)         | Check log-model conformance      |
| [Analytics](#analytics)             | Bottlenecks, rework, performance |
| [Predictions](#predictions)         | ML-based predictions             |
| [Filtering](#filtering)             | Filter event logs                |
| [OCPM](#ocpm-object-centric)        | Object-centric process mining    |
| [Organizational](#organizational)   | Social network analysis          |
| [Simulation](#simulation)           | What-if analysis, play-out       |
| [Workflows](#workflows)             | Workflow automation              |
| [LLM](#llm)                         | AI-enhanced analysis _(NEW)_     |
| [Privacy](#privacy)                 | Differential privacy _(NEW)_     |

---

## Projects (`/projects`)

Organize event logs into folders for better management.

### POST `/projects`

Create a new project.

```json
// Request
{
  "name": "Q4 Analysis",
  "description": "Q4 2024 process mining project",
  "tags": ["production", "priority"]
}
```

| Field         | Type     | Required | Notes          |
| ------------- | -------- | -------- | -------------- |
| `name`        | string   | ✅       | 1-255 chars    |
| `description` | string   | ❌       | Max 2000 chars |
| `tags`        | string[] | ❌       | For filtering  |

```json
// Response 201
{
  "id": "proj_abc123",
  "name": "Q4 Analysis",
  "description": "Q4 2024 process mining project",
  "tags": ["production", "priority"],
  "total_files": 0,
  "total_analyses": 0,
  "created_at": "2024-12-30T10:00:00Z",
  "updated_at": null
}
```

---

### GET `/projects`

List all projects with pagination.

| Param       | Type   | Default | Notes          |
| ----------- | ------ | ------- | -------------- |
| `page`      | int    | 1       | 1-indexed      |
| `page_size` | int    | 20      | Max 100        |
| `search`    | string | -       | Filter by name |

```json
// Response 200
{
  "items": [
    /* ProjectResponse[] */
  ],
  "total": 15,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

---

### GET `/projects/{project_id}`

Get project details with contained event logs.

```json
// Response 200
{
  "id": "proj_abc123",
  "name": "Q4 Analysis",
  "description": "Q4 2024 process mining project",
  "tags": ["production"],
  "total_files": 3,
  "total_analyses": 12,
  "created_at": "2024-12-30T10:00:00Z",
  "updated_at": "2024-12-31T15:30:00Z",
  "event_logs": [
    {
      "id": "log_xyz789",
      "name": "Orders Process",
      "source_format": "csv",
      "total_events": 15234,
      "total_cases": 1520,
      "total_activities": 12,
      "activities": ["Create", "Approve", "Ship"],
      "created_at": "2024-12-30T10:05:00Z"
    }
  ]
}
```

**Errors:**

- `404` - Project not found

---

### PUT `/projects/{project_id}`

Update project metadata.

```json
// Request (all fields optional)
{
  "name": "Q4 Analysis - Final",
  "description": "Updated description",
  "tags": ["production", "completed"]
}
```

```json
// Response 200
{
  /* ProjectResponse */
}
```

**Errors:**

- `404` - Project not found

---

### DELETE `/projects/{project_id}`

Delete project. Event logs are **not deleted**, just unlinked.

```text
Response: 204 No Content
```

**FE Notes:** Logs remain accessible via `/processes`. Only the folder is deleted.

---

### POST `/projects/{project_id}/files/{log_id}`

Add an existing event log to a project.

```json
// Response 200
{
  /* ProjectDetailResponse with updated event_logs */
}
```

**Errors:**

- `404` - Project or log not found

**FE Notes:** A log can only belong to one project. Adding to a new project moves it.

---

### DELETE `/projects/{project_id}/files/{log_id}`

Remove event log from project (doesn't delete the log).

```text
Response: 204 No Content
```

**Errors:**

- `400` - Log not in this project
- `404` - Project or log not found

---

## Event Logs (`/processes`)

### POST `/processes/upload`

Upload and ingest event log file.

| Field              | Type   | Required | Notes                    |
| ------------------ | ------ | -------- | ------------------------ |
| `file`             | File   | ✅       | CSV or XES format        |
| `name`             | string | ❌       | Custom log name          |
| `case_id_column`   | string | ❌       | CSV column for case ID   |
| `activity_column`  | string | ❌       | CSV column for activity  |
| `timestamp_column` | string | ❌       | CSV column for timestamp |
| `resource_column`  | string | ❌       | CSV column for resource  |

**Content-Type:** `multipart/form-data`

```json
// Response 200
{
  "id": "log_abc123",
  "name": "Purchase Order Process",
  "source_format": "csv",
  "total_events": 15234,
  "total_cases": 1520,
  "total_activities": 12,
  "activities": ["Create Order", "Approve", "Ship", "Invoice", "Pay"],
  "created_at": "2024-12-30T10:00:00Z"
}
```

**Errors:**

- `400` - No file provided
- `422` - Column mapping failed / Invalid format
- `500` - Ingestion error

**FE Notes:** Auto-detects columns if not provided. Use `/detect-columns` first for better UX.

---

### POST `/processes/detect-columns`

Detect column types from CSV file before upload.

| Field  | Type | Required |
| ------ | ---- | -------- |
| `file` | File | ✅       |

```json
// Response 200
{
  "columns": ["case", "activity", "timestamp", "user", "cost"],
  "suggestions": {
    "case_id": "case",
    "activity": "activity",
    "timestamp": "timestamp",
    "resource": "user"
  },
  "sample_rows": [
    { "case": "C1", "activity": "Start", "timestamp": "2024-01-01" }
  ],
  "row_count": 15234
}
```

---

### GET `/processes`

List all event logs with pagination.

| Param           | Type   | Default | Notes                           |
| --------------- | ------ | ------- | ------------------------------- |
| `page`          | int    | 1       | Page number (1-based)           |
| `page_size`     | int    | 20      | Items per page (max 100)        |
| `source_format` | string | -       | Filter by format (`csv`, `xes`) |

```json
// Response 200
{
  "items": [
    /* ProcessResponse[] */
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

**FE Notes:** Pagination is offset-based (not cursor). `pages` = total pages count.

---

### GET `/processes/{process_id}`

Get detailed log information.

```json
// Response 200
{
  "id": "log_abc123",
  "name": "Purchase Order Process",
  "source_format": "csv",
  "source_file": "orders.csv",
  "total_events": 15234,
  "total_cases": 1520,
  "total_activities": 12,
  "activities": ["Create Order", "Approve", ...],
  "statistics": { /* extended stats */ },
  "created_at": "2024-12-30T10:00:00Z",
  "updated_at": "2024-12-30T10:05:00Z"
}
```

---

### DELETE `/processes/{process_id}`

Delete event log and all associated data.

```json
// Response 200
{ "status": "deleted", "id": "log_abc123" }
```

---

### GET `/processes/{process_id}/statistics`

Comprehensive log statistics.

```json
// Response 200
{
  "total_events": 15234,
  "total_cases": 1520,
  "total_activities": 12,
  "total_variants": 85,
  "activities": ["Create Order", "Approve", ...],
  "start_activities": {"Create Order": 1520},
  "end_activities": {"Pay": 1200, "Cancel": 320},
  "avg_case_duration_seconds": 345600,
  "min_case_duration_seconds": 3600,
  "max_case_duration_seconds": 2592000,
  "date_range": {"start": "2024-01-01T00:00:00Z", "end": "2024-12-30T23:59:59Z"}
}
```

---

### GET `/processes/{process_id}/cases`

List cases with pagination.

| Param       | Type | Default |
| ----------- | ---- | ------- |
| `page`      | int  | 1       |
| `page_size` | int  | 20      |

```json
// Response 200
{
  "items": [
    {
      "case_id": "C1001",
      "event_count": 8,
      "variant": "Create→Approve→Ship→Invoice→Pay",
      "start_time": "2024-01-15T09:00:00Z",
      "end_time": "2024-01-19T17:00:00Z",
      "duration_seconds": 374400
    }
  ],
  "total": 1520,
  "page": 1,
  "page_size": 20,
  "pages": 76
}
```

---

### GET `/processes/{process_id}/variants`

Get process variants with frequencies.

| Param                | Type   | Default | Notes                                 |
| -------------------- | ------ | ------- | ------------------------------------- |
| `top_n`              | int    | 20      | Max variants to return                |
| `top_k_percent`      | float  | -       | Return variants covering K% of cases  |
| `include_complexity` | bool   | false   | Include complexity metrics            |
| `sort_by`            | string | -       | `frequency`, `complexity`, `duration` |

```json
// Response 200
[
  {
    "variant_key": "Create→Approve→Ship→Invoice→Pay",
    "activity_trace": "Create→Approve→Ship→Invoice→Pay",
    "case_count": 850,
    "frequency_percent": 55.92,
    "avg_duration_seconds": 345600,
    "complexity_score": 0.2,
    "rework_count": 0,
    "unique_activity_count": 5
  }
]
```

**FE Notes:** `top_k_percent=80` returns variants covering 80% of cases (Pareto).

---

### GET `/processes/{process_id}/activities`

Detailed activity statistics.

| Param     | Type   | Notes                               |
| --------- | ------ | ----------------------------------- |
| `sort_by` | string | `frequency`, `duration`, `position` |

```json
// Response 200
[
  {
    "activity": "Approve",
    "frequency": 1520,
    "frequency_percent": 9.98,
    "avg_duration_seconds": 3600,
    "min_duration_seconds": 60,
    "max_duration_seconds": 86400,
    "is_start_activity": false,
    "is_end_activity": false,
    "position_avg": 0.25,
    "resources": ["John", "Jane", "Admin"]
  }
]
```

---

## Discovery (`/discovery`)

### GET `/discovery/miners`

List available mining algorithms.

```json
// Response 200
[
  {
    "id": "alpha",
    "name": "Alpha Miner",
    "description": "Classic algorithm for sequential workflows",
    "output_format": "petri_net"
  },
  {
    "id": "inductive",
    "name": "Inductive Miner",
    "description": "Sound process trees with fitness guarantees",
    "output_format": "process_tree"
  },
  {
    "id": "heuristics",
    "name": "Heuristics Miner",
    "description": "Noise-tolerant frequency-based mining",
    "output_format": "petri_net"
  },
  {
    "id": "dfg",
    "name": "DFG Miner",
    "description": "Directly-Follows Graph",
    "output_format": "dfg"
  }
]
```

---

### POST `/discovery/discover`

Discover process model from event log.

```json
// Request
{
  "log_id": "log_abc123",
  "miner_type": "inductive",
  "model_name": "My Model"
}
```

| Field        | Type   | Required | Values                                                                                                                                                                                                                                           |
| ------------ | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `log_id`     | string | ✅       | -                                                                                                                                                                                                                                                |
| `miner_type` | enum   | ❌       | `alpha`, `alpha_plus`, `inductive`, `inductive_infrequent`, `heuristics`, `dfg`, `performance_dfg`, `ilp`, `powl`, `bpmn_inductive`, `declare`, `log_skeleton`, `temporal_profile`, `prefix_tree`, `transition_system`, `batches`, `correlation` |
| `model_name` | string | ❌       | -                                                                                                                                                                                                                                                |

```json
// Response 200
{
  "id": "model_xyz789",
  "name": "My Model",
  "miner_type": "inductive",
  "model_format": "process_tree",
  "log_id": "log_abc123",
  "fitness": 0.95,
  "precision": 0.87,
  "created_at": "2024-12-30T10:10:00Z"
}
```

---

### GET `/discovery/models`

List discovered models.

| Param       | Type   | Default |
| ----------- | ------ | ------- |
| `page`      | int    | 1       |
| `page_size` | int    | 20      |
| `log_id`    | string | -       |

---

### GET `/discovery/models/{model_id}`

Get model details.

---

### DELETE `/discovery/models/{model_id}`

Delete model.

---

## Visualization (`/visualization`)

### GET `/visualization/{log_id}/dfg`

Get DFG for React Flow / D3 rendering.

| Param                 | Type | Default | Notes                       |
| --------------------- | ---- | ------- | --------------------------- |
| `include_performance` | bool | false   | Add timing metrics to edges |

```json
// Response 200
{
  "nodes": [
    {
      "id": "Create Order",
      "name": "Create Order",
      "frequency": 1520,
      "is_start": true,
      "is_end": false
    }
  ],
  "edges": [
    {
      "source": "Create Order",
      "target": "Approve",
      "frequency": 1450,
      "probability": 0.954,
      "avg_duration_seconds": 3600,
      "min_duration_seconds": 60,
      "max_duration_seconds": 86400
    }
  ],
  "start_activities": { "Create Order": 1520 },
  "end_activities": { "Pay": 1200 },
  "total_frequency": 15234
}
```

**FE Notes:** `nodes[].id` = activity name. Use for React Flow `id` prop.

---

### GET `/visualization/{log_id}/explorer-data`

**⭐ Unified endpoint** - All data for Process Explorer in one request.

| Param                 | Type | Default |
| --------------------- | ---- | ------- |
| `include_performance` | bool | true    |
| `include_complexity`  | bool | true    |
| `top_variants`        | int  | 20      |

```json
// Response 200
{
  "log_id": "log_abc123",
  "dfg": {
    /* DFGResponse */
  },
  "variants": [
    /* VariantResponse[] */
  ],
  "activities": [
    /* ActivityDetailResponse[] */
  ],
  "statistics": {
    /* StatisticsResponse */
  }
}
```

**FE Notes:** Single request replaces 4 separate calls. Use for initial load.

---

### GET `/visualization/{model_id}/petri-net`

Get Petri net structure.

```json
// Response 200
{
  "places": [{ "id": "p1", "name": "start", "tokens": 1 }],
  "transitions": [
    { "id": "t1", "name": "Create Order", "label": "Create Order" }
  ],
  "arcs": [{ "source": "p1", "target": "t1", "weight": 1 }],
  "initial_marking": ["p1"],
  "final_marking": ["p_end"]
}
```

---

### GET `/visualization/{model_id}/svg`

Get SVG visualization of model.

**Response:** `image/svg+xml`

---

### GET `/visualization/{log_id}/dfg/svg`

Get DFG as SVG.

**Response:** `image/svg+xml`

---

### GET `/visualization/{log_id}/footprints`

Get behavioral footprints (sequence/parallel relations).

---

## Conformance (`/conformance`)

### POST `/conformance/check`

Check conformance between log and model.

```json
// Request
{
  "log_id": "log_abc123",
  "model_id": "model_xyz789",
  "method": "token_replay"
}
```

| Field    | Type | Values                                        |
| -------- | ---- | --------------------------------------------- |
| `method` | enum | `token_replay` (fast), `alignment` (accurate) |

```json
// Response 200
{
  "id": "conf_result_001",
  "log_id": "log_abc123",
  "model_id": "model_xyz789",
  "fitness": 0.92,
  "precision": 0.85,
  "generalization": 0.88,
  "simplicity": 0.75,
  "method": "token_replay",
  "is_conformant": true,
  "fitting_traces": 1400,
  "total_traces": 1520,
  "created_at": "2024-12-30T10:15:00Z"
}
```

---

### GET `/conformance/diagnostics`

Detailed diagnostics with deviations.

| Param      | Type   |
| ---------- | ------ |
| `log_id`   | string |
| `model_id` | string |

```json
// Response 200
{
  "fitness": 0.92,
  "precision": 0.85,
  "total_traces": 1520,
  "fitting_traces": 1400,
  "non_fitting_traces": 120,
  "fitness_ratio": 0.921,
  "deviations": [
    {
      "case_id": "C1042",
      "activity": "Ship",
      "violation_type": "missing",
      "expected_after": "Approve",
      "frequency": 15,
      "impact": "high"
    }
  ]
}
```

---

### GET `/conformance/deviations`

List specific deviations.

| Param       | Type   | Default |
| ----------- | ------ | ------- |
| `log_id`    | string | -       |
| `model_id`  | string | -       |
| `threshold` | float  | 0.8     |

---

### GET `/conformance/alignments/{log_id}/{model_id}`

Optimal alignments using PM4Py.

| Param       | Type | Default |
| ----------- | ---- | ------- |
| `max_cases` | int  | 100     |

```json
// Response 200
{
  "log_id": "log_abc123",
  "model_id": "model_xyz789",
  "total_cases": 1520,
  "fitting_cases": 1400,
  "average_fitness": 0.92,
  "case_alignments": [
    {
      "case_id": "C1001",
      "fitness": 1.0,
      "cost": 0,
      "alignment": [
        { "log_move": "Create", "model_move": "Create", "move_type": "sync" },
        { "log_move": null, "model_move": "Approve", "move_type": "model_only" }
      ],
      "is_fit": true
    }
  ]
}
```

---

### GET `/conformance/methods`

List available conformance methods.

---

### GET `/conformance/results`

List conformance check results with pagination.

| Param       | Type   | Default | Notes           |
| ----------- | ------ | ------- | --------------- |
| `log_id`    | string | -       | Filter by log   |
| `model_id`  | string | -       | Filter by model |
| `page`      | int    | 1       | 1-indexed       |
| `page_size` | int    | 20      | Max 100         |

```json
// Response 200
{
  "items": [
    /* ConformanceResponse[] */
  ],
  "total": 12,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

---

### GET `/conformance/results/{result_id}`

Get a specific conformance check result.

```json
// Response 200
{
  /* ConformanceResponse */
}
```

**Errors:**

- `404` - Result not found

---

### DELETE `/conformance/results/{result_id}`

Delete a conformance check result.

```json
// Response 200
{ "status": "deleted", "id": "conf_result_001" }
```

**Errors:**

- `404` - Result not found

---

## Analytics (`/analytics`)

### GET `/analytics/logs/{log_id}/bottlenecks`

Detect process bottlenecks.

```json
// Response 200
{
  "log_id": "log_abc123",
  "bottlenecks": [
    {
      "activity": "Approve",
      "avg_waiting_time_seconds": 86400,
      "avg_service_time_seconds": 3600,
      "frequency": 1520,
      "is_bottleneck": true,
      "severity": "high",
      "preceding_activities": ["Create Order", "Request"],
      "following_activities": ["Ship", "Reject"],
      "bottleneck_impact_score": 0.85
    }
  ],
  "total_bottlenecks": 3
}
```

**FE Notes:** Cached for 1 hour. `bottleneck_impact_score` = 0-1 (higher = worse).

---

### GET `/analytics/logs/{log_id}/rework`

Analyze repeated activities.

```json
// Response 200
{
  "log_id": "log_abc123",
  "rework_activities": [
    {
      "activity": "Review",
      "rework_count": 234,
      "cases_with_rework": 156,
      "rework_percentage": 10.26
    }
  ],
  "total_rework_cases": 312,
  "rework_percentage": 20.53
}
```

---

### GET `/analytics/logs/{log_id}/rework-chains`

Detect consecutive activity repetitions.

```json
// Response 200
{
  "log_id": "log_abc123",
  "chains": [
    {
      "activity": "Review",
      "chain_length": 3,
      "frequency": 45,
      "avg_chain_duration_seconds": 7200,
      "example_case_ids": ["C1001", "C1042", "C1099"]
    }
  ],
  "total_chains": 89,
  "most_problematic_activity": "Review",
  "cases_with_chains": 67,
  "chains_percentage": 4.41
}
```

---

### GET `/analytics/logs/{log_id}/service-times`

Service time per activity.

```json
// Response 200
[
  {
    "activity": "Approve",
    "min_seconds": 60,
    "max_seconds": 86400,
    "avg_seconds": 3600,
    "median_seconds": 1800,
    "std_dev_seconds": 5400
  }
]
```

---

### GET `/analytics/logs/{log_id}/cycle-time`

Case duration statistics.

```json
// Response 200
{
  "log_id": "log_abc123",
  "min_seconds": 3600,
  "max_seconds": 2592000,
  "avg_seconds": 345600,
  "median_seconds": 259200,
  "percentile_25_seconds": 86400,
  "percentile_75_seconds": 518400,
  "percentile_95_seconds": 1296000
}
```

---

### GET `/analytics/logs/{log_id}/throughput`

Throughput metrics.

```json
// Response 200
{
  "log_id": "log_abc123",
  "total_cases": 1520,
  "completed_cases": 1200,
  "cases_per_day": 4.16,
  "cases_per_week": 29.15,
  "cases_per_month": 126.67,
  "time_range_days": 365
}
```

---

### GET `/analytics/logs/{log_id}/patterns`

Frequent activity patterns.

| Param         | Type  | Default |
| ------------- | ----- | ------- |
| `min_support` | float | 0.1     |

```json
// Response 200
[{ "pattern": "Create→Approve→Ship", "frequency": 850, "support": 0.56 }]
```

---

### GET `/analytics/logs/{log_id}/performance`

**⭐ Combined dashboard** - All performance metrics.

```json
// Response 200
{
  "log_id": "log_abc123",
  "cycle_time": {
    /* CycleTimeResponse */
  },
  "throughput": {
    /* ThroughputResponse */
  },
  "top_bottlenecks": [
    /* BottleneckResponse[] - top 5 */
  ],
  "rework_summary": {
    "total_rework_cases": 312,
    "rework_percentage": 20.53,
    "top_rework_activity": "Review"
  }
}
```

---

## Predictions (`/predictions`)

### POST `/predictions/logs/{log_id}/train`

Train ML prediction model.

```json
// Request
{
  "target_type": "next_activity",
  "algorithm": "random_forest",
  "outcome_attribute": null
}
```

| Field         | Type | Values                                          |
| ------------- | ---- | ----------------------------------------------- |
| `target_type` | enum | `next_activity`, `remaining_time`, `outcome`    |
| `algorithm`   | enum | `random_forest`, `xgboost`, `gradient_boosting` |

| Param        | Type | Default |
| ------------ | ---- | ------- |
| `async_mode` | bool | true    |

**Async mode (default):**

```json
// Response 202
{
  "id": "job_abc123",
  "job_type": "train_predictor",
  "status": "pending",
  "progress": 0,
  "created_at": "2024-12-30T10:20:00Z"
}
```

**Sync mode:**

```json
// Response 200
{
  "id": "predictor_xyz789",
  "log_id": "log_abc123",
  "target_type": "next_activity",
  "algorithm": "random_forest",
  "metrics": { "accuracy": 0.85, "f1_score": 0.82 },
  "trained_at": "2024-12-30T10:20:30Z"
}
```

---

### GET `/predictions/jobs/{job_id}`

Get async job status.

```json
// Response 200
{
  "id": "job_abc123",
  "job_type": "train_predictor",
  "status": "completed",
  "progress": 100,
  "result": { "predictor_id": "predictor_xyz789" },
  "created_at": "2024-12-30T10:20:00Z"
}
```

| Status Values | Description       |
| ------------- | ----------------- |
| `pending`     | Queued            |
| `running`     | In progress       |
| `completed`   | Done successfully |
| `failed`      | Error occurred    |

---

### GET `/predictions/logs/{log_id}/predictors`

List predictors for a log.

---

### GET `/predictions/predictors/{predictor_id}`

Get predictor details.

---

### POST `/predictions/predictors/{predictor_id}/predict`

Single prediction.

```json
// Request
{
  "case_prefix": ["Create Order", "Approve"],
  "case_attributes": {"customer_type": "premium"}
}

// Response 200
{
  "predictor_id": "predictor_xyz789",
  "case_prefix": ["Create Order", "Approve"],
  "prediction": "Ship",
  "confidence": 0.87,
  "alternatives": [
    {"activity": "Ship", "probability": 0.87},
    {"activity": "Hold", "probability": 0.08},
    {"activity": "Cancel", "probability": 0.05}
  ]
}
```

---

### POST `/predictions/predictors/{predictor_id}/predict-batch`

Batch predictions.

```json
// Request
{
  "cases": [
    { "case_prefix": ["Create", "Approve"], "case_attributes": null },
    { "case_prefix": ["Create", "Reject"], "case_attributes": null }
  ]
}
```

---

### DELETE `/predictions/predictors/{predictor_id}`

Delete predictor.

---

## Filtering (`/filtering`)

### POST `/filtering/logs/{log_id}/apply`

Apply filters and create filtered log.

```json
// Request
{
  "name": "Q4 2024 Cases",
  "filters": [
    {
      "type": "time_range",
      "params": { "start": "2024-10-01", "end": "2024-12-31" }
    },
    { "type": "variants_top_k", "params": { "k": 10 } },
    {
      "type": "activities_include",
      "params": { "activities": ["Approve", "Ship"] }
    }
  ],
  "save_result": true
}
```

| Filter Types           | Params                       |
| ---------------------- | ---------------------------- |
| `time_range`           | `start`, `end`               |
| `variants_top_k`       | `k`                          |
| `variants_coverage`    | `coverage_percent`           |
| `activities_include`   | `activities[]`               |
| `activities_exclude`   | `activities[]`               |
| `performance_duration` | `min_seconds`, `max_seconds` |
| `case_size`            | `min_events`, `max_events`   |

```json
// Response 200
{
  "id": "log_filtered_001",
  "name": "Q4 2024 Cases",
  "source_log_id": "log_abc123",
  "is_filtered": true,
  "filter_config": [
    /* filters applied */
  ],
  "total_events": 5000,
  "total_cases": 500,
  "total_activities": 10,
  "statistics": {
    "original_cases": 1520,
    "filtered_cases": 500,
    "cases_removed": 1020,
    "cases_retained_pct": 32.89
  },
  "created_at": "2024-12-30T10:25:00Z"
}
```

---

### POST `/filtering/logs/{log_id}/preview`

Preview filter impact without saving.

```json
// Request
{
  "filters": [{"type": "time_range", "params": {"start": "2024-10-01", "end": "2024-12-31"}}]
}

// Response 200
{
  "would_retain_cases": 500,
  "would_retain_events": 5000,
  "statistics": { /* FilterStatistics */ },
  "filters_applied": [ /* FilterConfig[] */ ]
}
```

---

### GET `/filtering/logs/{log_id}/options`

Get available filter options for a log.

```json
// Response 200
{
  "activities": ["Create", "Approve", "Ship", ...],
  "resources": ["John", "Jane", ...],
  "start_activities": {"Create": 1520},
  "end_activities": {"Pay": 1200, "Cancel": 320},
  "total_variants": 85,
  "time_range": {"start": "2024-01-01", "end": "2024-12-30"},
  "case_size_range": {"min": 3, "max": 25, "avg": 10.02}
}
```

---

### GET `/filtering/logs/{log_id}/filtered`

List filtered versions of a log.

---

### DELETE `/filtering/logs/{log_id}/filtered/{filtered_id}`

Delete filtered log.

---

### GET `/filtering/templates`

Get pre-built filter templates.

```json
// Response 200
{
  "templates": [
    {
      "id": "happy_path",
      "name": "Happy Path Only",
      "description": "Top 5 most frequent variants",
      "filters": [{ "type": "variants_top_k", "params": { "k": 5 } }]
    }
  ]
}
```

---

## OCPM (`/ocpm`) — Object-Centric

### POST `/ocpm/upload`

Upload OCEL 2.0 file.

| Field  | Type   | Notes                              |
| ------ | ------ | ---------------------------------- |
| `file` | File   | `.jsonocel`, `.sqlite`, `.xmlocel` |
| `name` | string | -                                  |

```json
// Response 200
{
  "id": "ocel_abc123",
  "name": "Order Fulfillment",
  "source_file": "orders.jsonocel",
  "source_format": "ocel_json",
  "total_events": 50000,
  "total_objects": 12000,
  "total_object_types": 3,
  "object_types": ["Order", "Item", "Package"],
  "activities": ["Create", "Pick", "Pack", "Ship"],
  "created_at": "2024-12-30T10:30:00Z"
}
```

---

### GET `/ocpm/logs`

List OCEL logs.

---

### GET `/ocpm/logs/{log_id}`

Get OCEL log details.

---

### DELETE `/ocpm/logs/{log_id}`

Delete OCEL log.

---

### GET `/ocpm/logs/{log_id}/object-types`

Get object types with counts.

```json
// Response 200
[
  {
    "name": "Order",
    "object_count": 1500,
    "attributes": ["customer_id", "priority"]
  },
  { "name": "Item", "object_count": 8500, "attributes": ["sku", "quantity"] },
  {
    "name": "Package",
    "object_count": 2000,
    "attributes": ["carrier", "weight"]
  }
]
```

---

### GET `/ocpm/logs/{log_id}/statistics`

OCEL statistics.

---

### POST `/ocpm/discover`

Discover Object-Centric Petri Net.

```json
// Request
{ "log_id": "ocel_abc123", "model_name": "OC-PN Model" }
```

---

### GET `/ocpm/models`

List OC Petri Nets.

---

### GET `/ocpm/logs/{log_id}/oc-dfg`

Get Object-Centric DFG.

```json
// Response 200
{
  "log_id": "ocel_abc123",
  "object_types": ["Order", "Item", "Package"],
  "activities": ["Create", "Pick", "Pack", "Ship"],
  "graphs_by_type": {
    "Order": {
      "object_type": "Order",
      "nodes": [
        {
          "id": "Create",
          "name": "Create",
          "object_type": "Order",
          "frequency": 1500
        }
      ],
      "edges": [
        {
          "source": "Create",
          "target": "Pick",
          "object_type": "Order",
          "frequency": 1400
        }
      ],
      "start_activities": ["Create"],
      "end_activities": ["Ship", "Cancel"]
    }
  },
  "total_events": 50000,
  "total_objects": 12000
}
```

---

### GET `/ocpm/formats`

List supported OCEL formats.

---

## Organizational (`/organizational`)

### GET `/organizational/logs/{log_id}/handover-network`

Handover of work network.

```json
// Response 200
{
  "log_id": "log_abc123",
  "network_type": "handover",
  "nodes": [
    { "id": "John", "label": "John", "type": "resource", "weight": 450 }
  ],
  "edges": [
    { "source": "John", "target": "Jane", "weight": 120, "label": null }
  ],
  "metrics": { "density": 0.35, "avg_degree": 4.2 }
}
```

---

### GET `/organizational/logs/{log_id}/collaboration-network`

Working together network.

---

### GET `/organizational/logs/{log_id}/resource-similarity`

Resource similarity graph.

---

### GET `/organizational/logs/{log_id}/roles`

Discover organizational roles.

```json
// Response 200
[
  {
    "role_id": "role_1",
    "resources": ["John", "Jane"],
    "activities": ["Approve", "Review"]
  },
  { "role_id": "role_2", "resources": ["Bob"], "activities": ["Ship", "Pack"] }
]
```

---

### GET `/organizational/logs/{log_id}/resources/{resource}/profile`

Resource profile.

```json
// Response 200
{
  "resource": "John",
  "total_events": 2500,
  "activities": { "Approve": 1500, "Review": 800, "Escalate": 200 },
  "avg_processing_time_seconds": 1800,
  "first_activity": "2024-01-02T09:15:00Z",
  "last_activity": "2024-12-30T16:45:00Z"
}
```

---

### GET `/organizational/logs/{log_id}/workload`

Workload distribution.

```json
// Response 200
{
  "log_id": "log_abc123",
  "workload": { "John": 2500, "Jane": 2100, "Bob": 1800 },
  "avg_events_per_resource": 2133.33
}
```

---

## Simulation (`/simulation`)

### POST `/simulation/models/{model_id}/play-out`

Generate synthetic log from model.

```json
// Request
{"num_traces": 100}

// Response 200
{
  "model_id": "model_xyz789",
  "generated_log_id": "log_sim_001",
  "traces_generated": 100,
  "events_generated": 850
}
```

---

### POST `/simulation/logs/{log_id}/simulate`

Run what-if simulation.

```json
// Request
{
  "modifications": [
    {"type": "remove_activity", "activity": "Manual Review"},
    {"type": "speed_up", "activity": "Approve", "factor": 2.0}
  ]
}

// Response 200
{
  "log_id": "log_abc123",
  "scenario": "remove_activity:Manual Review, speed_up:Approve",
  "original_metrics": {"avg_cycle_time": 345600, "throughput_per_day": 4.16},
  "simulated_metrics": {"avg_cycle_time": 259200, "throughput_per_day": 5.55},
  "impact": {"cycle_time_reduction_pct": 25.0, "throughput_increase_pct": 33.4}
}
```

---

### POST `/simulation/logs/{log_id}/capacity-plan`

Estimate resource requirements.

| Param               | Type  |
| ------------------- | ----- |
| `target_throughput` | float |

---

## Workflows (`/workflows`)

### POST `/workflows`

Create workflow.

```json
// Request
{
  "name": "Weekly Analysis",
  "steps": [
    {
      "name": "Discover",
      "type": "discovery",
      "params": { "miner_type": "inductive" }
    },
    {
      "name": "Check",
      "type": "conformance",
      "params": { "method": "token_replay" }
    }
  ],
  "schedule": "0 0 * * 0"
}
```

---

### GET `/workflows`

List workflows.

---

### GET `/workflows/{workflow_id}`

Get workflow details.

---

### POST `/workflows/{workflow_id}/run`

Execute workflow.

```json
// Request
{ "log_id": "log_abc123", "params": {} }
```

---

### DELETE `/workflows/{workflow_id}`

Delete workflow.

---

### GET `/workflows/templates`

List predefined workflow templates.

```json
// Response 200
[
  {
    "id": "full_analysis",
    "name": "Full Analysis",
    "description": "Discovery + Conformance + Analytics",
    "steps": [
      { "name": "Discover", "type": "discovery" },
      { "name": "Check", "type": "conformance" },
      { "name": "Analyze", "type": "bottleneck_detection" }
    ]
  }
]
```

---

### GET `/workflows/{workflow_id}/runs`

List execution history for a workflow.

```json
// Response 200
[
  {
    "id": "run_001",
    "workflow_id": "wf_abc123",
    "log_id": "log_xyz789",
    "status": "completed",
    "started_at": "2024-12-30T10:00:00Z",
    "completed_at": "2024-12-30T10:05:00Z",
    "error": null
  }
]
```

---

### GET `/workflows/runs/{run_id}`

Get specific workflow run details.

```json
// Response 200
{
  "id": "run_001",
  "workflow_id": "wf_abc123",
  "log_id": "log_xyz789",
  "status": "completed",
  "started_at": "2024-12-30T10:00:00Z",
  "completed_at": "2024-12-30T10:05:00Z",
  "error": null
}
```

**Errors:**

- `404` - Run not found

---

## LLM (`/llm`) - AI-Enhanced Analysis

> **Added in PM4py Integration Phase 5**

### POST `/llm/analyze`

AI-powered process analysis using LLM providers.

```json
// Request
{
  "log_id": "log_abc123",
  "provider": "openai",
  "analysis_type": "general",
  "api_key": "sk-..."
}
```

| Field           | Type   | Required | Values                                |
| --------------- | ------ | -------- | ------------------------------------- |
| `log_id`        | string | ✅       | Event log ID                          |
| `provider`      | enum   | ❌       | `openai`, `google`, `anthropic`       |
| `analysis_type` | enum   | ❌       | `general`, `bottleneck`, `compliance` |
| `api_key`       | string | ✅       | Provider API key                      |

```json
// Response 200
{
  "analysis_type": "general",
  "provider": "openai",
  "response": "The process shows a linear flow with 5 main activities..."
}
```

---

### POST `/llm/abstract`

Generate text abstraction of log/model for LLM context.

```json
// Request
{
  "log_id": "log_abc123",
  "abstraction_type": "dfg"
}
```

| Field              | Type | Values                                                          |
| ------------------ | ---- | --------------------------------------------------------------- |
| `abstraction_type` | enum | `dfg`, `variants`, `attributes`, `features`, `temporal`, `ocel` |

---

### POST `/llm/hypotheses`

Generate automated hypotheses about the process.

```json
// Response 200
{
  "hypotheses": [
    ["Activity 'Approve' causes bottleneck", 0.85],
    ["Cases with 'Rework' have 3x longer duration", 0.72]
  ]
}
```

---

## Privacy (`/privacy`) - Differential Privacy

> **Added in PM4py Integration Phase 6**

### POST `/privacy/anonymize`

Anonymize event log using differential privacy.

```json
// Request
{
  "log_id": "log_abc123",
  "epsilon": 1.0,
  "k": 10,
  "p": 20
}
```

| Field     | Type  | Default | Notes                                 |
| --------- | ----- | ------- | ------------------------------------- |
| `epsilon` | float | 1.0     | Privacy budget (lower = more private) |
| `k`       | int   | 10      | K-anonymity parameter                 |
| `p`       | int   | 20      | PRIPEL percentage                     |

```json
// Response 200
{
  "anonymized_log_id": "log_anon_xyz",
  "metrics": {
    "original_variants": 85,
    "anonymized_variants": 42,
    "variant_preservation_ratio": 0.78
  }
}
```

---

### POST `/privacy/suppress`

Remove sensitive attributes from log.

```json
// Request
{
  "log_id": "log_abc123",
  "attributes": ["org:resource", "customer_email"]
}
```

---

### POST `/privacy/generalize-timestamps`

Generalize timestamps to reduce re-identification risk.

| Field       | Type | Values                         |
| ----------- | ---- | ------------------------------ |
| `precision` | enum | `year`, `month`, `day`, `hour` |

---

## Error Responses

All errors follow RFC 7807 format:

```json
{
  "type": "error",
  "title": "Not Found",
  "status": 404,
  "detail": "Event log not found: log_invalid",
  "instance": "/api/v1/processes/log_invalid"
}
```

| Status | Meaning                     |
| ------ | --------------------------- |
| `400`  | Bad request / Invalid input |
| `401`  | Unauthorized                |
| `404`  | Resource not found          |
| `422`  | Validation error            |
| `500`  | Internal server error       |

---

## Rate Limits & Caching

| Category            | Limit         | Notes                                    |
| ------------------- | ------------- | ---------------------------------------- |
| Analytics endpoints | Cached 1 hour | `bottlenecks`, `rework`, `service-times` |
| File uploads        | 100MB max     | Per-file limit                           |
| Batch predictions   | 1000 cases    | Per-request limit                        |

**FE Notes:** Cached endpoints return stale data for 1 hour. Force refresh by adding `?_t={timestamp}` (not recommended for production).
