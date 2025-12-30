# CHANGELOG.md — What Changed

All notable changes to the Process Mining Platform frontend.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [Unreleased]

### 🆕 Added

- (Document new features here)

### 🔄 Changed

- (Document changes to existing features)

### ⚠️ Breaking

- (Document breaking changes with migration steps)

### 🗑️ Deprecated

- (Document features scheduled for removal)

### 🐛 Fixed

- (Document bug fixes)

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
- `tokens` - Complete design token system
- `luminaTheme` - Ant Design theme configuration

**Infrastructure**

- TanStack Query v5 with optimized caching
- `SDKProvider` with mock API client
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
