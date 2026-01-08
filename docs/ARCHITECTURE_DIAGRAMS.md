# Architecture Diagrams

This document contains detailed Mermaid diagrams illustrating the Process Mining SaaS Platform architecture.

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Backend Layered Architecture](#2-backend-layered-architecture)
3. [Backend Domain Structure](#3-backend-domain-structure)
4. [Database Entity Relationships](#4-database-entity-relationships)
5. [API Request Flow](#5-api-request-flow)
6. [Frontend Architecture](#6-frontend-architecture)
7. [Data Ingestion Pipeline](#7-data-ingestion-pipeline)
8. [Process Discovery Flow](#8-process-discovery-flow)
9. [Authentication Flow](#9-authentication-flow)
10. [Multi-Tenancy Hierarchy](#10-multi-tenancy-hierarchy)

---

## 1. System Architecture Overview

High-level view of the entire platform stack.

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        Mobile[Mobile App]
    end

    subgraph "Frontend - React 19"
        ReactApp[React Application]
        TanStack[TanStack Query]
        Zustand[Zustand Stores]
        Cytoscape[Cytoscape Visualization]
    end

    subgraph "API Gateway"
        FastAPI[FastAPI Server<br/>Port 8001]
        Middleware[Middleware Stack<br/>Auth, CORS, Logging]
    end

    subgraph "Backend Services"
        subgraph "Domain Layer"
            Admin[Admin Domain<br/>Auth, Orgs, Workspaces]
            Datasets[Datasets Domain<br/>Upload, Ingestion]
            Analysis[Analysis Domain<br/>Process Mining]
        end

        subgraph "Application Layer"
            Commands[Commands<br/>Write Operations]
            Queries[Queries<br/>Read Operations]
            Projections[Projections<br/>Cached Views]
        end
    end

    subgraph "Infrastructure"
        Temporal[Temporal.io<br/>Workflow Engine]
        SQLite[(SQLite DB<br/>Async)]
        DuckDB[(DuckDB<br/>Analytics)]
        Redis[(Redis<br/>Cache)]
        S3[S3/MinIO<br/>Object Storage]
    end

    subgraph "External"
        PM4Py[PM4Py<br/>Mining Algorithms]
    end

    Browser --> ReactApp
    Mobile --> ReactApp
    ReactApp --> TanStack
    TanStack --> FastAPI
    ReactApp --> Zustand
    ReactApp --> Cytoscape

    FastAPI --> Middleware
    Middleware --> Admin
    Middleware --> Datasets
    Middleware --> Analysis

    Admin --> Commands
    Datasets --> Commands
    Analysis --> Commands
    Commands --> Queries
    Queries --> Projections

    Commands --> Temporal
    Temporal --> SQLite
    Temporal --> DuckDB
    Queries --> SQLite
    Queries --> Redis
    Datasets --> S3
    Analysis --> PM4Py
```

---

## 2. Backend Layered Architecture

Dependency flow enforced by import-linter.

```mermaid
graph TB
    subgraph "API Layer"
        direction LR
        MainApp[api/main.py<br/>App Factory]
        Routers[api/routers/<br/>Route Registry]
        Dependencies[api/dependencies.py<br/>DI Container]
    end

    subgraph "Features Layer"
        direction LR
        ProcessMining[features/process_mining/]
        Discovery[discovery/]
        Analytics[analytics/]
        Conformance[conformance/]
        Visualization[visualization/]
        Predictions[predictions/]
        OCPM[ocpm/]
    end

    subgraph "Application Layer"
        direction LR
        AppCommands[application/commands/]
        AppQueries[application/queries/]
        AppProjections[application/projections/]
    end

    subgraph "Infrastructure Layer"
        direction LR
        Core[infra/core/<br/>Config, Security, Exceptions]
        Infra[infra/infrastructure/<br/>DB, Cache, Storage]
        Users[infra/users/<br/>Auth, RBAC]
        TemporalInfra[infra/temporal/<br/>Workflows, Activities]
    end

    subgraph "Shared Layer"
        direction LR
        SharedDB[shared/database.py]
        SharedSchemas[shared/schemas.py]
        SharedUtils[shared/utils/]
    end

    API Layer -->|imports| Features Layer
    API Layer -->|imports| Application Layer
    API Layer -->|imports| Infrastructure Layer

    Features Layer -->|imports| Application Layer
    Features Layer -->|imports| Infrastructure Layer
    Features Layer -->|imports| Shared Layer

    Application Layer -->|imports| Infrastructure Layer
    Application Layer -->|imports| Shared Layer

    Infrastructure Layer -->|imports| Shared Layer

    style API Layer fill:#e1f5fe
    style Features Layer fill:#fff3e0
    style Application Layer fill:#f3e5f5
    style Infrastructure Layer fill:#e8f5e9
    style Shared Layer fill:#fce4ec
```

---

## 3. Backend Domain Structure

Detailed view of the process mining feature modules.

```mermaid
graph TB
    subgraph "features/process_mining/"
        subgraph "Data Management"
            Datasets[datasets/<br/>CRUD, Upload, Mapping]
            Ingestion[ingestion/<br/>DuckDB Parser, Service]
            Statistics[statistics/<br/>Case/Event Stats]
        end

        subgraph "Process Discovery"
            DiscoveryMod[discovery/<br/>Alpha, Inductive, Heuristic]
            Models[models/<br/>SQLAlchemy ORM]
            Schemas[schemas/<br/>Pydantic DTOs]
        end

        subgraph "Process Analysis"
            AnalyticsMod[analytics/<br/>Bottlenecks, Cycle Time]
            ConformanceMod[conformance/<br/>Token Replay, Alignments]
            Filtering[filtering/<br/>Event Log Filters]
        end

        subgraph "Advanced Features"
            VizMod[visualization/<br/>DFG, Petri Nets, BPMN]
            PredictionsMod[predictions/<br/>Next Activity, Time]
            OrgMod[organizational/<br/>Social Network]
            SimMod[simulation/<br/>What-If Analysis]
            OCPMMod[ocpm/<br/>Object-Centric Mining]
        end

        subgraph "Support"
            AI[ai/<br/>Chat Assistant]
            Analyses[analyses/<br/>Result Storage]
            BusinessUC[business_use_cases/<br/>P2P, O2C Templates]
        end
    end

    Datasets --> Ingestion
    Ingestion --> Models
    Models --> Schemas

    DiscoveryMod --> Models
    DiscoveryMod --> VizMod

    AnalyticsMod --> Models
    ConformanceMod --> Models

    PredictionsMod --> Models
    OrgMod --> Models
    SimMod --> Models
    OCPMMod --> Models

    AI --> Analyses
    BusinessUC --> AnalyticsMod
```

---

## 4. Database Entity Relationships

SQLAlchemy models and their relationships.

```mermaid
erDiagram
    Organization ||--o{ User : "has members"
    Organization ||--o{ Workspace : "contains"

    Workspace ||--o{ WorkspaceMember : "has"
    Workspace ||--o{ Project : "contains"

    User ||--o{ WorkspaceMember : "belongs to"

    WorkspaceMember {
        uuid id PK
        uuid user_id FK
        uuid workspace_id FK
        enum role "owner|admin|editor|viewer"
    }

    Project ||--o{ Dataset : "contains"

    Dataset ||--o{ DatasetColumn : "has"
    Dataset ||--o{ DatasetColumnMapping : "has"
    Dataset ||--o{ DatasetMetadata : "has"
    Dataset ||--o{ ProcessCase : "contains"
    Dataset ||--o{ ProcessModel : "produces"
    Dataset ||--o{ Analysis : "has"

    ProcessCase ||--o{ ProcessEvent : "contains"

    Dataset {
        uuid id PK
        uuid project_id FK
        string name
        enum status
        datetime created_at
    }

    ProcessCase {
        uuid id PK
        uuid dataset_id FK
        string case_id
        datetime start_time
        datetime end_time
    }

    ProcessEvent {
        uuid id PK
        uuid case_id FK
        string activity
        datetime timestamp
        string resource
        json attributes
    }

    ProcessModel {
        uuid id PK
        uuid dataset_id FK
        enum model_type
        json model_data
        json metrics
    }

    Analysis {
        uuid id PK
        uuid dataset_id FK
        enum analysis_type
        json parameters
        json results
    }

    ProcessVariant {
        uuid id PK
        uuid dataset_id FK
        string activity_sequence
        int case_count
        float avg_duration
    }

    Dataset ||--o{ ProcessVariant : "has"
```

---

## 5. API Request Flow

Typical request lifecycle through the backend.

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Middleware
    participant Router
    participant Service
    participant Temporal
    participant Database
    participant Cache

    Client->>FastAPI: HTTP Request
    FastAPI->>Middleware: Process Request

    Note over Middleware: Auth, CORS, Logging,<br/>Rate Limiting

    Middleware->>Middleware: Validate JWT Token
    Middleware->>Middleware: Check Permissions

    alt Unauthorized
        Middleware-->>Client: 401 Unauthorized
    end

    Middleware->>Router: Route to Handler
    Router->>Router: Validate Request Body

    alt Validation Error
        Router-->>Client: 422 Validation Error
    end

    Router->>Service: Call Business Logic

    alt Long-Running Operation
        Service->>Temporal: Start Workflow
        Temporal-->>Service: Workflow ID
        Service-->>Client: 202 Accepted + Workflow ID

        loop Workflow Execution
            Temporal->>Database: Execute Activities
            Temporal->>Cache: Update Progress
        end

        Client->>FastAPI: GET /operations/{id}/stream
        FastAPI-->>Client: SSE Progress Events
    else Quick Operation
        Service->>Cache: Check Cache
        alt Cache Hit
            Cache-->>Service: Cached Result
        else Cache Miss
            Service->>Database: Query Data
            Database-->>Service: Results
            Service->>Cache: Store in Cache
        end
        Service-->>Client: 200 OK + Response
    end
```

---

## 6. Frontend Architecture

React application structure and data flow.

```mermaid
graph TB
    subgraph "Entry Points"
        Main[main.tsx<br/>React 19 Root]
        App[App.tsx<br/>Providers, Router]
        Routes[routes.tsx<br/>Route Definitions]
    end

    subgraph "Feature Modules"
        Platform[platform/<br/>Projects, Upload]
        Explorer[explorer/<br/>Process Graph]
        AnalyticsFE[analytics/<br/>Dashboards]
        DiscoveryFE[discovery/<br/>Model Discovery]
        AIFE[ai/<br/>Predictions]
        KPI[kpi/<br/>KPI Dashboard]
        Auth[auth/<br/>Login]
        Landing[landing/<br/>Landing Page]
    end

    subgraph "Shared Layer"
        Components[shared/components/]
        Contexts[shared/context/<br/>User, Notifications]
        Hooks[shared/hooks/]
        UI[shared/ui/<br/>Error Boundaries]
        Lib[shared/lib/<br/>Logger, Telemetry]
    end

    subgraph "API Layer"
        APIHooks[api/hooks/<br/>TanStack Query]
        SDK[api/sdk.ts<br/>Service Facade]
        Client[api/client.ts<br/>Axios Instance]
        QueryClient[api/queryClient.ts]
    end

    subgraph "State Management"
        TanStackQuery[TanStack Query<br/>Server State]
        ZustandStores[Zustand Stores<br/>Client State]
    end

    subgraph "External Libraries"
        OpenAPISDK[libs/openapi-sdk/<br/>Generated Client]
        DesignSystem[libs/shared/<br/>Design System]
    end

    Main --> App
    App --> Routes
    Routes --> Platform
    Routes --> Explorer
    Routes --> AnalyticsFE
    Routes --> DiscoveryFE
    Routes --> AIFE
    Routes --> KPI
    Routes --> Auth
    Routes --> Landing

    Platform --> Components
    Explorer --> Components
    AnalyticsFE --> Components

    Components --> UI
    Components --> Hooks

    Platform --> APIHooks
    Explorer --> APIHooks
    AnalyticsFE --> APIHooks

    APIHooks --> SDK
    SDK --> OpenAPISDK
    OpenAPISDK --> Client

    APIHooks --> TanStackQuery
    Platform --> ZustandStores
    Explorer --> ZustandStores

    style Entry Points fill:#e3f2fd
    style Feature Modules fill:#fff8e1
    style Shared Layer fill:#f3e5f5
    style API Layer fill:#e8f5e9
    style State Management fill:#fce4ec
```

---

## 7. Data Ingestion Pipeline

Dataset upload and processing workflow.

```mermaid
flowchart TB
    subgraph "Upload Phase"
        Upload[User Uploads File]
        Presign[Get Presigned URL]
        S3Upload[Upload to S3/MinIO]
        Confirm[Confirm Upload]
    end

    subgraph "Detection Phase"
        DetectCols[Detect Columns<br/>Schema Inference]
        StoreSchema[Store DatasetColumn<br/>Records]
        ShowPreview[Show Column Preview<br/>to User]
    end

    subgraph "Mapping Phase"
        UserMaps[User Maps Columns]
        ValidateMap[Validate Mapping<br/>case_id, activity, timestamp]
        StoreMapping[Store DatasetColumnMapping]
    end

    subgraph "Ingestion Phase - Temporal Workflow"
        StartWorkflow[Start Ingestion Workflow]

        subgraph "Activities"
            ValidateData[Validate Data<br/>Activity]
            ParseCSV[Parse CSV<br/>DuckDB Activity]
            IngestEvents[Ingest Events<br/>Batch Insert Activity]
            ComputeStats[Compute Statistics<br/>Activity]
            Finalize[Finalize Ingestion<br/>Activity]
        end
    end

    subgraph "Ready State"
        Ready[Dataset READY]
        ProcessCases[(ProcessCase<br/>Records)]
        ProcessEvents[(ProcessEvent<br/>Records)]
        Metadata[(DatasetMetadata)]
    end

    Upload --> Presign
    Presign --> S3Upload
    S3Upload --> Confirm
    Confirm --> DetectCols

    DetectCols --> StoreSchema
    StoreSchema --> ShowPreview
    ShowPreview --> UserMaps

    UserMaps --> ValidateMap
    ValidateMap --> StoreMapping
    StoreMapping --> StartWorkflow

    StartWorkflow --> ValidateData
    ValidateData --> ParseCSV
    ParseCSV --> IngestEvents
    IngestEvents --> ComputeStats
    ComputeStats --> Finalize

    Finalize --> Ready
    Ready --> ProcessCases
    Ready --> ProcessEvents
    Ready --> Metadata

    style Upload Phase fill:#e3f2fd
    style Detection Phase fill:#fff3e0
    style Mapping Phase fill:#f3e5f5
    style Ingestion Phase - Temporal Workflow fill:#e8f5e9
    style Ready State fill:#c8e6c9
```

---

## 8. Process Discovery Flow

From dataset to process model visualization.

```mermaid
flowchart LR
    subgraph "Input"
        Dataset[(Dataset<br/>READY Status)]
        EventLog[Load Event Log<br/>PM4Py Format]
    end

    subgraph "Discovery Request"
        Request[POST /discovery/discover]
        Params[Parameters:<br/>- miner_type<br/>- filters<br/>- options]
    end

    subgraph "Temporal Workflow"
        Workflow[ProcessDiscoveryWorkflowV2]

        subgraph "Mining Algorithms"
            Alpha[Alpha Miner]
            Inductive[Inductive Miner]
            Heuristic[Heuristic Miner]
            Split[Split Miner]
        end

        Output[Petri Net<br/>im, fm]
    end

    subgraph "Post-Processing"
        Metrics[Compute Metrics<br/>Fitness, Precision]
        DFG[Generate DFG<br/>Nodes, Edges]
        Layout[Compute Layout<br/>Dagre/ELK]
    end

    subgraph "Storage"
        ProcessModel[(ProcessModel)]
        GraphCache[(GraphCache)]
    end

    subgraph "Visualization"
        CytoscapeViz[Cytoscape.js<br/>Process Graph]
        FilterPanel[Filter Panel<br/>Activities, Time]
        TokenAnimation[Token Animation<br/>Replay]
    end

    Dataset --> EventLog
    EventLog --> Request
    Request --> Params
    Params --> Workflow

    Workflow --> Alpha
    Workflow --> Inductive
    Workflow --> Heuristic
    Workflow --> Split

    Alpha --> Output
    Inductive --> Output
    Heuristic --> Output
    Split --> Output

    Output --> Metrics
    Output --> DFG
    DFG --> Layout

    Metrics --> ProcessModel
    Layout --> GraphCache

    GraphCache --> CytoscapeViz
    CytoscapeViz --> FilterPanel
    CytoscapeViz --> TokenAnimation
```

---

## 9. Authentication Flow

JWT-based authentication with refresh tokens.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant AuthRouter
    participant Security
    participant Database
    participant Redis

    Note over User,Redis: Login Flow

    User->>Frontend: Enter Credentials
    Frontend->>AuthRouter: POST /auth/login
    AuthRouter->>Database: Find User by Email
    Database-->>AuthRouter: User Record

    AuthRouter->>Security: Verify Password Hash

    alt Invalid Credentials
        AuthRouter-->>Frontend: 401 Unauthorized
        Frontend-->>User: Show Error
    end

    AuthRouter->>Security: Generate Access Token<br/>(15 min expiry)
    AuthRouter->>Security: Generate Refresh Token<br/>(7 day expiry)
    AuthRouter->>Redis: Store Refresh Token

    AuthRouter-->>Frontend: Tokens + User Info
    Frontend->>Frontend: Store Tokens<br/>(Memory/LocalStorage)
    Frontend-->>User: Redirect to Dashboard

    Note over User,Redis: Authenticated Request

    User->>Frontend: Navigate to Page
    Frontend->>AuthRouter: GET /api/v1/datasets<br/>Authorization: Bearer {token}
    AuthRouter->>Security: Validate JWT

    alt Token Expired
        AuthRouter-->>Frontend: 401 Token Expired
        Frontend->>AuthRouter: POST /auth/refresh<br/>{refresh_token}
        AuthRouter->>Redis: Validate Refresh Token
        AuthRouter->>Security: Generate New Access Token
        AuthRouter-->>Frontend: New Access Token
        Frontend->>AuthRouter: Retry Original Request
    end

    AuthRouter->>Database: Execute Query
    Database-->>AuthRouter: Results
    AuthRouter-->>Frontend: 200 OK + Data
    Frontend-->>User: Display Data

    Note over User,Redis: Logout Flow

    User->>Frontend: Click Logout
    Frontend->>AuthRouter: POST /auth/logout
    AuthRouter->>Redis: Invalidate Refresh Token
    AuthRouter-->>Frontend: 200 OK
    Frontend->>Frontend: Clear Stored Tokens
    Frontend-->>User: Redirect to Login
```

---

## 10. Multi-Tenancy Hierarchy

Organization, Workspace, and Project relationships with RBAC.

```mermaid
graph TB
    subgraph "Organization Level"
        Org[Organization<br/>mvp-org-001]
        OrgOwner[Organization Owner<br/>Full Control]
    end

    subgraph "Workspace Level"
        WS1[Workspace A<br/>Engineering Team]
        WS2[Workspace B<br/>Analytics Team]

        subgraph "Workspace A Members"
            WSOwner1[Owner<br/>Full workspace control]
            WSAdmin1[Admin<br/>Manage members, projects]
            WSEditor1[Editor<br/>Create/edit datasets]
            WSViewer1[Viewer<br/>Read-only access]
        end
    end

    subgraph "Project Level"
        Proj1[Project 1<br/>Q4 Analysis]
        Proj2[Project 2<br/>Customer Journey]
        Proj3[Project 3<br/>Supply Chain]
    end

    subgraph "Dataset Level"
        DS1[Dataset 1<br/>Sales Events]
        DS2[Dataset 2<br/>Order Events]
        DS3[Dataset 3<br/>Delivery Events]
    end

    subgraph "Analysis Level"
        An1[Analysis 1<br/>Bottleneck Detection]
        An2[Analysis 2<br/>Conformance Check]
        Model1[Process Model 1<br/>Inductive Miner]
    end

    Org --> OrgOwner
    Org --> WS1
    Org --> WS2

    WS1 --> WSOwner1
    WS1 --> WSAdmin1
    WS1 --> WSEditor1
    WS1 --> WSViewer1

    WS1 --> Proj1
    WS1 --> Proj2
    WS2 --> Proj3

    Proj1 --> DS1
    Proj1 --> DS2
    Proj3 --> DS3

    DS1 --> An1
    DS1 --> Model1
    DS2 --> An2

    style Organization Level fill:#ffcdd2
    style Workspace Level fill:#fff9c4
    style Project Level fill:#c8e6c9
    style Dataset Level fill:#bbdefb
    style Analysis Level fill:#e1bee7
```

---

## 11. Temporal Workflow Architecture

Workflow and activity organization for async operations.

```mermaid
graph TB
    subgraph "Workflow Starters"
        APIRoutes[API Route Handlers]
        Scheduler[Scheduled Tasks]
    end

    subgraph "Temporal Server"
        Server[Temporal Server<br/>Workflow Orchestration]
        TaskQueues[Task Queues]
    end

    subgraph "Workflows V2"
        IngestionWF[DatasetIngestionWorkflowV2<br/>Parse & Store Events]
        ValidationWF[DatasetValidationWorkflowV2<br/>Schema Detection]
        DiscoveryWF[ProcessDiscoveryWorkflowV2<br/>Mining Algorithms]
        ConformanceWF[ConformanceCheckWorkflowV2<br/>Token Replay]
    end

    subgraph "Activities V2"
        subgraph "Ingestion Activities"
            ValidateAct[validate_dataset]
            ParseAct[parse_csv_duckdb]
            IngestAct[ingest_events_batch]
            StatsAct[compute_statistics]
            FinalizeAct[finalize_ingestion]
        end

        subgraph "Analysis Activities"
            LoadLogAct[load_event_log]
            MineAct[execute_mining]
            MetricsAct[compute_metrics]
            StoreAct[store_results]
        end
    end

    subgraph "Workers"
        IngestionWorker[Ingestion Worker<br/>ingestion-queue]
        AnalysisWorker[Analysis Worker<br/>analysis-queue]
    end

    subgraph "Progress Tracking"
        QueryHandler[Workflow Query Handler]
        SSEEndpoint[SSE Endpoint<br/>/operations/{id}/stream]
        Frontend[Frontend<br/>Real-time Updates]
    end

    APIRoutes --> Server
    Scheduler --> Server
    Server --> TaskQueues

    TaskQueues --> IngestionWF
    TaskQueues --> ValidationWF
    TaskQueues --> DiscoveryWF
    TaskQueues --> ConformanceWF

    IngestionWF --> ValidateAct
    IngestionWF --> ParseAct
    IngestionWF --> IngestAct
    IngestionWF --> StatsAct
    IngestionWF --> FinalizeAct

    DiscoveryWF --> LoadLogAct
    DiscoveryWF --> MineAct
    DiscoveryWF --> MetricsAct
    DiscoveryWF --> StoreAct

    IngestionWorker --> Ingestion Activities
    AnalysisWorker --> Analysis Activities

    IngestionWF --> QueryHandler
    DiscoveryWF --> QueryHandler
    QueryHandler --> SSEEndpoint
    SSEEndpoint --> Frontend
```

---

## 12. Frontend State Management

TanStack Query and Zustand integration.

```mermaid
graph TB
    subgraph "Components"
        Page[Page Component]
        Feature[Feature Component]
        UI[UI Component]
    end

    subgraph "TanStack Query - Server State"
        QueryClient[QueryClient]

        subgraph "Queries"
            UseDatasets[useDatasets()]
            UseAnalytics[useAnalytics()]
            UseDiscovery[useDiscovery()]
        end

        subgraph "Mutations"
            UseUpload[useUploadDataset()]
            UseDiscover[useDiscoverModel()]
            UseDelete[useDeleteDataset()]
        end

        Cache[(Query Cache)]
    end

    subgraph "Zustand - Client State"
        subgraph "Stores"
            UserStore[userStore<br/>Auth State]
            FilterStore[filterStore<br/>Filter State]
            UIStore[uiStore<br/>UI Preferences]
            WizardStore[wizardStore<br/>Upload Wizard]
            SelectionStore[selectionStore<br/>Selected Items]
        end
    end

    subgraph "React Context"
        UserContext[UserContext<br/>Current User]
        NotifContext[NotificationContext<br/>Toasts]
        HealthContext[BackendHealthContext<br/>System Status]
    end

    subgraph "API Layer"
        SDK[SDK Facade]
        Axios[Axios Client]
        Backend[Backend API]
    end

    Page --> UseDatasets
    Page --> UseAnalytics
    Feature --> UseDiscovery
    Feature --> UseUpload

    UseDatasets --> QueryClient
    UseAnalytics --> QueryClient
    UseDiscovery --> QueryClient
    UseUpload --> QueryClient
    UseDiscover --> QueryClient
    UseDelete --> QueryClient

    QueryClient --> Cache
    QueryClient --> SDK
    SDK --> Axios
    Axios --> Backend

    Page --> FilterStore
    Page --> UIStore
    Feature --> WizardStore
    UI --> SelectionStore

    Page --> UserContext
    Page --> NotifContext
    Feature --> HealthContext

    UserContext --> UserStore

    style Components fill:#e3f2fd
    style TanStack Query - Server State fill:#c8e6c9
    style Zustand - Client State fill:#fff9c4
    style React Context fill:#f3e5f5
```

---

## 13. Error Handling Architecture

Multi-layer error handling strategy.

```mermaid
flowchart TB
    subgraph "Frontend Error Handling"
        GlobalEB[GlobalErrorBoundary<br/>App Level]
        FeatureEB[FeatureErrorBoundary<br/>Route Level]
        ComponentEB[ComponentErrorBoundary<br/>Component Level]

        QueryError[TanStack Query<br/>onError Handlers]
        AxiosInterceptor[Axios Response<br/>Interceptor]
    end

    subgraph "Backend Error Handling"
        Middleware[Exception Middleware]

        subgraph "Exception Types"
            AppException[AppException<br/>Base Class]
            ValidationError[ValidationError<br/>422]
            AuthError[AuthenticationError<br/>401]
            PermError[PermissionError<br/>403]
            NotFound[NotFoundError<br/>404]
            RateLimit[RateLimitError<br/>429]
        end

        ErrorCodes[ErrorCode Enum<br/>Typed Codes]
        RFC7807[RFC 7807<br/>Problem Details]
    end

    subgraph "Error Response Format"
        Response["{
            type: 'error_code',
            title: 'Error Title',
            status: 400,
            detail: 'Description',
            instance: '/path',
            errors: []
        }"]
    end

    subgraph "User Feedback"
        Toast[Toast Notification]
        ErrorPage[Error Page<br/>Retry Button]
        FormErrors[Form Field Errors]
    end

    GlobalEB --> FeatureEB
    FeatureEB --> ComponentEB

    QueryError --> AxiosInterceptor
    AxiosInterceptor --> Middleware

    Middleware --> AppException
    AppException --> ValidationError
    AppException --> AuthError
    AppException --> PermError
    AppException --> NotFound
    AppException --> RateLimit

    AppException --> ErrorCodes
    ErrorCodes --> RFC7807
    RFC7807 --> Response

    Response --> AxiosInterceptor
    AxiosInterceptor --> Toast
    AxiosInterceptor --> FormErrors

    GlobalEB --> ErrorPage
    FeatureEB --> ErrorPage
    ComponentEB --> ErrorPage
```

---

## 14. Process Mining Algorithm Pipeline

Available algorithms and their relationships.

```mermaid
graph LR
    subgraph "Input"
        EventLog[Event Log<br/>Cases, Events]
    end

    subgraph "Discovery Algorithms"
        Alpha[Alpha Miner<br/>Simple, Fast]
        AlphaPlus[Alpha+ Miner<br/>Loops Support]
        Inductive[Inductive Miner<br/>Sound Models]
        InductiveIMD[Inductive IMD<br/>Directly-Follows]
        InductiveIMF[Inductive IMF<br/>Infrequent]
        Heuristic[Heuristic Miner<br/>Noise Tolerant]
        Split[Split Miner<br/>Balanced]
    end

    subgraph "Model Types"
        PetriNet[Petri Net<br/>net, im, fm]
        ProcessTree[Process Tree<br/>Hierarchical]
        BPMN[BPMN Model<br/>Business Notation]
        DFG[Directly-Follows Graph<br/>Simple View]
    end

    subgraph "Conformance Checking"
        TokenReplay[Token Replay<br/>Fast, Approx]
        Alignments[Alignments<br/>Optimal, Slow]
        Footprints[Footprints<br/>Pattern Match]
    end

    subgraph "Analytics"
        Bottlenecks[Bottleneck<br/>Detection]
        CycleTime[Cycle Time<br/>Analysis]
        Throughput[Throughput<br/>Analysis]
        Rework[Rework<br/>Detection]
        WaitTime[Wait Time<br/>Analysis]
    end

    subgraph "Advanced"
        SNA[Social Network<br/>Analysis]
        Predictions[Predictions<br/>Next Activity, Time]
        Simulation[What-If<br/>Simulation]
        OCEL[Object-Centric<br/>OCEL 2.0]
    end

    EventLog --> Alpha
    EventLog --> AlphaPlus
    EventLog --> Inductive
    EventLog --> InductiveIMD
    EventLog --> InductiveIMF
    EventLog --> Heuristic
    EventLog --> Split

    Alpha --> PetriNet
    AlphaPlus --> PetriNet
    Inductive --> ProcessTree
    ProcessTree --> PetriNet
    Heuristic --> PetriNet
    Split --> PetriNet

    PetriNet --> BPMN
    PetriNet --> DFG

    PetriNet --> TokenReplay
    PetriNet --> Alignments
    DFG --> Footprints

    EventLog --> Bottlenecks
    EventLog --> CycleTime
    EventLog --> Throughput
    EventLog --> Rework
    EventLog --> WaitTime

    EventLog --> SNA
    EventLog --> Predictions
    PetriNet --> Simulation
    EventLog --> OCEL
```

---

## 15. Deployment Architecture

Production deployment topology.

```mermaid
graph TB
    subgraph "CDN / Edge"
        CDN[CDN<br/>Static Assets]
    end

    subgraph "Load Balancer"
        LB[Load Balancer<br/>HTTPS Termination]
    end

    subgraph "Application Tier"
        subgraph "Frontend Pods"
            FE1[React App<br/>Nginx]
            FE2[React App<br/>Nginx]
        end

        subgraph "Backend Pods"
            BE1[FastAPI<br/>Uvicorn]
            BE2[FastAPI<br/>Uvicorn]
            BE3[FastAPI<br/>Uvicorn]
        end
    end

    subgraph "Worker Tier"
        subgraph "Temporal Workers"
            TW1[Ingestion Worker]
            TW2[Analysis Worker]
        end
    end

    subgraph "Orchestration"
        TemporalServer[Temporal Server<br/>Workflow Engine]
    end

    subgraph "Data Tier"
        subgraph "Databases"
            SQLite[(SQLite<br/>Primary DB)]
            DuckDB[(DuckDB<br/>Analytics)]
        end

        subgraph "Cache"
            Redis[(Redis<br/>Cache + Sessions)]
        end

        subgraph "Storage"
            S3[(S3/MinIO<br/>Object Storage)]
        end
    end

    subgraph "Observability"
        Logs[Log Aggregation]
        Metrics[Metrics]
        Traces[Distributed Tracing]
    end

    CDN --> LB
    LB --> FE1
    LB --> FE2
    LB --> BE1
    LB --> BE2
    LB --> BE3

    BE1 --> TemporalServer
    BE2 --> TemporalServer
    BE3 --> TemporalServer

    TemporalServer --> TW1
    TemporalServer --> TW2

    BE1 --> SQLite
    BE2 --> SQLite
    BE3 --> SQLite

    TW1 --> DuckDB
    TW2 --> DuckDB

    BE1 --> Redis
    BE2 --> Redis
    BE3 --> Redis

    BE1 --> S3
    TW1 --> S3
    TW2 --> S3

    BE1 --> Logs
    BE1 --> Metrics
    BE1 --> Traces
```

---

## Summary

These diagrams provide a comprehensive view of the Process Mining SaaS Platform:

| Diagram | Purpose |
|---------|---------|
| System Architecture | High-level component overview |
| Backend Layers | Dependency flow and import rules |
| Domain Structure | Process mining feature organization |
| Database ERD | Entity relationships |
| API Request Flow | Request lifecycle |
| Frontend Architecture | React app structure |
| Data Ingestion | Upload to ready pipeline |
| Process Discovery | Mining algorithm flow |
| Authentication | JWT token flow |
| Multi-Tenancy | Organization hierarchy |
| Temporal Workflows | Async operation architecture |
| State Management | Frontend data flow |
| Error Handling | Multi-layer error strategy |
| Algorithm Pipeline | Available mining algorithms |
| Deployment | Production topology |
