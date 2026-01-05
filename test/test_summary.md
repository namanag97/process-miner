# API Test Summary

Generated: 2026-01-05T17:52:12.183474

## Executive Summary

- **Total Tests**: 149
- **Passed**: 39 (26%)
- **Failed**: 110 (73%)
- **Skipped**: 0

## Failed Tests (110)

### POST /api/v1/auth/register

- **Status Code**: 400
- **Error**: Bad Request
- **What was tested**: Request failed with 400

### POST /api/v1/auth/login

- **Status Code**: 401
- **Error**: Unauthorized
- **What was tested**: Request failed with 401

### POST /api/v1/auth/refresh

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/workspaces/{workspace_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### PUT /api/v1/workspaces/{workspace_id}

- **Status Code**: 422
- **Error**: Unprocessable Content
- **What was tested**: Request failed with 422

### DELETE /api/v1/workspaces/{workspace_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/workspaces/{workspace_id}/projects/{project_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/workspaces/{workspace_id}/projects/{project_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/projects

- **Status Code**: 400
- **Error**: Bad Request
- **What was tested**: Request failed with 400

### GET /api/v1/projects/{project_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### PUT /api/v1/projects/{project_id}

- **Status Code**: 422
- **Error**: Unprocessable Content
- **What was tested**: Request failed with 422

### DELETE /api/v1/projects/{project_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/projects/{project_id}/files/{dataset_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/projects/{project_id}/files/{dataset_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/datasets/upload/presigned

- **Status Code**: 422
- **Error**: Unprocessable Content
- **What was tested**: Request failed with 422

### POST /api/v1/datasets/{dataset_id}/trigger-validation

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/datasets/upload

- **Status Code**: 422
- **Error**: Unprocessable Content
- **What was tested**: Request failed with 422

### POST /api/v1/datasets/detect-columns

- **Status Code**: 422
- **Error**: Unprocessable Content
- **What was tested**: Request failed with 422

### POST /api/v1/datasets/{dataset_id}/ingest

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/datasets/{dataset_id}/detect-columns

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/datasets/{dataset_id}/preview

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/datasets/{dataset_id}/sheets

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/datasets/{dataset_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/datasets/{dataset_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/datasets/{dataset_id}/statistics

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/datasets/{dataset_id}/cases

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/datasets/{dataset_id}/variants

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/datasets/{dataset_id}/activities

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/datasets/{dataset_id}/domain/analysis

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/analyses

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/analyses/{analysis_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/analyses/{analysis_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/analyses/log/{dataset_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/discovery/discover

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/discovery/models/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/discovery/models/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/visualization/{dataset_id}/dfg

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/visualization/models/{model_id}/petri

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/visualization/models/{model_id}/svg

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/visualization/{dataset_id}/dfg/svg

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/visualization/{dataset_id}/footprints

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/visualization/{dataset_id}/explorer-data

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### POST /api/v1/conformance/check

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/conformance/results/{result_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/conformance/results/{result_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/conformance/diagnostics/{dataset_id}/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/conformance/deviations/{dataset_id}/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/conformance/alignments/{dataset_id}/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/conformance/quality/{dataset_id}/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/conformance/import-model

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/conformance/root-cause/{dataset_id}/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/conformance/deviations/by-activity/{dataset_id}/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/conformance/deviations/by-position/{dataset_id}/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/conformance/deviations/attribute-correlation/{dataset_id}/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/business/p2p/mavericks/{dataset_id}/{reference_model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/business/p2p/audit-report/{dataset_id}/{reference_model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/business/o2c/split-log/{dataset_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/business/o2c/compare/{dataset_id1}/{dataset_id2}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/business/supply-chain/simulate/{dataset_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/business/customer-journey/dropoffs/{dataset_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/ocpm/upload

- **Status Code**: 422
- **Error**: Unprocessable Content
- **What was tested**: Request failed with 422

### GET /api/v1/ocpm/datasets/{dataset_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/ocpm/datasets/{dataset_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/ocpm/datasets/{dataset_id}/object-types

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/ocpm/datasets/{dataset_id}/statistics

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/ocpm/discover

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/ocpm/models/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/ocpm/models/{model_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/ocpm/datasets/{dataset_id}/relationships

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/ocpm/datasets/{dataset_id}/oc-dfg

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/ocpm/datasets/{dataset_id}/flatten

- **Status Code**: 422
- **Error**: Unprocessable Content
- **What was tested**: Request failed with 422

### POST /api/v1/workflows

- **Status Code**: 400
- **Error**: Bad Request
- **What was tested**: Request failed with 400

### GET /api/v1/workflows/{workflow_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/workflows/{workflow_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/workflows/{workflow_id}/run

- **Status Code**: 422
- **Error**: Unprocessable Content
- **What was tested**: Request failed with 422

### GET /api/v1/workflows/runs/{run_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/filtering/datasets/{dataset_id}/apply

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/filtering/datasets/{dataset_id}/preview

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/filtering/datasets/{dataset_id}/options

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/filtering/datasets/{dataset_id}/results

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/filtering/datasets/{dataset_id}/results/{filtered_id}

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/analytics/datasets/{dataset_id}/bottlenecks

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/analytics/datasets/{dataset_id}/rework

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/analytics/datasets/{dataset_id}/service-times

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/analytics/datasets/{dataset_id}/cycle-time

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/analytics/datasets/{dataset_id}/throughput

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/analytics/datasets/{dataset_id}/patterns

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/analytics/datasets/{dataset_id}/rework-chains

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/analytics/datasets/{dataset_id}/performance

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/organizational/datasets/{dataset_id}/handover-network

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/organizational/datasets/{dataset_id}/collaboration-network

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/organizational/datasets/{dataset_id}/resource-similarity

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/organizational/datasets/{dataset_id}/roles

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/organizational/datasets/{dataset_id}/resources/{resource}/profile

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/organizational/datasets/{dataset_id}/workload

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/predictions/datasets/{dataset_id}/train

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/predictions/predictors/{predictor_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### DELETE /api/v1/predictions/predictors/{predictor_id}

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/predictions/predictors/{predictor_id}/predict

- **Status Code**: 422
- **Error**: Unprocessable Content
- **What was tested**: Request failed with 422

### POST /api/v1/predictions/predictors/{predictor_id}/predict-batch

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/simulation/models/{model_id}/play-out

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/simulation/datasets/{dataset_id}/simulate

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### POST /api/v1/simulation/datasets/{dataset_id}/capacity-plan

- **Status Code**: 404
- **Error**: Not Found
- **What was tested**: Request failed with 404

### GET /api/v1/jobs/{job_id}

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### DELETE /api/v1/jobs/{job_id}

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/jobs/{job_id}/stream

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/dev/data/tables

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

### GET /api/v1/dev/data/records/{table}

- **Status Code**: 400
- **Error**: Bad Request
- **What was tested**: Request failed with 400

### GET /api/v1/dev/data/record/{table}/{record_id}

- **Status Code**: 400
- **Error**: Bad Request
- **What was tested**: Request failed with 400

### POST /api/v1/telemetry/traces

- **Status Code**: 500
- **Error**: Internal Server Error
- **What was tested**: Request failed with 500

## Passed Tests (39)

### Analyses (2 tests)

- **GET /api/v1/analyses/metadata**: Successful GET request, schema validated
- **GET /api/v1/analyses**: Successful GET request, schema validated

### Auth (3 tests)

- **GET /api/v1/auth/me**: Successful GET request, schema validated
- **POST /api/v1/auth/logout**: Successful POST request, schema validated
- **GET /api/v1/auth/me/legacy**: Successful GET request, schema validated

### Conformance (2 tests)

- **GET /api/v1/conformance/results**: Successful GET request, schema validated
- **GET /api/v1/conformance/methods**: Successful GET request, schema validated

### Datasets (1 tests)

- **GET /api/v1/datasets**: Successful GET request, schema validated

### DevLogs (4 tests)

- **GET /api/v1/dev/logs/stream**: Successful GET request, schema validated
- **GET /api/v1/dev/logs/metrics**: Successful GET request, schema validated
- **GET /api/v1/dev/logs/recent**: Successful GET request, schema validated
- **DELETE /api/v1/dev/logs/clear**: Successful DELETE request, schema validated

### Development (3 tests)

- **POST /api/v1/dev/log**: Successful POST request, schema validated
- **GET /api/v1/dev/logs**: Successful GET request, schema validated
- **DELETE /api/v1/dev/logs**: Successful DELETE request, schema validated

### Discovery (2 tests)

- **GET /api/v1/discovery/miners**: Successful GET request, schema validated
- **GET /api/v1/discovery/models**: Successful GET request, schema validated

### Filtering (1 tests)

- **GET /api/v1/filtering/templates**: Successful GET request, schema validated

### Health (7 tests)

- **GET /**: Successful GET request, schema validated
- **GET /health/live**: Successful GET request, schema validated
- **GET /health/ready**: Successful GET request, schema validated
- **GET /health/startup**: Successful GET request, schema validated
- **GET /health/detailed**: Successful GET request, schema validated
- **GET /health**: Successful GET request, schema validated
- **GET /health/metrics**: Successful GET request, schema validated

### Jobs (1 tests)

- **GET /api/v1/jobs**: Successful GET request, schema validated

### Object-Centric Process Mining (3 tests)

- **GET /api/v1/ocpm/logs**: Successful GET request, schema validated
- **GET /api/v1/ocpm/models**: Successful GET request, schema validated
- **GET /api/v1/ocpm/formats**: Successful GET request, schema validated

### Predictions (2 tests)

- **GET /api/v1/predictions/jobs/{job_id}**: Successful GET request, schema validated
- **GET /api/v1/predictions/datasets/{dataset_id}/predictors**: Successful GET request, schema validated

### Projects (1 tests)

- **GET /api/v1/projects**: Successful GET request, schema validated

### Telemetry (1 tests)

- **POST /api/v1/telemetry/logs**: Successful POST request, schema validated

### Test (1 tests)

- **GET /api/v1/test-telemetry/trace**: Successful GET request, schema validated

### Workflows (3 tests)

- **GET /api/v1/workflows/templates**: Successful GET request, schema validated
- **GET /api/v1/workflows**: Successful GET request, schema validated
- **GET /api/v1/workflows/{workflow_id}/runs**: Successful GET request, schema validated

### Workspaces (2 tests)

- **GET /api/v1/workspaces**: Successful GET request, schema validated
- **POST /api/v1/workspaces**: Successful POST request, schema validated

