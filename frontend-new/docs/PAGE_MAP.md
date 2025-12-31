# PAGE_MAP.md — Every Route and Its Purpose

> [!NOTE]
> This map outlines all routes in the application. Routes are organized by implementation phase.

---

## Route Overview

| Route                    | Page Component             | Layout     | Data Source (SDK)                   | Purpose                      |
| ------------------------ | -------------------------- | ---------- | ----------------------------------- | ---------------------------- |
| `/login`                 | `LoginPage`                | None       | `sdk.auth.login()`                  | User authentication          |
| `/home`                  | `HomePage`                 | `AppShell` | `sdk.processes.list()`              | Dashboard and quick actions  |
| `/processes`             | `EventLogsPage`            | `AppShell` | `sdk.processes.list()`              | List and manage event logs   |
| `/processes/upload`      | `UploadWizardPage`         | `AppShell` | `sdk.processes.ingest()`            | Multi-step log upload        |
| `/processes/:id`         | `LogDetailPage`            | `AppShell` | `sdk.processes.get(id)`             | Log details and stats        |
| `/explorer`              | `ProcessExplorerIndexPage` | `AppShell` | `sdk.processes.list()`              | Select log to explore        |
| `/explorer/:logId`       | `ProcessExplorerPage`      | `AppShell` | `sdk.discovery.*`                   | Visual DFG exploration       |
| `/analytics`             | `AnalyticsPage`            | `AppShell` | `sdk.analytics.*`                   | Analytics dashboard          |
| `/analytics/performance` | `AnalyticsPage`            | `AppShell` | `sdk.analytics.getPerformance()`    | Performance tab              |
| `/analytics/conformance` | `AnalyticsPage`            | `AppShell` | `sdk.conformance.check()`           | Conformance tab              |
| `/analytics/rework`      | `AnalyticsPage`            | `AppShell` | `sdk.analytics.getRework()`         | Rework analysis tab          |
| `/ai`                    | Redirect                   | —          | —                                   | Redirects to `/ai/assistant` |
| `/ai/assistant`          | `AIAssistantPage`          | `AppShell` | `sdk.analytics.getProcessSummary()` | Chat-based AI assistant 🆕   |
| `/ai/insights`           | `AIInsightsPage`           | `AppShell` | `sdk.ai.getInsights()`              | Automated insights           |
| `/ai/predictions`        | `PredictionsPage`          | `AppShell` | `sdk.ai.listPredictors()`           | Prediction models            |
| `/ai/predictions/:id`    | `PredictorDetailPage`      | `AppShell` | `sdk.ai.getPredictorDetail()`       | Predictor configuration      |
| `/settings/*`            | `SettingsPage`             | `AppShell` | `sdk.auth.getProfile()`             | User settings                |
| `/notifications`         | `NotificationsPage`        | `AppShell` | `sdk.notifications.list()`          | Notification center          |
| `/help`                  | `HelpCenterPage`           | `AppShell` | —                                   | Help and documentation       |
| `/activity`              | `ActivityLogPage`          | `AppShell` | `sdk.activity.list()`               | User activity history        |
| `/audit-logs`            | `AuditLogsPage`            | `AppShell` | —                                   | System audit logs 🆕         |
| `/test-bench`            | `TestBenchPage`            | `AppShell` | All SDK methods                     | Developer testing 🆕         |

---

## Phase 1: Base Platform

### Home Dashboard

**File:** [src/pages/HomePage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/HomePage.tsx)

| Property   | Value                                                       |
| ---------- | ----------------------------------------------------------- |
| Route      | `/home`                                                     |
| SDK Calls  | `sdk.processes.list()`                                      |
| Components | `MetricCard`, `EmptyState`, `PageHeader`                    |
| User Flow  | View stats → Quick actions → Navigate to processes/explorer |

---

### Settings

**File:** [src/pages/settings/SettingsPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/settings/SettingsPage.tsx)

| Property    | Value                                                                   |
| ----------- | ----------------------------------------------------------------------- |
| Route       | `/settings/*`                                                           |
| Tabs        | Profile, Preferences, Notifications                                     |
| URL Pattern | `/settings/profile`, `/settings/preferences`, `/settings/notifications` |

---

### Notifications Center

**File:** [src/pages/NotificationsPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/NotificationsPage.tsx)

| Property  | Value                            |
| --------- | -------------------------------- |
| Route     | `/notifications`                 |
| SDK Calls | `sdk.notifications.list()`       |
| Actions   | Mark read, dismiss, view details |

---

### Help Center

**File:** [src/pages/HelpCenterPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/HelpCenterPage.tsx)

| Property  | Value                                        |
| --------- | -------------------------------------------- |
| Route     | `/help`                                      |
| SDK Calls | — (static content)                           |
| Sections  | Getting Started, User Guides, FAQ, Changelog |

---

### Activity Log

**File:** [src/pages/ActivityLogPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/ActivityLogPage.tsx)

| Property  | Value                 |
| --------- | --------------------- |
| Route     | `/activity`           |
| SDK Calls | `sdk.activity.list()` |

---

### Audit Logs 🆕

**File:** [src/pages/AuditLogsPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/AuditLogsPage.tsx)

| Property  | Value                                               |
| --------- | --------------------------------------------------- |
| Route     | `/audit-logs`                                       |
| SDK Calls | —                                                   |
| Features  | Searchable table, date filtering, export, IP toggle |

---

## Phase 2: Data Foundation

### Event Logs List

**File:** [src/pages/logs/EventLogsPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/logs/EventLogsPage.tsx)

| Property   | Value                                               |
| ---------- | --------------------------------------------------- |
| Route      | `/processes`                                        |
| SDK Calls  | `sdk.processes.list()`                              |
| Components | `PageHeader`, Data Table, Search                    |
| Actions    | View, Download, Delete                              |
| User Flow  | Search/filter → Select log → View detail or Explore |

---

### Upload Wizard

**File:** [src/pages/logs/UploadWizardPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/logs/UploadWizardPage.tsx)

| Property  | Value                                                     |
| --------- | --------------------------------------------------------- |
| Route     | `/processes/upload`                                       |
| SDK Calls | `sdk.processes.detectColumns()`, `sdk.processes.ingest()` |
| Steps     | Upload → Column Mapping → Confirm                         |
| Redirect  | → `/processes/:newId` on success                          |

---

### Log Detail

**File:** [src/pages/logs/LogDetailPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/logs/LogDetailPage.tsx)

| Property  | Value                                                |
| --------- | ---------------------------------------------------- |
| Route     | `/processes/:id`                                     |
| Params    | `id` - Process ID                                    |
| SDK Calls | `sdk.processes.get(id)`, `sdk.processes.analyze(id)` |
| Actions   | Explore, Download, Delete                            |

---

## Phase 3: Process Discovery

### Process Explorer Index

**File:** [src/pages/explorer/ProcessExplorerIndexPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/explorer/ProcessExplorerIndexPage.tsx)

| Property  | Value                             |
| --------- | --------------------------------- |
| Route     | `/explorer`                       |
| SDK Calls | `sdk.processes.list()`            |
| Purpose   | Select a log to explore           |
| Redirect  | → `/explorer/:logId` on selection |

---

### Process Explorer

**File:** [src/pages/explorer/ProcessExplorerPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/explorer/ProcessExplorerPage.tsx)

| Property     | Value                                                                  |
| ------------ | ---------------------------------------------------------------------- |
| Route        | `/explorer/:logId`                                                     |
| Params       | `logId` - Event log ID                                                 |
| SDK Calls    | `sdk.discovery.buildDFG()`, `sdk.discovery.getVariants()`              |
| Components   | `ProcessCanvas`, `FilterPanel`, `VariantPanel`, `ActivityDetailsPanel` |
| Interactions | Click nodes, select variants, apply filters, export                    |

**Component Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ PageHeader (breadcrumb, export button)                  │
├──────────┬──────────────────────────────┬───────────────┤
│ Filters  │     ProcessCanvas (DFG)      │   Variants    │
│  Panel   │                              │    Panel      │
│  (240px) │                              │    (280px)    │
├──────────┴──────────────────────────────┴───────────────┤
│ ActivityDetailsPanel (Drawer, right side)               │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 4: Analytics

### Analytics Dashboard

**File:** [src/pages/analytics/AnalyticsPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/analytics/AnalyticsPage.tsx)

| Property   | Value                                                                                 |
| ---------- | ------------------------------------------------------------------------------------- |
| Route      | `/analytics`, `/analytics/performance`, `/analytics/conformance`, `/analytics/rework` |
| Layout     | Log selector + MetricCard row + Tab content                                           |
| Components | `MetricCard`, `PerformanceTab`, `ConformanceTab`, `ReworkTab`, `ResourcesTab`         |

#### Tab Routes

| Tab         | Route                                    | SDK Call                           |
| ----------- | ---------------------------------------- | ---------------------------------- |
| Performance | `/analytics` or `/analytics/performance` | `sdk.analytics.getPerformance()`   |
| Conformance | `/analytics/conformance`                 | `sdk.conformance.check()`          |
| Rework      | `/analytics/rework`                      | `sdk.analytics.getRework()`        |
| Resources   | `/analytics/resources` 🆕                | `sdk.organizational.getWorkload()` |

---

### Resources Tab 🆕

**File:** [src/pages/analytics/ResourcesTab.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/analytics/ResourcesTab.tsx)

| Property  | Value                                                                         |
| --------- | ----------------------------------------------------------------------------- |
| Route     | `/analytics/resources` (tab)                                                  |
| SDK Calls | `sdk.organizational.getWorkload()`, `sdk.organizational.getHandoverNetwork()` |
| Features  | Resource performance metrics, workload distribution, handover analysis        |

---

## Phase 5: AI & Advanced

### AI Hub

**Route:** `/ai` → Redirects to `/ai/assistant`

---

### AI Assistant 🆕

**File:** [src/pages/ai/AIAssistantPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/ai/AIAssistantPage.tsx)

| Property   | Value                                                           |
| ---------- | --------------------------------------------------------------- |
| Route      | `/ai/assistant`                                                 |
| SDK Calls  | `sdk.analytics.getProcessSummary()`                             |
| Components | `ProcessSelector`, `ChatMessage`, `InsightCard`                 |
| Features   | Natural language querying, process data context, chat interface |

---

### AI Insights

**File:** [src/pages/ai/AIInsightsPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/ai/AIInsightsPage.tsx)

| Property   | Value                                                      |
| ---------- | ---------------------------------------------------------- |
| Route      | `/ai/insights`                                             |
| SDK Calls  | `sdk.ai.getInsights()`                                     |
| Features   | Performance insights, pattern detection, anomaly detection |
| Components | `InsightCard`, NL query input, log selector                |

---

### Predictions

**File:** [src/pages/ai/PredictionsPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/ai/PredictionsPage.tsx)

| Property  | Value                     |
| --------- | ------------------------- |
| Route     | `/ai/predictions`         |
| SDK Calls | `sdk.ai.listPredictors()` |

---

### Predictor Detail

**File:** [src/pages/ai/PredictorDetailPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/ai/PredictorDetailPage.tsx)

| Property  | Value                           |
| --------- | ------------------------------- |
| Route     | `/ai/predictions/:id`           |
| Params    | `id` - Predictor ID             |
| SDK Calls | `sdk.ai.getPredictorDetail(id)` |

---

## Developer Tools

### Test Bench 🆕

**File:** [src/pages/TestBenchPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/TestBenchPage.tsx)

| Property | Value                                                  |
| -------- | ------------------------------------------------------ |
| Route    | `/test-bench`                                          |
| Purpose  | Interactive testing of UI components and SDK endpoints |
| Features | Component showcase, API test console                   |

---

## Protected Routes

All routes except `/login` are wrapped in the `ProtectedRoute` component:

```tsx
// From App.tsx
<ProtectedRoute>
  <AppLayout /> {/* Contains all authenticated routes */}
</ProtectedRoute>
```

- **Authentication Check:** `useAuth().isAuthenticated`
- **Loading State:** Shows "Loading..." during auth check
- **Redirect:** Unauthenticated users → `/login`
- **Fallback:** Unknown routes → `/home`
