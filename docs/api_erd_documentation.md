# API Entity Relationship Diagrams (ERD)

This document provides a comprehensive overview of the data models and relationships handled by the various API endpoints.

## Global Overview

The following diagram shows the core entities and their high-level relationships across the Platform and Feature (Process Mining) layers.

```mermaid
erDiagram
    ORGANIZATION ||--o{ WORKSPACE : contains
    WORKSPACE ||--o{ PROJECT : contains
    WORKSPACE ||--o{ WORKSPACE_MEMBER : has
    USER ||--o{ WORKSPACE_MEMBER : member_of
    PROJECT ||--o{ DATASET : "belongs_to (FK in Dataset)"
    
    DATASET ||--o{ PROCESS_CASE : contains
    PROCESS_CASE ||--o{ PROCESS_EVENT : contains
    DATASET ||--o{ PROCESS_MODEL : generates
    DATASET ||--o{ ANALYSIS : "analyzed_by"
    DATASET ||--o{ ACTIVITY_MAPPING : maps
    DATASET ||--o{ ANALYTICS_CACHE : caches
    DATASET ||--o{ SOCIAL_NETWORK : "extracts (Org Mining)"
    DATASET ||--o{ PREDICTION_MODEL : trains
    DATASET ||--o{ RECOMMENDATION : "triggers"
    DATASET ||--o{ WORKFLOW_RUN : "executes_on"
    
    WORKFLOW ||--o{ WORKFLOW_RUN : "defines"
    PREDICTION_MODEL ||--o{ PREDICTION : "generates"
    PROCESS_MODEL ||--o{ PROCESS_MODEL_METRICS : "has_metrics"
    PROCESS_MODEL ||--o{ GRAPH_CACHE : "has_layout_cache"
    ACTIVITY_MAPPING ||--o{ HIERARCHICAL_PROCESS_MODEL : "supports"
    
    OCEL_LOG ||--o{ OCEL_OBJECT_TYPE : "defines_types"
    OCEL_LOG ||--o{ OC_PETRI_NET : "discovers"
    
    ASYNC_JOB ||--o| DATASET : "tracks_ingestion/validation"
```

---

## 1. Platform APIs

### Projects API (`/api/v1/projects`)
Handles project lifecycle within a workspace.

```mermaid
erDiagram
    WORKSPACE ||--o{ PROJECT : contains
    PROJECT {
        string id PK
        string workspace_id FK
        string name
        string description
        int total_files
        int total_analyses
        datetime created_at
    }
```

### Workspaces API (`/api/v1/workspaces`)
Manages workspaces and memberships.

```mermaid
erDiagram
    ORGANIZATION ||--o{ WORKSPACE : contains
    WORKSPACE ||--o{ WORKSPACE_MEMBER : members
    USER ||--o{ WORKSPACE_MEMBER : belongs_to
    WORKSPACE {
        string id PK
        string org_id FK
        string name
        string description
    }
    WORKSPACE_MEMBER {
        string id PK
        string workspace_id FK
        string user_id FK
        string role
    }
```

---

## 2. Process Mining APIs

### Datasets API (`/api/v1/datasets`)
Management of event logs, ingestion, and basic statistics.

```mermaid
erDiagram
    PROJECT ||--o{ DATASET : belongs_to
    DATASET ||--o{ PROCESS_CASE : contains
    DATASET ||--o{ UPLOADED_FILE : managed_via
    PROCESS_CASE ||--o{ PROCESS_EVENT : contains
    
    DATASET {
        string id PK
        string project_id FK
        string name
        string status
        int total_cases
        int total_events
    }
    PROCESS_CASE {
        string id PK
        string dataset_id FK
        string case_id
        datetime start_time
        datetime end_time
    }
    PROCESS_EVENT {
        string id PK
        string case_ref_id FK
        string activity
        datetime timestamp
    }
```

### Analyses API (`/api/v1/analyses`)
Execution and storage of process mining analyses.

```mermaid
erDiagram
    DATASET ||--o{ ANALYSIS : "analyzed_by"
    ANALYSIS ||--o| PROCESS_MODEL : "uses/creates"
    
    ANALYSIS {
        string id PK
        string dataset_id FK
        string name
        string analysis_type
        string status
        text result_json
    }
```

### Visualization API (`/api/v1/visualization`)
DFG and Petri Net visualization data.

```mermaid
erDiagram
    DATASET ||--o{ PROCESS_MODEL : discovers
    PROCESS_MODEL ||--o{ GRAPH_CACHE : caches_layout
    
    PROCESS_MODEL {
        string id PK
        string dataset_id FK
        string miner_type
        string model_format
    }
    GRAPH_CACHE {
        string id PK
        string model_id FK
        int abstraction_level
        text cached_layout_json
    }
```

### Analytics API (`/api/v1/analytics`)
Bottlenecks, rework, and performance metrics.

```mermaid
erDiagram
    DATASET ||--o{ ANALYTICS_CACHE : results
    ANALYTICS_CACHE {
        string id PK
        string dataset_id FK
        string metric_type
        text result_json
    }
```

### Predictions API (`/api/v1/predictions`)
Machine Learning models and predictions for process cases.

```mermaid
erDiagram
    DATASET ||--o{ PREDICTION_MODEL : trains
    PREDICTION_MODEL ||--o{ PREDICTION : generates
    
    PREDICTION_MODEL {
        string id PK
        string dataset_id FK
        string target_type
        string algorithm
    }
    PREDICTION {
        string id PK
        string model_id FK
        text prediction_json
        float confidence
    }
```

### Simulation & Recommendations API (`/api/v1/simulation`)
Process simulation and prescriptive recommendations.

```mermaid
erDiagram
    DATASET ||--o{ RECOMMENDATION : triggers
    RECOMMENDATION {
        string id PK
        string dataset_id FK
        string case_id
        string signal_type
        string action_type
        string priority
    }
```

### Object-Centric Process Mining (OCPM) API (`/api/v1/ocpm`)
Handling of OCEL (Object-Centric Event Logs).

```mermaid
erDiagram
    OCEL_LOG ||--o{ OCEL_OBJECT_TYPE : contains
    OCEL_LOG ||--o{ OC_PETRI_NET : discovers
    
    OCEL_LOG {
        string id PK
        string name
        int total_events
        int total_objects
    }
    OCEL_OBJECT_TYPE {
        string id PK
        string dataset_id FK
        string name
        int object_count
    }
```

### Workflows API (`/api/v1/workflows`)
Automated processing pipelines.

```mermaid
erDiagram
    WORKFLOW ||--o{ WORKFLOW_RUN : executes
    DATASET ||--o{ WORKFLOW_RUN : "context"
    
    WORKFLOW {
        string id PK
        string name
        text steps_json
    }
    WORKFLOW_RUN {
        string id PK
        string workflow_id FK
        string dataset_id FK
        string status
    }
```

---

## Endpoint to Entity Mapping (Key Examples)

| Router | Endpoint | Primary Entity | Secondary Entities |
| :--- | :--- | :--- | :--- |
| Datasets | `POST /datasets/upload` | `Dataset` | `UploadedFile`, `Project` |
| Datasets | `GET /datasets/{id}/cases` | `ProcessCase` | `Dataset` |
| Analyses | `POST /analyses` | `Analysis` | `Dataset`, `ProcessModel` |
| Visualization | `GET /datasets/{id}/dfg` | `Dataset` | `ProcessEvent` (calculated) |
| Predictions | `POST /predictions/train` | `PredictionModel` | `Dataset` |
| Simulation | `GET /recommendations` | `Recommendation` | `Dataset` |
| OCPM | `GET /ocpm/logs` | `OCELLog` | - |
| Workflows | `POST /workflows` | `Workflow` | - |
| Workflows | `POST /workflows/{id}/run` | `WorkflowRun` | `Workflow`, `Dataset` |
