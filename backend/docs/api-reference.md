# Process Mining API Reference

> **Base URL**: `/api/v1` | **Format**: JSON | **Errors**: RFC 7807

---

## 📁 Datasets

| Method   | Endpoint                         | Description             | Errors   |
| -------- | -------------------------------- | ----------------------- | -------- |
| `POST`   | `/datasets/upload`               | Upload CSV/XES file     | 400, 422 |
| `POST`   | `/datasets/detect-columns`       | Auto-detect CSV columns | 400, 422 |
| `GET`    | `/datasets`                      | List all datasets       | -        |
| `GET`    | `/datasets/{id}`                 | Get dataset details     | 404      |
| `DELETE` | `/datasets/{id}`                 | Delete dataset          | 404      |
| `GET`    | `/datasets/{id}/statistics`      | Get log statistics      | 404      |
| `GET`    | `/datasets/{id}/cases`           | List cases (paginated)  | 404      |
| `GET`    | `/datasets/{id}/variants`        | Get process variants    | 404      |
| `GET`    | `/datasets/{id}/activities`      | Get activity stats      | 404      |
| `GET`    | `/datasets/{id}/domain-analysis` | Rich domain analysis    | 404      |

**Query Params**: `page`, `page_size`, `top_n`, `top_k_percent`, `sort_by`, `include_complexity`

---

## 🔍 Discovery

| Method   | Endpoint                 | Description            | Errors        |
| -------- | ------------------------ | ---------------------- | ------------- |
| `GET`    | `/discovery/miners`      | List available miners  | -             |
| `POST`   | `/discovery/discover`    | Discover process model | 400, 404, 500 |
| `GET`    | `/discovery/models`      | List discovered models | -             |
| `GET`    | `/discovery/models/{id}` | Get model details      | 404           |
| `DELETE` | `/discovery/models/{id}` | Delete model           | 404           |

**Miners**: `alpha`, `heuristics`, `inductive`, `dfg`

---

## ✅ Conformance

| Method   | Endpoint                    | Description                 | Errors   |
| -------- | --------------------------- | --------------------------- | -------- |
| `POST`   | `/conformance/check`        | Check log-model conformance | 404, 500 |
| `GET`    | `/conformance/results`      | List conformance results    | -        |
| `GET`    | `/conformance/results/{id}` | Get result details          | 404      |
| `DELETE` | `/conformance/results/{id}` | Delete result               | 404      |
| `GET`    | `/conformance/diagnostics`  | Trace-level diagnostics     | 404      |
| `GET`    | `/conformance/deviations`   | List deviations             | 404      |
| `GET`    | `/conformance/alignments`   | Alignment diagnostics       | 404      |
| `GET`    | `/conformance/methods`      | List available methods      | -        |
| `GET`    | `/conformance/quality`      | Full quality metrics        | 404      |

**Methods**: `token_replay`, `alignment`

---

## 📊 Visualization

| Method | Endpoint                               | Description             | Errors |
| ------ | -------------------------------------- | ----------------------- | ------ |
| `GET`  | `/visualization/logs/{id}/dfg`         | Get DFG nodes/edges     | 404    |
| `GET`  | `/visualization/models/{id}/petri-net` | Get Petri net structure | 404    |
| `GET`  | `/visualization/models/{id}/svg`       | Export model SVG        | 404    |
| `GET`  | `/visualization/logs/{id}/dfg-svg`     | Export DFG SVG          | 404    |
| `GET`  | `/visualization/logs/{id}/footprints`  | Get footprint matrix    | 404    |
| `GET`  | `/visualization/logs/{id}/explorer`    | Unified explorer data   | 404    |

---

## 🔧 Filtering

| Method   | Endpoint                              | Description                 | Errors   |
| -------- | ------------------------------------- | --------------------------- | -------- |
| `POST`   | `/filtering/logs/{id}/apply`          | Apply filters (new log)     | 400, 404 |
| `POST`   | `/filtering/logs/{id}/preview`        | Preview filter impact       | 400, 404 |
| `GET`    | `/filtering/logs/{id}/options`        | Get available filter values | 404      |
| `GET`    | `/filtering/logs/{id}/filtered`       | List filtered versions      | 404      |
| `DELETE` | `/filtering/logs/{id}/filtered/{fid}` | Delete filtered log         | 404      |
| `GET`    | `/filtering/templates`                | Get filter templates        | -        |

**Filter Types**: `time_range`, `activities`, `variants`, `case_duration`, `attributes`

---

## 📈 Analytics

| Method | Endpoint                             | Description            | Errors |
| ------ | ------------------------------------ | ---------------------- | ------ |
| `GET`  | `/analytics/logs/{id}/bottlenecks`   | Detect bottlenecks     | 404    |
| `GET`  | `/analytics/logs/{id}/rework`        | Analyze rework         | 404    |
| `GET`  | `/analytics/logs/{id}/service-times` | Activity service times | 404    |
| `GET`  | `/analytics/logs/{id}/cycle-time`    | Case duration stats    | 404    |
| `GET`  | `/analytics/logs/{id}/throughput`    | Throughput metrics     | 404    |
| `GET`  | `/analytics/logs/{id}/patterns`      | Frequent patterns      | 404    |
| `GET`  | `/analytics/logs/{id}/rework-chains` | Rework chain detection | 404    |
| `GET`  | `/analytics/logs/{id}/performance`   | Full dashboard         | 404    |

---

## 👥 Organizational

| Method | Endpoint                                          | Description           | Errors |
| ------ | ------------------------------------------------- | --------------------- | ------ |
| `GET`  | `/organizational/logs/{id}/handover-network`      | Handover of work      | 404    |
| `GET`  | `/organizational/logs/{id}/collaboration-network` | Working together      | 404    |
| `GET`  | `/organizational/logs/{id}/resource-similarity`   | Resource similarity   | 404    |
| `GET`  | `/organizational/logs/{id}/roles`                 | Discover roles        | 404    |
| `GET`  | `/organizational/logs/{id}/resources/{r}/profile` | Resource profile      | 404    |
| `GET`  | `/organizational/logs/{id}/workload`              | Workload distribution | 404    |

---

## 🤖 Predictions

| Method   | Endpoint                                     | Description           | Errors   |
| -------- | -------------------------------------------- | --------------------- | -------- |
| `POST`   | `/predictions/logs/{id}/train`               | Train predictor       | 400, 404 |
| `GET`    | `/predictions/jobs/{id}`                     | Get training status   | 404      |
| `GET`    | `/predictions/logs/{id}/predictors`          | List predictors       | 404      |
| `GET`    | `/predictions/predictors/{id}`               | Get predictor details | 404      |
| `POST`   | `/predictions/predictors/{id}/predict`       | Single prediction     | 404      |
| `POST`   | `/predictions/predictors/{id}/predict-batch` | Batch predictions     | 404      |
| `DELETE` | `/predictions/predictors/{id}`               | Delete predictor      | 404      |

**Target Types**: `next_activity`, `remaining_time`, `outcome`

---

## 🎮 Simulation

| Method | Endpoint                              | Description            | Errors   |
| ------ | ------------------------------------- | ---------------------- | -------- |
| `POST` | `/simulation/models/{id}/play-out`    | Generate synthetic log | 400, 404 |
| `POST` | `/simulation/logs/{id}/simulate`      | What-if simulation     | 404      |
| `POST` | `/simulation/logs/{id}/capacity-plan` | Capacity planning      | 404      |

---

## 🔷 OCPM (Object-Centric)

| Method   | Endpoint                        | Description            | Errors   |
| -------- | ------------------------------- | ---------------------- | -------- |
| `POST`   | `/ocpm/upload`                  | Upload OCEL file       | 400, 422 |
| `GET`    | `/ocpm/logs`                    | List OCEL logs         | -        |
| `GET`    | `/ocpm/logs/{id}`               | Get OCEL details       | 404      |
| `DELETE` | `/ocpm/logs/{id}`               | Delete OCEL log        | 404      |
| `GET`    | `/ocpm/logs/{id}/object-types`  | Get object types       | 404      |
| `GET`    | `/ocpm/logs/{id}/statistics`    | OCEL statistics        | 404      |
| `POST`   | `/ocpm/discover-ocpn`           | Discover OC-Petri net  | 400, 404 |
| `GET`    | `/ocpm/models`                  | List OC-PNs            | -        |
| `GET`    | `/ocpm/models/{id}`             | Get OC-PN details      | 404      |
| `DELETE` | `/ocpm/models/{id}`             | Delete OC-PN           | 404      |
| `GET`    | `/ocpm/logs/{id}/relationships` | Object relationships   | 404      |
| `GET`    | `/ocpm/logs/{id}/oc-dfg`        | Object-centric DFG     | 404      |
| `GET`    | `/ocpm/formats`                 | Supported OCEL formats | -        |

---

## 🔄 Workflows

| Method   | Endpoint               | Description             | Errors |
| -------- | ---------------------- | ----------------------- | ------ |
| `GET`    | `/workflows/templates` | List workflow templates | -      |
| `POST`   | `/workflows`           | Create workflow         | 400    |
| `GET`    | `/workflows`           | List workflows          | -      |
| `GET`    | `/workflows/{id}`      | Get workflow            | 404    |
| `DELETE` | `/workflows/{id}`      | Delete workflow         | 404    |
| `POST`   | `/workflows/{id}/run`  | Execute workflow        | 404    |
| `GET`    | `/workflows/{id}/runs` | List runs               | 404    |
| `GET`    | `/workflows/runs/{id}` | Get run details         | 404    |

---

## 📂 Projects & Workspaces

### Projects

| Method   | Endpoint                     | Description         |
| -------- | ---------------------------- | ------------------- |
| `POST`   | `/projects`                  | Create project      |
| `GET`    | `/projects`                  | List projects       |
| `GET`    | `/projects/{id}`             | Get project         |
| `PUT`    | `/projects/{id}`             | Update project      |
| `DELETE` | `/projects/{id}`             | Delete project      |
| `POST`   | `/projects/{id}/files/{fid}` | Add file to project |
| `DELETE` | `/projects/{id}/files/{fid}` | Remove from project |

### Workspaces

| Method   | Endpoint                          | Description      |
| -------- | --------------------------------- | ---------------- |
| `GET`    | `/workspaces`                     | List workspaces  |
| `POST`   | `/workspaces`                     | Create workspace |
| `GET`    | `/workspaces/{id}`                | Get workspace    |
| `PUT`    | `/workspaces/{id}`                | Update workspace |
| `DELETE` | `/workspaces/{id}`                | Delete workspace |
| `POST`   | `/workspaces/{id}/projects/{pid}` | Add project      |
| `DELETE` | `/workspaces/{id}/projects/{pid}` | Remove project   |

---

## 🔐 Auth

| Method | Endpoint       | Description              |
| ------ | -------------- | ------------------------ |
| `GET`  | `/auth/me`     | Get current user context |
| `POST` | `/auth/login`  | Login (MVP: any email)   |
| `POST` | `/auth/logout` | Logout (MVP: no-op)      |

---

## ❤️ Health

| Method | Endpoint           | Description                |
| ------ | ------------------ | -------------------------- |
| `GET`  | `/health/live`     | Kubernetes liveness probe  |
| `GET`  | `/health/ready`    | Kubernetes readiness probe |
| `GET`  | `/health/startup`  | Kubernetes startup probe   |
| `GET`  | `/health/detailed` | Component health breakdown |
| `GET`  | `/health`          | Basic health check         |
| `GET`  | `/metrics`         | Prometheus metrics         |

---

## Error Codes

| Code    | HTTP | Description              | Retryable |
| ------- | ---- | ------------------------ | --------- |
| ERR_100 | 422  | Validation failed        | No        |
| ERR_101 | 422  | Invalid input            | No        |
| ERR_105 | 422  | Invalid file type        | No        |
| ERR_200 | 404  | Resource not found       | No        |
| ERR_202 | 404  | Process not found        | No        |
| ERR_203 | 404  | Model not found          | No        |
| ERR_300 | 500  | Processing failed        | Yes       |
| ERR_301 | 500  | Discovery failed         | Yes       |
| ERR_302 | 500  | Conformance check failed | Yes       |
| ERR_310 | 504  | Processing timeout       | Yes       |
| ERR_312 | 400  | Insufficient data        | No        |
| ERR_401 | 500  | PM4Py error              | Yes       |
| ERR_410 | 503  | Service unavailable      | Yes       |
| ERR_500 | 500  | Internal error           | No        |
| ERR_510 | 429  | Rate limit exceeded      | Yes       |

---

## Edge Cases & Stop Conditions

| Scenario                 | Response                        |
| ------------------------ | ------------------------------- |
| Empty dataset (0 events) | `ERR_312` Insufficient data     |
| Single activity log      | Returns single-node DFG         |
| No resource column       | `ERR_101` for org mining        |
| Filter removes all cases | `ERR_101` validation error      |
| Discovery timeout (>30s) | `ERR_310` with retry hint       |
| File too large (>100MB)  | `ERR_106` file size error       |
| Invalid miner type       | `ERR_101` with valid types list |
| Non-existent ID format   | `ERR_200` resource not found    |

---

## Common Query Parameters

| Parameter             | Type   | Description                 | Default |
| --------------------- | ------ | --------------------------- | ------- |
| `page`                | int    | Page number (1-based)       | 1       |
| `page_size`           | int    | Items per page (1-100)      | 20      |
| `log_id`              | string | Filter by event log         | -       |
| `model_id`            | string | Filter by model             | -       |
| `include_performance` | bool   | Include performance metrics | false   |
| `include_complexity`  | bool   | Include complexity scores   | false   |
| `top_n`               | int    | Limit to top N items        | -       |
| `top_k_percent`       | float  | Cover top K% of cases       | -       |
| `sort_by`             | string | Sort field                  | varies  |
