# API Routers - TLDR

Quick reference for the Process Mining API endpoints.

## Event Logs (`/api/v1/logs`)

| Endpoint                      | Method | Description                                              |
| ----------------------------- | ------ | -------------------------------------------------------- |
| `/upload`                     | POST   | Upload CSV/XES file                                      |
| `/preview`                    | POST   | **NEW** Preview file before ingestion                    |
| `/detect-columns`             | POST   | Auto-detect column mappings                              |
| `/`                           | GET    | List all logs                                            |
| `/{log_id}`                   | GET    | Get log details                                          |
| `/{log_id}/statistics`        | GET    | **NEW** Detailed stats (durations, start/end activities) |
| `/{log_id}/quality`           | GET    | **NEW** Quality report (completeness, validity, issues)  |
| `/{log_id}/variants`          | GET    | Basic variants                                           |
| `/{log_id}/variants/enhanced` | GET    | **NEW** Enhanced variants with performance               |
| `/{log_id}/activities`        | GET    | List activities                                          |

---

## Process Discovery (`/api/v1/discovery`)

| Endpoint                    | Method | Description                                                            |
| --------------------------- | ------ | ---------------------------------------------------------------------- |
| `/miners`                   | GET    | List available miners                                                  |
| `/discover`                 | POST   | Run discovery algorithm                                                |
| `/dfg/{log_id}`             | GET    | Basic DFG                                                              |
| `/dfg/{log_id}/detailed`    | GET    | **NEW** DFG with frequencies, probabilities                            |
| `/petri-net/{model_id}`     | GET    | **NEW** Structured Petri Net (places, transitions, arcs)               |
| `/process-tree/{model_id}`  | GET    | **NEW** Process Tree structure                                         |
| `/model/{model_id}/quality` | GET    | **NEW** Model quality (fitness, precision, generalization, simplicity) |
| `/visualize/{model_id}`     | GET    | SVG visualization                                                      |

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
```
