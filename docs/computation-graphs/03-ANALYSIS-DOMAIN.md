# Analysis Domain - Computation Graph

## Domain Overview

The Analysis domain encompasses all process mining and analytics capabilities: discovery, conformance, analytics, predictions, and organizational analysis.

## Discovery Algorithm Categories

```mermaid
graph TB
    subgraph "Discovery Algorithms"
        direction TB

        subgraph "Procedural Discovery"
            ALPHA[Alpha Miner<br/>Classic, simple]
            INDUCTIVE[Inductive Miner<br/>Sound, recommended]
            HEURISTICS[Heuristics Miner<br/>Frequency-based]
            ILP[ILP Miner<br/>Precise, slow]
        end

        subgraph "Declarative Discovery"
            DECLARE[Declare Miner<br/>Constraint-based]
            LOG_SKEL[Log Skeleton<br/>Relationships]
        end

        subgraph "Graph-Based"
            DFG[DFG Miner<br/>Directly-Follows]
            PERF_DFG[Performance DFG<br/>With metrics]
            PREFIX[Prefix Tree<br/>Full traces]
        end

        subgraph "Other"
            TEMP_PROF[Temporal Profile<br/>Time patterns]
            BATCHES[Batch Discovery<br/>Batch patterns]
            TRANS[Transition System<br/>State machine]
        end
    end

    subgraph "Output Formats"
        PETRI[Petri Net]
        BPMN[BPMN Model]
        TREE[Process Tree]
        GRAPH[Graph JSON]
        JSON[JSON Data]
    end

    ALPHA --> PETRI
    INDUCTIVE --> TREE
    INDUCTIVE --> PETRI
    HEURISTICS --> PETRI
    ILP --> PETRI
    DFG --> GRAPH
    PERF_DFG --> GRAPH
    DECLARE --> JSON
    LOG_SKEL --> JSON
    TEMP_PROF --> JSON
```

## Discovery Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant DiscoveryService
    participant MiningService
    participant PM4Py
    participant ModelSerializer
    participant S3
    participant Database

    Client->>API: POST /discovery/discover
    API->>API: Validate dataset.status == READY

    API->>DiscoveryService: discover(request)
    DiscoveryService->>Database: Load dataset metadata

    alt Synchronous (small dataset)
        DiscoveryService->>MiningService: run_algorithm(event_log, params)
        MiningService->>PM4Py: apply_algorithm()
        PM4Py-->>MiningService: ProcessModel

        MiningService->>ModelSerializer: serialize(model)
        ModelSerializer-->>MiningService: bytes

        MiningService->>S3: store(model_bytes)
        S3-->>MiningService: storage_path

        MiningService->>MiningService: generate_graph_json()
        MiningService->>Database: Create ProcessModel record
        MiningService-->>DiscoveryService: ProcessModel

        DiscoveryService-->>API: DiscoveryResponse
        API-->>Client: ProcessModel

    else Asynchronous (large dataset)
        DiscoveryService->>TemporalClient: start_workflow(DiscoveryWorkflow)
        TemporalClient-->>DiscoveryService: workflow_id

        DiscoveryService->>Database: Create Job record
        DiscoveryService-->>API: JobReference

        API-->>Client: {job_id, status: queued}
    end
```

## Event Log Loading Pipeline

```mermaid
flowchart LR
    subgraph "Data Sources"
        PARQUET[(S3 Parquet)]
        DB[(SQLite Events)]
    end

    subgraph "DuckDB Layer"
        DUCK[DuckDB Connection]
        QUERY[SQL Query]
        ARROW[Arrow Table]
    end

    subgraph "PM4Py Conversion"
        DF[Pandas DataFrame]
        FORMAT[Format Columns]
        EVENT_LOG[PM4Py EventLog]
    end

    PARQUET --> DUCK
    DB --> DUCK
    DUCK --> QUERY
    QUERY --> ARROW
    ARROW --> DF
    DF --> FORMAT
    FORMAT --> EVENT_LOG

    FORMAT --> |case:concept:name| CASE[Case ID Column]
    FORMAT --> |concept:name| ACT[Activity Column]
    FORMAT --> |time:timestamp| TIME[Timestamp Column]
    FORMAT --> |org:resource| RES[Resource Column]
```

## Algorithm Selection Logic

```mermaid
flowchart TD
    INPUT[Dataset Characteristics] --> ANALYZE[Analyze Dataset]

    ANALYZE --> SIZE{Event Count?}
    SIZE -->|< 10K| SMALL[Small Dataset]
    SIZE -->|10K - 100K| MEDIUM[Medium Dataset]
    SIZE -->|> 100K| LARGE[Large Dataset]

    SMALL --> QUALITY{Data Quality?}
    MEDIUM --> QUALITY
    LARGE --> PERF[Performance Critical]

    QUALITY -->|Clean| CLEAN[High Quality]
    QUALITY -->|Noisy| NOISY[Noisy Data]

    CLEAN --> INDUCTIVE_REC[Recommend: Inductive]
    NOISY --> HEUR_REC[Recommend: Heuristics]
    PERF --> DFG_REC[Recommend: DFG]

    subgraph "Algorithm Recommendations"
        INDUCTIVE_REC --> |Sound model| IND[Inductive Miner]
        HEUR_REC --> |Noise tolerant| HEUR[Heuristics Miner]
        DFG_REC --> |Fast, visual| DFG_M[DFG Miner]
    end
```

## Process Model Serialization

```mermaid
flowchart TB
    subgraph "PM4Py Objects"
        PETRI_OBJ[PetriNet Object]
        TREE_OBJ[ProcessTree Object]
        DFG_OBJ[DFG Dict]
    end

    subgraph "Serialization"
        JOBLIB[joblib.dump]
        JSON_SER[JSON Serializer]
    end

    subgraph "Storage"
        S3_STORE[(S3 Bucket)]
        DB_CACHE[(Graph JSON Cache)]
    end

    PETRI_OBJ --> JOBLIB
    TREE_OBJ --> JOBLIB
    DFG_OBJ --> JSON_SER

    JOBLIB --> |.joblib file| S3_STORE
    JSON_SER --> |graph_json| DB_CACHE
```

## Conformance Checking Flow

```mermaid
flowchart TD
    subgraph "Input"
        EVENT_LOG[Event Log]
        MODEL[Process Model]
    end

    subgraph "Conformance Techniques"
        TOKEN[Token Replay]
        ALIGN[Alignments]
        FOOTPRINT[Footprint Comparison]
    end

    subgraph "Metrics"
        FITNESS[Fitness Score<br/>0.0 - 1.0]
        PRECISION[Precision Score<br/>0.0 - 1.0]
        GENERAL[Generalization<br/>0.0 - 1.0]
        SIMPLE[Simplicity<br/>0.0 - 1.0]
    end

    subgraph "Deviation Analysis"
        DEVIATIONS[Trace Deviations]
        PATTERNS[Deviation Patterns]
        HOTSPOTS[Non-conforming Cases]
    end

    EVENT_LOG --> TOKEN
    MODEL --> TOKEN
    EVENT_LOG --> ALIGN
    MODEL --> ALIGN
    EVENT_LOG --> FOOTPRINT
    MODEL --> FOOTPRINT

    TOKEN --> FITNESS
    ALIGN --> FITNESS
    ALIGN --> PRECISION
    FOOTPRINT --> GENERAL

    TOKEN --> DEVIATIONS
    DEVIATIONS --> PATTERNS
    PATTERNS --> HOTSPOTS
```

## Analytics Query Architecture (CQRS)

```mermaid
flowchart TB
    subgraph "Query Handlers"
        Q_BOTTLE[GetBottlenecksQuery]
        Q_CYCLE[GetCycleTimeQuery]
        Q_REWORK[GetReworkQuery]
        Q_VARIANTS[GetVariantsQuery]
        Q_THROUGH[GetThroughputQuery]
    end

    subgraph "Cache Layer"
        CACHE_CHECK{Cache Hit?}
        REDIS[(Redis Cache)]
    end

    subgraph "DuckDB OLAP"
        DUCK_CONN[DuckDB Connection]
        SQL_EXEC[Execute SQL]
        PARQUET_READ[read_parquet from S3]
    end

    subgraph "Results"
        RESULT[Query Result]
        CACHE_SET[Update Cache]
    end

    Q_BOTTLE --> CACHE_CHECK
    Q_CYCLE --> CACHE_CHECK
    Q_REWORK --> CACHE_CHECK
    Q_VARIANTS --> CACHE_CHECK
    Q_THROUGH --> CACHE_CHECK

    CACHE_CHECK -->|Yes| REDIS
    REDIS --> RESULT

    CACHE_CHECK -->|No| DUCK_CONN
    DUCK_CONN --> PARQUET_READ
    PARQUET_READ --> SQL_EXEC
    SQL_EXEC --> RESULT
    RESULT --> CACHE_SET
    CACHE_SET --> REDIS
```

## Bottleneck Analysis

```mermaid
flowchart LR
    subgraph "Input"
        EVENTS[(Parquet Events)]
    end

    subgraph "Calculation"
        WAIT[Calculate Wait Times]
        SERVICE[Calculate Service Times]
        FREQ[Calculate Frequencies]
    end

    subgraph "Analysis"
        THRESHOLD[Apply Threshold]
        RANK[Rank by Severity]
        IMPACT[Calculate Impact Score]
    end

    subgraph "Output"
        BOTTLENECKS[Bottleneck List]
        HEATMAP[Heatmap Data]
        RECOMMEND[Recommendations]
    end

    EVENTS --> WAIT
    EVENTS --> SERVICE
    EVENTS --> FREQ

    WAIT --> THRESHOLD
    SERVICE --> THRESHOLD
    FREQ --> RANK

    THRESHOLD --> RANK
    RANK --> IMPACT

    IMPACT --> BOTTLENECKS
    IMPACT --> HEATMAP
    BOTTLENECKS --> RECOMMEND
```

## Rework Detection

```mermaid
flowchart TD
    subgraph "Rework Patterns"
        SELF_LOOP[Self-Loops<br/>A → A]
        SHORT_LOOP[Short Loops<br/>A → B → A]
        LONG_LOOP[Long Loops<br/>A → ... → A]
    end

    subgraph "Detection SQL"
        QUERY_SELF[SELECT activity<br/>WHERE next_activity = activity]
        QUERY_SHORT[SELECT activity, next<br/>WHERE next_next = activity]
        QUERY_LONG[Window functions<br/>for loop detection]
    end

    subgraph "Metrics"
        REWORK_RATE[Rework Rate %]
        REWORK_COST[Estimated Cost]
        REWORK_CASES[Affected Cases]
    end

    SELF_LOOP --> QUERY_SELF
    SHORT_LOOP --> QUERY_SHORT
    LONG_LOOP --> QUERY_LONG

    QUERY_SELF --> REWORK_RATE
    QUERY_SHORT --> REWORK_RATE
    QUERY_LONG --> REWORK_RATE

    REWORK_RATE --> REWORK_COST
    REWORK_RATE --> REWORK_CASES
```

## Prediction Models

```mermaid
flowchart TB
    subgraph "Training Pipeline"
        HIST_DATA[Historical Event Log]
        FEATURE_EXT[Feature Extraction]
        TRAIN_MODEL[Train ML Model]
        SAVE_MODEL[Save to S3]
    end

    subgraph "Features"
        CASE_FEAT[Case Features<br/>duration, events]
        ACT_FEAT[Activity Features<br/>sequence, position]
        TIME_FEAT[Time Features<br/>hour, day, month]
        RES_FEAT[Resource Features<br/>workload, skill]
    end

    subgraph "Prediction Types"
        NEXT_ACT[Next Activity<br/>Classification]
        REM_TIME[Remaining Time<br/>Regression]
        OUTCOME[Case Outcome<br/>Classification]
    end

    subgraph "Inference"
        LIVE_CASE[Active Case]
        LOAD_MODEL[Load Model]
        PREDICT[Generate Prediction]
        CONFIDENCE[Confidence Score]
    end

    HIST_DATA --> FEATURE_EXT
    FEATURE_EXT --> CASE_FEAT
    FEATURE_EXT --> ACT_FEAT
    FEATURE_EXT --> TIME_FEAT
    FEATURE_EXT --> RES_FEAT

    CASE_FEAT --> TRAIN_MODEL
    ACT_FEAT --> TRAIN_MODEL
    TIME_FEAT --> TRAIN_MODEL
    RES_FEAT --> TRAIN_MODEL

    TRAIN_MODEL --> NEXT_ACT
    TRAIN_MODEL --> REM_TIME
    TRAIN_MODEL --> OUTCOME

    TRAIN_MODEL --> SAVE_MODEL

    LIVE_CASE --> LOAD_MODEL
    LOAD_MODEL --> PREDICT
    PREDICT --> CONFIDENCE
```

## Organizational Analysis

```mermaid
flowchart TB
    subgraph "Social Network Analysis"
        HANDOVERS[Resource Handovers]
        COLLAB[Collaboration Patterns]
        WORKLOAD[Workload Distribution]
    end

    subgraph "Handover Types"
        DIRECT[Direct Handover<br/>A → B]
        JOINT[Joint Activities<br/>A & B on same case]
        SIMILAR[Similar Tasks<br/>Same activity types]
    end

    subgraph "Metrics"
        DEGREE[Degree Centrality]
        BETWEEN[Betweenness]
        CLUSTER[Clustering Coefficient]
    end

    subgraph "Visualizations"
        SNA_GRAPH[Social Network Graph]
        HEATMAP_RES[Resource Heatmap]
        SANKEY[Handover Sankey]
    end

    HANDOVERS --> DIRECT
    HANDOVERS --> JOINT
    COLLAB --> SIMILAR

    DIRECT --> DEGREE
    JOINT --> BETWEEN
    SIMILAR --> CLUSTER

    DEGREE --> SNA_GRAPH
    BETWEEN --> SNA_GRAPH
    CLUSTER --> HEATMAP_RES
    DIRECT --> SANKEY
```

## Simulation (What-If Analysis)

```mermaid
flowchart LR
    subgraph "Inputs"
        BASE_MODEL[Base Process Model]
        PARAMS[Simulation Parameters]
    end

    subgraph "Parameter Variations"
        RES_CHANGE[Resource Changes<br/>+/- staff]
        TIME_CHANGE[Processing Times<br/>+/- efficiency]
        ARRIVAL[Arrival Rate<br/>+/- demand]
    end

    subgraph "Simulation Engine"
        PLAYOUT[Process Tree Playout]
        DISCRETE[Discrete Event Sim]
    end

    subgraph "Results"
        CYCLE_SIM[Simulated Cycle Time]
        UTIL_SIM[Resource Utilization]
        BOTTLE_SIM[Bottleneck Prediction]
        COMPARE[Compare Scenarios]
    end

    BASE_MODEL --> PLAYOUT
    PARAMS --> PLAYOUT

    PARAMS --> RES_CHANGE
    PARAMS --> TIME_CHANGE
    PARAMS --> ARRIVAL

    PLAYOUT --> DISCRETE

    DISCRETE --> CYCLE_SIM
    DISCRETE --> UTIL_SIM
    DISCRETE --> BOTTLE_SIM

    CYCLE_SIM --> COMPARE
    UTIL_SIM --> COMPARE
    BOTTLE_SIM --> COMPARE
```

## API Endpoints Structure

```mermaid
graph TD
    subgraph "Discovery API"
        DIS_DISCOVER[POST /discovery/discover]
        DIS_ALGOS[GET /discovery/algorithms]
        DIS_MODELS[GET /discovery/models]
        DIS_MODEL[GET /discovery/models/:id]
    end

    subgraph "Conformance API"
        CONF_CHECK[POST /conformance/check]
        CONF_TOKEN[POST /conformance/token-replay]
        CONF_ALIGN[POST /conformance/alignments]
    end

    subgraph "Analytics API"
        ANA_BOTTLE[GET /analytics/bottlenecks]
        ANA_CYCLE[GET /analytics/cycle-time]
        ANA_REWORK[GET /analytics/rework]
        ANA_VARIANTS[GET /analytics/variants]
        ANA_THROUGH[GET /analytics/throughput]
    end

    subgraph "Predictions API"
        PRED_TRAIN[POST /predictions/train]
        PRED_NEXT[POST /predictions/next-activity]
        PRED_TIME[POST /predictions/remaining-time]
    end

    subgraph "Organizational API"
        ORG_HANDOVER[GET /organizational/handovers]
        ORG_SNA[GET /organizational/social-network]
        ORG_WORKLOAD[GET /organizational/workload]
    end
```

## Temporal Workflow for Discovery

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Temporal
    participant LoadActivity
    participant MineActivity
    participant SerializeActivity
    participant StoreActivity
    participant Database

    Client->>API: POST /discovery/discover
    API->>Temporal: start_workflow(ProcessDiscoveryWorkflowV2)

    Temporal->>LoadActivity: load_event_log(dataset_id)
    LoadActivity->>LoadActivity: DuckDB → Arrow → PM4Py
    LoadActivity-->>Temporal: EventLog

    Temporal->>MineActivity: run_discovery(event_log, algorithm)
    MineActivity->>MineActivity: PM4Py algorithm
    MineActivity-->>Temporal: ProcessModel (PM4Py object)

    Temporal->>SerializeActivity: serialize_model(model)
    SerializeActivity->>SerializeActivity: joblib.dump()
    SerializeActivity-->>Temporal: model_bytes

    Temporal->>StoreActivity: store_and_record(model_bytes)
    StoreActivity->>S3: Upload model file
    StoreActivity->>Database: Create ProcessModel record
    StoreActivity-->>Temporal: model_id

    Temporal-->>API: WorkflowComplete(model_id)
    API-->>Client: {model_id, status: completed}
```

## Key Files Reference

| Component | Path |
|-----------|------|
| Discovery Router | `src/features/process_mining/discovery/router.py` |
| Mining Service | `src/features/process_mining/discovery/mining_service.py` |
| Algorithm Registry | `src/features/process_mining/discovery/algorithms.py` |
| Analytics Router | `src/features/process_mining/analytics/router.py` |
| Analytics Queries | `src/application/queries/analytics_queries.py` |
| Analytics Cache | `src/application/projections/analytics_cache.py` |
| Conformance Router | `src/features/process_mining/conformance/router.py` |
| Predictions Router | `src/features/process_mining/predictions/router.py` |
| Organizational Router | `src/features/process_mining/organizational/router.py` |
| Discovery Workflow | `src/infra/temporal/workflows_v2/discovery.py` |
| Process Model Schema | `src/features/process_mining/schemas/analysis.py` |
