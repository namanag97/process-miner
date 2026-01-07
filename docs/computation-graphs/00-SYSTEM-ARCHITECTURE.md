# System Architecture - Computation Graph

## High-Level System Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[React SPA<br/>Port 4200]
        SDK[OpenAPI SDK]
    end

    subgraph "API Gateway"
        API[FastAPI<br/>Port 8001]
        MW[Middleware Layer]
        AUTH[JWT Auth]
    end

    subgraph "Application Layer - CQRS"
        CB[Command Bus]
        QB[Query Bus]
        EH[Event Handlers]
    end

    subgraph "Domain Layer"
        ADMIN[Admin Domain]
        DS[Datasets Domain]
        AN[Analysis Domain]
    end

    subgraph "Infrastructure Layer"
        DB[(SQLite/PostgreSQL)]
        DUCK[(DuckDB OLAP)]
        S3[(S3/MinIO Storage)]
        REDIS[(Redis Cache)]
        TEMP[Temporal.io]
    end

    FE --> SDK
    SDK --> API
    API --> MW
    MW --> AUTH
    AUTH --> CB
    AUTH --> QB

    CB --> EH
    CB --> ADMIN
    CB --> DS
    CB --> AN

    QB --> ADMIN
    QB --> DS
    QB --> AN

    ADMIN --> DB
    DS --> DB
    DS --> DUCK
    DS --> S3
    AN --> DUCK
    AN --> S3

    EH --> REDIS
    CB --> TEMP
    TEMP --> DS
    TEMP --> AN
```

## Request Flow Architecture

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Middleware
    participant JWTAuth
    participant CommandBus
    participant Handler
    participant Database
    participant EventStore

    Client->>FastAPI: HTTP Request
    FastAPI->>Middleware: Process Request
    Middleware->>JWTAuth: Validate Token
    JWTAuth-->>Middleware: User Context
    Middleware->>FastAPI: Authenticated Request

    alt Write Operation
        FastAPI->>CommandBus: Dispatch Command
        CommandBus->>Handler: Execute
        Handler->>Database: Write Data
        Handler->>EventStore: Emit Event
        EventStore-->>Handler: Event ID
        Handler-->>CommandBus: Result
        CommandBus-->>FastAPI: CommandSuccess
    else Read Operation
        FastAPI->>CommandBus: Dispatch Query
        CommandBus->>Handler: Execute
        Handler->>Database: Read Data
        Handler-->>CommandBus: Result
        CommandBus-->>FastAPI: QueryResult
    end

    FastAPI-->>Client: HTTP Response
```

## Dependency Graph

```mermaid
graph TB
    subgraph "Strict Dependency Rules"
        direction TB

        subgraph "API Layer"
            ROUTERS[API Routers]
            DEPS[Dependencies]
            SCHEMAS_API[Request/Response Schemas]
        end

        subgraph "Application Layer"
            COMMANDS[Commands]
            QUERIES[Queries]
            HANDLERS[Handlers]
            PROJECTIONS[Projections]
        end

        subgraph "Domain Layer"
            SERVICES[Domain Services]
            MODELS[Domain Models]
            SCHEMAS_DOM[Domain Schemas]
        end

        subgraph "Infrastructure Layer"
            DATABASE[Database]
            STORAGE[Object Storage]
            CACHE[Cache]
            TEMPORAL[Temporal Workflows]
        end
    end

    ROUTERS --> DEPS
    ROUTERS --> SCHEMAS_API
    ROUTERS --> COMMANDS
    ROUTERS --> QUERIES

    COMMANDS --> HANDLERS
    QUERIES --> HANDLERS
    HANDLERS --> SERVICES
    HANDLERS --> PROJECTIONS

    SERVICES --> MODELS
    SERVICES --> SCHEMAS_DOM

    PROJECTIONS --> DATABASE
    PROJECTIONS --> CACHE

    HANDLERS --> DATABASE
    HANDLERS --> STORAGE
    HANDLERS --> TEMPORAL

    %% Forbidden dependencies (marked with X)
    SERVICES -.-x ROUTERS
    MODELS -.-x DATABASE
    INFRASTRUCTURE -.-x DOMAIN
```

## Multi-Tenant Authorization Hierarchy

```mermaid
graph TB
    subgraph "Tenant Hierarchy"
        ORG[Organization]
        WS[Workspace]
        WM[Workspace Members]
        PROJ[Project]
        DS[Dataset]
        MODEL[Process Model]
        ANALYSIS[Analysis]
    end

    subgraph "RBAC Roles"
        OWNER[Owner]
        ADMIN[Admin]
        EDITOR[Editor]
        VIEWER[Viewer]
    end

    ORG --> WS
    WS --> WM
    WS --> PROJ
    PROJ --> DS
    DS --> MODEL
    DS --> ANALYSIS

    WM --> OWNER
    WM --> ADMIN
    WM --> EDITOR
    WM --> VIEWER

    OWNER -.->|Full Access + Delete| ORG
    ADMIN -.->|Full Access| WS
    EDITOR -.->|Read/Write| PROJ
    VIEWER -.->|Read Only| DS
```

## Data Flow Overview

```mermaid
flowchart LR
    subgraph Input
        CSV[CSV File]
        XES[XES File]
    end

    subgraph Processing
        UPLOAD[Upload Service]
        DETECT[Column Detection]
        MAP[Column Mapping]
        INGEST[DuckDB Ingestion]
    end

    subgraph Storage
        S3[(S3 Raw Files)]
        DB[(SQLite Metadata)]
        PARQUET[(Parquet Analytics)]
    end

    subgraph Analytics
        DISCOVERY[Discovery Algorithms]
        CONFORM[Conformance Checking]
        PERF[Performance Analytics]
        PRED[ML Predictions]
    end

    subgraph Output
        DFG[DFG Visualization]
        PETRI[Petri Net]
        METRICS[KPI Metrics]
        INSIGHTS[AI Insights]
    end

    CSV --> UPLOAD
    XES --> UPLOAD
    UPLOAD --> S3
    UPLOAD --> DETECT
    DETECT --> MAP
    MAP --> INGEST
    INGEST --> DB
    INGEST --> PARQUET

    PARQUET --> DISCOVERY
    PARQUET --> CONFORM
    PARQUET --> PERF
    PARQUET --> PRED

    DISCOVERY --> DFG
    DISCOVERY --> PETRI
    PERF --> METRICS
    PRED --> INSIGHTS
```

## Technology Stack Mapping

```mermaid
graph LR
    subgraph "Frontend Stack"
        REACT[React 19]
        ROUTER[React Router v6]
        QUERY[TanStack Query]
        ANTD[Ant Design]
        CYTO[Cytoscape.js]
    end

    subgraph "Backend Stack"
        FASTAPI[FastAPI]
        PYDANTIC[Pydantic]
        SQLA[SQLAlchemy Async]
        PM4PY[PM4Py]
    end

    subgraph "Data Stack"
        SQLITE[SQLite/PostgreSQL]
        DUCKDB[DuckDB]
        MINIO[MinIO/S3]
        REDIS_S[Redis]
    end

    subgraph "Orchestration"
        TEMPORAL_S[Temporal.io]
        CELERY[Celery]
    end

    REACT --> ROUTER
    REACT --> QUERY
    REACT --> ANTD
    REACT --> CYTO

    QUERY --> FASTAPI

    FASTAPI --> PYDANTIC
    FASTAPI --> SQLA
    FASTAPI --> PM4PY

    SQLA --> SQLITE
    PM4PY --> DUCKDB
    FASTAPI --> MINIO
    FASTAPI --> REDIS_S

    FASTAPI --> TEMPORAL_S
    FASTAPI --> CELERY
```
