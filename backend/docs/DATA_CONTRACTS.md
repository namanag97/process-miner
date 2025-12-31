# Data Contracts

> **Canonical Source:** TypeScript interfaces in `/sdk/src/types/`  
> **Python Source:** Pydantic models in `/backend/src/models/schemas.py`

---

## Quick Navigation

| Category                          | Schemas                         |
| --------------------------------- | ------------------------------- |
| [Common](#common)                 | Pagination, Errors              |
| [Projects](#projects)             | Create, Update, Response        |
| [Event Logs](#event-logs)         | Process, Case, Event, Variant   |
| [Discovery](#discovery)           | Miner, Model                    |
| [Visualization](#visualization)   | DFG, Petri Net                  |
| [Conformance](#conformance)       | Check, Diagnostics, Alignment   |
| [Analytics](#analytics)           | Bottleneck, Rework, Performance |
| [Filtering](#filtering)           | Filter, Preview, Options        |
| [Predictions](#predictions)       | Predictor, Prediction           |
| [OCPM](#ocpm)                     | OCEL Log, OC-DFG                |
| [Organizational](#organizational) | Network, Role, Profile          |
| [Simulation](#simulation)         | PlayOut, Simulation             |
| [Enums](#enums)                   | MinerType, ModelFormat, etc.    |

---

## Common

### PaginationParams

| Field       | Type | Required | Default | Notes     |
| ----------- | ---- | -------- | ------- | --------- |
| `page`      | int  | ❌       | 1       | 1-indexed |
| `page_size` | int  | ❌       | 20      | Max 100   |

### PaginatedResponse

```typescript
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
```

| Field       | Type | Notes          |
| ----------- | ---- | -------------- |
| `items`     | T[]  | Page data      |
| `total`     | int  | Total count    |
| `page`      | int  | Current page   |
| `page_size` | int  | Items per page |
| `pages`     | int  | Total pages    |

### ErrorResponse

RFC 7807 Problem Details format.

```typescript
interface ErrorResponse {
  type: string; // "error"
  title: string; // Human-readable title
  status: number; // HTTP status code
  detail: string; // Specific error message
  instance?: string; // Request path
}
```

---

## Projects

### ProjectCreateRequest

```typescript
interface ProjectCreateRequest {
  name: string;
  description?: string;
  tags?: string[];
}
```

**Python:** `src/models/schemas.py:ProjectCreateRequest`

| Field         | Type     | Required | Default | Notes          |
| ------------- | -------- | -------- | ------- | -------------- |
| `name`        | string   | ✅       | -       | 1-255 chars    |
| `description` | string   | ❌       | null    | Max 2000 chars |
| `tags`        | string[] | ❌       | []      | For filtering  |

### ProjectUpdateRequest

```typescript
interface ProjectUpdateRequest {
  name?: string;
  description?: string;
  tags?: string[];
}
```

| Field         | Type     | Required | Notes                   |
| ------------- | -------- | -------- | ----------------------- |
| `name`        | string   | ❌       | 1-255 chars if provided |
| `description` | string   | ❌       | Max 2000 chars          |
| `tags`        | string[] | ❌       | Replaces existing tags  |

### ProjectResponse

```typescript
interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  tags: string[];
  total_files: number;
  total_analyses: number;
  created_at: string; // ISO 8601
  updated_at: string | null;
}
```

**Python:** `src/models/schemas.py:ProjectResponse`

| Field            | Type     | Required | Notes                        |
| ---------------- | -------- | -------- | ---------------------------- |
| `id`             | string   | ✅       | UUID                         |
| `name`           | string   | ✅       | -                            |
| `description`    | string   | ❌       | -                            |
| `tags`           | string[] | ✅       | Empty array if none          |
| `total_files`    | int      | ✅       | Event logs in project        |
| `total_analyses` | int      | ✅       | Models + conformance results |
| `created_at`     | datetime | ✅       | ISO 8601                     |
| `updated_at`     | datetime | ❌       | null until first update      |

### ProjectListResponse

```typescript
interface ProjectListResponse extends PaginatedResponse<ProjectResponse> {
  items: ProjectResponse[];
}
```

### ProjectDetailResponse

Extends `ProjectResponse`:

```typescript
interface ProjectDetailResponse extends ProjectResponse {
  event_logs: ProcessResponse[];
}
```

| Field        | Type              | Notes                              |
| ------------ | ----------------- | ---------------------------------- |
| `event_logs` | ProcessResponse[] | All logs belonging to this project |

---

## Event Logs

### ProcessResponse

```typescript
interface ProcessResponse {
  id: string;
  name: string;
  source_format: string;
  total_events: number;
  total_cases: number;
  total_activities: number;
  activities: string[];
  created_at: string; // ISO 8601
  source_file?: string;
}
```

**Python:** `src/models/schemas.py:ProcessResponse`

| Field              | Type     | Required | Notes                     |
| ------------------ | -------- | -------- | ------------------------- |
| `id`               | string   | ✅       | UUID                      |
| `name`             | string   | ✅       | User-provided or filename |
| `source_format`    | string   | ✅       | `csv`, `xes`              |
| `total_events`     | int      | ✅       | -                         |
| `total_cases`      | int      | ✅       | -                         |
| `total_activities` | int      | ✅       | -                         |
| `activities`       | string[] | ✅       | Unique activity names     |
| `created_at`       | datetime | ✅       | ISO 8601                  |
| `source_file`      | string   | ❌       | Original filename         |

### ProcessDetailResponse

Extends `ProcessResponse`:

| Field        | Type     | Required | Notes          |
| ------------ | -------- | -------- | -------------- |
| `statistics` | object   | ❌       | Extended stats |
| `updated_at` | datetime | ❌       | Last update    |

### CaseResponse

```typescript
interface CaseResponse {
  case_id: string;
  event_count: number;
  variant?: string;
  start_time?: string;
  end_time?: string;
  duration_seconds?: number;
}
```

| Field              | Type     | Required | Notes             |
| ------------------ | -------- | -------- | ----------------- |
| `case_id`          | string   | ✅       | Business case ID  |
| `event_count`      | int      | ✅       | Events in case    |
| `variant`          | string   | ❌       | Activity sequence |
| `start_time`       | datetime | ❌       | First event time  |
| `end_time`         | datetime | ❌       | Last event time   |
| `duration_seconds` | float    | ❌       | End - Start       |

### VariantResponse

```typescript
interface VariantResponse {
  variant_key: string;
  activity_trace: string;
  case_count: number;
  frequency_percent: number;
  avg_duration_seconds?: number;
  complexity_score?: number;
  rework_count?: number;
  unique_activity_count?: number;
}
```

| Field                   | Type   | Required | Notes                              |
| ----------------------- | ------ | -------- | ---------------------------------- |
| `variant_key`           | string | ✅       | Unique identifier                  |
| `activity_trace`        | string | ✅       | `A→B→C` format                     |
| `case_count`            | int    | ✅       | Cases with this variant            |
| `frequency_percent`     | float  | ✅       | % of total cases                   |
| `avg_duration_seconds`  | float  | ❌       | Average case duration              |
| `complexity_score`      | float  | ❌       | 0-1, requires `include_complexity` |
| `rework_count`          | int    | ❌       | Repeated activities                |
| `unique_activity_count` | int    | ❌       | Distinct activities                |

### ActivityDetailResponse

```typescript
interface ActivityDetailResponse {
  activity: string;
  frequency: number;
  frequency_percent: number;
  avg_duration_seconds?: number;
  min_duration_seconds?: number;
  max_duration_seconds?: number;
  is_start_activity: boolean;
  is_end_activity: boolean;
  position_avg?: number;
  resources: string[];
}
```

| Field                  | Type     | Required | Default | Notes                     |
| ---------------------- | -------- | -------- | ------- | ------------------------- |
| `activity`             | string   | ✅       | -       | Activity name             |
| `frequency`            | int      | ✅       | -       | Total occurrences         |
| `frequency_percent`    | float    | ✅       | -       | % of total events         |
| `avg_duration_seconds` | float    | ❌       | null    | Time to next activity     |
| `min_duration_seconds` | float    | ❌       | null    | -                         |
| `max_duration_seconds` | float    | ❌       | null    | -                         |
| `is_start_activity`    | bool     | ✅       | false   | First in any case         |
| `is_end_activity`      | bool     | ✅       | false   | Last in any case          |
| `position_avg`         | float    | ❌       | null    | 0=start, 1=end            |
| `resources`            | string[] | ✅       | []      | Resources performing this |

### StatisticsResponse

```typescript
interface StatisticsResponse {
  total_events: number;
  total_cases: number;
  total_activities: number;
  total_variants: number;
  activities: string[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  avg_case_duration_seconds?: number;
  min_case_duration_seconds?: number;
  max_case_duration_seconds?: number;
  date_range?: { start: string; end: string };
}
```

### ColumnDetectionResponse

```typescript
interface ColumnDetectionResponse {
  columns: string[];
  suggestions: {
    case_id?: string;
    activity?: string;
    timestamp?: string;
    resource?: string;
  };
  sample_rows: Record<string, unknown>[];
  row_count: number;
}
```

---

## Discovery

### MinerInfo

```typescript
interface MinerInfo {
  id: string;
  name: string;
  description: string;
  output_format: string;
}
```

| Field           | Type   | Notes                              |
| --------------- | ------ | ---------------------------------- |
| `id`            | string | `alpha`, `inductive`, etc.         |
| `name`          | string | Display name                       |
| `description`   | string | Brief description                  |
| `output_format` | string | `petri_net`, `process_tree`, `dfg` |

### DiscoverRequest

```typescript
interface DiscoverRequest {
  log_id: string;
  miner_type?: MinerType;
  model_name?: string;
}
```

| Field        | Type   | Required | Default        |
| ------------ | ------ | -------- | -------------- |
| `log_id`     | string | ✅       | -              |
| `miner_type` | enum   | ❌       | `inductive`    |
| `model_name` | string | ❌       | Auto-generated |

### ModelResponse

```typescript
interface ModelResponse {
  id: string;
  name: string;
  miner_type: string;
  model_format: string;
  log_id?: string;
  fitness?: number;
  precision?: number;
  created_at: string;
}
```

| Field          | Type     | Required | Notes               |
| -------------- | -------- | -------- | ------------------- |
| `id`           | string   | ✅       | UUID                |
| `name`         | string   | ✅       | -                   |
| `miner_type`   | string   | ✅       | Algorithm used      |
| `model_format` | string   | ✅       | Output format       |
| `log_id`       | string   | ❌       | Source log          |
| `fitness`      | float    | ❌       | 0-1, quality metric |
| `precision`    | float    | ❌       | 0-1, quality metric |
| `created_at`   | datetime | ✅       | -                   |

---

## Visualization

### DFGNode

```typescript
interface DFGNode {
  id: string;
  name: string;
  frequency: number;
  is_start: boolean;
  is_end: boolean;
}
```

| Field       | Type   | Default | Notes                                |
| ----------- | ------ | ------- | ------------------------------------ |
| `id`        | string | -       | Activity name (use as React node ID) |
| `name`      | string | -       | Display name                         |
| `frequency` | int    | -       | Occurrence count                     |
| `is_start`  | bool   | false   | Start activity                       |
| `is_end`    | bool   | false   | End activity                         |

### DFGEdge

```typescript
interface DFGEdge {
  source: string;
  target: string;
  frequency: number;
  probability: number;
  avg_duration_seconds?: number;
  min_duration_seconds?: number;
  max_duration_seconds?: number;
}
```

| Field                  | Type   | Required | Notes                           |
| ---------------------- | ------ | -------- | ------------------------------- |
| `source`               | string | ✅       | Source activity                 |
| `target`               | string | ✅       | Target activity                 |
| `frequency`            | int    | ✅       | Transition count                |
| `probability`          | float  | ✅       | 0-1, transition probability     |
| `avg_duration_seconds` | float  | ❌       | When `include_performance=true` |
| `min_duration_seconds` | float  | ❌       | -                               |
| `max_duration_seconds` | float  | ❌       | -                               |

### DFGResponse

```typescript
interface DFGResponse {
  nodes: DFGNode[];
  edges: DFGEdge[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  total_frequency: number;
}
```

### ProcessExplorerDataResponse

**⭐ Combined response for Process Explorer UI**

```typescript
interface ProcessExplorerDataResponse {
  log_id: string;
  dfg: DFGResponse;
  variants: VariantResponse[];
  activities: ActivityDetailResponse[];
  statistics: StatisticsResponse;
}
```

### PetriNetPlace

```typescript
interface PetriNetPlace {
  id: string;
  name: string;
  tokens: number;
}
```

### PetriNetTransition

```typescript
interface PetriNetTransition {
  id: string;
  name: string;
  label?: string;
}
```

### PetriNetArc

```typescript
interface PetriNetArc {
  source: string;
  target: string;
  weight: number;
}
```

### PetriNetResponse

```typescript
interface PetriNetResponse {
  places: PetriNetPlace[];
  transitions: PetriNetTransition[];
  arcs: PetriNetArc[];
  initial_marking: string[];
  final_marking: string[];
}
```

---

## Conformance

### ConformanceCheckRequest

```typescript
interface ConformanceCheckRequest {
  log_id: string;
  model_id: string;
  method?: ConformanceMethod;
}
```

| Field    | Type | Default        |
| -------- | ---- | -------------- |
| `method` | enum | `token_replay` |

### ConformanceResponse

```typescript
interface ConformanceResponse {
  id: string;
  log_id: string;
  model_id: string;
  fitness: number;
  precision?: number;
  generalization?: number;
  simplicity?: number;
  method: string;
  is_conformant: boolean;
  fitting_traces: number;
  total_traces: number;
  created_at: string;
}
```

### DeviationDetail

```typescript
interface DeviationDetail {
  case_id: string;
  activity: string;
  violation_type: string;
  expected_after?: string;
  frequency: number;
  impact: string;
}
```

| Field            | Type   | Notes                             |
| ---------------- | ------ | --------------------------------- |
| `violation_type` | string | `missing`, `extra`, `wrong_order` |
| `impact`         | string | `low`, `medium`, `high`           |

### DiagnosticsResponse

```typescript
interface DiagnosticsResponse {
  fitness: number;
  precision?: number;
  generalization?: number;
  simplicity?: number;
  total_traces: number;
  fitting_traces: number;
  non_fitting_traces: number;
  fitness_ratio: number;
  deviations?: DeviationDetail[];
}
```

### AlignmentMove

```typescript
interface AlignmentMove {
  log_move?: string;
  model_move?: string;
  move_type: string;
}
```

| Field       | Type   | Notes                            |
| ----------- | ------ | -------------------------------- |
| `move_type` | string | `sync`, `log_only`, `model_only` |

### CaseAlignmentResponse

```typescript
interface CaseAlignmentResponse {
  case_id: string;
  fitness: number;
  cost: number;
  alignment: AlignmentMove[];
  is_fit: boolean;
}
```

### AlignmentDiagnosticsResponse

```typescript
interface AlignmentDiagnosticsResponse {
  log_id: string;
  model_id: string;
  total_cases: number;
  fitting_cases: number;
  average_fitness: number;
  case_alignments: CaseAlignmentResponse[];
}
```

---

## Analytics

### BottleneckResponse

```typescript
interface BottleneckResponse {
  activity: string;
  avg_waiting_time_seconds: number;
  avg_service_time_seconds: number;
  frequency: number;
  is_bottleneck: boolean;
  severity: string;
  preceding_activities: string[];
  following_activities: string[];
  bottleneck_impact_score: number;
}
```

| Field                     | Type     | Default | Notes                   |
| ------------------------- | -------- | ------- | ----------------------- |
| `severity`                | string   | -       | `low`, `medium`, `high` |
| `preceding_activities`    | string[] | []      | Top 5 before            |
| `following_activities`    | string[] | []      | Top 5 after             |
| `bottleneck_impact_score` | float    | 0.0     | 0-1 composite score     |

### BottleneckListResponse

```typescript
interface BottleneckListResponse {
  log_id: string;
  bottlenecks: BottleneckResponse[];
  total_bottlenecks: number;
}
```

### ReworkResponse

```typescript
interface ReworkResponse {
  activity: string;
  rework_count: number;
  cases_with_rework: number;
  rework_percentage: number;
}
```

### ReworkListResponse

```typescript
interface ReworkListResponse {
  log_id: string;
  rework_activities: ReworkResponse[];
  total_rework_cases: number;
  rework_percentage: number;
}
```

### ReworkChain

```typescript
interface ReworkChain {
  activity: string;
  chain_length: number;
  frequency: number;
  avg_chain_duration_seconds: number;
  example_case_ids: string[];
}
```

### ReworkChainListResponse

```typescript
interface ReworkChainListResponse {
  log_id: string;
  chains: ReworkChain[];
  total_chains: number;
  most_problematic_activity?: string;
  cases_with_chains: number;
  chains_percentage: number;
}
```

### ServiceTimeResponse

```typescript
interface ServiceTimeResponse {
  activity: string;
  min_seconds: number;
  max_seconds: number;
  avg_seconds: number;
  median_seconds: number;
  std_dev_seconds: number;
}
```

### CycleTimeResponse

```typescript
interface CycleTimeResponse {
  log_id: string;
  min_seconds: number;
  max_seconds: number;
  avg_seconds: number;
  median_seconds: number;
  percentile_25_seconds: number;
  percentile_75_seconds: number;
  percentile_95_seconds: number;
}
```

### ThroughputResponse

```typescript
interface ThroughputResponse {
  log_id: string;
  total_cases: number;
  completed_cases: number;
  cases_per_day: number;
  cases_per_week: number;
  cases_per_month: number;
  time_range_days: number;
}
```

### PatternResponse

```typescript
interface PatternResponse {
  pattern: string;
  frequency: number;
  support: number;
}
```

### PerformanceDashboardResponse

```typescript
interface PerformanceDashboardResponse {
  log_id: string;
  cycle_time: CycleTimeResponse;
  throughput: ThroughputResponse;
  top_bottlenecks: BottleneckResponse[];
  rework_summary: Record<string, unknown>;
}
```

---

## Filtering

### FilterConfig

```typescript
interface FilterConfig {
  type: string;
  params: Record<string, unknown>;
}
```

| type                   | params                       |
| ---------------------- | ---------------------------- |
| `time_range`           | `{start, end}`               |
| `variants_top_k`       | `{k}`                        |
| `variants_coverage`    | `{coverage_percent}`         |
| `activities_include`   | `{activities[]}`             |
| `activities_exclude`   | `{activities[]}`             |
| `performance_duration` | `{min_seconds, max_seconds}` |
| `case_size`            | `{min_events, max_events}`   |

### FilterRequest

```typescript
interface FilterRequest {
  name?: string;
  filters: FilterConfig[];
  save_result: boolean;
}
```

### FilterPreviewRequest

```typescript
interface FilterPreviewRequest {
  filters: FilterConfig[];
}
```

### FilterStatistics

```typescript
interface FilterStatistics {
  original_cases: number;
  filtered_cases: number;
  cases_removed: number;
  cases_retained_pct: number;
  original_events: number;
  filtered_events: number;
  events_removed: number;
  events_retained_pct: number;
  original_activities: number;
  filtered_activities: number;
  activities_removed: number;
}
```

### FilterPreviewResponse

```typescript
interface FilterPreviewResponse {
  would_retain_cases: number;
  would_retain_events: number;
  statistics: FilterStatistics;
  filters_applied: FilterConfig[];
}
```

### FilteredLogResponse

```typescript
interface FilteredLogResponse {
  id: string;
  name: string;
  source_log_id: string;
  is_filtered: boolean;
  filter_config: FilterConfig[];
  total_events: number;
  total_cases: number;
  total_activities: number;
  statistics?: FilterStatistics;
  created_at: string;
}
```

### FilterOptionsResponse

```typescript
interface FilterOptionsResponse {
  activities: string[];
  resources: string[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  total_variants: number;
  time_range: { start?: string; end?: string };
  case_size_range: { min: number; max: number; avg: number };
}
```

### FilterTemplateResponse

```typescript
interface FilterTemplateResponse {
  id: string;
  name: string;
  description: string;
  filters: FilterConfig[];
}
```

---

## Predictions

### TrainPredictorRequest

```typescript
interface TrainPredictorRequest {
  target_type: string;
  algorithm: string;
  outcome_attribute?: string;
}
```

| Field         | Type | Values                                          |
| ------------- | ---- | ----------------------------------------------- |
| `target_type` | enum | `next_activity`, `remaining_time`, `outcome`    |
| `algorithm`   | enum | `random_forest`, `xgboost`, `gradient_boosting` |

### PredictorResponse

```typescript
interface PredictorResponse {
  id: string;
  log_id: string;
  target_type: string;
  algorithm: string;
  metrics: Record<string, number>;
  trained_at: string;
}
```

| Field     | Type   | Notes                                   |
| --------- | ------ | --------------------------------------- |
| `metrics` | object | `{accuracy, f1_score}` or `{mae, rmse}` |

### PredictionRequest

```typescript
interface PredictionRequest {
  case_prefix: string[];
  case_attributes?: Record<string, unknown>;
}
```

### PredictionResponse

```typescript
interface PredictionResponse {
  predictor_id: string;
  case_prefix: string[];
  prediction: unknown;
  confidence?: number;
  alternatives?: Array<{ activity: string; probability: number }>;
}
```

### BatchPredictionRequest

```typescript
interface BatchPredictionRequest {
  cases: PredictionRequest[];
}
```

### BatchPredictionResponse

```typescript
interface BatchPredictionResponse {
  predictor_id: string;
  predictions: PredictionResponse[];
}
```

### JobStatusResponse

```typescript
interface JobStatusResponse {
  id: string;
  job_type: string;
  status: string;
  progress: number;
  result?: Record<string, unknown>;
  error?: string;
  created_at: string;
}
```

| Field      | Type | Notes                                       |
| ---------- | ---- | ------------------------------------------- |
| `status`   | enum | `pending`, `running`, `completed`, `failed` |
| `progress` | int  | 0-100                                       |

---

## OCPM

### OCELLogResponse

```typescript
interface OCELLogResponse {
  id: string;
  name: string;
  source_file?: string;
  source_format: string;
  total_events: number;
  total_objects: number;
  total_object_types: number;
  object_types: string[];
  activities: string[];
  created_at: string;
}
```

### OCELObjectTypeResponse

```typescript
interface OCELObjectTypeResponse {
  name: string;
  object_count: number;
  attributes: string[];
}
```

### OCELStatisticsResponse

```typescript
interface OCELStatisticsResponse {
  log_id: string;
  total_events: number;
  total_objects: number;
  total_object_types: number;
  total_activities: number;
  object_types: string[];
  activities: string[];
  objects_per_type: Record<string, number>;
}
```

### OCDFGNode

```typescript
interface OCDFGNode {
  id: string;
  name: string;
  object_type: string;
  frequency: number;
}
```

### OCDFGEdge

```typescript
interface OCDFGEdge {
  source: string;
  target: string;
  object_type: string;
  frequency: number;
}
```

### OCDFGTypeGraph

```typescript
interface OCDFGTypeGraph {
  object_type: string;
  nodes: OCDFGNode[];
  edges: OCDFGEdge[];
  start_activities: string[];
  end_activities: string[];
}
```

### OCDFGResponse

```typescript
interface OCDFGResponse {
  log_id: string;
  object_types: string[];
  activities: string[];
  graphs_by_type: Record<string, OCDFGTypeGraph>;
  total_events: number;
  total_objects: number;
}
```

### OCPetriNetResponse

```typescript
interface OCPetriNetResponse {
  id: string;
  log_id: string;
  name: string;
  object_types: string[];
  created_at: string;
}
```

---

## Organizational

### NetworkNode

```typescript
interface NetworkNode {
  id: string;
  label: string;
  type: string;
  weight: number;
}
```

### NetworkEdge

```typescript
interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
  label?: string;
}
```

### SocialNetworkResponse

```typescript
interface SocialNetworkResponse {
  log_id: string;
  network_type: string;
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  metrics: Record<string, unknown>;
}
```

| Field          | Type   | Notes                                     |
| -------------- | ------ | ----------------------------------------- |
| `network_type` | string | `handover`, `collaboration`, `similarity` |
| `metrics`      | object | `{density, avg_degree, ...}`              |

### ResourceRoleResponse

```typescript
interface ResourceRoleResponse {
  role_id: string;
  resources: string[];
  activities: string[];
}
```

### ResourceProfileResponse

```typescript
interface ResourceProfileResponse {
  resource: string;
  total_events: number;
  activities: Record<string, number>;
  avg_processing_time_seconds: number;
  first_activity?: string;
  last_activity?: string;
}
```

### ResourceWorkloadResponse

```typescript
interface ResourceWorkloadResponse {
  log_id: string;
  workload: Record<string, number>;
  avg_events_per_resource: number;
}
```

---

## Simulation

### PlayOutRequest

```typescript
interface PlayOutRequest {
  num_traces: number;
}
```

| Field        | Type | Default | Range   |
| ------------ | ---- | ------- | ------- |
| `num_traces` | int  | 100     | 1-10000 |

### PlayOutResponse

```typescript
interface PlayOutResponse {
  model_id: string;
  generated_log_id: string;
  traces_generated: number;
  events_generated: number;
}
```

### SimulationRequest

```typescript
interface SimulationRequest {
  modifications: Array<Record<string, unknown>>;
}
```

| Modification Type | Params               |
| ----------------- | -------------------- |
| `remove_activity` | `{activity}`         |
| `speed_up`        | `{activity, factor}` |
| `add_activity`    | `{activity, after}`  |

### SimulationResponse

```typescript
interface SimulationResponse {
  log_id: string;
  scenario: string;
  original_metrics: Record<string, number>;
  simulated_metrics: Record<string, number>;
  impact: Record<string, number>;
}
```

---

## Enums

### MinerType

```typescript
type MinerType =
  | "alpha"
  | "alpha_plus"
  | "inductive"
  | "inductive_infrequent"
  | "heuristics"
  | "dfg";
```

**Python:** `src/core/enums.py:MinerType`

### ModelFormat

```typescript
type ModelFormat = "petri_net" | "process_tree" | "dfg" | "bpmn";
```

### SourceFormat

```typescript
type SourceFormat = "csv" | "xes" | "ocel_json" | "ocel_sqlite";
```

### ConformanceMethod

```typescript
type ConformanceMethod = "token_replay" | "alignment";
```

### WorkflowStatus

```typescript
type WorkflowStatus = "pending" | "running" | "completed" | "failed";
```

---

## Type Mapping: Python → TypeScript

| Python         | TypeScript          |
| -------------- | ------------------- |
| `str`          | `string`            |
| `int`          | `number`            |
| `float`        | `number`            |
| `bool`         | `boolean`           |
| `datetime`     | `string` (ISO 8601) |
| `list[T]`      | `T[]`               |
| `dict[str, T]` | `Record<string, T>` |
| `Optional[T]`  | `T \| undefined`    |
| `Any`          | `unknown`           |

---

## Nullable Fields Convention

- **Python:** `Optional[T] = None`
- **TypeScript:** `field?: T`
- **JSON:** Omitted or `null`

FE should always use optional chaining (`?.`) for nullable fields.
