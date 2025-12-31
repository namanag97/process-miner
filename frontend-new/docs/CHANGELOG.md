# CHANGELOG.md — What Changed

All notable changes to the Process Mining Platform frontend.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [Unreleased]

### 🆕 Added

- **AI Assistant Page** (`/ai/assistant`) - Chat-based interface for natural language process analysis
- **Audit Logs Page** (`/audit-logs`) - System audit trail with search, filtering, and export
- **Test Bench Page** (`/test-bench`) - Developer tool for testing UI components and SDK endpoints
- **Resources Tab** in Analytics - Organizational mining with workload and handover analysis
- **SDK Modules:**
  - `organizational` - Social network analysis, role discovery, workload distribution
  - `simulation` - What-if simulation, capacity planning
  - `predictions` - ML model training and prediction results
  - `projects` - Project management and process grouping
- **Components:**
  - `ProcessSelector` - Process dropdown for AI Assistant
  - `ChatMessage` - Chat bubble component with user/assistant variants
  - `InsightCard` - AI insight display card

### 🔄 Changed

- Renamed `logs` module to `processes` throughout SDK
- Route restructure: `/logs/*` → `/processes/*`
- `/ai` now redirects to `/ai/assistant`
- Updated query keys from `['logs', ...]` to `['processes', ...]`

### 🐛 Fixed

- SDK module exports now properly typed
- Fixed organizational network type validation

---

## [1.0.0] - 2024-12-30

Initial release of the Process Mining Platform frontend.

### 🆕 Added

**Phase 1: Base Platform**

- `AppShell` - Collapsible sidebar with navigation
- `SettingsPage` with Profile, Preferences, Notifications tabs
- `NotificationsPage` - Notification center
- `HelpCenterPage` - Static help content
- `ActivityLogPage` - User activity history
- Logging infrastructure with `createLogger()`

**Phase 2: Data Foundation**

- `EventLogsPage` - List and manage event logs
- `UploadWizardPage` - Multi-step file upload
- `LogDetailPage` - Log statistics and actions

**Phase 3: Process Discovery**

- `ProcessExplorerPage` - Full canvas DFG visualization
- `ProcessCanvas` - React Flow-based graph component
- `FilterPanel` - Time, activity, variant threshold filters
- `VariantPanel` - Scrollable variant list with selection
- `ActivityDetailsPanel` - Node detail drawer

**Phase 4: Analytics**

- `AnalyticsPage` with tabbed sub-views
- `PerformanceTab` - Cycle time, throughput metrics
- `ConformanceTab` - Fitness scores, violations
- `ReworkTab` - Loop analysis, waste detection

**Phase 5: AI & Advanced**

- `AIInsightsPage` - Bottleneck detection, anomaly alerts
- `PredictionsPage` - ML predictor management
- `PredictorDetailPage` - Model configuration

**Design System** (`@lumina/design-system`)

- `MetricCard` - KPI display with trends
- `EmptyState` - No-data feedback
- `PageHeader` - Standardized page headers
- `SkeletonCard` - Loading placeholders
- `tokens` - Complete design token system
- `luminaTheme` - Ant Design theme configuration

**Infrastructure**

- TanStack Query v5 with optimized caching
- `SDKProvider` with real API client
- React Router v6 with nested routes

---

## Version Template

```markdown
## [X.Y.Z] - YYYY-MM-DD

### 🆕 Added

- Feature description

### 🔄 Changed

- Change description

### ⚠️ Breaking

- Breaking change description
- **Migration:** Steps to migrate

### 🗑️ Deprecated

- Deprecated feature (removal in vX.Y.Z)

### 🐛 Fixed

- Bug fix description
```
