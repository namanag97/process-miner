# PAGE_MAP.md — Every Route and Its Purpose

> [!NOTE]
> This map outlines all 22 routes in the application. Routes are organized by implementation phase.

---

## Route Overview

| Route                     | Page Component             | Layout     | Data Source (SDK)                | Purpose                     |
| ------------------------- | -------------------------- | ---------- | -------------------------------- | --------------------------- |
| `/login`                  | `LoginPage`                | None       | `sdk.auth.login()`               | User authentication         |
| `/home`                   | `HomePage`                 | `AppShell` | `sdk.logs.list()`                | Dashboard and quick actions |
| `/logs`                   | `EventLogsPage`            | `AppShell` | `sdk.logs.list()`                | List and manage event logs  |
| `/logs/upload`            | `UploadWizardPage`         | `AppShell` | `sdk.logs.ingest()`              | Multi-step log upload       |
| `/logs/:id`               | `LogDetailPage`            | `AppShell` | `sdk.logs.get(id)`               | Log details and stats       |
| `/explorer`               | `ProcessExplorerIndexPage` | `AppShell` | `sdk.logs.list()`                | Select log to explore       |
| `/explorer/:logId`        | `ProcessExplorerPage`      | `AppShell` | `sdk.discovery.*`                | Visual DFG exploration      |
| `/analytics`              | `AnalyticsPage`            | `AppShell` | `sdk.analytics.*`                | Analytics dashboard         |
| `/analytics/performance`  | `AnalyticsPage`            | `AppShell` | `sdk.analytics.getPerformance()` | Performance tab             |
| `/analytics/conformance`  | `AnalyticsPage`            | `AppShell` | `sdk.conformance.check()`        | Conformance tab             |
| `/analytics/rework`       | `AnalyticsPage`            | `AppShell` | `sdk.analytics.getRework()`      | Rework analysis tab         |
| `/ai`                     | `AIIndexPage`              | `AppShell` | —                                | AI features hub             |
| `/ai/insights`            | `AIInsightsPage`           | `AppShell` | `sdk.ai.getInsights()`           | Automated insights          |
| `/ai/predictions`         | `PredictionsPage`          | `AppShell` | `sdk.ai.listPredictors()`        | Prediction models           |
| `/ai/predictions/:id`     | `PredictorDetailPage`      | `AppShell` | `sdk.ai.getPredictorDetail()`    | Predictor configuration     |
| `/settings/*`             | `SettingsPage`             | `AppShell` | `sdk.auth.getProfile()`          | User settings               |
| `/settings/profile`       | `SettingsPage` (tab)       | `AppShell` | `sdk.auth.getProfile()`          | Profile settings            |
| `/settings/preferences`   | `SettingsPage` (tab)       | `AppShell` | —                                | App preferences             |
| `/settings/notifications` | `SettingsPage` (tab)       | `AppShell` | —                                | Notification settings       |
| `/notifications`          | `NotificationsPage`        | `AppShell` | `sdk.notifications.list()`       | Notification center         |
| `/help`                   | `HelpCenterPage`           | `AppShell` | —                                | Help and documentation      |
| `/activity`               | `ActivityLogPage`          | `AppShell` | `sdk.activity.list()`            | User activity history       |

---

## Phase 1: Base Platform

### Home Dashboard

**File:** [src/pages/HomePage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/HomePage.tsx)

| Property   | Value                                                  |
| ---------- | ------------------------------------------------------ |
| Route      | `/home`                                                |
| SDK Calls  | `sdk.logs.list()`                                      |
| Components | `MetricCard`, `EmptyState`, `PageHeader`               |
| User Flow  | View stats → Quick actions → Navigate to logs/explorer |

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

| Property  | Value              |
| --------- | ------------------ |
| Route     | `/help`            |
| SDK Calls | — (static content) |

---

### Activity Log

**File:** [src/pages/ActivityLogPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/ActivityLogPage.tsx)

| Property  | Value                 |
| --------- | --------------------- |
| Route     | `/activity`           |
| SDK Calls | `sdk.activity.list()` |

---

## Phase 2: Data Foundation

### Event Logs List

**File:** [src/pages/logs/EventLogsPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/logs/EventLogsPage.tsx)

| Property   | Value                                               |
| ---------- | --------------------------------------------------- |
| Route      | `/logs`                                             |
| SDK Calls  | `sdk.logs.list()`                                   |
| Components | `PageHeader`, Data Table, Search                    |
| Actions    | View, Download, Delete                              |
| User Flow  | Search/filter → Select log → View detail or Explore |

---

### Upload Wizard

**File:** [src/pages/logs/UploadWizardPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/logs/UploadWizardPage.tsx)

| Property  | Value                                           |
| --------- | ----------------------------------------------- |
| Route     | `/logs/upload`                                  |
| SDK Calls | `sdk.logs.detectColumns()`, `sdk.logs.ingest()` |
| Steps     | Upload → Column Mapping → Confirm               |
| Redirect  | → `/logs/:newId` on success                     |

---

### Log Detail

**File:** [src/pages/logs/LogDetailPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/logs/LogDetailPage.tsx)

| Property  | Value                                      |
| --------- | ------------------------------------------ |
| Route     | `/logs/:id`                                |
| Params    | `id` - Log ID                              |
| SDK Calls | `sdk.logs.get(id)`, `sdk.logs.analyze(id)` |
| Actions   | Explore, Download, Delete                  |

---

## Phase 3: Process Discovery

### Process Explorer Index

**File:** [src/pages/explorer/ProcessExplorerIndexPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/explorer/ProcessExplorerIndexPage.tsx)

| Property  | Value                             |
| --------- | --------------------------------- |
| Route     | `/explorer`                       |
| SDK Calls | `sdk.logs.list()`                 |
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
| Components | `MetricCard`, `PerformanceTab`, `ConformanceTab`, `ReworkTab`                         |

#### Tab Routes

| Tab         | Route                                    | SDK Call                         |
| ----------- | ---------------------------------------- | -------------------------------- |
| Performance | `/analytics` or `/analytics/performance` | `sdk.analytics.getPerformance()` |
| Conformance | `/analytics/conformance`                 | `sdk.conformance.check()`        |
| Rework      | `/analytics/rework`                      | `sdk.analytics.getRework()`      |

---

## Phase 5: AI & Advanced

### AI Hub

**File:** [src/pages/ai/AIIndexPage.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/ai/AIIndexPage.tsx)

| Property | Value                          |
| -------- | ------------------------------ |
| Route    | `/ai`                          |
| Purpose  | Navigation hub for AI features |

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
