# Datasets Domain - Computation Graph

## Domain Overview

The Datasets domain handles the complete data lifecycle for event logs: upload, validation, column mapping, and ingestion.

## Dataset Status State Machine

```mermaid
stateDiagram-v2
    [*] --> PENDING: Create Dataset
    PENDING --> UPLOADING: Start Upload
    UPLOADING --> UPLOADED: Upload Complete
    UPLOADED --> VALIDATING: Auto-trigger
    VALIDATING --> VALIDATED: Columns Detected
    VALIDATED --> MAPPING: User Starts Mapping
    MAPPING --> MAPPED: Mapping Complete
    MAPPED --> INGESTING: Trigger Ingest
    INGESTING --> READY: Ingest Complete
    INGESTING --> FAILED: Ingest Error

    VALIDATING --> ERROR: Validation Error
    UPLOADED --> ERROR: Invalid File
    ERROR --> [*]: Delete

    READY --> [*]: Dataset Available

    note right of PENDING
        Dataset record created
        No file uploaded yet
    end note

    note right of MAPPED
        User has mapped
        case_id, activity, timestamp
    end note

    note right of READY
        Parquet exported
        Ready for analysis
    end note
```

## Complete Upload & Ingestion Pipeline

```mermaid
flowchart TB
    subgraph "Phase 1: Upload"
        START[Client Request] --> UPLOAD_TYPE{Upload Type?}
        UPLOAD_TYPE -->|Multipart| DIRECT[Direct Upload]
        UPLOAD_TYPE -->|Large File| PRESIGNED[Presigned URL]

        DIRECT --> VALIDATE_FILE[Validate File Extension]
        PRESIGNED --> GET_URL[Generate S3 Presigned URL]
        GET_URL --> CLIENT_UPLOAD[Client Uploads to S3]
        CLIENT_UPLOAD --> CONFIRM[Confirm Upload]

        VALIDATE_FILE --> CREATE_DS[Create Dataset Record]
        CONFIRM --> CREATE_DS
        CREATE_DS --> STORE_S3[Store in S3]
        STORE_S3 --> STATUS_UPLOADED[Status: UPLOADED]
    end

    subgraph "Phase 2: Validation"
        STATUS_UPLOADED --> TRIGGER_VAL[Trigger Validation]
        TRIGGER_VAL --> READ_SAMPLE[Read Sample Rows]
        READ_SAMPLE --> DETECT_COLS[Detect Columns]
        DETECT_COLS --> INFER_TYPES[Infer Column Types]
        INFER_TYPES --> SUGGEST_MAP[Suggest Mappings]
        SUGGEST_MAP --> STORE_COLS[Store DatasetColumn Records]
        STORE_COLS --> STATUS_VALIDATED[Status: VALIDATED]
    end

    subgraph "Phase 3: Mapping"
        STATUS_VALIDATED --> GET_COLS[GET /columns]
        GET_COLS --> USER_MAPS[User Selects Mappings]
        USER_MAPS --> VALIDATE_MAP[Validate Mapping]
        VALIDATE_MAP --> STORE_MAP[Store ColumnMapping]
        STORE_MAP --> STATUS_MAPPED[Status: MAPPED]
    end

    subgraph "Phase 4: Ingestion"
        STATUS_MAPPED --> START_INGEST[POST /ingest]
        START_INGEST --> TEMPORAL_WF[Temporal Workflow]
        TEMPORAL_WF --> CHUNK_LIST[Get Chunk List]
        CHUNK_LIST --> PROCESS_CHUNKS[Process Chunks in Parallel]
        PROCESS_CHUNKS --> AGGREGATE[Aggregate Cases]
        AGGREGATE --> COMPUTE_STATS[Compute Statistics]
        COMPUTE_STATS --> EXPORT_PARQUET[Export to Parquet]
        EXPORT_PARQUET --> STATUS_READY[Status: READY]
    end
```

## Column Detection Algorithm

```mermaid
flowchart TD
    subgraph "DuckDB Column Detection"
        FILE[S3 File] --> DUCK[DuckDB Connection]
        DUCK --> SAMPLE[Read First 1000 Rows]
        SAMPLE --> SCHEMA[Extract Schema]

        SCHEMA --> LOOP[For Each Column]
        LOOP --> ANALYZE[Analyze Values]

        ANALYZE --> TYPE_CHECK{Infer Type}
        TYPE_CHECK -->|Integers| INT[INTEGER]
        TYPE_CHECK -->|Decimals| FLOAT[FLOAT]
        TYPE_CHECK -->|Dates| DATETIME[DATETIME]
        TYPE_CHECK -->|Text| STRING[STRING]

        INT --> SUGGEST
        FLOAT --> SUGGEST
        DATETIME --> SUGGEST
        STRING --> SUGGEST

        SUGGEST[Suggest PM4Py Role]

        SUGGEST --> CASE_CHECK{Contains 'case' or 'id'?}
        CASE_CHECK -->|Yes| CASE_ID[Suggest: case_id]

        SUGGEST --> ACT_CHECK{Contains 'activity' or 'event'?}
        ACT_CHECK -->|Yes| ACTIVITY[Suggest: activity]

        SUGGEST --> TIME_CHECK{Is datetime?}
        TIME_CHECK -->|Yes| TIMESTAMP[Suggest: timestamp]

        SUGGEST --> RES_CHECK{Contains 'resource' or 'user'?}
        RES_CHECK -->|Yes| RESOURCE[Suggest: resource]
    end
```

## Column Mapping Schema

```mermaid
erDiagram
    Dataset ||--o{ DatasetColumn : has
    Dataset ||--o| DatasetColumnMapping : has

    Dataset {
        uuid id PK
        string name
        string storage_key
        enum status
        json statistics
        datetime created_at
    }

    DatasetColumn {
        uuid id PK
        uuid dataset_id FK
        string name
        string inferred_type
        string[] sample_values
        float confidence
        string suggested_role
    }

    DatasetColumnMapping {
        uuid id PK
        uuid dataset_id FK
        string case_id_column
        string activity_column
        string timestamp_column
        string resource_column
        json additional_columns
    }
```

## Temporal Ingestion Workflow

```mermaid
sequenceDiagram
    participant API
    participant TemporalClient
    participant Workflow
    participant ValidateActivity
    participant ChunkActivity
    participant ProcessActivity
    participant FinalizeActivity
    participant Database

    API->>TemporalClient: start_workflow(DatasetIngestionWorkflowV2)
    TemporalClient->>Workflow: Execute

    Workflow->>ValidateActivity: validate_file(dataset_id)
    ValidateActivity->>ValidateActivity: Check format, encoding
    ValidateActivity-->>Workflow: ValidationResult

    alt Validation Failed
        Workflow->>Database: Update status = ERROR
        Workflow-->>TemporalClient: WorkflowFailed
    end

    Workflow->>ChunkActivity: get_chunk_list(dataset_id)
    ChunkActivity->>ChunkActivity: Calculate chunk boundaries
    ChunkActivity-->>Workflow: List[ChunkInfo]

    loop For Each Chunk
        Workflow->>ProcessActivity: process_chunk(chunk)
        ProcessActivity->>ProcessActivity: DuckDB parse
        ProcessActivity->>ProcessActivity: Convert to Arrow
        ProcessActivity->>Database: Insert process_events
        ProcessActivity-->>Workflow: ChunkResult
    end

    Workflow->>FinalizeActivity: finalize_ingestion(dataset_id)
    FinalizeActivity->>Database: Aggregate events to cases
    FinalizeActivity->>FinalizeActivity: Compute statistics
    FinalizeActivity->>FinalizeActivity: Export to Parquet
    FinalizeActivity->>Database: Update status = READY
    FinalizeActivity-->>Workflow: FinalizeResult

    Workflow-->>TemporalClient: WorkflowCompleted
    TemporalClient-->>API: Job Complete
```

## DuckDB Ingestion Pipeline

```mermaid
flowchart LR
    subgraph "Input"
        CSV[CSV File in S3]
        XES[XES File in S3]
    end

    subgraph "DuckDB Processing"
        CONN[Isolated Connection]
        READ[read_csv / read_parquet]
        TRANSFORM[Apply Column Mapping]
        VALIDATE[Validate Timestamps]
        CONVERT[Convert to Arrow]
    end

    subgraph "Database Insert"
        ARROW[Arrow Table]
        BATCH[Batch Insert]
        EVENTS[(process_events)]
    end

    subgraph "Post-Processing"
        AGGREGATE[Aggregate by case_id]
        CASES[(process_cases)]
        STATS[Compute Statistics]
        PARQUET[Export Parquet]
        S3[(S3 parquet_key)]
    end

    CSV --> CONN
    XES --> CONN
    CONN --> READ
    READ --> TRANSFORM
    TRANSFORM --> VALIDATE
    VALIDATE --> CONVERT
    CONVERT --> ARROW
    ARROW --> BATCH
    BATCH --> EVENTS

    EVENTS --> AGGREGATE
    AGGREGATE --> CASES
    EVENTS --> STATS
    STATS --> PARQUET
    PARQUET --> S3
```

## Chunk Processing Architecture

```mermaid
flowchart TB
    subgraph "Chunk Strategy"
        FILE[Large CSV File<br/>100MB+] --> ANALYZE[Analyze File Size]
        ANALYZE --> CALCULATE[Calculate Chunks]
        CALCULATE --> CHUNK_SIZE[Chunk Size: 10MB]
        CHUNK_SIZE --> BOUNDARIES[Calculate Byte Offsets]
    end

    subgraph "Parallel Processing"
        BOUNDARIES --> C1[Chunk 1<br/>0-10MB]
        BOUNDARIES --> C2[Chunk 2<br/>10-20MB]
        BOUNDARIES --> C3[Chunk 3<br/>20-30MB]
        BOUNDARIES --> CN[Chunk N<br/>...]

        C1 --> P1[Worker 1]
        C2 --> P2[Worker 2]
        C3 --> P3[Worker 3]
        CN --> PN[Worker N]

        P1 --> R1[Partial Result]
        P2 --> R2[Partial Result]
        P3 --> R3[Partial Result]
        PN --> RN[Partial Result]
    end

    subgraph "Aggregation"
        R1 --> MERGE[Merge Results]
        R2 --> MERGE
        R3 --> MERGE
        RN --> MERGE
        MERGE --> FINAL[Final Dataset]
    end
```

## Event Log Data Model

```mermaid
erDiagram
    ProcessCase ||--o{ ProcessEvent : contains
    Dataset ||--o{ ProcessCase : has

    Dataset {
        uuid id PK
        string name
        json statistics
        int case_count
        int event_count
        int activity_count
        string[] activities
        datetime start_time
        datetime end_time
    }

    ProcessCase {
        uuid id PK
        uuid dataset_id FK
        string case_id
        datetime start_time
        datetime end_time
        interval duration
        int event_count
        string[] trace
    }

    ProcessEvent {
        uuid id PK
        uuid case_id FK
        string activity
        datetime timestamp
        string resource
        json attributes
        int sequence_number
    }
```

## Statistics Computation

```mermaid
flowchart TD
    subgraph "Dataset Statistics"
        EVENTS[(process_events)] --> QUERY[SQL Aggregations]

        QUERY --> CASE_COUNT[COUNT DISTINCT case_id]
        QUERY --> EVENT_COUNT[COUNT *]
        QUERY --> ACTIVITY_COUNT[COUNT DISTINCT activity]
        QUERY --> TIME_RANGE[MIN/MAX timestamp]
        QUERY --> AVG_DURATION[AVG case duration]

        CASE_COUNT --> STATS[Statistics JSON]
        EVENT_COUNT --> STATS
        ACTIVITY_COUNT --> STATS
        TIME_RANGE --> STATS
        AVG_DURATION --> STATS

        STATS --> UPDATE[Update Dataset Record]
    end

    subgraph "Activity Statistics"
        EVENTS --> ACT_QUERY[Group by Activity]
        ACT_QUERY --> ACT_FREQ[Frequency]
        ACT_QUERY --> ACT_DUR[Avg Duration]
        ACT_QUERY --> ACT_FIRST[First Occurrence %]
        ACT_QUERY --> ACT_LAST[Last Occurrence %]
    end

    subgraph "Variant Statistics"
        EVENTS --> VAR_QUERY[Group by Trace]
        VAR_QUERY --> VAR_COUNT[Variant Count]
        VAR_QUERY --> VAR_FREQ[Frequency Distribution]
        VAR_QUERY --> TOP_VARIANTS[Top 10 Variants]
    end
```

## API Endpoints Flow

```mermaid
graph TD
    subgraph "Upload Endpoints"
        UP_CREATE[POST /datasets<br/>Create + Upload]
        UP_PRESIGNED[POST /datasets/presigned<br/>Get Presigned URL]
        UP_CONFIRM[POST /datasets/:id/confirm<br/>Confirm Upload]
    end

    subgraph "Mapping Endpoints"
        MAP_COLS[GET /datasets/:id/columns<br/>Get Detected Columns]
        MAP_SET[POST /datasets/:id/mapping<br/>Set Column Mapping]
        MAP_PREVIEW[GET /datasets/:id/preview<br/>Preview Data]
    end

    subgraph "Ingestion Endpoints"
        ING_START[POST /datasets/:id/ingest<br/>Start Ingestion]
        ING_STATUS[GET /jobs/:id<br/>Check Job Status]
    end

    subgraph "CRUD Endpoints"
        CRUD_LIST[GET /datasets<br/>List Datasets]
        CRUD_GET[GET /datasets/:id<br/>Get Dataset]
        CRUD_DELETE[DELETE /datasets/:id<br/>Delete Dataset]
    end

    subgraph "Export Endpoints"
        EXP_CSV[GET /datasets/:id/export/csv]
        EXP_XES[GET /datasets/:id/export/xes]
        EXP_PARQUET[GET /datasets/:id/export/parquet]
    end

    UP_CREATE --> MAP_COLS
    UP_PRESIGNED --> UP_CONFIRM
    UP_CONFIRM --> MAP_COLS
    MAP_COLS --> MAP_SET
    MAP_SET --> ING_START
    ING_START --> ING_STATUS
    ING_STATUS --> CRUD_GET
```

## Error Handling & Recovery

```mermaid
flowchart TD
    subgraph "Error Types"
        E_FILE[File Error]
        E_PARSE[Parse Error]
        E_MAP[Mapping Error]
        E_INGEST[Ingestion Error]
    end

    subgraph "Recovery Actions"
        E_FILE --> |Invalid format| R_REJECT[Reject Upload]
        E_FILE --> |Corrupt file| R_RETRY[Request Re-upload]

        E_PARSE --> |Encoding issue| R_DETECT[Try Encoding Detection]
        E_PARSE --> |Malformed rows| R_SKIP[Skip Invalid Rows]

        E_MAP --> |Missing columns| R_SUGGEST[Suggest Alternatives]
        E_MAP --> |Invalid types| R_COERCE[Attempt Type Coercion]

        E_INGEST --> |Partial failure| R_RESUME[Resume from Checkpoint]
        E_INGEST --> |Complete failure| R_CLEANUP[Cleanup + Retry]
    end

    subgraph "Status Updates"
        R_REJECT --> STATUS_ERROR[Status: ERROR]
        R_SKIP --> STATUS_WARN[Status: READY<br/>with warnings]
        R_CLEANUP --> STATUS_FAILED[Status: FAILED]
    end
```

## Key Files Reference

| Component | Path |
|-----------|------|
| Dataset Models | `src/features/process_mining/datasets/models.py` |
| Upload Router | `src/features/process_mining/datasets/api/upload.py` |
| Mapping Router | `src/features/process_mining/datasets/api/mapping.py` |
| Ingest Router | `src/features/process_mining/datasets/api/ingest.py` |
| DuckDB Parser | `src/features/process_mining/ingestion/duckdb_parser.py` |
| Ingestion Service | `src/features/process_mining/ingestion/service.py` |
| Temporal Workflow | `src/infra/temporal/workflows_v2/ingestion.py` |
| Temporal Activities | `src/infra/temporal/activities_v2/ingestion.py` |
| Object Storage | `src/infra/infrastructure/object_storage.py` |
| DuckDB Manager | `src/infra/infrastructure/duckdb.py` |
