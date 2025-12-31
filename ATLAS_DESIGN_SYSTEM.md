# ATLAS Process Mining Platform
## Design System & Implementation Blueprint

**Prepared by: Fictive Kin Design Studio**
**Version: 1.0**
**Date: December 2024**

---

# Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Current State Audit](#current-state-audit)
3. [Object-to-Component Mapping](#object-to-component-mapping)
4. [Component Inventory](#component-inventory)
5. [Gap Analysis](#gap-analysis)
6. [Flow Specifications](#flow-specifications)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Design Tokens Reference](#design-tokens-reference)

---

# Design Philosophy

## Core Principles (Fictive Kin Framework)

### 1. DESIGN AS BLUEPRINT
The UI is not decoration—it's the structural logic of the application. Every component serves a purpose in the user's mental model of process mining.

### 2. SOLVE THROUGH SUBTRACTION
Process mining is inherently complex. Our job is to expose the **core essence** of each analysis without overwhelming users. Kill features that don't test a hypothesis.

### 3. THE HUD NAVIGATION
Borrowed from gamer UI—users should navigate intuitively without looking away from their data. The sidebar is a **control panel**, not a menu.

### 4. THE SEINFELD APP PRINCIPLE
If the plumbing isn't perfect, no amount of features will save the product. Core flows must be flawless:
- Upload → Process → Explore → Analyze → Act

### 5. DATA DENSITY WITHOUT CHAOS
Enterprise analytics demands high information density. We achieve this through:
- Consistent spacing (4px base unit)
- Architectural precision (2px radius for controls)
- Semantic color coding
- Progressive disclosure

---

# Current State Audit

## Existing Infrastructure

### Frontend Architecture
```
frontend-new/
├── src/
│   ├── core/                    # Hook factories, FeaturePage, PageSection
│   ├── features/                # Feature modules
│   │   ├── ai/                  # AI Assistant, Insights, Predictions
│   │   ├── analytics/           # Performance, Conformance, Bottlenecks
│   │   ├── explorer/            # Process Explorer, DFG Visualization
│   │   ├── kpi/                 # KPI Dashboard
│   │   └── projects/            # Workspace/Project Management
│   ├── pages/                   # Legacy pages (being migrated)
│   └── context/                 # UserContext, Notifications
└── libs/shared/design-system/   # Component library
```

### Design System Components (26 Exports)
| Category | Components | Status |
|----------|-----------|--------|
| **Layout** | AppShell | ✅ Production |
| **Data Display** | MetricCard, DataTable, DataSourceCard, ProcessNode | ✅ Production |
| **Page Sections** | PageHeader, FeaturePage, PageSection | ✅ Production |
| **States** | EmptyState, LoadingState (5 variants), SkeletonCard | ✅ Production |
| **Errors** | QueryError (4 variants), ErrorBoundary | ✅ Production |
| **Utilities** | toast, notify, format* functions | ✅ Production |
| **SDK** | SDKProvider, useSDK, queryClient | ✅ Production |

### Backend API (13 Routers, 80+ Endpoints)
| Router | Endpoints | pm4py Integration |
|--------|-----------|-------------------|
| Projects | 7 | N/A |
| Processes | 9 | ✅ Full |
| Discovery | 4 | ✅ Full |
| Visualization | 3 | ✅ Full |
| Conformance | 3 | ✅ Full |
| Analytics | 10 | ✅ Partial |
| Predictions | 7 | Custom ML |
| Filtering | 5 | ✅ Partial |
| OCPM | 6 | ✅ Partial |
| Organizational | 2 | ✅ Full |
| Workflows | 3 | Custom |
| Simulation | 1 | Custom |
| Dev Log | Debug | N/A |

---

# Object-to-Component Mapping

## Core Domain Objects

### Workspace → ProjectsListPage
| Object Attribute | UI Element | Component |
|-----------------|------------|-----------|
| `name` | Title | PageHeader |
| `description` | Subtitle | PageHeader description |
| `event_log_count` | Metric badge | MetricCard |
| `model_count` | Metric badge | MetricCard |
| `status` | Status pill | Tag (Ant Design) |
| `created_at` | Timestamp | formatDuration() |

**Current Implementation:** `src/features/projects/pages/ProjectsListPage.tsx`

### Event Log → ExplorerIndexPage / ProcessDetailPage
| Object Attribute | UI Element | Component |
|-----------------|------------|-----------|
| `name` | Header | PageHeader |
| `status` | Status badge | Tag with state color |
| `event_count` | Statistic | MetricCard |
| `case_count` | Statistic | MetricCard |
| `activity_count` | Statistic | MetricCard |
| `variant_count` | Statistic | MetricCard |
| `date_range_start/end` | Date range | Custom DateRange |
| `duration_avg_seconds` | KPI | MetricCard with trend |
| `quality_score` | Progress | Progress (Ant Design) |

**Current Implementation:** `src/features/explorer/pages/ExplorerIndexPage.tsx`

### Process Model → DFG Visualization
| Object Attribute | UI Element | Component |
|-----------------|------------|-----------|
| `nodes` | Graph nodes | ProcessNode (React Flow) |
| `edges` | Graph edges | Edge (React Flow) |
| `start_activities` | Green nodes | ProcessNode variant="start" |
| `end_activities` | Red nodes | ProcessNode variant="end" |
| `frequency` | Node size/label | Dynamic sizing |
| `avg_duration_seconds` | Edge tooltip | Custom tooltip |

**Current Implementation:** `src/features/explorer/pages/ExplorerDetailPage.tsx`

### Conformance Result → ConformanceTab
| Object Attribute | UI Element | Component |
|-----------------|------------|-----------|
| `fitness` | Gauge/Score | MetricCard or Gauge |
| `precision` | Gauge/Score | MetricCard |
| `deviating_case_count` | Count | MetricCard (error status) |
| `deviations[]` | Table | DataTable |
| `method` | Label | Tag |

**Current Implementation:** `src/features/analytics/components/ConformanceTab.tsx`

### Variant → VariantsPanel
| Object Attribute | UI Element | Component |
|-----------------|------------|-----------|
| `sequence` | Activity path | Custom VariantPath |
| `case_count` | Frequency | Text + bar |
| `case_percentage` | Bar width | Progress bar |
| `avg_duration_seconds` | Duration | formatDuration() |
| `is_happy_path` | Highlight | Star icon |

**Current Implementation:** Custom in Explorer (needs component extraction)

### Performance Analysis → AnalyticsPage
| Object Attribute | UI Element | Component |
|-----------------|------------|-----------|
| `case_duration_stats` | Distribution chart | Chart (custom) |
| `activity_durations[]` | Heatmap/Table | DataTable or Heatmap |
| `bottlenecks[]` | Alert list | List with severity |
| `throughput_daily[]` | Time series | Line Chart |
| `resource_workloads[]` | Bar chart | Bar Chart |

**Current Implementation:** `src/features/analytics/pages/AnalyticsPage.tsx`

---

# Component Inventory

## Existing Components (Production Ready)

### Layout Components
```typescript
// AppShell - Main application container
<AppShell
  logo={<Logo />}
  navItems={[
    { id: 'workspace', icon: <FolderIcon />, label: 'Workspace', path: '/workspace' },
    { id: 'explorer', icon: <SearchIcon />, label: 'Explorer', path: '/explorer' },
    // ...
  ]}
  bottomNavItems={[
    { id: 'ai', icon: <BrainIcon />, label: 'AI Assistant', path: '/ai' },
  ]}
  userName="Naman"
  notificationCount={3}
/>
```

### Data Display Components
```typescript
// MetricCard - KPI display
<MetricCard
  title="Total Cases"
  value={12450}
  prefix={<CaseIcon />}
  trend={{ value: 12.5, isPositive: true, label: "vs last month" }}
  status="success"
  onClick={() => navigate('/cases')}
/>

// DataTable - Feature-rich table
<DataTable
  columns={columns}
  data={variants}
  searchable
  searchPlaceholder="Search variants..."
  pagination={{ pageSize: 20 }}
  onRowClick={(row) => openVariant(row.id)}
/>

// ProcessNode - DFG node (React Flow)
<ProcessNode
  data={{
    label: "Submit Application",
    count: 1250,
    isStart: false,
    isEnd: false,
  }}
  selected={false}
/>
```

### State Components
```typescript
// EmptyState - No data placeholder
<EmptyState
  icon={<FileIcon />}
  title="No Event Logs"
  description="Upload your first event log to start mining"
  actionLabel="Upload Log"
  onAction={() => setUploadOpen(true)}
/>

// LoadingState variants
<LoadingState type="skeleton" /> // Card skeleton
<LoadingState type="spinner" />  // Centered spinner
<MetricsLoadingState />          // 4 metric cards skeleton
<TableLoadingState />            // Table with skeleton rows
<PageLoadingState />             // Full page skeleton
```

### Error Components
```typescript
// QueryError - Intelligent error display
<QueryError
  error={error}
  variant="card"
  onRetry={refetch}
  title="Failed to load process data"
/>

// ErrorBoundary - Catch component errors
<ErrorBoundary
  fallback={<ErrorFallback />}
  onError={(error) => logError(error)}
>
  <ChildComponent />
</ErrorBoundary>
```

### Page Wrapper
```typescript
// FeaturePage - Standard page layout
<FeaturePage
  title="Process Explorer"
  breadcrumb={[
    { label: 'Home', href: '/' },
    { label: 'Explorer' },
  ]}
  isLoading={isLoading}
  error={error}
  onRetry={refetch}
  isEmpty={!data?.items.length}
  emptyState={{
    title: 'No processes',
    description: 'Upload an event log to get started',
    actionLabel: 'Upload',
    onAction: () => openUpload(),
  }}
  actions={
    <Button type="primary" icon={<UploadIcon />}>
      Upload Log
    </Button>
  }
>
  <PageSection title="Recent Processes">
    <ProcessGrid data={data.items} />
  </PageSection>
</FeaturePage>
```

---

# Gap Analysis

## Missing Components (Priority Order)

### P0 - Critical for Core Flows

| Component | Purpose | Object Model Reference |
|-----------|---------|----------------------|
| **UploadWizard** | Multi-step file upload with column mapping | Event Log (source_type, column_mapping) |
| **StateIndicator** | Visual state machine indicator | All stateful objects |
| **FilterBuilder** | Visual filter construction | Filter Preset (conditions[]) |
| **VariantPath** | Visual activity sequence | Variant (sequence[]) |

### P1 - Required for Discovery Layer

| Component | Purpose | Object Model Reference |
|-----------|---------|----------------------|
| **PetriNetViewer** | Petri net visualization | Petri Net (places, transitions, arcs) |
| **BPMNViewer** | BPMN model viewer | BPMN Model (nodes, flows) |
| **ProcessTreeViewer** | Tree visualization | Process Tree (root, children) |
| **ModelComparisonPanel** | Side-by-side model comparison | Multiple Process Models |

### P1 - Required for Analysis Layer

| Component | Purpose | Object Model Reference |
|-----------|---------|----------------------|
| **DeviationList** | Conformance deviation display | Deviation (type, expected, actual) |
| **BottleneckCard** | Bottleneck visualization | Bottleneck (location, severity, impact) |
| **PerformanceHeatmap** | Activity duration heatmap | ActivityDuration[] |
| **ThroughputChart** | Time series throughput | ThroughputPoint[] |

### P2 - Required for Intelligence Layer

| Component | Purpose | Object Model Reference |
|-----------|---------|----------------------|
| **PredictionCard** | ML prediction display | Prediction Model (type, confidence) |
| **RiskIndicator** | Risk score visualization | Risk Score |
| **RecommendationList** | Action recommendations | Recommendation[] |
| **RootCauseTree** | Factor analysis tree | RootCauseFactor[] |

### P2 - Required for OCEL/Object-Centric

| Component | Purpose | Object Model Reference |
|-----------|---------|----------------------|
| **ObjectTypeSelector** | Object type picker | ObjectType[] |
| **ObjectRelationGraph** | E2O/O2O visualization | OCEL Relations |

### P3 - Automation Layer

| Component | Purpose | Object Model Reference |
|-----------|---------|----------------------|
| **TriggerBuilder** | Automation trigger config | Trigger (type, config) |
| **ActionDefinitionForm** | Action setup | ActionDefinition |
| **AlertList** | Alert management | Alert[] |
| **WorkQueuePanel** | Case prioritization | WorkQueueItem[] |
| **DashboardBuilder** | Custom dashboard creation | Dashboard (widgets[]) |

---

## Missing Pages

### P0 - Core Flow Pages
| Page | Route | Purpose |
|------|-------|---------|
| UploadPage | `/upload` | Event log upload wizard |
| MappingPage | `/upload/:id/mapping` | Column mapping step |

### P1 - Analysis Pages
| Page | Route | Purpose |
|------|-------|---------|
| ConformanceDetailPage | `/conformance/:resultId` | Detailed deviation view |
| VariantDetailPage | `/variants/:variantId` | Single variant analysis |
| ResourceAnalysisPage | `/resources` | Organizational mining |

### P2 - Intelligence Pages
| Page | Route | Purpose |
|------|-------|---------|
| SimulationPage | `/simulation` | What-if analysis |
| PredictionDetailPage | `/predictions/:modelId` | Model details & predictions |
| RootCausePage | `/analysis/root-cause` | Root cause analysis |

### P3 - Operations Pages
| Page | Route | Purpose |
|------|-------|---------|
| WorkQueuePage | `/queues/:queueId` | Work queue management |
| AlertsPage | `/alerts` | Alert management |
| AutomationPage | `/automation` | Trigger/action setup |
| DashboardEditorPage | `/dashboards/:id/edit` | Dashboard customization |

---

## Missing Backend Endpoints

### P0 - Critical
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/processes/{id}/status` | PATCH | Update event log status |
| `/processes/{id}/validate` | POST | Trigger validation |

### P1 - Analysis
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/conformance/{id}/deviations` | GET | Paginated deviations |
| `/analytics/{id}/root-cause` | POST | Root cause analysis |
| `/organizational/{id}/roles` | GET | Discovered roles |
| `/organizational/{id}/handovers` | GET | Handover network |

### P2 - Intelligence
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/simulation/models` | GET/POST | Simulation model CRUD |
| `/simulation/runs` | GET/POST | Simulation execution |
| `/recommendations/{caseId}` | GET | Case recommendations |

### P3 - Automation
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/actions` | CRUD | Action definitions |
| `/triggers` | CRUD | Trigger management |
| `/alerts` | CRUD | Alert management |
| `/queues` | CRUD | Work queue management |
| `/dashboards` | CRUD | Dashboard management |

---

# Flow Specifications

## Flow 1: Event Log Upload (P0)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SELECT    │────▶│   UPLOAD    │────▶│    MAP      │────▶│   READY     │
│    FILE     │     │   (async)   │     │  COLUMNS    │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Drag & Drop │     │  Progress   │     │ Column      │     │ Statistics  │
│ or Browse   │     │  Bar        │     │ Mapper      │     │ Summary     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Components Required:**
- `UploadDropzone` - File selection UI
- `UploadProgress` - Progress indicator with cancel
- `ColumnMapper` - Column mapping interface
- `MappingPreview` - Sample data preview
- `StatisticsSummary` - Post-processing summary

**State Management:**
```typescript
type UploadState =
  | { status: 'idle' }
  | { status: 'uploading', progress: number, filename: string }
  | { status: 'validating', logId: string }
  | { status: 'mapping', logId: string, columns: DetectedColumn[] }
  | { status: 'processing', logId: string }
  | { status: 'complete', logId: string, statistics: Statistics }
  | { status: 'error', error: string, step: string }
```

---

## Flow 2: Process Discovery (P0)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SELECT    │────▶│  CONFIGURE  │────▶│   DISCOVER  │────▶│  VISUALIZE  │
│    LOG      │     │  ALGORITHM  │     │   (async)   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Log Picker  │     │ Algorithm   │     │  Progress   │     │ Interactive │
│             │     │ Selector    │     │  with Job   │     │ DFG/BPMN    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Components Required:**
- `LogSelector` - Event log picker with preview
- `AlgorithmCard` - Algorithm option with description
- `ParameterForm` - Algorithm-specific parameters
- `DiscoveryProgress` - Async job status
- `ModelViewer` - Multi-format model visualization

---

## Flow 3: Conformance Checking (P1)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SELECT    │────▶│   SELECT    │────▶│    CHECK    │────▶│   REVIEW    │
│    LOG      │     │   MODEL     │     │  (async)    │     │ DEVIATIONS  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Components Required:**
- `ModelPicker` - Select reference model
- `ConformanceConfig` - Method selection (token/alignment)
- `ConformanceResults` - Fitness/precision gauges
- `DeviationExplorer` - Interactive deviation list

---

## Flow 4: Predictive Analytics (P2)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SELECT    │────▶│  CONFIGURE  │────▶│    TRAIN    │────▶│   PREDICT   │
│   TARGET    │     │   MODEL     │     │   (async)   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Target Type │     │ Algorithm   │     │  Training   │     │ Predictions │
│ Picker      │     │ & Features  │     │  Progress   │     │ Table/List  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Prediction Types:**
- Next Activity
- Remaining Time
- Outcome (completion)
- Risk Score (SLA breach)

---

## Flow 5: Dashboard Creation (P3)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CREATE    │────▶│    ADD      │────▶│  CONFIGURE  │────▶│    SAVE     │
│  DASHBOARD  │     │  WIDGETS    │     │   LAYOUT    │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Widget Types:**
- `kpi_card` - MetricCard
- `time_series` - Line chart
- `bar_chart` - Bar chart
- `process_map` - DFG mini viewer
- `variant_list` - Top variants
- `case_table` - Case listing
- `alert_list` - Active alerts

---

# Implementation Roadmap

## Phase 1: Core Foundation (P0)

### Sprint 1: Upload Flow
**Goal:** Complete event log upload with column mapping

| Task | Component/File | Effort |
|------|---------------|--------|
| Create UploadDropzone | design-system/UploadDropzone.tsx | M |
| Create ColumnMapper | design-system/ColumnMapper.tsx | L |
| Create MappingPreview | design-system/MappingPreview.tsx | S |
| Build UploadPage | features/upload/UploadPage.tsx | L |
| Add upload hooks | features/upload/hooks/index.ts | M |
| Integrate with backend | SDK upload module | M |

### Sprint 2: Explorer Enhancement
**Goal:** Production-ready process exploration

| Task | Component/File | Effort |
|------|---------------|--------|
| Extract VariantPath component | design-system/VariantPath.tsx | M |
| Create FilterBuilder | design-system/FilterBuilder.tsx | L |
| Add StateIndicator | design-system/StateIndicator.tsx | S |
| Enhance DFG interactions | features/explorer/DFGViewer.tsx | M |
| Add variant detail view | features/explorer/VariantDetail.tsx | M |

### Sprint 3: State Machine Integration
**Goal:** Proper lifecycle management

| Task | Component/File | Effort |
|------|---------------|--------|
| Add EventLog status field | backend/models/orm.py | S |
| Create status endpoints | backend/routers/processes.py | S |
| Add frontend status hooks | features/explorer/hooks.ts | M |
| Implement status transitions | UI state indicators | M |

---

## Phase 2: Analysis Layer (P1)

### Sprint 4: Conformance
**Goal:** Full conformance checking flow

| Task | Component/File | Effort |
|------|---------------|--------|
| Create DeviationList | design-system/DeviationList.tsx | M |
| Build ConformanceDetailPage | features/conformance/ConformanceDetailPage.tsx | L |
| Add conformance hooks | features/conformance/hooks/index.ts | M |
| Enhance ConformanceTab | features/analytics/ConformanceTab.tsx | M |

### Sprint 5: Performance Analytics
**Goal:** Comprehensive performance analysis

| Task | Component/File | Effort |
|------|---------------|--------|
| Create BottleneckCard | design-system/BottleneckCard.tsx | M |
| Create PerformanceHeatmap | design-system/PerformanceHeatmap.tsx | L |
| Create ThroughputChart | design-system/ThroughputChart.tsx | M |
| Build PerformanceDashboard | features/analytics/PerformanceDashboard.tsx | L |

### Sprint 6: Organizational Mining
**Goal:** Resource and handover analysis

| Task | Component/File | Effort |
|------|---------------|--------|
| Create HandoverNetwork | design-system/HandoverNetwork.tsx | L |
| Create ResourceList | design-system/ResourceList.tsx | M |
| Build ResourcePage | features/organizational/ResourcePage.tsx | L |
| Add organizational hooks | features/organizational/hooks/index.ts | M |

---

## Phase 3: Intelligence Layer (P2)

### Sprint 7: Predictions
**Goal:** ML prediction interface

| Task | Component/File | Effort |
|------|---------------|--------|
| Create PredictionCard | design-system/PredictionCard.tsx | M |
| Create RiskIndicator | design-system/RiskIndicator.tsx | S |
| Enhance PredictionsPage | features/ai/PredictionsPage.tsx | L |
| Add prediction batch UI | features/ai/BatchPredictions.tsx | M |

### Sprint 8: Recommendations
**Goal:** Prescriptive analytics

| Task | Component/File | Effort |
|------|---------------|--------|
| Create RecommendationList | design-system/RecommendationList.tsx | M |
| Create RootCauseTree | design-system/RootCauseTree.tsx | L |
| Build RecommendationsPage | features/ai/RecommendationsPage.tsx | L |

### Sprint 9: OCEL Support
**Goal:** Object-centric process mining

| Task | Component/File | Effort |
|------|---------------|--------|
| Create ObjectTypeSelector | design-system/ObjectTypeSelector.tsx | M |
| Create ObjectRelationGraph | design-system/ObjectRelationGraph.tsx | L |
| Build OCELExplorerPage | features/ocpm/OCELExplorerPage.tsx | L |

---

## Phase 4: Automation Layer (P3)

### Sprint 10: Alerting
**Goal:** Alert management

| Task | Component/File | Effort |
|------|---------------|--------|
| Create AlertCard | design-system/AlertCard.tsx | M |
| Build AlertsPage | features/alerts/AlertsPage.tsx | L |
| Add alert backend | backend/routers/alerts.py | L |

### Sprint 11: Work Queues
**Goal:** Case prioritization

| Task | Component/File | Effort |
|------|---------------|--------|
| Create WorkQueuePanel | design-system/WorkQueuePanel.tsx | L |
| Build WorkQueuePage | features/queues/WorkQueuePage.tsx | L |
| Add queue backend | backend/routers/queues.py | L |

### Sprint 12: Dashboards
**Goal:** Custom dashboard builder

| Task | Component/File | Effort |
|------|---------------|--------|
| Create DashboardGrid | design-system/DashboardGrid.tsx | L |
| Create WidgetPicker | design-system/WidgetPicker.tsx | M |
| Build DashboardEditorPage | features/dashboards/DashboardEditorPage.tsx | XL |

---

# Design Tokens Reference

## Color System

```typescript
const colors = {
  // Primary - Precision Cobalt
  primary: {
    50: '#EFF6FF',
    100: '#DBEAFE',
    200: '#BFDBFE',
    400: '#60A5FA',
    500: '#0F52FF',  // Main
    600: '#0A3FCC',
    700: '#1E40AF',
  },

  // Semantic
  success: '#10B981',  // Emerald
  warning: '#F59E0B',  // Amber
  error: '#EF4444',    // Red
  info: '#3B82F6',     // Blue

  // Neutral (9-step)
  neutral: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },

  // Surface
  surface: {
    page: '#F8FAFC',
    sidebar: '#FFFFFF',
    card: '#FFFFFF',
    cardHover: '#F9FAFB',
    dark: '#1F2937',
    darkHover: '#374151',
  },
}
```

## Spacing Scale (4px base)

```typescript
const spacing = {
  0: '0px',
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
}
```

## Typography

```typescript
const typography = {
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, system-ui, sans-serif',
  fontSize: {
    xs: '11px',
    sm: '12px',
    base: '14px',
    md: '16px',
    lg: '18px',
    xl: '24px',
    '2xl': '32px',
    '3xl': '42px',
    '4xl': '56px',
    '5xl': '75px',
  },
  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
}
```

## Border Radius

```typescript
const radius = {
  xs: '2px',   // Buttons, inputs (architectural precision)
  sm: '4px',   // Small elements
  md: '8px',   // Cards, containers
  lg: '16px',  // Page surfaces
  xl: '24px',  // Large containers
  full: '9999px', // Pills, avatars
}
```

## Shadows

```typescript
const shadow = {
  xs: '0 1px 2px rgba(0, 0, 0, 0.04)',
  sm: '0 1px 3px rgba(0, 0, 0, 0.08)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.15)',
  focus: '0 0 0 3px rgba(37, 99, 235, 0.2)',
}
```

## Animation

```typescript
const animation = {
  duration: {
    fast: '100ms',
    normal: '150ms',
    moderate: '200ms',
    slow: '300ms',
  },
  easing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',
    in: 'cubic-bezier(0.4, 0, 1, 1)',
    out: 'cubic-bezier(0, 0, 0.2, 1)',
    inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },
}
```

## Layout Constants

```typescript
const layout = {
  sidebar: {
    width: 240,
    collapsedWidth: 64,
  },
  header: {
    height: 64,
  },
  controlHeight: {
    sm: 32,
    default: 40,
    lg: 48,
  },
}
```

---

# Appendix: Component Naming Conventions

## File Naming
- Components: `PascalCase.tsx` (e.g., `MetricCard.tsx`)
- Hooks: `camelCase.ts` (e.g., `useProcesses.ts`)
- Types: `types.ts` (per feature)
- Stories: `ComponentName.stories.tsx`

## Component Props Pattern
```typescript
interface MetricCardProps {
  // Required
  title: string;
  value: number | string;

  // Optional display
  prefix?: ReactNode;
  suffix?: string;
  icon?: ReactNode;

  // Optional behavior
  trend?: {
    value: number;
    isPositive: boolean;
    label?: string;
  };
  status?: 'default' | 'success' | 'warning' | 'error';
  loading?: boolean;

  // Optional interaction
  onClick?: () => void;

  // Styling
  className?: string;
  style?: CSSProperties;
}
```

## Hook Pattern
```typescript
// Query hook
export const useProcesses = createQueryHook<ProcessListResponse, ProcessListOptions>({
  queryKey: (options) => ['processes', 'list', options],
  queryFn: (sdk, options) => sdk.processes.list(options),
  staleTime: 5 * 60 * 1000,
});

// Mutation hook
export const useDeleteProcess = createMutationHook<void, string>({
  mutationFn: (sdk, id) => sdk.processes.delete(id),
  invalidateKeys: [['processes', 'list']],
  onSuccessMessage: 'Process deleted successfully',
});
```

---

**Document Version:** 1.0
**Last Updated:** December 2024
**Maintainer:** Fictive Kin Design Studio

---

> "Solve through subtraction. Most products suffer from feature creep. The right amount of complexity is the minimum needed for the current task."
>
> — Fictive Kin Design Philosophy
