# API Test Plan

Generated: 2026-01-05T17:51:35.285025

## Summary

- Total Endpoints: 149
- Categories: 23

## Test Strategy

For each endpoint, we will:
1. Execute happy path test with valid data
2. Validate response status code (expect 200-299)
3. Validate response body against OpenAPI schema
4. Check for required fields
5. Verify data types

## Endpoints by Category

### Analyses (6 endpoints)

- **GET /api/v1/analyses/metadata**: Get Analysis Metadata
- **POST /api/v1/analyses**: Create Analysis
- **GET /api/v1/analyses**: List Analyses
- **GET /api/v1/analyses/{analysis_id}**: Get Analysis
- **DELETE /api/v1/analyses/{analysis_id}**: Delete Analysis
- **GET /api/v1/analyses/log/{dataset_id}**: List Analyses For Log

### Analytics (8 endpoints)

- **GET /api/v1/analytics/datasets/{dataset_id}/bottlenecks**: Get Bottlenecks
- **GET /api/v1/analytics/datasets/{dataset_id}/rework**: Get Rework
- **GET /api/v1/analytics/datasets/{dataset_id}/service-times**: Get Service Times
- **GET /api/v1/analytics/datasets/{dataset_id}/cycle-time**: Get Cycle Time
- **GET /api/v1/analytics/datasets/{dataset_id}/throughput**: Get Throughput
- **GET /api/v1/analytics/datasets/{dataset_id}/patterns**: Get Patterns
- **GET /api/v1/analytics/datasets/{dataset_id}/rework-chains**: Get Rework Chains
- **GET /api/v1/analytics/datasets/{dataset_id}/performance**: Get Performance Dashboard

### Auth (6 endpoints)

- **POST /api/v1/auth/register**: Register
- **POST /api/v1/auth/login**: Login
- **POST /api/v1/auth/refresh**: Refresh Token
- **GET /api/v1/auth/me**: Get Current User Info
- **POST /api/v1/auth/logout**: Logout
- **GET /api/v1/auth/me/legacy**: Get Current User Legacy

### Business Use Cases (6 endpoints)

- **GET /api/v1/business/p2p/mavericks/{dataset_id}/{reference_model_id}**: Detect P2P Mavericks
- **GET /api/v1/business/p2p/audit-report/{dataset_id}/{reference_model_id}**: Generate P2P Audit Report
- **GET /api/v1/business/o2c/split-log/{dataset_id}**: Split Log By Attribute
- **GET /api/v1/business/o2c/compare/{dataset_id1}/{dataset_id2}**: Compare Process Variants
- **POST /api/v1/business/supply-chain/simulate/{dataset_id}**: Simulate Process Changes
- **GET /api/v1/business/customer-journey/dropoffs/{dataset_id}**: Detect Journey Dropoffs

### Conformance (14 endpoints)

- **POST /api/v1/conformance/check**: Check Conformance
- **GET /api/v1/conformance/results**: List Conformance Results
- **GET /api/v1/conformance/results/{result_id}**: Get Conformance Result
- **DELETE /api/v1/conformance/results/{result_id}**: Delete Conformance Result
- **GET /api/v1/conformance/diagnostics/{dataset_id}/{model_id}**: Get Conformance Diagnostics
- **GET /api/v1/conformance/deviations/{dataset_id}/{model_id}**: Get Deviations
- **GET /api/v1/conformance/alignments/{dataset_id}/{model_id}**: Get Alignment Diagnostics
- **GET /api/v1/conformance/methods**: List Conformance Methods
- **GET /api/v1/conformance/quality/{dataset_id}/{model_id}**: Get Quality Metrics
- **POST /api/v1/conformance/import-model**: Import Reference Model
- **GET /api/v1/conformance/root-cause/{dataset_id}/{model_id}**: Get Root Cause Analysis
- **GET /api/v1/conformance/deviations/by-activity/{dataset_id}/{model_id}**: Get Deviations By Activity
- **GET /api/v1/conformance/deviations/by-position/{dataset_id}/{model_id}**: Get Deviations By Position
- **GET /api/v1/conformance/deviations/attribute-correlation/{dataset_id}/{model_id}**: Get Attribute Correlation

### Datasets (16 endpoints)

- **POST /api/v1/datasets/upload/presigned**: Get Presigned S3 Upload URL
- **POST /api/v1/datasets/{dataset_id}/trigger-validation**: Trigger Dataset Validation
- **POST /api/v1/datasets/upload**: Upload Event Log File
- **POST /api/v1/datasets/detect-columns**: Detect Columns
- **POST /api/v1/datasets/{dataset_id}/ingest**: Ingest Dataset
- **GET /api/v1/datasets/{dataset_id}/detect-columns**: Detect Columns For Dataset
- **GET /api/v1/datasets/{dataset_id}/preview**: Get Data Preview
- **GET /api/v1/datasets/{dataset_id}/sheets**: Get Sheets
- **GET /api/v1/datasets**: List Datasets
- **GET /api/v1/datasets/{dataset_id}**: Get Dataset
- **DELETE /api/v1/datasets/{dataset_id}**: Delete Dataset
- **GET /api/v1/datasets/{dataset_id}/statistics**: Get Statistics
- **GET /api/v1/datasets/{dataset_id}/cases**: List Cases
- **GET /api/v1/datasets/{dataset_id}/variants**: Get Variants
- **GET /api/v1/datasets/{dataset_id}/activities**: Get Activities
- **GET /api/v1/datasets/{dataset_id}/domain/analysis**: Get Domain Analysis

### DevData (3 endpoints)

- **GET /api/v1/dev/data/tables**: List Tables
- **GET /api/v1/dev/data/records/{table}**: Get Records
- **GET /api/v1/dev/data/record/{table}/{record_id}**: Get Record

### DevLogs (4 endpoints)

- **GET /api/v1/dev/logs/stream**: Stream Logs
- **GET /api/v1/dev/logs/metrics**: Get Current Metrics
- **GET /api/v1/dev/logs/recent**: Get Recent Logs
- **DELETE /api/v1/dev/logs/clear**: Clear Logs

### Development (3 endpoints)

- **POST /api/v1/dev/log**: Receive Log
- **GET /api/v1/dev/logs**: Get Logs
- **DELETE /api/v1/dev/logs**: Clear Logs

### Discovery (5 endpoints)

- **GET /api/v1/discovery/miners**: List Miners
- **POST /api/v1/discovery/discover**: Discover Model
- **GET /api/v1/discovery/models**: List Models
- **GET /api/v1/discovery/models/{model_id}**: Get Model
- **DELETE /api/v1/discovery/models/{model_id}**: Delete Model

### Filtering (6 endpoints)

- **POST /api/v1/filtering/datasets/{dataset_id}/apply**: Apply Filters
- **POST /api/v1/filtering/datasets/{dataset_id}/preview**: Preview Filters
- **GET /api/v1/filtering/datasets/{dataset_id}/options**: Get Filter Options
- **GET /api/v1/filtering/datasets/{dataset_id}/results**: List Filtered Logs
- **DELETE /api/v1/filtering/datasets/{dataset_id}/results/{filtered_id}**: Delete Filtered Log
- **GET /api/v1/filtering/templates**: Get Filter Templates

### Health (7 endpoints)

- **GET /**: Root
- **GET /health/live**: Liveness Probe
- **GET /health/ready**: Readiness Probe
- **GET /health/startup**: Startup Probe
- **GET /health/detailed**: Detailed Health
- **GET /health**: Health Check
- **GET /health/metrics**: Prometheus Metrics

### Jobs (4 endpoints)

- **GET /api/v1/jobs**: List Jobs
- **GET /api/v1/jobs/{job_id}**: Get Job Status
- **DELETE /api/v1/jobs/{job_id}**: Cancel Job
- **GET /api/v1/jobs/{job_id}/stream**: Stream Job Progress

### Object-Centric Process Mining (14 endpoints)

- **POST /api/v1/ocpm/upload**: Upload Ocel
- **GET /api/v1/ocpm/logs**: List Ocel Logs
- **GET /api/v1/ocpm/datasets/{dataset_id}**: Get Ocel Log
- **DELETE /api/v1/ocpm/datasets/{dataset_id}**: Delete Ocel Log
- **GET /api/v1/ocpm/datasets/{dataset_id}/object-types**: Get Object Types
- **GET /api/v1/ocpm/datasets/{dataset_id}/statistics**: Get Ocel Statistics
- **POST /api/v1/ocpm/discover**: Discover Oc Petri Net
- **GET /api/v1/ocpm/models**: List Oc Petri Nets
- **GET /api/v1/ocpm/models/{model_id}**: Get Oc Petri Net
- **DELETE /api/v1/ocpm/models/{model_id}**: Delete Oc Petri Net
- **GET /api/v1/ocpm/datasets/{dataset_id}/relationships**: Get Object Relationships
- **GET /api/v1/ocpm/datasets/{dataset_id}/oc-dfg**: Get Oc Dfg
- **GET /api/v1/ocpm/formats**: List Supported Formats
- **POST /api/v1/ocpm/datasets/{dataset_id}/flatten**: Flatten Ocel To Dataset

### Organizational Mining (6 endpoints)

- **GET /api/v1/organizational/datasets/{dataset_id}/handover-network**: Get Handover Network
- **GET /api/v1/organizational/datasets/{dataset_id}/collaboration-network**: Get Collaboration Network
- **GET /api/v1/organizational/datasets/{dataset_id}/resource-similarity**: Get Resource Similarity
- **GET /api/v1/organizational/datasets/{dataset_id}/roles**: Get Roles
- **GET /api/v1/organizational/datasets/{dataset_id}/resources/{resource}/profile**: Get Resource Profile
- **GET /api/v1/organizational/datasets/{dataset_id}/workload**: Get Workload

### Predictions (7 endpoints)

- **POST /api/v1/predictions/datasets/{dataset_id}/train**: Train Predictor
- **GET /api/v1/predictions/jobs/{job_id}**: Get Job Status
- **GET /api/v1/predictions/datasets/{dataset_id}/predictors**: List Predictors
- **GET /api/v1/predictions/predictors/{predictor_id}**: Get Predictor
- **DELETE /api/v1/predictions/predictors/{predictor_id}**: Delete Predictor
- **POST /api/v1/predictions/predictors/{predictor_id}/predict**: Predict
- **POST /api/v1/predictions/predictors/{predictor_id}/predict-batch**: Predict Batch

### Projects (7 endpoints)

- **POST /api/v1/projects**: Create Project
- **GET /api/v1/projects**: List Projects
- **GET /api/v1/projects/{project_id}**: Get Project
- **PUT /api/v1/projects/{project_id}**: Update Project
- **DELETE /api/v1/projects/{project_id}**: Delete Project
- **POST /api/v1/projects/{project_id}/files/{dataset_id}**: Add File To Project
- **DELETE /api/v1/projects/{project_id}/files/{dataset_id}**: Remove File From Project

### Simulation (3 endpoints)

- **POST /api/v1/simulation/models/{model_id}/play-out**: Play Out Model
- **POST /api/v1/simulation/datasets/{dataset_id}/simulate**: Simulate Scenario
- **POST /api/v1/simulation/datasets/{dataset_id}/capacity-plan**: Estimate Capacity

### Telemetry (2 endpoints)

- **POST /api/v1/telemetry/traces**: Proxy Traces
- **POST /api/v1/telemetry/logs**: Proxy Logs

### Test (1 endpoints)

- **GET /api/v1/test-telemetry/trace**: Test Trace

### Visualization (6 endpoints)

- **GET /api/v1/visualization/{dataset_id}/dfg**: Get Dfg
- **GET /api/v1/visualization/models/{model_id}/petri**: Get Petri Net
- **GET /api/v1/visualization/models/{model_id}/svg**: Get Model Svg
- **GET /api/v1/visualization/{dataset_id}/dfg/svg**: Get Dfg Svg
- **GET /api/v1/visualization/{dataset_id}/footprints**: Get Footprints
- **GET /api/v1/visualization/{dataset_id}/explorer-data**: Get Explorer Data

### Workflows (8 endpoints)

- **GET /api/v1/workflows/templates**: List Templates
- **GET /api/v1/workflows**: List Workflows
- **POST /api/v1/workflows**: Create Workflow
- **GET /api/v1/workflows/{workflow_id}**: Get Workflow
- **DELETE /api/v1/workflows/{workflow_id}**: Delete Workflow
- **POST /api/v1/workflows/{workflow_id}/run**: Run Workflow
- **GET /api/v1/workflows/{workflow_id}/runs**: List Workflow Runs
- **GET /api/v1/workflows/runs/{run_id}**: Get Workflow Run

### Workspaces (7 endpoints)

- **GET /api/v1/workspaces**: List Workspaces
- **POST /api/v1/workspaces**: Create Workspace
- **GET /api/v1/workspaces/{workspace_id}**: Get Workspace
- **PUT /api/v1/workspaces/{workspace_id}**: Update Workspace
- **DELETE /api/v1/workspaces/{workspace_id}**: Delete Workspace
- **POST /api/v1/workspaces/{workspace_id}/projects/{project_id}**: Add Project To Workspace
- **DELETE /api/v1/workspaces/{workspace_id}/projects/{project_id}**: Remove Project From Workspace

