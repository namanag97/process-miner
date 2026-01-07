# Process Mining Features - Computation Graph

## Feature Overview

This document covers the specialized process mining features: filtering, visualization, OCPM, and AI integration.

## Event Log Filtering

```mermaid
flowchart TB
    subgraph "Filter Types"
        ACT_FILTER[Activity Filter]
        CASE_FILTER[Case Filter]
        TIME_FILTER[Time Range Filter]
        ATTR_FILTER[Attribute Filter]
        PERF_FILTER[Performance Filter]
    end

    subgraph "Filter Operations"
        INCLUDE[Include Matching]
        EXCLUDE[Exclude Matching]
        BETWEEN[Between Range]
        CONTAINS[Contains Pattern]
    end

    subgraph "Processing"
        ORIGINAL[(Original Dataset)]
        APPLY[Apply Filters]
        DERIVED[(Derived Dataset)]
        STATS[Recompute Statistics]
    end

    ACT_FILTER --> INCLUDE
    ACT_FILTER --> EXCLUDE
    CASE_FILTER --> INCLUDE
    CASE_FILTER --> EXCLUDE
    TIME_FILTER --> BETWEEN
    ATTR_FILTER --> CONTAINS
    PERF_FILTER --> BETWEEN

    ORIGINAL --> APPLY
    INCLUDE --> APPLY
    EXCLUDE --> APPLY
    BETWEEN --> APPLY
    CONTAINS --> APPLY

    APPLY --> DERIVED
    DERIVED --> STATS
```

## Filter Application Pipeline

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant FilterService
    participant DuckDB
    participant Database

    Client->>API: POST /datasets/:id/filter
    Note over Client,API: FilterRequest with criteria

    API->>FilterService: apply_filter(dataset_id, criteria)

    FilterService->>Database: Get original dataset metadata
    Database-->>FilterService: Dataset

    FilterService->>DuckDB: Build filter SQL
    Note over FilterService,DuckDB: Dynamic WHERE clauses

    loop For Each Filter
        FilterService->>DuckDB: Apply filter condition
    end

    DuckDB-->>FilterService: Filtered Arrow Table

    FilterService->>Database: Create derived Dataset
    FilterService->>FilterService: Export filtered Parquet

    FilterService->>Database: Update statistics
    FilterService-->>API: FilterResult

    API-->>Client: {derived_dataset_id, statistics}
```

## Filter SQL Generation

```mermaid
flowchart LR
    subgraph "Filter Input"
        ACT_IN[activities: [A, B, C]]
        TIME_IN[start: 2024-01-01<br/>end: 2024-12-31]
        PERF_IN[min_duration: 1h<br/>max_duration: 24h]
    end

    subgraph "SQL Builder"
        BASE[SELECT * FROM events]
        WHERE[WHERE clause builder]
    end

    subgraph "Generated SQL"
        SQL[SELECT * FROM events<br/>WHERE activity IN ('A','B','C')<br/>AND timestamp BETWEEN ...<br/>AND duration BETWEEN ...]
    end

    ACT_IN --> WHERE
    TIME_IN --> WHERE
    PERF_IN --> WHERE

    BASE --> WHERE
    WHERE --> SQL
```

## Visualization Pipeline

```mermaid
flowchart TB
    subgraph "Model Types"
        DFG_MODEL[DFG Model]
        PETRI_MODEL[Petri Net]
        BPMN_MODEL[BPMN Model]
        TREE_MODEL[Process Tree]
    end

    subgraph "Graph Generation"
        PARSE[Parse Model]
        NODES[Extract Nodes]
        EDGES[Extract Edges]
        LAYOUT[Apply Layout Algorithm]
    end

    subgraph "Layout Algorithms"
        DAGRE[Dagre (hierarchical)]
        FORCE[Force-directed]
        GRID[Grid layout]
    end

    subgraph "Output Formats"
        CYTO_JSON[Cytoscape JSON]
        DOT[DOT/GraphViz]
        SVG[SVG Image]
    end

    DFG_MODEL --> PARSE
    PETRI_MODEL --> PARSE
    BPMN_MODEL --> PARSE
    TREE_MODEL --> PARSE

    PARSE --> NODES
    PARSE --> EDGES
    NODES --> LAYOUT
    EDGES --> LAYOUT

    LAYOUT --> DAGRE
    LAYOUT --> FORCE
    LAYOUT --> GRID

    DAGRE --> CYTO_JSON
    FORCE --> CYTO_JSON
    GRID --> DOT
    DOT --> SVG
```

## DFG Visualization Data Structure

```mermaid
graph TD
    subgraph "DFG Response"
        NODES_ARR[nodes: Array]
        EDGES_ARR[edges: Array]
        STATS_OBJ[stats: Object]
    end

    subgraph "Node Structure"
        N_ID[id: string]
        N_LABEL[label: activity name]
        N_FREQ[frequency: number]
        N_PERF[performance: metrics]
        N_POS[position: x, y]
    end

    subgraph "Edge Structure"
        E_SOURCE[source: node_id]
        E_TARGET[target: node_id]
        E_WEIGHT[weight: frequency]
        E_TIME[avg_time: duration]
    end

    subgraph "Stats"
        S_CASES[total_cases]
        S_EVENTS[total_events]
        S_ACTS[activities_count]
        S_VARIANTS[variants_count]
    end

    NODES_ARR --> N_ID
    NODES_ARR --> N_LABEL
    NODES_ARR --> N_FREQ
    NODES_ARR --> N_PERF
    NODES_ARR --> N_POS

    EDGES_ARR --> E_SOURCE
    EDGES_ARR --> E_TARGET
    EDGES_ARR --> E_WEIGHT
    EDGES_ARR --> E_TIME

    STATS_OBJ --> S_CASES
    STATS_OBJ --> S_EVENTS
    STATS_OBJ --> S_ACTS
    STATS_OBJ --> S_VARIANTS
```

## Object-Centric Process Mining (OCPM)

```mermaid
flowchart TB
    subgraph "OCEL 2.0 Input"
        OCEL_FILE[OCEL JSON/SQLite]
        OBJECTS[Object Types]
        EVENTS_OC[Object-Centric Events]
        O2O[Object-to-Object Relations]
    end

    subgraph "Object Types Example"
        ORDER[Order]
        ITEM[Item]
        PACKAGE[Package]
        DELIVERY[Delivery]
    end

    subgraph "Analysis Capabilities"
        OBJ_GRAPH[Object Graph]
        OBJ_DFG[Object-Centric DFG]
        OBJ_LIFECYCLE[Object Lifecycle]
        INTERACTION[Object Interactions]
    end

    OCEL_FILE --> OBJECTS
    OCEL_FILE --> EVENTS_OC
    OCEL_FILE --> O2O

    OBJECTS --> ORDER
    OBJECTS --> ITEM
    OBJECTS --> PACKAGE
    OBJECTS --> DELIVERY

    ORDER --> OBJ_GRAPH
    ITEM --> OBJ_GRAPH
    EVENTS_OC --> OBJ_DFG
    O2O --> INTERACTION
    EVENTS_OC --> OBJ_LIFECYCLE
```

## OCEL Data Model

```mermaid
erDiagram
    OCELEvent ||--o{ EventObjectAssoc : has
    OCELObject ||--o{ EventObjectAssoc : referenced_in
    OCELObject ||--o{ ObjectToObject : source
    OCELObject ||--o{ ObjectToObject : target
    ObjectType ||--o{ OCELObject : categorizes

    OCELEvent {
        string ocel_id PK
        string ocel_type
        datetime ocel_time
        json ocel_vmap
    }

    OCELObject {
        string ocel_id PK
        string ocel_type FK
        json ocel_ovmap
    }

    ObjectType {
        string ocel_type PK
        string[] attributes
    }

    EventObjectAssoc {
        string event_id FK
        string object_id FK
        string qualifier
    }

    ObjectToObject {
        string source_id FK
        string target_id FK
        string qualifier
    }
```

## AI Integration Architecture

```mermaid
flowchart TB
    subgraph "Process Context"
        DATASET[Dataset]
        METRICS[Computed Metrics]
        BOTTLENECKS[Bottleneck Analysis]
        PATTERNS[Discovered Patterns]
    end

    subgraph "Context Builder"
        SUMMARIZE[Summarize Process]
        FORMAT[Format for LLM]
        CONTEXT_JSON[Context JSON]
    end

    subgraph "LLM Integration"
        PROMPT[User Prompt]
        SYSTEM[System Prompt]
        API_CALL[LLM API Call]
        RESPONSE[LLM Response]
    end

    subgraph "Response Processing"
        PARSE_RESP[Parse Response]
        EXTRACT_INSIGHT[Extract Insights]
        STRUCTURE[Structure Output]
    end

    DATASET --> SUMMARIZE
    METRICS --> SUMMARIZE
    BOTTLENECKS --> SUMMARIZE
    PATTERNS --> SUMMARIZE

    SUMMARIZE --> FORMAT
    FORMAT --> CONTEXT_JSON

    CONTEXT_JSON --> SYSTEM
    PROMPT --> API_CALL
    SYSTEM --> API_CALL

    API_CALL --> RESPONSE
    RESPONSE --> PARSE_RESP
    PARSE_RESP --> EXTRACT_INSIGHT
    EXTRACT_INSIGHT --> STRUCTURE
```

## AI Chat Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AIService
    participant AnalyticsService
    participant LLM

    User->>Frontend: Select Process
    Frontend->>API: GET /ai/processes/:id/summary
    API->>AnalyticsService: Get process metrics

    AnalyticsService->>AnalyticsService: Compute bottlenecks
    AnalyticsService->>AnalyticsService: Compute rework
    AnalyticsService->>AnalyticsService: Get variants

    AnalyticsService-->>API: ProcessSummary
    API-->>Frontend: ProcessSummary

    User->>Frontend: Enter question
    Frontend->>API: POST /ai/chat

    API->>AIService: process_message(question, context)

    AIService->>AIService: Build system prompt
    AIService->>AIService: Include process context
    AIService->>LLM: Send to LLM

    LLM-->>AIService: Response stream
    AIService-->>API: Parsed insights
    API-->>Frontend: ChatResponse

    Frontend->>User: Display insights
```

## AI Insight Types

```mermaid
graph TB
    subgraph "Insight Categories"
        BOTTLE_INS[Bottleneck Insights]
        REWORK_INS[Rework Insights]
        PATTERN_INS[Pattern Insights]
        OPT_INS[Optimization Suggestions]
        ANOMALY_INS[Anomaly Detection]
    end

    subgraph "Insight Structure"
        TYPE[type: category]
        SEVERITY[severity: low/medium/high]
        TITLE[title: summary]
        DESC[description: details]
        DATA[data: supporting metrics]
        ACTIONS[actions: recommendations]
    end

    BOTTLE_INS --> TYPE
    REWORK_INS --> TYPE
    PATTERN_INS --> TYPE
    OPT_INS --> TYPE
    ANOMALY_INS --> TYPE

    TYPE --> SEVERITY
    SEVERITY --> TITLE
    TITLE --> DESC
    DESC --> DATA
    DATA --> ACTIONS
```

## Variant Analysis

```mermaid
flowchart TB
    subgraph "Variant Extraction"
        EVENTS[(Event Log)]
        GROUP[Group by Case ID]
        TRACE[Extract Activity Sequence]
        HASH[Hash Sequence]
    end

    subgraph "Variant Aggregation"
        COUNT[Count Occurrences]
        RANK[Rank by Frequency]
        TOP_N[Select Top N]
    end

    subgraph "Variant Analysis"
        HAPPY[Happy Path Detection]
        REWORK_VAR[Rework Variants]
        DEVIANT[Deviant Variants]
    end

    subgraph "Output"
        VAR_LIST[Variant List]
        VAR_DIST[Distribution Chart]
        VAR_COMPARE[Variant Comparison]
    end

    EVENTS --> GROUP
    GROUP --> TRACE
    TRACE --> HASH

    HASH --> COUNT
    COUNT --> RANK
    RANK --> TOP_N

    TOP_N --> HAPPY
    TOP_N --> REWORK_VAR
    TOP_N --> DEVIANT

    HAPPY --> VAR_LIST
    REWORK_VAR --> VAR_DIST
    DEVIANT --> VAR_COMPARE
```

## Workflow Definition & Execution

```mermaid
flowchart TB
    subgraph "Workflow Definition"
        DEFINE[Define Workflow]
        STEPS[Define Steps]
        TRANSITIONS[Define Transitions]
        CONDITIONS[Define Conditions]
    end

    subgraph "Workflow Structure"
        START_NODE[Start Node]
        TASK_NODE[Task Nodes]
        GATEWAY[Gateway Nodes]
        END_NODE[End Node]
    end

    subgraph "Execution"
        INSTANCE[Create Instance]
        EXECUTE[Execute Steps]
        EVAL[Evaluate Conditions]
        COMPLETE[Complete Workflow]
    end

    subgraph "Monitoring"
        STATUS[Track Status]
        METRICS_WF[Collect Metrics]
        ALERTS[Trigger Alerts]
    end

    DEFINE --> STEPS
    STEPS --> TRANSITIONS
    TRANSITIONS --> CONDITIONS

    STEPS --> START_NODE
    STEPS --> TASK_NODE
    STEPS --> GATEWAY
    STEPS --> END_NODE

    START_NODE --> INSTANCE
    INSTANCE --> EXECUTE
    EXECUTE --> EVAL
    EVAL --> GATEWAY
    GATEWAY --> EXECUTE
    EXECUTE --> COMPLETE

    EXECUTE --> STATUS
    STATUS --> METRICS_WF
    METRICS_WF --> ALERTS
```

## Export Functionality

```mermaid
flowchart LR
    subgraph "Source"
        DATASET_EXP[(Dataset)]
        MODEL_EXP[Process Model]
    end

    subgraph "Export Formats"
        CSV_EXP[CSV Export]
        XES_EXP[XES Export]
        PARQUET_EXP[Parquet Export]
        PNML[PNML Export]
        DOT_EXP[DOT/GraphViz]
        BPMN_EXP[BPMN XML]
    end

    subgraph "Process"
        CONVERT[Convert Format]
        STREAM[Stream to S3]
        PRESIGNED[Generate Presigned URL]
    end

    DATASET_EXP --> CSV_EXP
    DATASET_EXP --> XES_EXP
    DATASET_EXP --> PARQUET_EXP

    MODEL_EXP --> PNML
    MODEL_EXP --> DOT_EXP
    MODEL_EXP --> BPMN_EXP

    CSV_EXP --> CONVERT
    XES_EXP --> CONVERT
    PARQUET_EXP --> CONVERT
    PNML --> CONVERT
    DOT_EXP --> CONVERT
    BPMN_EXP --> CONVERT

    CONVERT --> STREAM
    STREAM --> PRESIGNED
```

## Feature Dependencies

```mermaid
graph TB
    subgraph "Core Dependencies"
        DATASETS_DEP[Datasets Domain]
        DUCKDB_DEP[DuckDB Infrastructure]
        S3_DEP[S3 Storage]
        PM4PY_DEP[PM4Py Library]
    end

    subgraph "Feature Modules"
        FILTER_MOD[Filtering]
        VIZ_MOD[Visualization]
        OCPM_MOD[OCPM]
        AI_MOD[AI Integration]
        VARIANT_MOD[Variant Analysis]
        EXPORT_MOD[Export]
    end

    subgraph "Shared Services"
        EVENT_LOG_SVC[EventLog Service]
        CACHE_SVC[Cache Service]
        JOB_SVC[Job Service]
    end

    DATASETS_DEP --> FILTER_MOD
    DATASETS_DEP --> VIZ_MOD
    DATASETS_DEP --> OCPM_MOD
    DATASETS_DEP --> AI_MOD
    DATASETS_DEP --> VARIANT_MOD
    DATASETS_DEP --> EXPORT_MOD

    DUCKDB_DEP --> FILTER_MOD
    DUCKDB_DEP --> VARIANT_MOD

    PM4PY_DEP --> VIZ_MOD
    PM4PY_DEP --> OCPM_MOD

    S3_DEP --> EXPORT_MOD

    EVENT_LOG_SVC --> FILTER_MOD
    EVENT_LOG_SVC --> VIZ_MOD
    CACHE_SVC --> AI_MOD
    JOB_SVC --> EXPORT_MOD
```

## API Endpoints

```mermaid
graph TD
    subgraph "Filtering API"
        FILT_APPLY[POST /datasets/:id/filter]
        FILT_PREVIEW[POST /datasets/:id/filter/preview]
    end

    subgraph "Visualization API"
        VIZ_DFG[GET /visualization/dfg/:id]
        VIZ_PETRI[GET /visualization/petri/:id]
        VIZ_BPMN[GET /visualization/bpmn/:id]
    end

    subgraph "OCPM API"
        OCPM_UPLOAD[POST /ocpm/upload]
        OCPM_OBJECTS[GET /ocpm/:id/objects]
        OCPM_GRAPH[GET /ocpm/:id/graph]
    end

    subgraph "AI API"
        AI_SUMMARY[GET /ai/processes/:id/summary]
        AI_CHAT[POST /ai/chat]
        AI_INSIGHTS[GET /ai/processes/:id/insights]
    end

    subgraph "Export API"
        EXP_CSV[GET /datasets/:id/export/csv]
        EXP_XES[GET /datasets/:id/export/xes]
        EXP_MODEL[GET /models/:id/export/:format]
    end
```

## Key Files Reference

| Component | Path |
|-----------|------|
| Filtering Router | `src/features/process_mining/filtering/router.py` |
| Filter Service | `src/features/process_mining/filtering/service.py` |
| Visualization Router | `src/features/process_mining/visualization/router.py` |
| Graph Generator | `src/features/process_mining/visualization/graph.py` |
| OCPM Router | `src/features/process_mining/ocpm/router.py` |
| OCEL Parser | `src/features/process_mining/ocpm/ocel_parser.py` |
| AI Router | `src/features/process_mining/ai/router.py` |
| AI Service | `src/features/process_mining/ai/service.py` |
| Export Router | `src/features/process_mining/export/router.py` |
| Variant Service | `src/features/process_mining/analytics/variants.py` |
