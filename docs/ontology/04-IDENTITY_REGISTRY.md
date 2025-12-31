# Identity Registry — How Each Object Type is Uniquely Identified

> **ATLAS Ontological Analysis**  
> Generated: 2025-12-31  
> System: Process Mining SaaS Platform

---

## Overview

This document specifies identity patterns for each domain object, including primary keys, natural keys, reference formats, and identity scope.

---

## Backend ORM Entities

### Project

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
    format: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  natural_key:
    fields: [name]
    constraint: none (duplicates allowed)
  scope: global
  immutability: always
  reference_format:
    internal: /api/v1/projects/{id}
    frontend: /projects/{id}
  external_references: none
```

### EventLog

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
    format: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  natural_key:
    fields: [name, source_file]
    constraint: none (duplicates allowed)
  scope: global
  immutability: always
  reference_format:
    internal: /api/v1/processes/{id}
    frontend: /processes/{id}
    explorer: /explorer/{id}
  composite_references:
    - project_id (optional parent)
    - source_log_id (for filtered logs)
  external_references:
    - PM4Py EventLog object (in-memory only)
```

### ProcessCase

```yaml
identity:
  strategy: composite_key (logical), surrogate_key (storage)
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  business_key:
    fields: [log_id, case_id]
    constraint: unique together (implied)
    semantic: "case_id within the context of a specific log"
  natural_key:
    field: case_id
    source: user-provided (CSV column)
    examples: ["ORDER-12345", "INC-2024-001", "12345"]
  scope: per_log (case_id unique within EventLog)
  immutability: after_creation
  reference_format:
    internal: /api/v1/processes/{log_id}/cases/{case_id}
  external_references:
    - Original source system case ID
```

### ProcessEvent

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  natural_key:
    fields: [case_ref_id, activity, timestamp]
    constraint: none (duplicates possible - same activity at same time)
  scope: per_case
  immutability: always
  reference_format:
    internal: /api/v1/processes/{log_id}/cases/{case_id}/events/{id}
  ordering: by timestamp within case
  external_references: none
```

### ProcessModel

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  natural_key:
    fields: [name, log_id, miner_type]
    constraint: none (can rediscover same model)
  scope: global
  immutability: always
  reference_format:
    internal: /api/v1/discovery/models/{id}
    visualization: /api/v1/visualization/models/{id}
  external_references:
    - PM4Py model object (serialized in model_binary)
```

### ConformanceResult

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  composite_key:
    fields: [log_id, model_id, method]
    constraint: none (can re-run conformance)
  scope: global
  immutability: always (results are point-in-time)
  reference_format:
    internal: /api/v1/conformance/results/{id}
  external_references:
    - References EventLog (log_id)
    - References ProcessModel (model_id)
```

### Workflow

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  natural_key:
    field: name
    constraint: none (duplicates allowed)
  scope: global
  immutability: always (id only)
  reference_format:
    internal: /api/v1/workflows/{id}
  template_references:
    - Template IDs: "discovery_basic", "conformance_check", "full_analysis"
```

### WorkflowRun

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  composite_key:
    fields: [workflow_id, started_at]
    constraint: none
  scope: per_workflow
  immutability: always
  reference_format:
    internal: /api/v1/workflows/{workflow_id}/runs/{id}
  external_references:
    - References Workflow (workflow_id)
    - References EventLog (log_id, optional)
```

### OCELLog

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  natural_key:
    fields: [name, source_file]
    constraint: none
  scope: global
  immutability: always
  reference_format:
    internal: /api/v1/ocpm/logs/{id}
  external_references:
    - PM4Py OCEL object (stored in ocel_data)
```

### OCELObjectType

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  composite_key:
    fields: [log_id, name]
    constraint: unique together (implied)
  scope: per_ocel_log
  immutability: always
  reference_format:
    internal: /api/v1/ocpm/logs/{log_id}/types/{name}
```

### OCPetriNet

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  composite_key:
    fields: [log_id, name]
    constraint: none
  scope: per_ocel_log
  immutability: always
  reference_format:
    internal: /api/v1/ocpm/logs/{log_id}/models/{id}
```

### PredictionModel

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  composite_key:
    fields: [log_id, target_type, algorithm]
    constraint: none (can train multiple)
  scope: per_log
  immutability: always
  reference_format:
    internal: /api/v1/predictions/predictors/{id}
  external_references:
    - scikit-learn model (stored in model_binary)
```

### SocialNetwork

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  composite_key:
    fields: [log_id, network_type]
    constraint: none (can regenerate)
  scope: per_log
  immutability: always
  reference_format:
    internal: /api/v1/organizational/logs/{log_id}/networks/{network_type}
  network_types:
    - handover
    - collaboration
    - similarity
```

### AnalyticsCache

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  composite_key:
    fields: [log_id, metric_type]
    constraint: unique together (implied - only one cache per metric)
  scope: per_log
  immutability: conditional (replaced on refresh)
  reference_format:
    internal: internal use only (not exposed via API)
  ttl: configurable (default 3600 seconds)
```

### AsyncJob

```yaml
identity:
  strategy: surrogate_key
  primary_key:
    field: id
    type: UUID string
    generation: auto (uuid4)
  scope: global
  immutability: always (id only)
  reference_format:
    internal: /api/v1/predictions/jobs/{id}
  temporal_scope: bounded (jobs expire/cleanup)
```

---

## Frontend Types

### User (AuthContext)

```yaml
identity:
  strategy: varies (mock vs real auth)
  mock_mode:
    field: id
    type: string
    generation: static ("1" or "guest")
  real_auth_mode:
    field: id
    type: string
    source: external_api (JWT claim)
  session_storage:
    key: "lumina_auth_user"
    token_key: "auth_token"
  scope: session (localStorage)
  reference_format:
    internal: context only (no API route)
```

### DFGNode

```yaml
identity:
  strategy: natural_key
  primary_key:
    field: id
    source: activity name
  scope: per_dfg
  immutability: always (derived data)
  reference_format:
    visualization: node ID in graph renderer
```

### DFGEdge

```yaml
identity:
  strategy: composite_key
  primary_key:
    field: id
    format: "edge-{source}-{target}-{index}"
    generation: computed at transform
  scope: per_dfg
  immutability: always (derived data)
```

### Variant

```yaml
identity:
  strategy: natural_key
  primary_key:
    field: key
    source: variant_key (activity sequence hash)
  scope: per_log
  immutability: always (derived data)
  reference_format:
    display: activity_trace ("A → B → C")
```

---

## Identity Pattern Summary

| Entity            | Strategy             | Primary Key    | Scope        | Mutable     |
| ----------------- | -------------------- | -------------- | ------------ | ----------- |
| Project           | Surrogate            | UUID           | Global       | No          |
| EventLog          | Surrogate            | UUID           | Global       | No          |
| ProcessCase       | Surrogate + Business | UUID / case_id | Per-Log      | No          |
| ProcessEvent      | Surrogate            | UUID           | Per-Case     | No          |
| ProcessModel      | Surrogate            | UUID           | Global       | No          |
| ConformanceResult | Surrogate            | UUID           | Global       | No          |
| Workflow          | Surrogate            | UUID           | Global       | No          |
| WorkflowRun       | Surrogate            | UUID           | Per-Workflow | No          |
| OCELLog           | Surrogate            | UUID           | Global       | No          |
| OCELObjectType    | Surrogate            | UUID           | Per-OCEL     | No          |
| OCPetriNet        | Surrogate            | UUID           | Per-OCEL     | No          |
| PredictionModel   | Surrogate            | UUID           | Per-Log      | No          |
| SocialNetwork     | Surrogate            | UUID           | Per-Log      | No          |
| AnalyticsCache    | Surrogate            | UUID           | Per-Log      | TTL         |
| AsyncJob          | Surrogate            | UUID           | Global       | Status only |

---

## External System References

| Internal Entity       | External Reference | Format                 |
| --------------------- | ------------------ | ---------------------- |
| ProcessCase.case_id   | Source system ID   | String (user-provided) |
| ProcessEvent.resource | Source system user | String (user-provided) |
| EventLog.source_file  | Original filename  | String (user-provided) |
| User.id               | Auth provider ID   | String (OAuth/JWT)     |

---

## API Route Patterns

```
Base URL: /api/v1

# Resource Routes
GET    /projects                         → List projects
GET    /projects/{id}                    → Get project
POST   /projects                         → Create project
PUT    /projects/{id}                    → Update project
DELETE /projects/{id}                    → Delete project

GET    /processes                        → List logs
POST   /processes/upload                 → Upload log
GET    /processes/{id}                   → Get log details
DELETE /processes/{id}                   → Delete log
GET    /processes/{id}/cases             → List cases
GET    /processes/{id}/statistics        → Get statistics
GET    /processes/{id}/variants          → Get variants

GET    /discovery/miners                 → List miners
POST   /discovery/discover               → Discover model
GET    /discovery/models                 → List models
GET    /discovery/models/{id}            → Get model

GET    /visualization/dfg/{log_id}       → Get DFG
GET    /visualization/models/{id}        → Visualize model

GET    /conformance/results              → List results
POST   /conformance/check                → Check conformance
GET    /conformance/diagnostics          → Get diagnostics

GET    /analytics/logs/{id}/bottlenecks  → Detect bottlenecks
GET    /analytics/logs/{id}/rework       → Analyze rework
GET    /analytics/logs/{id}/performance  → Performance dashboard

GET    /predictions/logs/{id}/predictors → List predictors
POST   /predictions/logs/{id}/train      → Train predictor
POST   /predictions/predictors/{id}/predict → Make prediction

GET    /organizational/logs/{id}/handover → Handover network
GET    /organizational/logs/{id}/roles    → Role discovery
```
