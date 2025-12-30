# COMPONENT_CATALOG.md — Every Reusable Component

> [!NOTE]
> This catalog lists all UI components in the Process Mining Platform. Components are organized by layer: **Design System** (shared across app) and **Feature Components** (page-specific but reusable).

---

## Quick Reference

| Component              | Layer         | Data Source                          | Cache Key             |
| ---------------------- | ------------- | ------------------------------------ | --------------------- |
| `AppShell`             | Design System | `AuthContext`, `NotificationContext` | —                     |
| `MetricCard`           | Design System | Props (server data)                  | —                     |
| `EmptyState`           | Design System | —                                    | —                     |
| `PageHeader`           | Design System | —                                    | —                     |
| `ProcessCanvas`        | Feature       | `sdk.discovery.buildDFG()`           | `['dfg', logId]`      |
| `FilterPanel`          | Feature       | `MockFilterOptions`                  | —                     |
| `VariantPanel`         | Feature       | `sdk.discovery.getVariants()`        | `['variants', logId]` |
| `ActivityDetailsPanel` | Feature       | `sdk.discovery.getActivityDetail()`  | `['activity', id]`    |

---

## Design System Components

### 1. AppShell ✅ Stable

**Location:** [libs/shared/design-system/src/components/AppShell.tsx](file:///Users/namanagarwal/system/frontend-new/libs/shared/design-system/src/components/AppShell.tsx)

The primary layout component containing the collapsible sidebar, top navigation, and main content area.

#### Props

| Name                | Type                   | Required | Default           | Description                    |
| ------------------- | ---------------------- | :------: | ----------------- | ------------------------------ |
| `children`          | `ReactNode`            |   Yes    | —                 | Main content to render         |
| `navItems`          | `NavItem[]`            |    No    | `defaultNavItems` | Links in the sidebar           |
| `activeId`          | `string`               |    No    | —                 | Current active navigation ID   |
| `onNavigate`        | `(id: string) => void` |    No    | —                 | Callback when nav item clicked |
| `userName`          | `string`               |    No    | `'User'`          | User name for profile section  |
| `userEmail`         | `string`               |    No    | —                 | User email                     |
| `notificationCount` | `number`               |    No    | `0`               | Unread count for bell icon     |

#### Usage

```tsx
import { AppShell } from '@lumina/design-system';

<AppShell
  activeId="home"
  onNavigate={(id) => navigate(`/${id}`)}
  userName="John Doe"
  notificationCount={5}
>
  <YourPageContent />
</AppShell>;
```

#### States

- **Expanded:** Default view (240px sidebar)
- **Collapsed:** Icon-only view (64px sidebar)

---

### 2. MetricCard ✅ Stable

**Location:** [libs/shared/design-system/src/components/MetricCard.tsx](file:///Users/namanagarwal/system/frontend-new/libs/shared/design-system/src/components/MetricCard.tsx)

Enterprise-grade KPI card with trend indicators and status colors.

#### Props

| Name      | Type                                                     | Required | Default     | Description                        |
| --------- | -------------------------------------------------------- | :------: | ----------- | ---------------------------------- |
| `title`   | `string`                                                 |   Yes    | —           | KPI label (e.g., "Avg Cycle Time") |
| `value`   | `string \| number`                                       |   Yes    | —           | Primary metric value               |
| `trend`   | `{ value: number, isPositive: boolean, label?: string }` |    No    | —           | Percentage trend                   |
| `status`  | `'default' \| 'success' \| 'warning' \| 'error'`         |    No    | `'default'` | Semantic coloring                  |
| `loading` | `boolean`                                                |    No    | `false`     | Shows skeleton state               |

#### Usage

```tsx
<MetricCard
  title="Rework Rate"
  value="23.4%"
  trend={{ value: 5.2, isPositive: false, label: 'vs last week' }}
  status="warning"
/>
```

---

### 3. EmptyState ✅ Stable

**Location:** [libs/shared/design-system/src/components/EmptyState.tsx](file:///Users/namanagarwal/system/frontend-new/libs/shared/design-system/src/components/EmptyState.tsx)

Used to provide feedback and instructions when no data is available.

#### Props

| Name          | Type         | Required | Default | Description                 |
| ------------- | ------------ | :------: | ------- | --------------------------- |
| `icon`        | `ReactNode`  |    No    | —       | Centered icon/illustration  |
| `title`       | `string`     |   Yes    | —       | Primary heading             |
| `description` | `string`     |    No    | —       | Detailed explanation        |
| `actionLabel` | `string`     |    No    | —       | Label for CTA button        |
| `onAction`    | `() => void` |    No    | —       | Callback for primary action |

#### Usage

```tsx
<EmptyState
  icon={<FolderOutlined />}
  title="No event logs yet"
  description="Upload your first event log to start analyzing."
  actionLabel="Upload File"
  onAction={handleUpload}
/>
```

---

### 4. PageHeader ✅ Stable

**Location:** [libs/shared/design-system/src/components/PageHeader.tsx](file:///Users/namanagarwal/system/frontend-new/libs/shared/design-system/src/components/PageHeader.tsx)

Standardized header for all pages, supporting breadcrumbs and action buttons.

#### Props

| Name          | Type                                | Required | Default | Description           |
| ------------- | ----------------------------------- | :------: | ------- | --------------------- |
| `title`       | `string`                            |   Yes    | —       | Main page title       |
| `description` | `string`                            |    No    | —       | Page subtitle/context |
| `breadcrumb`  | `Array<{ label, href?, onClick? }>` |    No    | —       | Navigation path       |
| `actions`     | `ReactNode`                         |    No    | —       | Action buttons        |
| `showBack`    | `boolean`                           |    No    | `false` | Shows back arrow      |

#### Usage

```tsx
<PageHeader
  title="Event Logs"
  description="Manage your uploaded event log files"
  actions={<Button type="primary">Upload File</Button>}
/>
```

---

## Feature Components

### 5. ProcessCanvas 🧪 Experimental

**Location:** [src/pages/explorer/components/ProcessCanvas.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/explorer/components/ProcessCanvas.tsx)

React Flow-based DFG (Directly-Follows Graph) visualization with interactive nodes.

#### Props

| Name              | Type                       | Required | Default | Description                          |
| ----------------- | -------------------------- | :------: | ------- | ------------------------------------ |
| `dfgNodes`        | `DFGNode[]`                |   Yes    | —       | Process activity nodes               |
| `dfgEdges`        | `DFGEdge[]`                |   Yes    | —       | Connections between nodes            |
| `selectedNodeId`  | `string \| null`           |    No    | —       | Currently selected node              |
| `highlightedPath` | `string[]`                 |    No    | `[]`    | Node IDs to highlight (variant path) |
| `onNodeClick`     | `(nodeId: string) => void` |    No    | —       | Node click handler                   |

#### Usage

```tsx
<ProcessCanvas
  dfgNodes={[{ id: 'a1', label: 'Submit', frequency: 1250 }]}
  dfgEdges={[{ source: 'a1', target: 'a2', frequency: 1100 }]}
  selectedNodeId={selectedActivity}
  highlightedPath={selectedVariant?.activities}
  onNodeClick={setSelectedActivity}
/>
```

#### Node Types

- **Start Node:** Green border (success color)
- **End Node:** Red border (error color)
- **Selected Node:** Blue border with shadow
- **Highlighted Node:** Blue background (variant path)

---

### 6. FilterPanel ✅ Stable

**Location:** [src/pages/explorer/components/FilterPanel.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/explorer/components/FilterPanel.tsx)

Collapsible filter controls for time range, activity selection, and variant threshold.

#### Props

| Name                | Type                              | Required | Default | Description              |
| ------------------- | --------------------------------- | :------: | ------- | ------------------------ |
| `filterOptions`     | `MockFilterOptions`               |   Yes    | —       | Available filter values  |
| `appliedFilters`    | `AppliedFilter[]`                 |   Yes    | —       | Currently active filters |
| `onApplyFilter`     | `(filter: AppliedFilter) => void` |    No    | —       | Apply new filter         |
| `onRemoveFilter`    | `(filterId: string) => void`      |    No    | —       | Remove filter by ID      |
| `onClearAllFilters` | `() => void`                      |    No    | —       | Clear all filters        |

#### Filter Types

| Type        | Label                      | Value                      |
| ----------- | -------------------------- | -------------------------- |
| `timeRange` | `"Jan 1 – Mar 31, 2024"`   | `{ start: ISO, end: ISO }` |
| `activity`  | `"Activities: 3 selected"` | `string[]`                 |
| `topK`      | `"Top 80% variants"`       | `number`                   |

#### Usage

```tsx
<FilterPanel
  filterOptions={{ activities: ['Submit', 'Review'], timeRange: {...} }}
  appliedFilters={filters}
  onApplyFilter={addFilter}
  onRemoveFilter={removeFilter}
  onClearAllFilters={clearFilters}
/>
```

---

### 7. VariantPanel ✅ Stable

**Location:** [src/pages/explorer/components/VariantPanel.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/explorer/components/VariantPanel.tsx)

Scrollable list of process variants with frequency bars and selection.

#### Props

| Name                 | Type                            | Required | Default | Description                |
| -------------------- | ------------------------------- | :------: | ------- | -------------------------- |
| `variants`           | `MockVariant[]`                 |   Yes    | —       | List of process variants   |
| `selectedVariantKey` | `string \| null`                |    No    | —       | Currently selected variant |
| `onSelectVariant`    | `(key: string \| null) => void` |    No    | —       | Selection handler          |
| `onFilterToVariant`  | `(key: string) => void`         |    No    | —       | Filter cases to variant    |

#### Usage

```tsx
<VariantPanel
  variants={discoveryData.variants}
  selectedVariantKey={selectedVariant}
  onSelectVariant={setSelectedVariant}
  onFilterToVariant={handleFilterToVariant}
/>
```

#### Visual Indicators

- ✅ **Happy Path:** Green checkmark icon
- 📊 **Frequency:** Progress bar + percentage tag
- ➜ **Path Preview:** Activity sequence (ellipsized)

---

### 8. ActivityDetailsPanel ✅ Stable

**Location:** [src/pages/explorer/components/ActivityDetailsPanel.tsx](file:///Users/namanagarwal/system/frontend-new/src/pages/explorer/components/ActivityDetailsPanel.tsx)

Detail drawer for selected activity node showing statistics and filter actions.

#### Props

| Name              | Type                           | Required | Default | Description                      |
| ----------------- | ------------------------------ | :------: | ------- | -------------------------------- |
| `activity`        | `MockActivityDetail \| null`   |   Yes    | —       | Activity data                    |
| `onClose`         | `() => void`                   |    No    | —       | Close panel                      |
| `onFilterWith`    | `(activityId: string) => void` |    No    | —       | Filter to cases with activity    |
| `onFilterWithout` | `(activityId: string) => void` |    No    | —       | Filter to cases without activity |

#### Data Displayed

| Field               | Example                     |
| ------------------- | --------------------------- |
| Total occurrences   | `12,450`                    |
| Cases with activity | `78%`                       |
| Average duration    | `2.4 hours`                 |
| Duration range      | `5 min – 12 hours`          |
| Resources           | `["User A", "User B", ...]` |

#### Usage

```tsx
<ActivityDetailsPanel
  activity={selectedActivityDetail}
  onClose={() => setSelectedActivity(null)}
  onFilterWith={handleFilterWith}
  onFilterWithout={handleFilterWithout}
/>
```

---

## Utility Exports

The design system also exports these utilities from `@lumina/design-system`:

| Export                      | Type     | Description             |
| --------------------------- | -------- | ----------------------- |
| `toast`                     | Function | Toast notifications     |
| `notify`                    | Function | Notification helper     |
| `formatDuration`            | Function | Human-readable duration |
| `formatDurationFromSeconds` | Function | Seconds to readable     |
| `formatCompactNumber`       | Function | `1234` → `"1.2K"`       |
| `formatPercentage`          | Function | Decimal to percent      |
| `tokens`                    | Object   | Design tokens           |
| `luminaTheme`               | Object   | Ant Design theme config |
