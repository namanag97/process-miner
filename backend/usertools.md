# Process Mining Platform - User Tools Inventory

> Comprehensive API & SDK reference organized by user-facing capabilities

---

## Table of Contents

1. [Event Log Management](#1-event-log-management)
2. [Process Discovery](#2-process-discovery)
3. [Conformance Checking](#3-conformance-checking)
4. [Performance Analytics](#4-performance-analytics)
5. [ML Predictions](#5-ml-predictions)
6. [Process Simulation](#6-process-simulation)
7. [Visualization](#7-visualization)
8. [Filtering & Segmentation](#8-filtering--segmentation)
9. [Organizational Mining](#9-organizational-mining)
10. [Object-Centric Process Mining (OCPM)](#10-object-centric-process-mining-ocpm)
11. [Workflow Automation](#11-workflow-automation)

---

## 1. Event Log Management

### 1.1 Upload Event Log

| Property               | Details                                                                                                   |
| ---------------------- | --------------------------------------------------------------------------------------------------------- |
| **Core Function**      | Ingest CSV/XES event logs into the platform with automatic parsing and validation                         |
| **Inputs**             | `file` (CSV/XES), `name?`, `case_id_column?`, `activity_column?`, `timestamp_column?`, `resource_column?` |
| **Outputs**            | `{id, name, total_events, total_cases, total_activities, activities[], created_at}`                       |
| **Dependencies**       | None (entry point)                                                                                        |
| **Sync/Async**         | **Synchronous** - blocks until file is parsed and stored                                                  |
| **Processing Time**    | ~1-5 seconds for small logs (<10k events), scales with file size                                          |
| **Failure Modes**      | Invalid file format (422), parsing error (500), missing required columns (422), file too large (413)      |
| **Success Indicators** | Returns log ID, total counts > 0, HTTP 200                                                                |
| **File Limitations**   | Max file size depends on server config; supports CSV, XES formats                                         |
| **Offline Behavior**   | ❌ Requires backend connectivity                                                                          |

**API:** `POST /api/v1/processes/upload`  
**SDK:** `sdk.logs.ingest(file, options)`

---

### 1.2 Detect Column Mappings

| Property               | Details                                                                     |
| ---------------------- | --------------------------------------------------------------------------- |
| **Core Function**      | Auto-detect case_id, activity, timestamp, resource columns from CSV headers |
| **Inputs**             | `file` (CSV only)                                                           |
| **Outputs**            | `{columns[], suggested_mappings, row_count, sample_rows[]}`                 |
| **Dependencies**       | None                                                                        |
| **Sync/Async**         | **Synchronous**                                                             |
| **Processing Time**    | <1 second                                                                   |
| **Failure Modes**      | Non-CSV file (400), empty file (400)                                        |
| **Success Indicators** | Returns column list with confidence scores                                  |
| **File Limitations**   | CSV only; reads first 100 rows for detection                                |
| **Offline Behavior**   | ❌ Requires backend                                                         |

**API:** `POST /api/v1/processes/detect-columns`  
**SDK:** `sdk.logs.detectColumns(file)`

---

### 1.3 List Event Logs

| Property               | Details                                                 |
| ---------------------- | ------------------------------------------------------- |
| **Core Function**      | Paginated list of all uploaded event logs with metadata |
| **Inputs**             | `page?`, `page_size?`, `source_format?`                 |
| **Outputs**            | `{items[], total, page, pages}`                         |
| **Dependencies**       | At least one log must exist                             |
| **Sync/Async**         | **Synchronous**                                         |
| **Processing Time**    | <100ms                                                  |
| **Failure Modes**      | Database error (500)                                    |
| **Success Indicators** | Returns array (may be empty)                            |

**API:** `GET /api/v1/processes`  
**SDK:** `sdk.logs.list(options)`

---

### 1.4 Get Event Log Statistics

| Property               | Details                                                                                                                                  |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Core Function**      | Comprehensive statistics: activities, variants, durations, date ranges                                                                   |
| **Inputs**             | `process_id`                                                                                                                             |
| **Outputs**            | `{total_events, total_cases, total_variants, activities[], start_activities[], end_activities[], avg/min/max_case_duration, date_range}` |
| **Dependencies**       | Log must exist with cases and events                                                                                                     |
| **Sync/Async**         | **Synchronous**                                                                                                                          |
| **Processing Time**    | ~100-500ms depending on log size                                                                                                         |
| **Failure Modes**      | Log not found (404)                                                                                                                      |
| **Success Indicators** | All fields populated with meaningful values                                                                                              |

**API:** `GET /api/v1/processes/{id}/statistics`  
**SDK:** `sdk.logs.analyze(logId)`

---

### 1.5 Get Process Variants

| Property               | Details                                                                                |
| ---------------------- | -------------------------------------------------------------------------------------- |
| **Core Function**      | Extract unique activity sequences with frequencies and durations                       |
| **Inputs**             | `process_id`, `top_n?` (default: 20, max: 100)                                         |
| **Outputs**            | `[{variant_key, activity_trace, case_count, frequency_percent, avg_duration_seconds}]` |
| **Dependencies**       | Log must have cases with events                                                        |
| **Sync/Async**         | **Synchronous**                                                                        |
| **Processing Time**    | ~100-300ms                                                                             |
| **Failure Modes**      | Log not found (404)                                                                    |
| **Success Indicators** | Returns sorted variants by frequency                                                   |

**API:** `GET /api/v1/processes/{id}/variants`  
**SDK:** `sdk.logs.listVariants(logId, limit)`

---

### 1.6 Delete Event Log

| Property               | Details                                                                |
| ---------------------- | ---------------------------------------------------------------------- |
| **Core Function**      | Permanently remove log and all associated data (cases, events, models) |
| **Inputs**             | `process_id`                                                           |
| **Outputs**            | `{status: "deleted", id}`                                              |
| **Dependencies**       | Log must exist                                                         |
| **Sync/Async**         | **Synchronous**                                                        |
| **Processing Time**    | <500ms                                                                 |
| **Failure Modes**      | Log not found (404), database error (500)                              |
| **Success Indicators** | Returns status "deleted"                                               |

**API:** `DELETE /api/v1/processes/{id}`  
**SDK:** `sdk.logs.remove(logId)`

---

## 2. Process Discovery

### 2.1 List Available Miners

| Property            | Details                                                   |
| ------------------- | --------------------------------------------------------- |
| **Core Function**   | Get list of available mining algorithms with capabilities |
| **Inputs**          | None                                                      |
| **Outputs**         | `[{id, name, description, output_format}]`                |
| **Dependencies**    | None                                                      |
| **Algorithms**      | `alpha`, `inductive`, `heuristics`, `dfg`                 |
| **Sync/Async**      | **Synchronous**                                           |
| **Processing Time** | <10ms                                                     |

**API:** `GET /api/v1/discovery/miners`  
**SDK:** `sdk.discovery.listAlgorithms()`

---

### 2.2 Discover Process Model

| Property                  | Details                                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Core Function**         | Run mining algorithm on event log to produce process model                                             |
| **Inputs**                | `log_id`, `miner_type` (alpha/inductive/heuristics/dfg), `model_name?`                                 |
| **Outputs**               | `{id, name, miner_type, model_format, log_id, fitness?, precision?, created_at}`                       |
| **Dependencies**          | Log must exist with sufficient data                                                                    |
| **Sync/Async**            | **Synchronous**                                                                                        |
| **Processing Time**       | 1-30 seconds (depends on log size and algorithm complexity)                                            |
| **Failure Modes**         | Log not found (404), invalid miner (400), mining failure (500)                                         |
| **Success Indicators**    | Returns model ID; fitness/precision values present for Petri net models                                |
| **Algorithm Performance** | DFG: fastest; Alpha: fast but limited; Inductive: medium, high quality; Heuristics: handles noise well |

**API:** `POST /api/v1/discovery/discover`  
**SDK:** `sdk.discovery.discover({logId, minerType, modelName})`

---

### 2.3 List Process Models

| Property            | Details                                                  |
| ------------------- | -------------------------------------------------------- |
| **Core Function**   | List all discovered models with pagination and filtering |
| **Inputs**          | `page?`, `page_size?`, `log_id?`                         |
| **Outputs**         | `{items[], total, page, pages}`                          |
| **Dependencies**    | At least one model must exist                            |
| **Sync/Async**      | **Synchronous**                                          |
| **Processing Time** | <100ms                                                   |

**API:** `GET /api/v1/discovery/models`  
**SDK:** `sdk.models.list(options)`

---

### 2.4 Get/Delete Model

| Property          | Details                                     |
| ----------------- | ------------------------------------------- |
| **Core Function** | Retrieve or delete a specific process model |
| **Inputs**        | `model_id`                                  |
| **Outputs**       | Model details or deletion confirmation      |
| **Dependencies**  | Model must exist                            |
| **Sync/Async**    | **Synchronous**                             |

**API:** `GET/DELETE /api/v1/discovery/models/{id}`  
**SDK:** `sdk.models.get(modelId)` / `sdk.models.delete(modelId)`

---

## 3. Conformance Checking

### 3.1 Check Conformance

| Property               | Details                                                                                      |
| ---------------------- | -------------------------------------------------------------------------------------------- |
| **Core Function**      | Measure how well event log traces fit a process model                                        |
| **Inputs**             | `log_id`, `model_id`, `method?` (token_replay/alignment)                                     |
| **Outputs**            | `{id, fitness, precision?, method, is_conformant, fitting_traces, total_traces, created_at}` |
| **Dependencies**       | Both log and model must exist; model must have serialized data                               |
| **Sync/Async**         | **Synchronous**                                                                              |
| **Processing Time**    | Token replay: 1-10s; Alignment: 10-120s (depends on complexity)                              |
| **Failure Modes**      | Log/model not found (404), no model data (400), algorithm failure (500)                      |
| **Success Indicators** | fitness >= 0.8 typically indicates good conformance                                          |
| **Method Comparison**  | Token replay: fast, approximate; Alignment: slow, precise                                    |

**API:** `POST /api/v1/conformance/check`  
**SDK:** `sdk.conformance.check({logId, modelId, method})`

---

### 3.2 Get Conformance Diagnostics

| Property            | Details                                                                                                |
| ------------------- | ------------------------------------------------------------------------------------------------------ |
| **Core Function**   | Detailed trace-level conformance analysis with deviation breakdown                                     |
| **Inputs**          | `log_id`, `model_id`                                                                                   |
| **Outputs**         | `{fitness, precision?, total_traces, fitting_traces, non_fitting_traces, fitness_ratio, deviations[]}` |
| **Dependencies**    | Log and model must exist                                                                               |
| **Sync/Async**      | **Synchronous**                                                                                        |
| **Processing Time** | 2-30 seconds                                                                                           |
| **Failure Modes**   | Log/model not found (404), analysis failure (500)                                                      |

**API:** `GET /api/v1/conformance/diagnostics/{log_id}/{model_id}`  
**SDK:** `sdk.conformance.getDiagnostics(logId, modelId)`

---

### 3.3 Detect Deviations

| Property            | Details                                                     |
| ------------------- | ----------------------------------------------------------- |
| **Core Function**   | Get case-level deviations from process model                |
| **Inputs**          | `log_id`, `model_id`, `threshold?` (default: 0.8)           |
| **Outputs**         | `[{case_id, activity?, deviation_type, details}]` (max 100) |
| **Dependencies**    | Log and model must exist                                    |
| **Sync/Async**      | **Synchronous**                                             |
| **Processing Time** | 2-30 seconds                                                |
| **Failure Modes**   | Log/model not found (404), analysis failure (500)           |

**API:** `GET /api/v1/conformance/deviations/{log_id}/{model_id}`  
**SDK:** `sdk.conformance.detectDeviations(logId, modelId, threshold)`

---

### 3.4 List Conformance Methods

| Property          | Details                                        |
| ----------------- | ---------------------------------------------- |
| **Core Function** | List available conformance checking algorithms |
| **Inputs**        | None                                           |
| **Outputs**       | `[{id, name, description, is_default}]`        |
| **Methods**       | `token_replay` (default), `alignment`          |

**API:** `GET /api/v1/conformance/methods`

---

## 4. Performance Analytics

> **Note:** Analytics endpoints are **cached for 1 hour** to improve response times.

### 4.1 Detect Bottlenecks

| Property            | Details                                                                                                              |
| ------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Core Function**   | Identify activities with highest waiting times                                                                       |
| **Inputs**          | `log_id`                                                                                                             |
| **Outputs**         | `{log_id, bottlenecks[{activity, avg_waiting_time, median_waiting_time, occurrences, severity}], total_bottlenecks}` |
| **Dependencies**    | Log with timestamp data                                                                                              |
| **Sync/Async**      | **Synchronous** (cached)                                                                                             |
| **Processing Time** | First call: 1-5s; Cached: <50ms                                                                                      |
| **Cache TTL**       | 1 hour                                                                                                               |
| **Failure Modes**   | Log not found (404), insufficient timestamp data (500)                                                               |

**API:** `GET /api/v1/analytics/logs/{log_id}/bottlenecks`  
**SDK:** `sdk.analytics.getBottlenecks(logId)`

---

### 4.2 Analyze Rework

| Property            | Details                                                                                                        |
| ------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Core Function**   | Identify repeated activities indicating rework patterns                                                        |
| **Inputs**          | `log_id`                                                                                                       |
| **Outputs**         | `{log_id, rework_activities[{activity, rework_count, affected_cases}], total_rework_cases, rework_percentage}` |
| **Dependencies**    | Log with activity sequences                                                                                    |
| **Sync/Async**      | **Synchronous** (cached)                                                                                       |
| **Processing Time** | First call: 1-3s; Cached: <50ms                                                                                |
| **Cache TTL**       | 1 hour                                                                                                         |

**API:** `GET /api/v1/analytics/logs/{log_id}/rework`  
**SDK:** `sdk.analytics.getRework(logId)`

---

### 4.3 Get Service Times

| Property          | Details                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------- |
| **Core Function** | Calculate average/min/max service times per activity                                    |
| **Inputs**        | `log_id`                                                                                |
| **Outputs**       | `[{activity, avg_duration_seconds, min_duration_seconds, max_duration_seconds, count}]` |
| **Dependencies**  | Log with timestamps                                                                     |
| **Sync/Async**    | **Synchronous** (cached)                                                                |
| **Cache TTL**     | 1 hour                                                                                  |

**API:** `GET /api/v1/analytics/logs/{log_id}/service-times`  
**SDK:** `sdk.analytics.getServiceTimes(logId)`

---

### 4.4 Get Cycle Time

| Property          | Details                                                                            |
| ----------------- | ---------------------------------------------------------------------------------- |
| **Core Function** | Case duration statistics (end-to-end)                                              |
| **Inputs**        | `log_id`                                                                           |
| **Outputs**       | `{log_id, avg_seconds, median_seconds, min_seconds, max_seconds, std_dev_seconds}` |
| **Dependencies**  | Log with start/end timestamps                                                      |
| **Sync/Async**    | **Synchronous**                                                                    |

**API:** `GET /api/v1/analytics/logs/{log_id}/cycle-time`  
**SDK:** `sdk.analytics.getCycleTime(logId)`

---

### 4.5 Get Throughput

| Property          | Details                                                                  |
| ----------------- | ------------------------------------------------------------------------ |
| **Core Function** | Cases completed per time period                                          |
| **Inputs**        | `log_id`                                                                 |
| **Outputs**       | `{log_id, cases_per_day, cases_per_week, cases_per_month, peak_periods}` |
| **Dependencies**  | Log with timestamps                                                      |
| **Sync/Async**    | **Synchronous**                                                          |

**API:** `GET /api/v1/analytics/logs/{log_id}/throughput`  
**SDK:** `sdk.analytics.getThroughput(logId)`

---

### 4.6 Get Frequent Patterns

| Property            | Details                                           |
| ------------------- | ------------------------------------------------- |
| **Core Function**   | Mine frequent activity subsequences               |
| **Inputs**          | `log_id`, `min_support?` (default: 0.1)           |
| **Outputs**         | `[{pattern, support, occurrences}]`               |
| **Dependencies**    | Log with multiple cases                           |
| **Sync/Async**      | **Synchronous**                                   |
| **Processing Time** | 2-10s depending on log size and support threshold |

**API:** `GET /api/v1/analytics/logs/{log_id}/patterns`  
**SDK:** `sdk.analytics.getPatterns(logId, minSupport)`

---

### 4.7 Get Performance Dashboard

| Property            | Details                                                                              |
| ------------------- | ------------------------------------------------------------------------------------ |
| **Core Function**   | Comprehensive performance summary combining multiple metrics                         |
| **Inputs**          | `log_id`                                                                             |
| **Outputs**         | `{log_id, cycle_time{...}, throughput{...}, top_bottlenecks[], rework_summary{...}}` |
| **Dependencies**    | Log with complete data                                                               |
| **Sync/Async**      | **Synchronous**                                                                      |
| **Processing Time** | 3-15s (aggregates multiple analyses)                                                 |

**API:** `GET /api/v1/analytics/logs/{log_id}/performance`  
**SDK:** `sdk.analytics.getPerformanceDashboard(logId)`

---

## 5. ML Predictions

### 5.1 Train Prediction Model

| Property                  | Details                                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------------- |
| **Core Function**         | Train ML model to predict next activity or remaining time                                      |
| **Inputs**                | `log_id`, `target_type` (next_activity/remaining_time), `algorithm?` (random_forest/xgboost)   |
| **Outputs (sync)**        | `{id, log_id, target_type, algorithm, metrics{accuracy, mae, rmse, activities[]}, trained_at}` |
| **Outputs (async)**       | `{job_id, status: "pending", message}`                                                         |
| **Dependencies**          | Log with sufficient cases (recommend >100)                                                     |
| **Sync/Async**            | **Both** - controlled by `async_mode` parameter                                                |
| **Processing Time**       | Sync: 10-120s; Async: same but returns immediately                                             |
| **Background Processing** | When async, uses Celery worker; check status via `/jobs/{job_id}`                              |
| **Failure Modes**         | Log not found (404), invalid target type (400), training failure (500, rare for RF)            |
| **Success Indicators**    | Model saved; accuracy >70% for classification                                                  |
| **ML Features**           | Last 5 activities (one-hot), prefix length, position ratio                                     |
| **Train/Test Split**      | 80/20                                                                                          |

**API:** `POST /api/v1/predictions/logs/{log_id}/train?async_mode={bool}`  
**SDK:** `sdk.predictions.trainPredictor(logId, request, asyncMode)`

---

### 5.2 Get Training Job Status

| Property          | Details                                                                                                     |
| ----------------- | ----------------------------------------------------------------------------------------------------------- |
| **Core Function** | Check status of async training job                                                                          |
| **Inputs**        | `job_id`                                                                                                    |
| **Outputs**       | `{job_id, status (pending/running/completed/failed), job_type, created_at, completed_at?, result?, error?}` |
| **Dependencies**  | Valid Celery job ID                                                                                         |
| **Sync/Async**    | **Synchronous**                                                                                             |

**API:** `GET /api/v1/predictions/jobs/{job_id}`  
**SDK:** `sdk.predictions.getTrainingJob(jobId)`

---

### 5.3 List Predictors

| Property          | Details                                                                          |
| ----------------- | -------------------------------------------------------------------------------- |
| **Core Function** | List all trained predictors for a log                                            |
| **Inputs**        | `log_id`                                                                         |
| **Outputs**       | `{log_id, predictors[{id, target_type, algorithm, metrics, trained_at}], total}` |
| **Dependencies**  | Log must exist                                                                   |
| **Sync/Async**    | **Synchronous**                                                                  |

**API:** `GET /api/v1/predictions/logs/{log_id}/predictors`  
**SDK:** `sdk.predictions.listPredictors(logId)`

---

### 5.4 Make Prediction

| Property               | Details                                                                                       |
| ---------------------- | --------------------------------------------------------------------------------------------- |
| **Core Function**      | Predict next activity or remaining time for a case prefix                                     |
| **Inputs**             | `predictor_id`, `{case_prefix: string[]}`                                                     |
| **Outputs**            | `{predictor_id, case_prefix, prediction, confidence, alternatives?[{activity, probability}]}` |
| **Dependencies**       | Predictor must exist with trained model                                                       |
| **Sync/Async**         | **Synchronous**                                                                               |
| **Processing Time**    | <100ms (model already loaded)                                                                 |
| **Failure Modes**      | Predictor not found (404), model not loaded (400)                                             |
| **Success Indicators** | Confidence > 0.5 typically reliable                                                           |

**API:** `POST /api/v1/predictions/predictors/{predictor_id}/predict`  
**SDK:** `sdk.predictions.predict(predictorId, {casePrefix})`

---

### 5.5 Batch Prediction

| Property            | Details                                                              |
| ------------------- | -------------------------------------------------------------------- |
| **Core Function**   | Predict for multiple case prefixes efficiently                       |
| **Inputs**          | `predictor_id`, `{cases: [{case_prefix: string[]}]}`                 |
| **Outputs**         | `{predictor_id, predictions[{case_prefix, prediction, confidence}]}` |
| **Dependencies**    | Predictor must exist                                                 |
| **Sync/Async**      | **Synchronous**                                                      |
| **Processing Time** | ~10ms per case                                                       |

**API:** `POST /api/v1/predictions/predictors/{predictor_id}/predict-batch`  
**SDK:** `sdk.predictions.predictBatch(predictorId, request)`

---

### 5.6 Delete Predictor

| Property          | Details                                 |
| ----------------- | --------------------------------------- |
| **Core Function** | Remove trained predictor and model data |
| **Inputs**        | `predictor_id`                          |
| **Outputs**       | `{message}`                             |
| **Dependencies**  | Predictor must exist                    |
| **Sync/Async**    | **Synchronous**                         |

**API:** `DELETE /api/v1/predictions/predictors/{predictor_id}`  
**SDK:** `sdk.predictions.deletePredictor(predictorId)`

---

## 6. Process Simulation

### 6.1 Model Play-Out

| Property               | Details                                                            |
| ---------------------- | ------------------------------------------------------------------ |
| **Core Function**      | Generate synthetic event log from process model                    |
| **Inputs**             | `model_id`, `{num_traces}`                                         |
| **Outputs**            | `{model_id, generated_log_id, traces_generated, events_generated}` |
| **Dependencies**       | Model with serialized data                                         |
| **Sync/Async**         | **Synchronous**                                                    |
| **Processing Time**    | 1-30s depending on num_traces and model complexity                 |
| **Failure Modes**      | Model not found (404), no model data (400), play-out failure (500) |
| **Success Indicators** | New event log created with expected trace count                    |

**API:** `POST /api/v1/simulation/models/{model_id}/play-out`  
**SDK:** `sdk.simulation.playOut(modelId, {numTraces})`

---

### 6.2 What-If Simulation

| Property               | Details                                                                |
| ---------------------- | ---------------------------------------------------------------------- |
| **Core Function**      | Simulate process changes and compare metrics                           |
| **Inputs**             | `log_id`, `{modifications[{type, params}]}`                            |
| **Outputs**            | `{log_id, scenario, original_metrics, simulated_metrics, impact{...}}` |
| **Dependencies**       | Log with complete data                                                 |
| **Sync/Async**         | **Synchronous**                                                        |
| **Processing Time**    | 2-15s                                                                  |
| **Modification Types** | activity_duration, remove_activity, add_resource, change_routing       |

**API:** `POST /api/v1/simulation/logs/{log_id}/simulate`  
**SDK:** `sdk.simulation.simulate(logId, {modifications})`

---

### 6.3 Capacity Planning

| Property            | Details                                                                                            |
| ------------------- | -------------------------------------------------------------------------------------------------- |
| **Core Function**   | Estimate resource requirements for target throughput                                               |
| **Inputs**          | `log_id`, `target_throughput` (cases/day)                                                          |
| **Outputs**         | `{log_id, current_throughput, target_throughput, required_resources{...}, bottleneck_relief{...}}` |
| **Dependencies**    | Log with resource data                                                                             |
| **Sync/Async**      | **Synchronous**                                                                                    |
| **Processing Time** | 2-10s                                                                                              |

**API:** `POST /api/v1/simulation/logs/{log_id}/capacity-plan`  
**SDK:** `sdk.simulation.capacityPlan(logId, targetThroughput)`

---

## 7. Visualization

### 7.1 Get DFG (Directly-Follows Graph)

| Property               | Details                                                                                                                      |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Core Function**      | Extract graph data optimized for React Flow / D3 rendering                                                                   |
| **Inputs**             | `log_id`                                                                                                                     |
| **Outputs**            | `{nodes[{id, label, frequency}], edges[{source, target, frequency}], start_activities[], end_activities[], total_frequency}` |
| **Dependencies**       | Log with cases and events                                                                                                    |
| **Sync/Async**         | **Synchronous**                                                                                                              |
| **Processing Time**    | 100-500ms                                                                                                                    |
| **Failure Modes**      | Log not found (404)                                                                                                          |
| **Success Indicators** | Nodes and edges arrays populated                                                                                             |

**API:** `GET /api/v1/visualization/{log_id}/dfg`  
**SDK:** `sdk.visualization.getDFG(logId)`

---

### 7.2 Get Petri Net Structure

| Property            | Details                                                                                                                            |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Core Function**   | Extract Petri net places, transitions, arcs for visualization                                                                      |
| **Inputs**          | `model_id`                                                                                                                         |
| **Outputs**         | `{places[{id, name, tokens}], transitions[{id, name, label}], arcs[{source, target, weight}], initial_marking[], final_marking[]}` |
| **Dependencies**    | Model must be Petri net or process tree format                                                                                     |
| **Sync/Async**      | **Synchronous**                                                                                                                    |
| **Processing Time** | 100-300ms                                                                                                                          |
| **Failure Modes**   | Model not found (404), incompatible format (400)                                                                                   |

**API:** `GET /api/v1/visualization/models/{model_id}/petri`  
**SDK:** `sdk.visualization.getPetriNet(modelId)`

---

### 7.3 Get Model SVG

| Property            | Details                                            |
| ------------------- | -------------------------------------------------- |
| **Core Function**   | Render process model as SVG image                  |
| **Inputs**          | `model_id`                                         |
| **Outputs**         | `image/svg+xml` binary                             |
| **Dependencies**    | Model with serialized data                         |
| **Sync/Async**      | **Synchronous**                                    |
| **Processing Time** | 500-2000ms (includes graphviz rendering)           |
| **Failure Modes**   | Model not found (404), visualization failure (500) |

**API:** `GET /api/v1/visualization/models/{model_id}/svg`  
**SDK:** `sdk.visualization.getModelSVG(modelId)`

---

### 7.4 Get DFG SVG

| Property            | Details                                   |
| ------------------- | ----------------------------------------- |
| **Core Function**   | Render DFG as SVG image directly from log |
| **Inputs**          | `log_id`                                  |
| **Outputs**         | `image/svg+xml` binary                    |
| **Dependencies**    | Log with cases and events                 |
| **Sync/Async**      | **Synchronous**                           |
| **Processing Time** | 500-2000ms                                |

**API:** `GET /api/v1/visualization/{log_id}/dfg/svg`  
**SDK:** `sdk.visualization.getDFGSVG(logId)`

---

### 7.5 Get Footprints

| Property            | Details                                                                          |
| ------------------- | -------------------------------------------------------------------------------- |
| **Core Function**   | Extract behavioral relations (sequence, parallel, choice) between activities     |
| **Inputs**          | `log_id`                                                                         |
| **Outputs**         | `{activities[], sequence_relations[], parallel_relations[], choice_relations[]}` |
| **Dependencies**    | Log with activity data                                                           |
| **Sync/Async**      | **Synchronous**                                                                  |
| **Processing Time** | 200-1000ms                                                                       |

**API:** `GET /api/v1/visualization/{log_id}/footprints`  
**SDK:** `sdk.visualization.getFootprints(logId)`

---

## 8. Filtering & Segmentation

### 8.1 Apply Filters

| Property               | Details                                                                                                                                |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Core Function**      | Create filtered copy of event log using criteria chain                                                                                 |
| **Inputs**             | `log_id`, `{filters[{type, params}], name?, save_result?}`                                                                             |
| **Outputs**            | `{id, name, source_log_id, is_filtered, filter_config, total_events, total_cases, total_activities, statistics{...}}`                  |
| **Dependencies**       | Source log must exist                                                                                                                  |
| **Sync/Async**         | **Synchronous**                                                                                                                        |
| **Processing Time**    | 1-10s depending on log size and filter complexity                                                                                      |
| **Filter Types**       | `time_range`, `variant_top_k`, `variant_coverage`, `activity_include`, `activity_exclude`, `duration_min`, `duration_max`, `case_size` |
| **Failure Modes**      | Log not found (404), invalid filter config (400)                                                                                       |
| **Success Indicators** | New filtered log created (if save_result=true)                                                                                         |
| **Non-Destructive**    | Original log preserved; creates new filtered copy                                                                                      |

**API:** `POST /api/v1/filtering/logs/{log_id}/apply`  
**SDK:** `sdk.filtering.applyFilter(logId, request)`

---

### 8.2 Preview Filters

| Property               | Details                                                                       |
| ---------------------- | ----------------------------------------------------------------------------- |
| **Core Function**      | Preview filter impact without saving                                          |
| **Inputs**             | `log_id`, `{filters[{type, params}]}`                                         |
| **Outputs**            | `{would_retain_cases, would_retain_events, statistics{...}, filters_applied}` |
| **Dependencies**       | Source log must exist                                                         |
| **Sync/Async**         | **Synchronous**                                                               |
| **Processing Time**    | 500-3000ms                                                                    |
| **Success Indicators** | Shows exactly what would be retained/removed                                  |

**API:** `POST /api/v1/filtering/logs/{log_id}/preview`  
**SDK:** `sdk.filtering.previewFilter(logId, request)`

---

### 8.3 Get Filter Options

| Property            | Details                                                                                             |
| ------------------- | --------------------------------------------------------------------------------------------------- |
| **Core Function**   | Get available filter values based on log contents                                                   |
| **Inputs**          | `log_id`                                                                                            |
| **Outputs**         | `{activities[], resources[], time_range{start, end}, variant_count, case_duration_range{min, max}}` |
| **Dependencies**    | Log must exist                                                                                      |
| **Sync/Async**      | **Synchronous**                                                                                     |
| **Processing Time** | 200-500ms                                                                                           |

**API:** `GET /api/v1/filtering/logs/{log_id}/options`  
**SDK:** `sdk.filtering.getFilterOptions(logId)`

---

### 8.4 List Filtered Logs

| Property          | Details                                                       |
| ----------------- | ------------------------------------------------------------- |
| **Core Function** | List all filtered versions of a source log                    |
| **Inputs**        | `log_id`                                                      |
| **Outputs**       | `{source_log_id, source_log_name, filtered_logs[...], total}` |
| **Dependencies**  | Source log must exist; may return empty if no filters applied |
| **Sync/Async**    | **Synchronous**                                               |

**API:** `GET /api/v1/filtering/logs/{log_id}/results`  
**SDK:** `sdk.filtering.listFilteredLogs(logId)`

---

### 8.5 Get Filter Templates

| Property                | Details                                                                                |
| ----------------------- | -------------------------------------------------------------------------------------- |
| **Core Function**       | Pre-built filter configurations for common use cases                                   |
| **Inputs**              | None                                                                                   |
| **Outputs**             | `{templates[{id, name, description, filters[]}]}`                                      |
| **Templates Available** | "Happy Path Only", "Exclude Outliers", "Recent Cases", "High Duration", "Rework Cases" |

**API:** `GET /api/v1/filtering/templates`  
**SDK:** `sdk.filtering.getTemplates()`

---

## 9. Organizational Mining

### 9.1 Handover of Work Network

| Property            | Details                                                                                                                            |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Core Function**   | Social network showing work handoffs between resources                                                                             |
| **Inputs**          | `log_id`                                                                                                                           |
| **Outputs**         | `{log_id, network_type: "handover", nodes[{id, label, frequency}], edges[{source, target, weight}], metrics{density, avg_degree}}` |
| **Dependencies**    | Log with resource attribute                                                                                                        |
| **Sync/Async**      | **Synchronous**                                                                                                                    |
| **Processing Time** | 500-2000ms                                                                                                                         |
| **Failure Modes**   | Log not found (404), no resource data (empty result)                                                                               |

**API:** `GET /api/v1/organizational/logs/{log_id}/handover-network`  
**SDK:** `sdk.org.buildHandoverNetwork(logId)`

---

### 9.2 Collaboration Network

| Property            | Details                                                              |
| ------------------- | -------------------------------------------------------------------- |
| **Core Function**   | Network showing resources who work together on same cases            |
| **Inputs**          | `log_id`                                                             |
| **Outputs**         | `{log_id, network_type: "collaboration", nodes[], edges[], metrics}` |
| **Dependencies**    | Log with resource and case data                                      |
| **Sync/Async**      | **Synchronous**                                                      |
| **Processing Time** | 500-2000ms                                                           |

**API:** `GET /api/v1/organizational/logs/{log_id}/collaboration-network`  
**SDK:** `sdk.org.buildCollaborationNetwork(logId)`

---

### 9.3 Resource Similarity

| Property            | Details                                                           |
| ------------------- | ----------------------------------------------------------------- |
| **Core Function**   | Cluster resources by similar activity patterns                    |
| **Inputs**          | `log_id`                                                          |
| **Outputs**         | `{log_id, network_type: "similarity", nodes[], edges[], metrics}` |
| **Dependencies**    | Log with diverse resource-activity data                           |
| **Sync/Async**      | **Synchronous**                                                   |
| **Processing Time** | 1-5s                                                              |

**API:** `GET /api/v1/organizational/logs/{log_id}/resource-similarity`  
**SDK:** `sdk.org.getResourceSimilarity(logId)`

---

### 9.4 Discover Roles

| Property            | Details                                               |
| ------------------- | ----------------------------------------------------- |
| **Core Function**   | Identify organizational roles from activity patterns  |
| **Inputs**          | `log_id`                                              |
| **Outputs**         | `[{role_id, resources[], activities[], event_count}]` |
| **Dependencies**    | Log with resource and activity data                   |
| **Sync/Async**      | **Synchronous**                                       |
| **Processing Time** | 1-5s                                                  |

**API:** `GET /api/v1/organizational/logs/{log_id}/roles`  
**SDK:** `sdk.org.discoverRoles(logId)`

---

### 9.5 Resource Profile

| Property            | Details                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------- |
| **Core Function**   | Detailed profile for a specific resource                                                    |
| **Inputs**          | `log_id`, `resource`                                                                        |
| **Outputs**         | `{resource, activities[], case_count, event_count, avg_duration_seconds, workload_trend[]}` |
| **Dependencies**    | Resource must exist in log                                                                  |
| **Sync/Async**      | **Synchronous**                                                                             |
| **Processing Time** | 200-500ms                                                                                   |
| **Failure Modes**   | Log not found (404), resource not found in log (empty/404)                                  |

**API:** `GET /api/v1/organizational/logs/{log_id}/resources/{resource}/profile`  
**SDK:** `sdk.org.profileResource(logId, resourceName)`

---

### 9.6 Workload Distribution

| Property            | Details                                                                                                              |
| ------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Core Function**   | Workload metrics across all resources                                                                                |
| **Inputs**          | `log_id`                                                                                                             |
| **Outputs**         | `{log_id, resources[{resource, event_count, case_count, utilization_percent}], gini_coefficient, workload_variance}` |
| **Dependencies**    | Log with resource data                                                                                               |
| **Sync/Async**      | **Synchronous**                                                                                                      |
| **Processing Time** | 500-2000ms                                                                                                           |

**API:** `GET /api/v1/organizational/logs/{log_id}/workload`  
**SDK:** `sdk.org.getWorkloadDistribution(logId)`

---

## 10. Object-Centric Process Mining (OCPM)

### 10.1 Upload OCEL

| Property              | Details                                                                                                                             |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Core Function**     | Ingest OCEL 2.0 file for object-centric analysis                                                                                    |
| **Inputs**            | `file` (jsonocel/sqlite/xmlocel), `name?`                                                                                           |
| **Outputs**           | `{id, name, source_file, source_format, total_events, total_objects, total_object_types, object_types[], activities[], created_at}` |
| **Dependencies**      | None (entry point for OCPM)                                                                                                         |
| **Sync/Async**        | **Synchronous**                                                                                                                     |
| **Processing Time**   | 1-10s depending on file size                                                                                                        |
| **Supported Formats** | `.jsonocel`, `.sqlite`, `.xmlocel`                                                                                                  |
| **Failure Modes**     | Invalid format (400), parsing error (400)                                                                                           |

**API:** `POST /api/v1/ocpm/upload`  
**SDK:** `sdk.ocpm.ingest(file, options)`

---

### 10.2 List/Get OCEL Logs

| Property          | Details                            |
| ----------------- | ---------------------------------- |
| **Core Function** | Manage OCEL logs (CRUD operations) |
| **Inputs**        | `log_id` for get/delete            |
| **Outputs**       | OCEL log details or list           |
| **Dependencies**  | OCEL log must exist for get/delete |
| **Sync/Async**    | **Synchronous**                    |

**API:** `GET /api/v1/ocpm/logs`, `GET/DELETE /api/v1/ocpm/logs/{log_id}`  
**SDK:** `sdk.ocpm.list()`, `sdk.ocpm.get(logId)`, `sdk.ocpm.delete(logId)`

---

### 10.3 Get Object Types

| Property                 | Details                                   |
| ------------------------ | ----------------------------------------- |
| **Core Function**        | List object types in OCEL log with counts |
| **Inputs**               | `log_id`                                  |
| **Outputs**              | `[{name, object_count, attributes[]}]`    |
| **Dependencies**         | OCEL log must exist                       |
| **Sync/Async**           | **Synchronous**                           |
| **Object Type Examples** | Order, Item, Package, Customer, Delivery  |

**API:** `GET /api/v1/ocpm/logs/{log_id}/object-types`  
**SDK:** `sdk.ocpm.getObjectTypes(logId)`

---

### 10.4 Get OCEL Statistics

| Property          | Details                                                                                                                         |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Core Function** | Detailed OCEL statistics including objects per type                                                                             |
| **Inputs**        | `log_id`                                                                                                                        |
| **Outputs**       | `{log_id, total_events, total_objects, total_object_types, total_activities, object_types[], activities[], objects_per_type{}}` |
| **Dependencies**  | OCEL log must exist                                                                                                             |
| **Sync/Async**    | **Synchronous**                                                                                                                 |

**API:** `GET /api/v1/ocpm/logs/{log_id}/statistics`  
**SDK:** `sdk.ocpm.getStatistics(logId)`

---

### 10.5 Discover OC Petri Net

| Property            | Details                                          |
| ------------------- | ------------------------------------------------ |
| **Core Function**   | Discover Object-Centric Petri Net from OCEL      |
| **Inputs**          | `{log_id, model_name?}`                          |
| **Outputs**         | `{id, log_id, name, object_types[], created_at}` |
| **Dependencies**    | OCEL log must exist                              |
| **Sync/Async**      | **Synchronous**                                  |
| **Processing Time** | 5-60s depending on complexity                    |
| **Failure Modes**   | Log not found (404), discovery failure (500)     |

**API:** `POST /api/v1/ocpm/discover`  
**SDK:** `sdk.ocpm.discoverOCPN(request)`

---

### 10.6 List Supported Formats

| Property          | Details                                       |
| ----------------- | --------------------------------------------- |
| **Core Function** | List supported OCEL file formats              |
| **Inputs**        | None                                          |
| **Outputs**       | `[{extension, name, description, mime_type}]` |
| **Formats**       | jsonocel, sqlite, xmlocel                     |

**API:** `GET /api/v1/ocpm/formats`

---

## 11. Workflow Automation

### 11.1 List Workflow Templates

| Property                | Details                                                                           |
| ----------------------- | --------------------------------------------------------------------------------- |
| **Core Function**       | Pre-built workflow templates for common pipelines                                 |
| **Inputs**              | None                                                                              |
| **Outputs**             | `[{id, name, description, steps[]}]`                                              |
| **Templates Available** | "Full Analysis", "Conformance Pipeline", "Performance Review", "Compliance Audit" |

**API:** `GET /api/v1/workflows/templates`  
**SDK:** `sdk.workflows.getTemplates()`

---

### 11.2 Create Workflow

| Property               | Details                                                    |
| ---------------------- | ---------------------------------------------------------- |
| **Core Function**      | Define reusable multi-step workflow pipeline               |
| **Inputs**             | `{name, steps[{type, name, params}], schedule?}`           |
| **Outputs**            | `{id, name, steps[], schedule?, is_active, created_at}`    |
| **Dependencies**       | Valid step configurations                                  |
| **Sync/Async**         | **Synchronous**                                            |
| **Step Types**         | `discover`, `conformance`, `analytics`, `filter`, `export` |
| **Failure Modes**      | Invalid step config (400)                                  |
| **Success Indicators** | Workflow ID returned                                       |

**API:** `POST /api/v1/workflows`  
**SDK:** `sdk.workflows.create(request)`

---

### 11.3 Run Workflow

| Property               | Details                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------- |
| **Core Function**      | Execute workflow on an event log                                                                  |
| **Inputs**             | `workflow_id`, `{log_id, params{}}`                                                               |
| **Outputs**            | `{id, workflow_id, log_id, status (running/completed/failed), started_at, completed_at?, error?}` |
| **Dependencies**       | Workflow and log must exist                                                                       |
| **Sync/Async**         | **Synchronous** (executes all steps sequentially)                                                 |
| **Processing Time**    | Varies by steps – can be 10s to minutes                                                           |
| **Failure Modes**      | Workflow/log not found (404), step failure (sets status=failed)                                   |
| **Success Indicators** | Status = "completed"                                                                              |

**API:** `POST /api/v1/workflows/{workflow_id}/run`  
**SDK:** `sdk.workflows.run(workflowId, {logId, params})`

---

### 11.4 List/Get Workflow Runs

| Property          | Details                                                                  |
| ----------------- | ------------------------------------------------------------------------ |
| **Core Function** | View execution history for workflows                                     |
| **Inputs**        | `workflow_id` for list, `run_id` for get                                 |
| **Outputs**       | `[{id, workflow_id, log_id, status, started_at, completed_at?, error?}]` |
| **Dependencies**  | Workflow must exist                                                      |
| **Sync/Async**    | **Synchronous**                                                          |

**API:** `GET /api/v1/workflows/{workflow_id}/runs`, `GET /api/v1/workflows/runs/{run_id}`  
**SDK:** `sdk.workflows.listRuns(workflowId)`, `sdk.workflows.getRun(runId)`

---

## Technical Summary

### Sync vs Async Operations

| Operation Type       | Sync | Async       |
| -------------------- | ---- | ----------- |
| File upload/parse    | ✅   | ❌          |
| Process discovery    | ✅   | ❌          |
| Conformance checking | ✅   | ❌          |
| Analytics (cached)   | ✅   | ❌          |
| ML training          | ✅   | ✅ (Celery) |
| ML prediction        | ✅   | ❌          |
| Simulation           | ✅   | ❌          |
| Workflow execution   | ✅   | ❌          |

### Caching

| Feature              | TTL    | Cache Key                |
| -------------------- | ------ | ------------------------ |
| Bottleneck detection | 1 hour | `bottlenecks:{log_id}`   |
| Rework analysis      | 1 hour | `rework:{log_id}`        |
| Service times        | 1 hour | `service_times:{log_id}` |

### Data/File Limitations

| Resource            | Limit                        |
| ------------------- | ---------------------------- |
| File upload size    | Server-configurable          |
| Deviations returned | 100 max                      |
| Variants returned   | 100 max                      |
| Pagination          | 100 items/page max           |
| Batch predictions   | No hard limit (memory-bound) |

### Offline Behavior

- All operations require backend connectivity
- No offline caching or local processing
- SDK does not persist data locally

---

## SDK Quick Reference

```typescript
import { ProcessMiningSdk } from 'process-mining-sdk';

const sdk = new ProcessMiningSdk({ baseUrl: 'http://localhost:8001' });

// Event Logs
await sdk.logs.ingest(file, { name: 'My Process' });
await sdk.logs.list({ page: 1, pageSize: 20 });
await sdk.logs.analyze(logId);
await sdk.logs.listVariants(logId);

// Discovery
await sdk.discovery.discover({ logId, minerType: 'inductive' });
await sdk.models.list();

// Conformance
await sdk.conformance.check({ logId, modelId });
await sdk.conformance.getDiagnostics(logId, modelId);

// Analytics
await sdk.analytics.getBottlenecks(logId);
await sdk.analytics.getPerformanceDashboard(logId);

// Predictions
await sdk.predictions.trainPredictor(logId, { targetType: 'next_activity' }, true);
await sdk.predictions.predict(predictorId, { casePrefix: ['A', 'B', 'C'] });

// Simulation
await sdk.simulation.simulate(logId, { modifications: [...] });

// Visualization
await sdk.visualization.getDFG(logId);
await sdk.visualization.getPetriNet(modelId);

// Filtering
await sdk.filtering.applyFilter(logId, { filters: [...], saveResult: true });

// Organizational
await sdk.org.buildHandoverNetwork(logId);
await sdk.org.discoverRoles(logId);

// OCPM
await sdk.ocpm.ingest(ocelFile);
await sdk.ocpm.discoverOCPN({ logId });

// Workflows
await sdk.workflows.run(workflowId, { logId });
```

---

_Generated: 2025-12-30_
