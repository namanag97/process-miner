# UI_FLOW_DIAGRAM.md — Complete User Journey Map

> [!NOTE]
> This diagram shows the complete frontend UI/UX flow of the Process Mining Platform, including all user journeys from authentication through analysis.

---

## Complete Application Flow

```mermaid
flowchart TB
    %% Entry Point
    Start([User Opens App]) --> AuthCheck{Authenticated?}
    AuthCheck -->|No| Login["/login<br/>LoginPage"]
    AuthCheck -->|Yes| Home
    Login -->|Success| Home["/home<br/>HomePage"]
    Login -->|Failure| Login

    %% Home Dashboard
    Home --> HomeActions{User Action}
    HomeActions -->|View Processes| Processes
    HomeActions -->|Quick Upload| Upload
    HomeActions -->|Explore| ExplorerIndex
    HomeActions -->|Analytics| Analytics
    HomeActions -->|AI Assistant| AIAssistant
    HomeActions -->|Settings| Settings
    HomeActions -->|Notifications| Notifications

    %% Data Foundation Phase
    subgraph DataFoundation["📁 Data Foundation"]
        Processes["/processes<br/>EventLogsPage"]
        Upload["/processes/upload<br/>UploadWizardPage"]
        ProcessDetail["/processes/:id<br/>LogDetailPage"]

        Processes -->|Upload New| Upload
        Processes -->|Select Log| ProcessDetail
        Upload -->|Step 1| UploadFile["Upload File"]
        UploadFile -->|Step 2| MapColumns["Map Columns"]
        MapColumns -->|Step 3| Confirm["Confirm & Process"]
        Confirm -->|Success| ProcessDetail
        ProcessDetail -->|Explore| ExplorerPage
        ProcessDetail -->|Delete| Processes
    end

    %% Process Discovery Phase
    subgraph Discovery["🔍 Process Discovery"]
        ExplorerIndex["/explorer<br/>ProcessExplorerIndexPage"]
        ExplorerPage["/explorer/:logId<br/>ProcessExplorerPage"]

        ExplorerIndex -->|Select Process| ExplorerPage
        ExplorerPage --> Canvas["ProcessCanvas<br/>DFG Visualization"]
        ExplorerPage --> Filters["FilterPanel<br/>Time/Activity/Variant"]
        ExplorerPage --> Variants["VariantPanel<br/>Process Variants"]
        ExplorerPage --> ActivityDetail["ActivityDetailsPanel<br/>Node Statistics"]

        Canvas <-->|Click Node| ActivityDetail
        Variants -->|Highlight Path| Canvas
        Filters -->|Apply| Canvas
    end

    %% Analytics Phase
    subgraph AnalyticsSection["📊 Analytics"]
        Analytics["/analytics<br/>AnalyticsPage"]
        PerfTab["Performance Tab<br/>Cycle Time, Throughput"]
        ConfTab["Conformance Tab<br/>Fitness, Violations"]
        ReworkTab["Rework Tab<br/>Loops, Waste"]
        ResourcesTab["Resources Tab<br/>Workload, Handovers"]

        Analytics --> PerfTab
        Analytics --> ConfTab
        Analytics --> ReworkTab
        Analytics --> ResourcesTab
    end

    %% AI & Advanced Phase
    subgraph AIAdvanced["🤖 AI & Advanced"]
        AIAssistant["/ai/assistant<br/>AIAssistantPage"]
        AIInsights["/ai/insights<br/>AIInsightsPage"]
        Predictions["/ai/predictions<br/>PredictionsPage"]
        PredictorDetail["/ai/predictions/:id<br/>PredictorDetailPage"]

        AIAssistant -->|Select Process| ChatInterface["Chat Interface"]
        ChatInterface -->|Query| AIResponse["AI Response"]
        AIAssistant --> AIInsights
        AIInsights --> Predictions
        Predictions -->|View Model| PredictorDetail
    end

    %% Settings & Support
    subgraph Support["⚙️ Settings & Support"]
        Settings["/settings<br/>SettingsPage"]
        Notifications["/notifications<br/>NotificationsPage"]
        Help["/help<br/>HelpCenterPage"]
        Activity["/activity<br/>ActivityLogPage"]
        AuditLogs["/audit-logs<br/>AuditLogsPage"]

        Settings --> ProfileTab["Profile"]
        Settings --> PrefsTab["Preferences"]
        Settings --> NotifsTab["Notifications"]
        Help --> AuditLogs
    end

    %% Cross-Navigation
    ProcessDetail -->|Analyze| Analytics
    ExplorerPage -->|Deep Analysis| Analytics
    Analytics -->|AI Insights| AIAssistant
    Notifications -->|View Related| ProcessDetail

    %% Developer Tools
    TestBench["/test-bench<br/>TestBenchPage"]
    Home -.->|Dev Mode| TestBench

    %% Styling
    classDef entryPoint fill:#10b981,stroke:#059669,color:#fff
    classDef authFlow fill:#f59e0b,stroke:#d97706,color:#fff
    classDef dataPhase fill:#3b82f6,stroke:#2563eb,color:#fff
    classDef discoveryPhase fill:#8b5cf6,stroke:#7c3aed,color:#fff
    classDef analyticsPhase fill:#ec4899,stroke:#db2777,color:#fff
    classDef aiPhase fill:#06b6d4,stroke:#0891b2,color:#fff
    classDef supportPhase fill:#6b7280,stroke:#4b5563,color:#fff

    class Start entryPoint
    class Login,AuthCheck authFlow
    class Processes,Upload,ProcessDetail,UploadFile,MapColumns,Confirm dataPhase
    class ExplorerIndex,ExplorerPage,Canvas,Filters,Variants,ActivityDetail discoveryPhase
    class Analytics,PerfTab,ConfTab,ReworkTab,ResourcesTab analyticsPhase
    class AIAssistant,AIInsights,Predictions,PredictorDetail,ChatInterface,AIResponse aiPhase
    class Settings,Notifications,Help,Activity,AuditLogs,ProfileTab,PrefsTab,NotifsTab,TestBench supportPhase
```

---

## Legend

| Color     | Phase     | Description                           |
| --------- | --------- | ------------------------------------- |
| 🟢 Green  | Entry     | Application entry point               |
| 🟠 Orange | Auth      | Authentication flow                   |
| 🔵 Blue   | Data      | Process upload and management         |
| 🟣 Purple | Discovery | Process visualization and exploration |
| 🩷 Pink   | Analytics | Performance and conformance analysis  |
| 🩵 Cyan   | AI        | AI assistant and predictions          |
| ⬜ Gray   | Support   | Settings, help, and admin features    |

---

## Key User Journeys

### 1. First-Time User Flow

```
Login → Home → Upload → Map Columns → Confirm → Process Detail → Explorer
```

### 2. Analyst Flow

```
Home → Processes → Select Log → Explorer → Filter Variants → Analytics
```

### 3. AI-Assisted Analysis

```
Home → AI Assistant → Select Process → Ask Questions → View Insights
```

### 4. Admin Flow

```
Home → Settings → Audit Logs → Activity Log
```
