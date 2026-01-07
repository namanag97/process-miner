# Frontend Features - Computation Graph

## Frontend Architecture Overview

```mermaid
graph TB
    subgraph "Application Shell"
        APP[App.tsx]
        ROUTER[React Router]
        PROVIDERS[Context Providers]
    end

    subgraph "Context Providers"
        USER_CTX[UserContext]
        NOTIF_CTX[NotificationContext]
        HEALTH_CTX[BackendHealthContext]
        QUERY_CTX[QueryClientProvider]
    end

    subgraph "Navigation"
        SIDEBAR[AppShell Sidebar]
        NAV_ITEMS[Navigation Items]
        DATASET_NAV[Dataset-Scoped Nav]
    end

    subgraph "Feature Modules"
        PLATFORM[Platform]
        EXPLORER[Explorer]
        DISCOVERY[Discovery]
        ANALYTICS[Analytics]
        KPI[KPI Dashboard]
        AI[AI Assistant]
    end

    APP --> PROVIDERS
    PROVIDERS --> USER_CTX
    PROVIDERS --> NOTIF_CTX
    PROVIDERS --> HEALTH_CTX
    PROVIDERS --> QUERY_CTX

    APP --> ROUTER
    ROUTER --> SIDEBAR
    SIDEBAR --> NAV_ITEMS
    SIDEBAR --> DATASET_NAV

    ROUTER --> PLATFORM
    ROUTER --> EXPLORER
    ROUTER --> DISCOVERY
    ROUTER --> ANALYTICS
    ROUTER --> KPI
    ROUTER --> AI
```

## Routing Structure

```mermaid
graph TD
    subgraph "Root Routes"
        LANDING[/ Landing Page]
        WORKSPACE[/workspace]
    end

    subgraph "Workspace Routes"
        PROJECTS[/workspace Projects List]
        PROJECT[/workspace/:projectId]
        UPLOAD[/workspace/:projectId/upload]
    end

    subgraph "Dataset-Scoped Routes"
        EXPLORE_DS[/workspace/:projectId/data/:datasetId/explorer]
        DISCOVER_DS[/workspace/:projectId/data/:datasetId/discovery]
        KPI_DS[/workspace/:projectId/data/:datasetId/kpi]
        QUESTIONS[/workspace/:projectId/data/:datasetId/questions]
    end

    subgraph "Standalone Routes"
        EXPLORE_STAND[/explore]
        ANALYTICS_STAND[/analytics]
        AI_STAND[/ai]
        SETTINGS[/settings/*]
    end

    LANDING --> WORKSPACE
    WORKSPACE --> PROJECTS
    PROJECTS --> PROJECT
    PROJECT --> UPLOAD
    PROJECT --> EXPLORE_DS
    PROJECT --> DISCOVER_DS
    PROJECT --> KPI_DS
    PROJECT --> QUESTIONS

    WORKSPACE --> EXPLORE_STAND
    WORKSPACE --> ANALYTICS_STAND
    WORKSPACE --> AI_STAND
    WORKSPACE --> SETTINGS
```

## Platform Feature - Projects

```mermaid
flowchart TB
    subgraph "Projects List Page"
        PL_FETCH[useProjectList hook]
        PL_TABLE[DataTable component]
        PL_SEARCH[Search filter]
        PL_CREATE[Create Project button]
    end

    subgraph "Project Detail Page"
        PD_FETCH[useProjectDetail hook]
        PD_INFO[Project info display]
        PD_SOURCES[Data sources list]
        PD_ACTIONS[Quick actions]
    end

    subgraph "API Calls"
        API_LIST[GET /projects]
        API_GET[GET /projects/:id]
        API_CREATE[POST /projects]
        API_UPDATE[PATCH /projects/:id]
        API_DELETE[DELETE /projects/:id]
    end

    PL_FETCH --> API_LIST
    PL_TABLE --> PL_SEARCH
    PL_CREATE --> API_CREATE

    PD_FETCH --> API_GET
    PD_ACTIONS --> API_UPDATE
    PD_ACTIONS --> API_DELETE
```

## Upload Wizard Flow

```mermaid
stateDiagram-v2
    [*] --> UploadStep: Start Wizard
    UploadStep --> ConfigureStep: File Uploaded
    ConfigureStep --> MapDataStep: Preview Shown
    MapDataStep --> FinalizeStep: Mapping Set
    FinalizeStep --> [*]: Dataset Ready

    state UploadStep {
        [*] --> DragDrop
        DragDrop --> Uploading: Drop File
        Uploading --> Complete: Upload Success
        Uploading --> Error: Upload Failed
        Error --> DragDrop: Retry
    }

    state ConfigureStep {
        [*] --> LoadPreview
        LoadPreview --> ShowColumns
        ShowColumns --> AutoMap
    }

    state MapDataStep {
        [*] --> ShowMapping
        ShowMapping --> SelectCase
        SelectCase --> SelectActivity
        SelectActivity --> SelectTimestamp
        SelectTimestamp --> SelectResource
        SelectResource --> ValidateMapping
    }

    state FinalizeStep {
        [*] --> StartJob
        StartJob --> Polling
        Polling --> Processing
        Processing --> Complete
        Processing --> Failed
    }
```

## Upload Wizard State Management

```mermaid
flowchart TB
    subgraph "Wizard State"
        STATE[useUploadWizard Hook]
        STEP[currentStep: 1-4]
        DS_ID[datasetId: string]
        FILENAME[filename: string]
        PREVIEW[preview: DataPreview]
        MAPPING[mapping: ColumnMapping]
        JOB_ID[jobId: string]
    end

    subgraph "Actions"
        GO_STEP[goToStep(n)]
        SET_UPLOAD[setUploadResult()]
        SET_MAP[setMapping()]
        START[startAnalysis()]
    end

    subgraph "Resume Logic"
        CHECK_URL[Check URL params]
        GET_DS[Fetch existing dataset]
        RESUME_STEP[Determine resume step]
    end

    STATE --> STEP
    STATE --> DS_ID
    STATE --> FILENAME
    STATE --> PREVIEW
    STATE --> MAPPING
    STATE --> JOB_ID

    GO_STEP --> STEP
    SET_UPLOAD --> DS_ID
    SET_UPLOAD --> FILENAME
    SET_MAP --> MAPPING
    START --> JOB_ID

    CHECK_URL --> GET_DS
    GET_DS --> RESUME_STEP
    RESUME_STEP --> STEP
```

## Explorer Feature

```mermaid
flowchart TB
    subgraph "Explorer Page"
        PAGE[ExplorerDetailPage]
        KPI_BAR[ProcessKPIBar]
        CANVAS[CytoscapeCanvas]
        PANELS[Side Panels]
    end

    subgraph "Data Hooks"
        USE_DATA[useExplorerData]
        USE_FILTERS[useExplorerFilters]
        USE_GRAPH[useProcessGraph]
        USE_INTERACT[useGraphInteractions]
    end

    subgraph "Panels"
        VAR_PANEL[VariantPanel]
        ACT_PANEL[ActivityDetailsPanel]
        EDGE_PANEL[EdgeDetailsPanel]
        FILTER_PANEL[FilterPanel]
    end

    subgraph "Graph State"
        NODES[nodes array]
        EDGES[edges array]
        SELECTED[selectedNode/Edge]
        ZOOM[zoom level]
        PAN[pan position]
    end

    PAGE --> KPI_BAR
    PAGE --> CANVAS
    PAGE --> PANELS

    USE_DATA --> NODES
    USE_DATA --> EDGES
    USE_FILTERS --> FILTER_PANEL
    USE_GRAPH --> CANVAS
    USE_INTERACT --> SELECTED

    PANELS --> VAR_PANEL
    PANELS --> ACT_PANEL
    PANELS --> EDGE_PANEL
    PANELS --> FILTER_PANEL

    SELECTED --> ACT_PANEL
    SELECTED --> EDGE_PANEL
```

## Explorer Data Flow

```mermaid
sequenceDiagram
    participant User
    participant ExplorerPage
    participant useExplorerData
    participant SDK
    participant Backend

    ExplorerPage->>useExplorerData: Initialize with datasetId
    useExplorerData->>SDK: discovery.getExplorerData()
    SDK->>Backend: GET /explorer/:datasetId

    Backend-->>SDK: {nodes, edges, variants, stats}
    SDK-->>useExplorerData: ExplorerData
    useExplorerData-->>ExplorerPage: Data ready

    ExplorerPage->>ExplorerPage: Render CytoscapeCanvas

    User->>ExplorerPage: Click on node
    ExplorerPage->>ExplorerPage: setSelectedNode()
    ExplorerPage->>ExplorerPage: Show ActivityDetailsPanel

    User->>ExplorerPage: Apply filter
    ExplorerPage->>useExplorerData: Refetch with filters
    useExplorerData->>SDK: discovery.getExplorerData(filters)
    SDK->>Backend: GET /explorer/:datasetId?filters=...
    Backend-->>SDK: Filtered data
    SDK-->>useExplorerData: Updated ExplorerData
    useExplorerData-->>ExplorerPage: Re-render graph
```

## Filter Panel Architecture

```mermaid
flowchart TB
    subgraph "Filter Types"
        ACT_FILT[Activity Filter]
        SEQ_FILT[Sequence Filter]
        DUR_FILT[Duration Filter]
        TIME_FILT[Time Range Filter]
        RES_FILT[Resource Filter]
        REW_FILT[Rework Filter]
    end

    subgraph "Filter State"
        URL_STATE[URL Query Params]
        LOCAL_STATE[Local State]
        APPLIED[Applied Filters]
    end

    subgraph "Bidirectional Sync"
        TO_URL[State → URL]
        FROM_URL[URL → State]
    end

    ACT_FILT --> LOCAL_STATE
    SEQ_FILT --> LOCAL_STATE
    DUR_FILT --> LOCAL_STATE
    TIME_FILT --> LOCAL_STATE
    RES_FILT --> LOCAL_STATE
    REW_FILT --> LOCAL_STATE

    LOCAL_STATE --> TO_URL
    TO_URL --> URL_STATE
    URL_STATE --> FROM_URL
    FROM_URL --> APPLIED
```

## Discovery Feature

```mermaid
flowchart TB
    subgraph "Discovery Page"
        PAGE_D[DiscoveryPage]
        MODEL_LIST[ModelList]
        JOB_PANEL[JobStatusPanel]
        VIEWER[GraphViewer/JSONViewer]
    end

    subgraph "Algorithm Selection"
        MODAL[AnalysisModeSelector]
        ALGO_SELECT[Algorithm Dropdown]
        PARAMS[Parameter Config]
        SUBMIT[Submit Button]
    end

    subgraph "Job Tracking"
        CREATE_JOB[Create Job]
        POLL_JOB[useJobStream]
        STATUS[Job Status Display]
    end

    subgraph "Visualization"
        SELECT_MODEL[Select Model]
        FETCH_VIZ[useModelVisualization]
        RENDER[Render Graph/JSON]
    end

    PAGE_D --> MODEL_LIST
    PAGE_D --> JOB_PANEL
    PAGE_D --> VIEWER

    MODEL_LIST --> MODAL
    MODAL --> ALGO_SELECT
    MODAL --> PARAMS
    MODAL --> SUBMIT

    SUBMIT --> CREATE_JOB
    CREATE_JOB --> POLL_JOB
    POLL_JOB --> STATUS
    STATUS --> JOB_PANEL

    MODEL_LIST --> SELECT_MODEL
    SELECT_MODEL --> FETCH_VIZ
    FETCH_VIZ --> RENDER
    RENDER --> VIEWER
```

## Discovery Job Flow

```mermaid
sequenceDiagram
    participant User
    participant DiscoveryPage
    participant JobStream
    participant SDK
    participant Backend
    participant Temporal

    User->>DiscoveryPage: Select algorithm + params
    DiscoveryPage->>SDK: discovery.startDiscovery()
    SDK->>Backend: POST /discovery/discover

    Backend->>Temporal: Start workflow
    Temporal-->>Backend: workflow_id
    Backend-->>SDK: {job_id, status: queued}
    SDK-->>DiscoveryPage: JobReference

    DiscoveryPage->>JobStream: Start polling

    loop Every 2 seconds
        JobStream->>SDK: jobs.getStatus(job_id)
        SDK->>Backend: GET /jobs/:id
        Backend-->>SDK: {status, progress}
        SDK-->>JobStream: JobStatus
        JobStream-->>DiscoveryPage: Update UI
    end

    Note over Backend,Temporal: Workflow completes
    Backend-->>SDK: {status: completed, model_id}
    SDK-->>JobStream: Final status
    JobStream-->>DiscoveryPage: Job complete

    DiscoveryPage->>SDK: discovery.getModels()
    SDK->>Backend: GET /discovery/models
    Backend-->>SDK: Model list
    SDK-->>DiscoveryPage: Updated models
```

## Analytics Feature

```mermaid
flowchart TB
    subgraph "Analytics Page"
        PAGE_A[AnalyticsPage]
        TABS[Tab Navigation]
        CONTENT[Tab Content]
    end

    subgraph "Tabs"
        PERF_TAB[Performance Tab]
        CONF_TAB[Conformance Tab]
        REW_TAB[Rework Tab]
        RES_TAB[Resources Tab]
    end

    subgraph "Data Fetching"
        LOG_LIST[useQuery - logs]
        METRICS[useQuery - metrics]
        SELECTED[Selected log state]
    end

    PAGE_A --> TABS
    TABS --> PERF_TAB
    TABS --> CONF_TAB
    TABS --> REW_TAB
    TABS --> RES_TAB

    PERF_TAB --> CONTENT
    CONF_TAB --> CONTENT
    REW_TAB --> CONTENT
    RES_TAB --> CONTENT

    LOG_LIST --> SELECTED
    SELECTED --> METRICS
    METRICS --> CONTENT
```

## KPI Dashboard Feature

```mermaid
flowchart TB
    subgraph "KPI Page"
        PAGE_K[KPIPage]
        TAB_NAV[Tab Navigation]
        TAB_CONTENT[Active Tab]
    end

    subgraph "KPI Tabs"
        PERF_K[Performance Tab]
        DEAD_K[Deadlines Tab]
        UNWANT_K[Unwanted Activities]
        AUTO_K[Automation Tab]
    end

    subgraph "URL State"
        TAB_PARAM[?tab=performance]
        AUTO_LOAD[Auto-load from URL]
        PERSIST[Persist selection]
    end

    subgraph "Audit"
        AUDIT_LOG[useKPIAuditLogger]
        LOG_VIEW[Log KPI access]
    end

    PAGE_K --> TAB_NAV
    TAB_NAV --> PERF_K
    TAB_NAV --> DEAD_K
    TAB_NAV --> UNWANT_K
    TAB_NAV --> AUTO_K

    TAB_NAV --> TAB_PARAM
    TAB_PARAM --> AUTO_LOAD
    TAB_NAV --> PERSIST

    PAGE_K --> AUDIT_LOG
    AUDIT_LOG --> LOG_VIEW
```

## AI Assistant Feature

```mermaid
flowchart TB
    subgraph "AI Assistant Page"
        PAGE_AI[AIAssistantPage]
        PROC_SELECT[ProcessSelector]
        CHAT[Chat Interface]
        SUGGESTIONS[Prompt Suggestions]
    end

    subgraph "Context Loading"
        FETCH_PROCS[useAIProcesses]
        FETCH_SUMMARY[useAIProcessSummary]
        BUILD_CTX[Build LLM Context]
    end

    subgraph "Chat System"
        MESSAGES[Messages Array]
        INPUT[User Input]
        SEND[useSendAIMessage]
        STREAM[Response Stream]
    end

    subgraph "Insight Display"
        PARSE_INS[Parse Insights]
        INSIGHT_CARD[InsightCard Component]
        SEVERITY[Severity Indicator]
    end

    PAGE_AI --> PROC_SELECT
    PAGE_AI --> CHAT
    PAGE_AI --> SUGGESTIONS

    PROC_SELECT --> FETCH_PROCS
    PROC_SELECT --> FETCH_SUMMARY
    FETCH_SUMMARY --> BUILD_CTX

    CHAT --> MESSAGES
    INPUT --> SEND
    BUILD_CTX --> SEND
    SEND --> STREAM
    STREAM --> MESSAGES

    STREAM --> PARSE_INS
    PARSE_INS --> INSIGHT_CARD
    INSIGHT_CARD --> SEVERITY
```

## AI Chat Data Flow

```mermaid
sequenceDiagram
    participant User
    participant AIPage
    participant ProcessSummary
    participant ChatMutation
    participant Backend
    participant LLM

    User->>AIPage: Select process
    AIPage->>ProcessSummary: useAIProcessSummary(processId)
    ProcessSummary->>Backend: GET /ai/processes/:id/summary

    Backend->>Backend: Compute metrics
    Backend-->>ProcessSummary: {bottlenecks, rework, patterns}
    ProcessSummary-->>AIPage: Context ready

    AIPage->>AIPage: Show prompt suggestions

    User->>AIPage: Enter question
    AIPage->>ChatMutation: sendMessage(question, context)
    ChatMutation->>Backend: POST /ai/chat

    Backend->>LLM: Stream request
    LLM-->>Backend: Response chunks

    loop Streaming
        Backend-->>ChatMutation: Response chunk
        ChatMutation-->>AIPage: Update message
    end

    AIPage->>AIPage: Parse insights from response
    AIPage->>AIPage: Display InsightCards
```

## Shared Hooks Architecture

```mermaid
graph TB
    subgraph "Query Hooks"
        USE_QUERY[useQueryWithErrorHandling]
        USE_TOAST[useQueryWithToast]
        USE_SILENT[useSilentQuery]
    end

    subgraph "Async Hooks"
        USE_SAFE[useSafeAsync]
        USE_SAFE_TOAST[useSafeAsyncWithToast]
        USE_MUT[useSafeMutation]
    end

    subgraph "State Hooks"
        USE_URL[useURLState]
        USE_EXPLORE[useExplorerState]
        USE_FILT[useExplorerFilters]
    end

    subgraph "Monitoring Hooks"
        USE_NET[useNetworkStatus]
        USE_SLOW[useSlowRequestDetection]
        USE_LOGS[useBackendLogs]
    end

    subgraph "Audit Hooks"
        USE_AUDIT[useAuditLogger]
        USE_PAGE[usePageLogging]
    end

    USE_QUERY --> USE_TOAST
    USE_QUERY --> USE_SILENT

    USE_SAFE --> USE_SAFE_TOAST
    USE_SAFE --> USE_MUT

    USE_URL --> USE_EXPLORE
    USE_EXPLORE --> USE_FILT
```

## API Integration Pattern

```mermaid
flowchart TB
    subgraph "Hook Factory"
        CREATE_QUERY[createQueryHook]
        CREATE_MUT[createMutationHook]
    end

    subgraph "SDK Integration"
        USE_SDK[useSDK hook]
        SDK_CLIENT[OpenAPI SDK Client]
        SDK_METHODS[sdk.projects, sdk.datasets, etc]
    end

    subgraph "Feature Hooks"
        PROJ_HOOKS[useProjectList, useCreateProject]
        DS_HOOKS[useDatasets, useUpload]
        DISC_HOOKS[useDiscoveryModels]
    end

    subgraph "TanStack Query"
        QUERY_CLIENT[QueryClient]
        CACHE[Query Cache]
        INVALIDATE[Invalidation]
    end

    CREATE_QUERY --> USE_SDK
    CREATE_MUT --> USE_SDK
    USE_SDK --> SDK_CLIENT
    SDK_CLIENT --> SDK_METHODS

    CREATE_QUERY --> PROJ_HOOKS
    CREATE_QUERY --> DS_HOOKS
    CREATE_QUERY --> DISC_HOOKS

    PROJ_HOOKS --> QUERY_CLIENT
    DS_HOOKS --> QUERY_CLIENT
    DISC_HOOKS --> QUERY_CLIENT

    QUERY_CLIENT --> CACHE
    CREATE_MUT --> INVALIDATE
    INVALIDATE --> CACHE
```

## Error Boundary Strategy

```mermaid
flowchart TB
    subgraph "Global Level"
        GLOBAL_EB[GlobalErrorBoundary]
        GLOBAL_FB[Full-page Error + Reload]
    end

    subgraph "Route Level"
        ROUTE_EB[withErrorBoundary Wrapper]
        FEATURE_FB[FeatureErrorFallback]
    end

    subgraph "Component Level"
        COMP_EB[ComponentErrorBoundary]
        CARD_FB[Card Error + Retry]
        ALERT_FB[Alert Error]
    end

    subgraph "Query Level"
        QUERY_ERR[useQueryWithErrorHandling]
        NOTIF[Notification Toast]
        DEV_LOG[DevConsole Logging]
    end

    GLOBAL_EB --> GLOBAL_FB
    ROUTE_EB --> FEATURE_FB
    COMP_EB --> CARD_FB
    COMP_EB --> ALERT_FB

    QUERY_ERR --> NOTIF
    QUERY_ERR --> DEV_LOG
```

## Component Hierarchy

```mermaid
graph TB
    subgraph "Page Components"
        FEATURE_PAGE[FeaturePage Wrapper]
        BREADCRUMB[Breadcrumb]
        ACTIONS[Page Actions]
        LOADING[Loading State]
        ERROR[Error State]
        EMPTY[Empty State]
    end

    subgraph "Data Display"
        DATA_TABLE[DataTable]
        FORM[Ant Design Form]
        MODAL[Modal Dialog]
    end

    subgraph "Visualization"
        CYTO[CytoscapeCanvas]
        CHART[Chart Components]
        HEATMAP[Heatmap]
    end

    FEATURE_PAGE --> BREADCRUMB
    FEATURE_PAGE --> ACTIONS
    FEATURE_PAGE --> LOADING
    FEATURE_PAGE --> ERROR
    FEATURE_PAGE --> EMPTY

    FEATURE_PAGE --> DATA_TABLE
    FEATURE_PAGE --> FORM
    FEATURE_PAGE --> MODAL

    FEATURE_PAGE --> CYTO
    FEATURE_PAGE --> CHART
    FEATURE_PAGE --> HEATMAP
```

## State Management Overview

```mermaid
graph TB
    subgraph "Global State"
        USER[UserContext<br/>Auth + Workspace]
        NOTIF[NotificationContext<br/>In-app notifications]
        HEALTH[BackendHealthContext<br/>API status]
    end

    subgraph "Server State"
        QUERY[TanStack Query<br/>API data cache]
        STALE[Stale time config]
        INVALIDATE_S[Auto-invalidation]
    end

    subgraph "URL State"
        PARAMS[Query Parameters]
        ROUTE[Route Parameters]
        FILTER_URL[Filter state in URL]
    end

    subgraph "Local State"
        MODAL_STATE[Modal open/close]
        FORM_STATE[Form values]
        SELECT_STATE[Selection state]
    end

    USER --> QUERY
    HEALTH --> QUERY

    QUERY --> STALE
    QUERY --> INVALIDATE_S

    PARAMS --> FILTER_URL
    ROUTE --> QUERY

    MODAL_STATE --> LOCAL_STATE
    FORM_STATE --> LOCAL_STATE
    SELECT_STATE --> LOCAL_STATE
```

## Key Files Reference

| Component | Path |
|-----------|------|
| App Entry | `src/App.tsx` |
| Routes | `src/routes.tsx` |
| Navigation Config | `src/navigation.ts` |
| User Context | `src/shared/context/UserContext.tsx` |
| Notification Context | `src/shared/context/NotificationContext.tsx` |
| Projects Pages | `src/features/platform/projects/pages/` |
| Upload Wizard | `src/features/platform/upload-wizard/pages/UploadWizardPage.tsx` |
| Explorer Page | `src/features/explorer/pages/ExplorerDetailPage.tsx` |
| Discovery Page | `src/features/discovery/pages/DiscoveryPage.tsx` |
| Analytics Page | `src/features/analytics/pages/AnalyticsPage.tsx` |
| KPI Page | `src/features/kpi/pages/KPIPage.tsx` |
| AI Assistant | `src/features/ai/pages/AIAssistantPage.tsx` |
| Query Hooks | `src/shared/hooks/useQueryWithErrorHandling.ts` |
| Safe Async | `src/shared/hooks/useSafeAsync.ts` |
