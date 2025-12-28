# API Routers - TLDR

Quick reference for the Process Mining API endpoints.

## Event Logs (`/api/v1/logs`)

| Endpoint                      | Method | Description                                      |
| ----------------------------- | ------ | ------------------------------------------------ |
| `/upload`                     | POST   | Upload CSV/XES file                              |
| `/preview`                    | POST   | Preview file before ingestion                    |
| `/detect-columns`             | POST   | Auto-detect column mappings                      |
| `/`                           | GET    | List logs (paginated with search/sort)           |
| `/{log_id}`                   | GET    | Get log details                                  |
| `/{log_id}`                   | PATCH  | **NEW** Update log name/description              |
| `/{log_id}`                   | DELETE | Delete log                                       |
| `/{log_id}/statistics`        | GET    | Detailed stats (durations, start/end activities) |
| `/{log_id}/quality`           | GET    | Quality report (completeness, validity, issues)  |
| `/{log_id}/variants`          | GET    | Basic variants                                   |
| `/{log_id}/variants/enhanced` | GET    | Enhanced variants with performance               |
| `/{log_id}/activities`        | GET    | List activities                                  |

### List Logs Query Parameters

| Parameter    | Type   | Default      | Description                          |
| ------------ | ------ | ------------ | ------------------------------------ |
| `page`       | int    | 1            | Page number                          |
| `page_size`  | int    | 20           | Items per page                       |
| `search`     | string | -            | Filter by name (case-insensitive)    |
| `sort_by`    | string | `created_at` | Sort field (created_at, name, etc.)  |
| `sort_order` | string | `desc`       | Sort direction (asc, desc)           |
| `state`      | string | -            | Filter by state (draft, ready, etc.) |

---

## Process Discovery (`/api/v1/discovery`)

| Endpoint                    | Method | Description                                                    |
| --------------------------- | ------ | -------------------------------------------------------------- |
| `/miners`                   | GET    | List available miners                                          |
| `/discover`                 | POST   | Run discovery algorithm                                        |
| `/dfg/{log_id}`             | GET    | Basic DFG                                                      |
| `/dfg/{log_id}/detailed`    | GET    | DFG with frequencies, probabilities                            |
| `/petri-net/{model_id}`     | GET    | Structured Petri Net (places, transitions, arcs)               |
| `/process-tree/{model_id}`  | GET    | Process Tree structure                                         |
| `/model/{model_id}/quality` | GET    | Model quality (fitness, precision, generalization, simplicity) |
| `/visualize/{model_id}`     | GET    | SVG visualization                                              |

---

## Process Models (`/api/v1/models`)

| Endpoint                | Method | Description                           |
| ----------------------- | ------ | ------------------------------------- |
| `/`                     | GET    | List all models                       |
| `/{model_id}`           | GET    | Get model details                     |
| `/{model_id}`           | PATCH  | **NEW** Update model name/description |
| `/{model_id}`           | DELETE | Delete model                          |
| `/{model_id}/visualize` | GET    | Visualize model as SVG                |

---

## Conformance Checking (`/api/v1/conformance`)

| Endpoint              | Method | Description                          |
| --------------------- | ------ | ------------------------------------ |
| `/check`              | POST   | Run conformance check                |
| `/fitness`            | GET    | Calculate fitness                    |
| `/precision`          | GET    | Calculate precision                  |
| `/diagnostics`        | GET    | Detailed diagnostics                 |
| `/deviations`         | GET    | List deviations                      |
| `/alignment`          | POST   | **NEW** Per-case alignment results   |
| `/deviation-patterns` | GET    | **NEW** Clustered deviation patterns |
| `/quality-metrics`    | GET    | **NEW** All 4 quality dimensions     |

---

## Performance Analysis (`/api/v1/performance`) — **NEW Phase 5.1**

| Endpoint                       | Method | Description                                  |
| ------------------------------ | ------ | -------------------------------------------- |
| `/analyze/{log_id}`            | POST   | Run performance analysis, detect bottlenecks |
| `/summary/{log_id}`            | GET    | Aggregated performance summary               |
| `/bottlenecks/{log_id}`        | GET    | List detected bottlenecks                    |
| `/duration-histogram/{log_id}` | GET    | Case duration distribution (histogram)       |
| `/activities/{log_id}`         | GET    | Per-activity performance metrics             |
| `/transitions/{log_id}`        | GET    | Per-transition (DFG edge) metrics            |

### Performance Analysis Query Parameters

| Parameter      | Endpoint              | Type   | Description                             |
| -------------- | --------------------- | ------ | --------------------------------------- |
| `min_severity` | `/bottlenecks`        | float  | Min severity score (0.0-1.0)            |
| `bins`         | `/duration-histogram` | int    | Number of histogram bins (5-50)         |
| `sort_by`      | `/activities`         | string | Sort by execution_count or avg_duration |
| `limit`        | All                   | int    | Max results to return                   |

---

## Quick Start

```bash
# 1. Preview a file
curl -X POST /api/v1/logs/preview -F "file=@data.csv"

# 2. Upload with column mapping
curl -X POST /api/v1/logs/upload \
  -F "file=@data.csv" \
  -F "case_id_column=CaseID" \
  -F "activity_column=Activity"

# 3. Get detailed DFG
curl /api/v1/discovery/dfg/{log_id}/detailed

# 4. Discover model
curl -X POST /api/v1/discovery/discover \
  -d '{"log_id": "...", "miner_type": "inductive"}'

# 5. Check conformance
curl -X POST /api/v1/conformance/check \
  -d '{"log_id": "...", "model_id": "..."}'

# 6. Get quality metrics
curl /api/v1/conformance/quality-metrics?log_id=...&model_id=...

# 7. Run performance analysis (NEW)
curl -X POST /api/v1/performance/analyze/{log_id} \
  -d '{"analysis_type": "duration"}'

# 8. Get bottlenecks (NEW)
curl /api/v1/performance/bottlenecks/{log_id}?min_severity=0.3
```

---

## UAT Testing Scope (v0.6.0)

**Coverage:** 26% of 237 business activities implemented

### ✅ Testable Flows

| Flow                 | Coverage | Test Focus                                   |
| -------------------- | -------- | -------------------------------------------- |
| Event Log Ingestion  | 90%      | Upload, preview, statistics, quality         |
| Process Discovery    | 53%      | All miners, DFG, Petri net, Process tree     |
| Conformance Checking | 45%      | Token replay, alignments, deviation patterns |
| Performance Analysis | 40%      | Duration, bottlenecks, histograms            |
| Org Mining           | 47%      | Handover network, working together, roles    |

### ❌ Known Limitations (Not in UAT Scope)

- Model export (BPMN/PNML) - not implemented
- Case drill-down (individual case view) - not implemented
- Report generation (PDF/Excel) - not implemented
- Variant filtering/visualization - basic only
- Drift detection, OCEL, Simulation - not implemented

### UAT Access Points

| Resource       | URL                                              |
| -------------- | ------------------------------------------------ |
| Swagger Docs   | http://localhost:8001/docs                       |
| ReDoc          | http://localhost:8001/redoc                      |
| API Test Bench | http://localhost:8001/static/api_test_bench.html |
