# Lumina: Enterprise Process Mining Platform - Frontend Plan

## Decisions
- **App Strategy**: New app (`apps/lumina/`) - fresh start, parallel with existing
- **MVP Scope**: Full suite including Predictions (Data → Explorer → Analytics → Conformance → Predictions)
- **Auth**: Mock auth for now, real auth later
- **Code Reuse**: 100% fresh start - new files, new patterns

---

## Business Requirements Summary

**Source**: `/Users/namanagarwal/system/docs/businessusecase.md`

### Scope: 237 Business Activities across 15 Use Cases

| Use Case | Activities | PM4PY Coverage | Custom Build |
|----------|------------|----------------|--------------|
| Process Discovery | 15 | 12 | 3 |
| Variant Analysis | 15 | 10 | 5 |
| Conformance Checking | 22 | 15 | 7 |
| Performance Analysis | 20 | 14 | 6 |
| Bottleneck Detection | 12 | 8 | 4 |
| Root Cause Analysis | 13 | 6 | 7 |
| Organizational Mining | 15 | 10 | 5 |
| Predictive Monitoring | 15 | 8 | 7 |
| Drift Detection | 12 | 6 | 6 |
| Object-Centric (OCEL) | 19 | 16 | 3 |
| RPA Discovery | 14 | 8 | 6 |
| Compliance Monitoring | 17 | 10 | 7 |
| Simulation & What-If | 14 | 6 | 8 |
| Dashboard & Reporting | 18 | 4 | 14 |
| Alerting & Monitoring | 16 | 2 | 14 |

### Primary Personas & Their Daily Tasks

**Process Analyst** (Power User)
- Daily: View process model, filter data, analyze variants, view statistics
- Weekly: Upload logs, run discovery, create dashboards, train ML models
- Journey: Import → Explore → Discover → Analyze → Report

**Compliance Officer**
- Daily: Check conformance scores, review violations, view compliance dashboard
- Weekly: Run compliance checks, generate audit reports, set alerts
- Journey: Define Rules → Check → Review Violations → Remediate → Report

**Operations Manager**
- Daily: Monitor KPIs, view alerts, check running cases
- Weekly: Identify bottlenecks, run root cause analysis, simulate changes
- Journey: Monitor → Identify Issues → Analyze Causes → Optimize → Track

---

## 16 Application Screens (from Business Requirements)

| # | Screen | Primary Activities | Priority |
|---|--------|-------------------|----------|
| 1 | **Home Dashboard** | KPI overview, alerts, quick actions | P0 |
| 2 | **Data Import** | Upload, column mapping, validation | P0 |
| 3 | **Log Explorer** | Statistics, filtering, preview | P0 |
| 4 | **Process Discovery** | Algorithm selection, discovery execution | P0 |
| 5 | **Model Viewer** | DFG/Petri visualization, annotation | P0 |
| 6 | **Variant Explorer** | Variant list, comparison, happy path | P1 |
| 7 | **Performance Analysis** | Duration, throughput, bottlenecks | P1 |
| 8 | **Conformance Checker** | Fitness/precision, deviations | P1 |
| 9 | **Predictive Monitoring** | Model training, live predictions | P2 |
| 10 | **Social Network** | SNA graphs, resource profiles | P2 |
| 11 | **OCEL Analysis** | Object-centric mining | P3 |
| 12 | **Simulation Studio** | What-if scenarios, comparison | P2 |
| 13 | **Alert Management** | Alert config, history, acknowledgment | P2 |
| 14 | **Report Builder** | Dashboard creation, export, scheduling | P2 |
| 15 | **Compliance Center** | Rules, audit trail, evidence | P2 |
| 16 | **Settings** | User, workspace, integrations | P1 |

---

## Design System (from user input)

```typescript
// tokens.ts - Celonis-inspired design tokens
export const tokens = {
  colorPrimary: '#0052CC',
  colorPrimaryHover: '#0065FF',
  colorPrimaryActive: '#003D99',
  colorBgBase: '#FFFFFF',
  colorBgLayout: '#F4F5F7',
  colorText: '#172B4D',
  colorTextSecondary: '#5E6C84',
  colorBorder: '#DFE1E6',
  colorSuccess: '#36B37E',
  colorWarning: '#FFAB00',
  colorError: '#DE350B',
  padding: 12,
  paddingXS: 4,
  paddingSM: 8,
  paddingLG: 16,
  fontFamily: "'Inter', -apple-system, sans-serif",
  fontSize: 13,
  borderRadius: 4,
};

// antd-theme.ts - Ant Design 6 with compact algorithm
export const lightTheme: ThemeConfig = {
  algorithm: theme.compactAlgorithm, // HIGH DENSITY
  token: { ...tokens },
  components: {
    Layout: { headerBg: '#FFFFFF', headerHeight: 48 },
    Menu: { itemHeight: 36 },
    Table: { headerBg: '#FAFBFC', cellPaddingBlock: 8 },
    Button: { controlHeight: 32 },
  },
};
```

---

## 7 Core Business Capabilities

### 1. PROCESS VISIBILITY ("See the Truth")

**Business Need**: "Show me how my process ACTUALLY works"

**Questions Answered**:
- What paths do cases take?
- What's the happy path vs. exceptions?
- How complex is our process really?
- Where do cases go off-track?

**User Journey**:
```
Upload Data → Auto-discover process → View DFG →
Filter by variant → Drill into specific paths →
Compare expected vs actual → Share findings
```

**Key Screens**:
- **Process Explorer**: Interactive DFG with zoom, pan, filter
- **Variant Analyzer**: List variants by frequency, compare paths
- **Case Inspector**: Drill into individual case journeys

---

### 2. PERFORMANCE ANALYSIS ("Find the Waste")

**Business Need**: "Where is time/money being wasted?"

**Questions Answered**:
- Where are bottlenecks?
- Which activities take too long?
- Where does rework happen?
- Is performance improving or degrading?

**User Journey**:
```
View KPI dashboard → Identify bottleneck activity →
Analyze root cause (time? resources? rework?) →
Quantify impact ($, time) → Prioritize fixes → Track improvement
```

**Key Screens**:
- **Performance Dashboard**: KPI tiles, trend charts, bottleneck heatmap
- **Bottleneck Deep-dive**: Activity-level analysis, waiting vs service time
- **Rework Analysis**: Loop detection, rework rates by activity
- **Throughput Monitor**: Cases over time, SLA tracking

---

### 3. CONFORMANCE ("Ensure Compliance")

**Business Need**: "Are we following the rules?"

**Questions Answered**:
- What % of cases follow the defined process?
- What are the deviations?
- Which deviations are violations vs. acceptable variants?
- Which cases need investigation?

**User Journey**:
```
Define/import reference model → Run conformance check →
View fitness score → Drill into deviations →
Classify (violation/acceptable) → Generate audit report
```

**Key Screens**:
- **Conformance Dashboard**: Fitness/precision scores, deviation summary
- **Deviation Explorer**: List deviations by type, frequency, severity
- **Case Audit**: Individual case vs. expected path overlay
- **Compliance Report**: Exportable audit documentation

---

### 4. PREDICTIONS ("See the Future")

**Business Need**: "Predict problems before they happen"

**Questions Answered**:
- Will this case be delayed?
- What activity comes next?
- Which cases are at risk?
- Where should I intervene now?

**User Journey**:
```
Select prediction target (time? next activity?) →
Train model on historical data → Evaluate accuracy →
Deploy model → View predictions on active cases →
Set alerts for at-risk cases → Take action
```

**Key Screens**:
- **Model Studio**: Train, evaluate, compare models
- **Prediction Dashboard**: At-risk cases, prediction accuracy
- **Case Predictions**: Per-case predictions with confidence
- **Alert Configuration**: Set thresholds, notification rules

---

### 5. RESOURCE INTELLIGENCE ("Optimize Your Team")

**Business Need**: "Understand and optimize how people work"

**Questions Answered**:
- Who does what?
- Who collaborates with whom?
- Is workload balanced?
- Who are bottleneck resources?

**User Journey**:
```
Analyze resource behavior → View social network →
Identify workload imbalances → Find collaboration patterns →
Discover informal roles → Recommend rebalancing
```

**Key Screens**:
- **Resource Network**: SNA visualization (handover, collaboration)
- **Workload Dashboard**: Distribution charts, utilization metrics
- **Resource Profiles**: Individual resource performance cards
- **Role Discovery**: Auto-detected roles and assignments

---

### 6. SIMULATION ("Test Before You Change")

**Business Need**: "What if we made this change?"

**Questions Answered**:
- What if we add resources?
- What if we automate a step?
- What's the ROI of this improvement?
- What's the optimal configuration?

**User Journey**:
```
Select baseline process → Define scenario (add resources,
change routing, etc.) → Run simulation →
Compare baseline vs scenario → Calculate ROI →
Build business case → Present to stakeholders
```

**Key Screens**:
- **Scenario Builder**: Define what-if parameters
- **Simulation Results**: Side-by-side comparison
- **Capacity Planner**: Resource requirement calculator
- **ROI Calculator**: Cost/benefit analysis

---

### 7. DATA FOUNDATION ("Get Data In")

**Business Need**: "Connect my systems and ensure data quality"

**Questions Answered**:
- Is my data format correct?
- Are there quality issues?
- Is data refreshing correctly?
- What systems are connected?

**User Journey**:
```
Upload file / connect system → Map columns →
Validate data quality → Review warnings →
Confirm ingestion → Set refresh schedule
```

**Key Screens**:
- **Data Hub**: List all event logs, upload new
- **Upload Wizard**: Column mapping, validation, preview
- **Quality Report**: Data quality scores, issues
- **Connectors**: System integrations (SAP, Salesforce, etc.)

---

## Information Architecture

### Primary Navigation (Sidebar)
```
LOGO: Lumina

ANALYZE
├── Dashboard (global overview)
├── Process Explorer (DFG visualization)
├── Analytics (performance metrics)
└── Variants (path analysis)

MONITOR
├── Conformance (compliance checking)
├── Predictions (ML insights)
└── Alerts (notifications)

OPTIMIZE
├── Resources (organizational mining)
├── Simulation (what-if)
└── Automation (workflows)

DATA
├── Event Logs (data hub)
├── Models (discovered models)
└── Connectors (integrations)

SETTINGS
├── Workspace
├── Users
└── API Keys
```

### URL Structure
```
/                           → Dashboard
/explorer/:logId            → Process Explorer
/explorer/:logId/variants   → Variant Analysis
/analytics/:logId           → Performance Analytics
/analytics/:logId/bottlenecks → Bottleneck Deep-dive
/conformance/:logId         → Conformance Dashboard
/conformance/:logId/deviations → Deviation Explorer
/predictions/:logId         → Prediction Dashboard
/predictions/studio         → Model Training Studio
/resources/:logId           → Resource Network
/resources/:logId/profiles  → Resource Profiles
/simulation/:logId          → Simulation Lab
/data/logs                  → Event Log List
/data/logs/:id              → Log Detail
/data/upload                → Upload Wizard
/data/models                → Model List
/data/connectors            → Connectors
/settings/*                 → Settings pages
```

---

## Key Page Designs

### 1. Global Dashboard (`/`)

**Purpose**: Executive overview across all processes

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header: "Dashboard" + Date Range Picker + Refresh       │
├─────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│ │Total    │ │Active   │ │Avg Cycle│ │Conformance│       │
│ │Cases    │ │Logs     │ │Time     │ │Score     │        │
│ │125,432  │ │12       │ │4.2 days │ │94.2%     │        │
│ │↑ 12%    │ │         │ │↓ 8%     │ │↑ 2%     │        │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘        │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────┐ ┌─────────────────────────┐│
│ │ Cases Over Time (Line)  │ │ Top Bottlenecks (Bar)   ││
│ │ [Chart]                 │ │ [Chart]                 ││
│ └─────────────────────────┘ └─────────────────────────┘│
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────┐ ┌─────────────────────────┐│
│ │ Recent Event Logs       │ │ Alerts & Notifications  ││
│ │ - Order-to-Cash  12k    │ │ - 3 SLA breaches today  ││
│ │ - Procure-to-Pay 8k     │ │ - Model accuracy dropped││
│ │ - Incident Mgmt  2k     │ │ - New connector ready   ││
│ └─────────────────────────┘ └─────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

**Data Sources**:
- `sdk.logs.list()` → Recent logs
- `sdk.analytics.getPerformanceDashboard()` → Aggregated KPIs
- `sdk.analytics.getBottlenecks()` → Top bottlenecks

---

### 2. Process Explorer (`/explorer/:logId`)

**Purpose**: Interactive process visualization

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header: Log Name + Breadcrumb                           │
│ Tabs: [DFG] [Petri Net] [BPMN] [Variants]              │
├────────────────┬────────────────────────────────────────┤
│ FILTERS        │ PROCESS MAP (ReactFlow)               │
│ ┌────────────┐ │ ┌────────────────────────────────────┐│
│ │Activities  │ │ │                                    ││
│ │☑ Create    │ │ │    [Start] ──► [Review] ──►       ││
│ │☑ Approve   │ │ │                    │              ││
│ │☐ Reject    │ │ │                    ▼              ││
│ │            │ │ │              [Approve] ──► [End]  ││
│ │Time Range  │ │ │                    │              ││
│ │[===|===]   │ │ │                    ▼              ││
│ │            │ │ │              [Reject] ──►         ││
│ │Variants    │ │ │                                    ││
│ │Top 5 ▼     │ │ └────────────────────────────────────┘│
│ │            │ │ Zoom: [-][100%][+] | Fit | Export     │
│ └────────────┘ │                                        │
├────────────────┴────────────────────────────────────────┤
│ DETAILS PANEL (collapsible)                             │
│ Selected: "Approve" activity                            │
│ Frequency: 12,432 | Avg Duration: 2.3h | Resources: 5   │
└─────────────────────────────────────────────────────────┘
```

**Interactions**:
- Click node → Show activity details
- Click edge → Show transition details
- Drag to pan, scroll to zoom
- Filter panel updates DFG in real-time
- Color coding: frequency (blue gradient) or duration (red = slow)

**Data Sources**:
- `sdk.visualization.getDFG(logId)` → Nodes/edges
- `sdk.filtering.getFilterOptions(logId)` → Filter options
- `sdk.logs.get(logId)` → Log metadata

---

### 3. Analytics Dashboard (`/analytics/:logId`)

**Purpose**: Performance metrics and bottleneck identification

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header: "Performance Analytics" + Log Selector          │
├─────────────────────────────────────────────────────────┤
│ KPI ROW                                                 │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │
│ │Cycle   │ │Through-│ │Bottle- │ │Rework  │ │SLA     │ │
│ │Time    │ │put     │ │necks   │ │Rate    │ │Breach  │ │
│ │4.2 days│ │52/day  │ │3       │ │12%     │ │8%      │ │
│ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐ │
│ │ BOTTLENECK HEATMAP                                  │ │
│ │ Activity      │ Frequency │ Waiting │ Service │ ●   │ │
│ │ ─────────────────────────────────────────────────── │ │
│ │ Manual Review │ 8,234     │ 18.2h   │ 2.1h    │ 🔴  │ │
│ │ Approval      │ 12,432    │ 4.5h    │ 0.5h    │ 🟡  │ │
│ │ Data Entry    │ 15,123    │ 1.2h    │ 0.8h    │ 🟢  │ │
│ └─────────────────────────────────────────────────────┘ │
├──────────────────────────┬──────────────────────────────┤
│ CYCLE TIME DISTRIBUTION  │ THROUGHPUT TREND             │
│ [Histogram]              │ [Line Chart]                 │
│                          │                              │
└──────────────────────────┴──────────────────────────────┘
```

**Data Sources**:
- `sdk.analytics.getPerformanceDashboard(logId)`
- `sdk.analytics.getBottlenecks(logId)`
- `sdk.analytics.getCycleTime(logId)`
- `sdk.analytics.getThroughput(logId)`
- `sdk.analytics.getRework(logId)`

---

### 4. Conformance Dashboard (`/conformance/:logId`)

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header: "Conformance" + Model Selector                  │
├─────────────────────────────────────────────────────────┤
│ CONFORMANCE SCORE                                       │
│ ┌──────────────────┐ ┌──────────────────┐              │
│ │ FITNESS          │ │ PRECISION        │              │
│ │ ████████░░ 82%   │ │ ██████████ 96%   │              │
│ │ 10,234 fitting   │ │                  │              │
│ │ 2,198 deviating  │ │                  │              │
│ └──────────────────┘ └──────────────────┘              │
├─────────────────────────────────────────────────────────┤
│ TOP DEVIATIONS                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Deviation Type        │ Cases │ % Total │ Severity  │ │
│ │ ────────────────────────────────────────────────────│ │
│ │ Skipped "Approval"    │ 1,234 │ 9.9%    │ High  🔴  │ │
│ │ Extra "Re-review"     │ 542   │ 4.4%    │ Med   🟡  │ │
│ │ Wrong sequence A→C    │ 422   │ 3.4%    │ Low   🟢  │ │
│ └─────────────────────────────────────────────────────┘ │
│ [View All Deviations →]                                 │
├─────────────────────────────────────────────────────────┤
│ DEVIATION TREND (Line chart over time)                  │
└─────────────────────────────────────────────────────────┘
```

---

### 5. Prediction Studio (`/predictions/studio`)

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header: "Prediction Studio"                             │
│ Tabs: [Train Model] [My Models] [Predictions]           │
├─────────────────────────────────────────────────────────┤
│ TRAIN NEW MODEL                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 1. Select Event Log     [Order-to-Cash ▼]          │ │
│ │                                                     │ │
│ │ 2. Prediction Target    ○ Next Activity            │ │
│ │                         ● Remaining Time           │ │
│ │                         ○ Case Outcome             │ │
│ │                                                     │ │
│ │ 3. Algorithm            [Random Forest ▼]          │ │
│ │                                                     │ │
│ │ 4. Model Name           [Q4 Cycle Time Predictor]  │ │
│ │                                                     │ │
│ │                    [Train Model]                    │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ MY MODELS                                               │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Model Name        │ Target    │ Accuracy │ Status  │  │
│ │ ─────────────────────────────────────────────────  │  │
│ │ Q4 Cycle Pred     │ Time      │ 84%      │ Ready   │  │
│ │ Next Step Model   │ Activity  │ 91%      │ Ready   │  │
│ │ [Training...]     │ Outcome   │ --       │ 43%     │  │
│ └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Nx Monorepo Structure

```
frontend/
├── apps/
│   ├── lumina/                      # Main SPA
│   │   ├── src/
│   │   │   ├── main.tsx
│   │   │   ├── app/
│   │   │   │   ├── App.tsx          # Root with providers
│   │   │   │   ├── routes.tsx       # Route definitions
│   │   │   │   └── layout/
│   │   │   │       ├── AppShell.tsx
│   │   │   │       ├── Sidebar.tsx
│   │   │   │       └── Header.tsx
│   │   │   └── pages/               # Route pages (thin, compose domains)
│   │   │       ├── dashboard/
│   │   │       ├── explorer/
│   │   │       ├── analytics/
│   │   │       ├── conformance/
│   │   │       ├── predictions/
│   │   │       ├── resources/
│   │   │       ├── simulation/
│   │   │       ├── data/
│   │   │       └── settings/
│   │   ├── rsbuild.config.ts
│   │   └── project.json
│   └── lumina-e2e/                  # E2E tests
│
├── libs/
│   ├── shared/
│   │   ├── design-system/           # @lumina/design-system
│   │   │   └── src/
│   │   │       ├── components/
│   │   │       │   ├── layout/      # AppShell, PageContainer, SplitPane
│   │   │       │   ├── data/        # DataTable, StatCard, KPIGrid
│   │   │       │   ├── charts/      # LineChart, BarChart, Heatmap
│   │   │       │   ├── feedback/    # EmptyState, ErrorBoundary, Skeleton
│   │   │       │   └── inputs/      # FilterBuilder, DateRange, Select
│   │   │       ├── theme/
│   │   │       │   ├── tokens.ts    # Design tokens
│   │   │       │   ├── antd-theme.ts # Ant Design theme config
│   │   │       │   └── tailwind-preset.ts
│   │   │       └── index.ts
│   │   │
│   │   ├── data-access/             # @lumina/shared/data-access
│   │   │   └── src/
│   │   │       ├── sdk-provider.tsx
│   │   │       ├── query-client.ts
│   │   │       └── hooks/           # Generic hooks
│   │   │
│   │   └── state/                   # @lumina/shared/state
│   │       └── src/
│   │           ├── stores/
│   │           │   ├── ui.store.ts      # Sidebar, theme, layout
│   │           │   ├── filters.store.ts # Global filter state
│   │           │   └── selection.store.ts
│   │           └── index.ts
│   │
│   └── domains/                     # Vertical slice features
│       ├── process-explorer/        # @lumina/process-explorer
│       │   └── src/
│       │       ├── components/
│       │       │   ├── ProcessMap.tsx
│       │       │   ├── FilterPanel.tsx
│       │       │   ├── ActivityDetails.tsx
│       │       │   └── VariantList.tsx
│       │       ├── hooks/
│       │       │   ├── use-dfg.ts
│       │       │   └── use-variants.ts
│       │       └── index.ts
│       │
│       ├── analytics/               # @lumina/analytics
│       │   └── src/
│       │       ├── components/
│       │       │   ├── KPIDashboard.tsx
│       │       │   ├── BottleneckTable.tsx
│       │       │   ├── CycleTimeChart.tsx
│       │       │   └── ThroughputChart.tsx
│       │       ├── hooks/
│       │       │   ├── use-performance.ts
│       │       │   └── use-bottlenecks.ts
│       │       └── index.ts
│       │
│       ├── conformance/             # @lumina/conformance
│       │   └── src/
│       │       ├── components/
│       │       │   ├── ConformanceScore.tsx
│       │       │   ├── DeviationTable.tsx
│       │       │   └── CaseAudit.tsx
│       │       ├── hooks/
│       │       │   └── use-conformance.ts
│       │       └── index.ts
│       │
│       ├── predictions/             # @lumina/predictions
│       │   └── src/
│       │       ├── components/
│       │       │   ├── ModelTrainer.tsx
│       │       │   ├── ModelList.tsx
│       │       │   ├── PredictionPanel.tsx
│       │       │   └── AccuracyChart.tsx
│       │       ├── hooks/
│       │       │   ├── use-predictors.ts
│       │       │   └── use-predictions.ts
│       │       └── index.ts
│       │
│       ├── resources/               # @lumina/resources
│       │   └── src/
│       │       ├── components/
│       │       │   ├── SNAGraph.tsx
│       │       │   ├── WorkloadChart.tsx
│       │       │   └── ResourceProfile.tsx
│       │       ├── hooks/
│       │       │   └── use-organizational.ts
│       │       └── index.ts
│       │
│       ├── simulation/              # @lumina/simulation
│       │   └── src/
│       │       ├── components/
│       │       │   ├── ScenarioBuilder.tsx
│       │       │   ├── SimulationResults.tsx
│       │       │   └── CapacityPlanner.tsx
│       │       ├── hooks/
│       │       │   └── use-simulation.ts
│       │       └── index.ts
│       │
│       └── data-hub/                # @lumina/data-hub
│           └── src/
│               ├── components/
│               │   ├── LogList.tsx
│               │   ├── UploadWizard.tsx
│               │   ├── ColumnMapper.tsx
│               │   └── QualityReport.tsx
│               ├── hooks/
│               │   ├── use-logs.ts
│               │   └── use-upload.ts
│               └── index.ts
│
├── package.json
├── nx.json
├── tsconfig.base.json
└── tailwind.config.ts
```

---

## Implementation Phases

### Phase 1: Foundation & Shell
**Goal**: Working app shell with navigation

```
apps/lumina/
├── src/
│   ├── main.tsx                 # Entry point with providers
│   ├── app/
│   │   ├── App.tsx              # Router + Layout
│   │   └── routes.tsx           # Route definitions
│   └── styles.css               # Global styles (Inter font, scrollbars)
libs/shared/design-system/
├── src/
│   ├── theme/
│   │   ├── tokens.ts            # Design tokens
│   │   └── antd-theme.ts        # Ant Design config
│   └── components/
│       └── layout/
│           ├── AppShell.tsx     # Sidebar + Header + Content
│           └── CelonisSidebar.tsx
```

**Deliverables**:
- [ ] Nx app scaffolding with Rsbuild
- [ ] Design tokens + Ant Design 6 theme (compact algorithm)
- [ ] AppShell with collapsible sidebar
- [ ] Route structure for all 16 screens
- [ ] Mock auth context
- [ ] SDK provider + React Query setup

### Phase 2: Data Hub (P0 Screens)
**Goal**: Upload, manage, explore event logs

**Activities Covered**: DIS-001 to DIS-004, VAR-001 to VAR-005

```
libs/domains/data-hub/
├── components/
│   ├── LogList.tsx              # DataTable with search/filter
│   ├── UploadWizard/
│   │   ├── UploadWizard.tsx     # Stepper wizard
│   │   ├── FileDropzone.tsx     # Drag & drop
│   │   ├── ColumnMapper.tsx     # Map CSV columns
│   │   └── ValidationStep.tsx   # Quality check
│   ├── LogDetail.tsx            # Stats + metadata
│   └── QualityReport.tsx        # Quality score breakdown
├── hooks/
│   ├── use-logs.ts
│   └── use-upload.ts
```

**Deliverables**:
- [ ] Log list with search, sort, filter (DataTable)
- [ ] Upload wizard: dropzone → column mapping → validation → confirm
- [ ] Log detail page with statistics cards
- [ ] Quality assessment display

### Phase 3: Process Discovery & Visualization (P0)
**Goal**: Discover and visualize process models

**Activities Covered**: DIS-005 to DIS-015

```
libs/domains/process-explorer/
├── components/
│   ├── ProcessMap/
│   │   ├── ProcessMap.tsx       # ReactFlow container
│   │   ├── ActivityNode.tsx     # Custom node
│   │   ├── TransitionEdge.tsx   # Custom edge with frequency
│   │   └── MiniMap.tsx
│   ├── DiscoveryPanel.tsx       # Algorithm selector
│   ├── FilterPanel.tsx          # Activity/time/variant filters
│   ├── ActivityDetails.tsx      # Side panel on click
│   └── ModelToolbar.tsx         # Zoom, fit, export
├── hooks/
│   ├── use-dfg.ts
│   ├── use-discovery.ts
│   └── use-model.ts
```

**Deliverables**:
- [ ] Process map with ReactFlow (DFG visualization)
- [ ] Interactive nodes (click → details panel)
- [ ] Discovery algorithm selector (Alpha, Inductive, Heuristics)
- [ ] Filter panel (activities, time range, top-k variants)
- [ ] Frequency/performance color coding
- [ ] Export to PNG/SVG

### Phase 4: Variant Analysis (P1)
**Goal**: Analyze process variants

**Activities Covered**: VAR-001 to VAR-015

```
libs/domains/variants/
├── components/
│   ├── VariantList.tsx          # Sortable list
│   ├── VariantComparison.tsx    # Side-by-side
│   ├── VariantTrace.tsx         # Single variant visualization
│   ├── HappyPathBadge.tsx
│   └── VariantStatistics.tsx
├── hooks/
│   └── use-variants.ts
```

**Deliverables**:
- [ ] Variant list with frequency, duration, case count
- [ ] Sort by frequency/performance
- [ ] Variant comparison view
- [ ] Happy path identification
- [ ] Drill-down to cases

### Phase 5: Performance Analytics (P1)
**Goal**: Bottlenecks, cycle time, throughput

**Activities Covered**: PER-001 to PER-020, BOT-001 to BOT-012

```
libs/domains/analytics/
├── components/
│   ├── KPIDashboard.tsx         # 4-6 KPI cards
│   ├── BottleneckTable.tsx      # Sortable with severity
│   ├── BottleneckHeatmap.tsx    # Activity heatmap
│   ├── CycleTimeChart.tsx       # Histogram
│   ├── ThroughputChart.tsx      # Line chart over time
│   ├── ReworkAnalysis.tsx       # Loop detection
│   └── PerformanceSpectrum.tsx  # PM4Py spectrum
├── hooks/
│   ├── use-performance.ts
│   ├── use-bottlenecks.ts
│   └── use-analytics.ts
```

**Deliverables**:
- [ ] KPI dashboard (cycle time, throughput, bottleneck count, rework rate)
- [ ] Bottleneck table with waiting/service time
- [ ] Bottleneck heatmap overlay on process map
- [ ] Cycle time histogram
- [ ] Throughput trend chart
- [ ] Rework analysis

### Phase 6: Conformance Checking (P1)
**Goal**: Check compliance, find deviations

**Activities Covered**: CON-001 to CON-022

```
libs/domains/conformance/
├── components/
│   ├── ConformanceDashboard.tsx # Fitness/precision gauges
│   ├── DeviationTable.tsx       # List with severity
│   ├── DeviationDetails.tsx     # Case-level alignment
│   ├── ConformanceHeatmap.tsx   # Deviations on model
│   └── ComplianceTrend.tsx      # Over time
├── hooks/
│   └── use-conformance.ts
```

**Deliverables**:
- [ ] Conformance score gauges (fitness, precision)
- [ ] Deviation list with classification
- [ ] Deviation details with trace alignment
- [ ] Conformance trend chart
- [ ] Export compliance report

### Phase 7: Predictive Monitoring (P2)
**Goal**: Train ML models, predict outcomes

**Activities Covered**: PRD-001 to PRD-015

```
libs/domains/predictions/
├── components/
│   ├── PredictionStudio/
│   │   ├── ModelTrainer.tsx     # Training wizard
│   │   ├── ModelList.tsx        # Trained models
│   │   └── ModelMetrics.tsx     # Accuracy display
│   ├── PredictionPanel.tsx      # Single case prediction
│   ├── RunningCases.tsx         # Live case monitoring
│   └── AtRiskCases.tsx          # Risk predictions
├── hooks/
│   ├── use-predictors.ts
│   └── use-predictions.ts
```

**Deliverables**:
- [ ] Model training wizard (target, algorithm, hyperparameters)
- [ ] Model list with accuracy metrics
- [ ] Single case prediction interface
- [ ] Running cases dashboard
- [ ] At-risk case alerts

### Phase 8: Organizational & Resources (P2)
**Goal**: SNA, resource analysis

**Activities Covered**: ORG-001 to ORG-015

```
libs/domains/resources/
├── components/
│   ├── SNAGraph.tsx             # Social network visualization
│   ├── WorkloadChart.tsx        # Distribution
│   ├── ResourceProfile.tsx      # Individual stats
│   └── RoleDiscovery.tsx        # Auto-detected roles
├── hooks/
│   └── use-organizational.ts
```

**Deliverables**:
- [ ] Handover network graph
- [ ] Working-together network
- [ ] Workload distribution chart
- [ ] Resource profile cards

### Phase 9: Simulation (P2)
**Goal**: What-if analysis

**Activities Covered**: SIM-001 to SIM-014

```
libs/domains/simulation/
├── components/
│   ├── ScenarioBuilder.tsx      # Define parameters
│   ├── SimulationResults.tsx    # Comparison
│   └── CapacityPlanner.tsx      # Resource planning
├── hooks/
│   └── use-simulation.ts
```

**Deliverables**:
- [ ] Scenario builder (modify resources, timing)
- [ ] Baseline vs scenario comparison
- [ ] Capacity planning recommendations

### Phase 10: Polish & Enterprise
**Deliverables**:
- [ ] Dark mode support
- [ ] Dashboard builder (drag & drop widgets)
- [ ] Report export (PDF, Excel)
- [ ] Alert configuration
- [ ] Keyboard shortcuts
- [ ] E2E tests with Playwright

---

## State Management

### React Query (Server State)
```typescript
// Query key structure
const queryKeys = {
  logs: {
    all: ['logs'],
    list: (params) => ['logs', 'list', params],
    detail: (id) => ['logs', id],
    stats: (id) => ['logs', id, 'stats'],
  },
  analytics: {
    dashboard: (logId) => ['analytics', logId, 'dashboard'],
    bottlenecks: (logId) => ['analytics', logId, 'bottlenecks'],
  },
  // ... etc
}

// Stale times
const STALE_TIMES = {
  logs: 5 * 60 * 1000,      // 5 min
  analytics: 10 * 60 * 1000, // 10 min (cached on backend anyway)
  static: Infinity,          // Miners list, etc.
}
```

### Zustand (Client State)
```typescript
// UI Store
interface UIStore {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
}

// Filter Store (per-log filters, persisted to URL)
interface FilterStore {
  logId: string | null;
  activities: string[];
  timeRange: [Date, Date] | null;
  variants: string[];
  setFilter: (key, value) => void;
  clearFilters: () => void;
}

// Selection Store
interface SelectionStore {
  selectedLogId: string | null;
  selectedModelId: string | null;
  selectedActivity: string | null;
}
```

### URL State
Filters sync to URL for shareability:
```
/explorer/abc123?activities=Create,Approve&timeRange=2024-01-01,2024-03-01&variants=top5
```

---

## Design Tokens

```typescript
export const tokens = {
  colors: {
    primary: {
      50: '#E6F0FF',
      100: '#CCE0FF',
      500: '#0052CC',  // Main brand
      600: '#0043A6',
      700: '#003380',
    },
    success: '#36B37E',
    warning: '#FAAD14',
    error: '#DE350B',
    neutral: {
      50: '#FAFBFC',
      100: '#F4F5F7',
      200: '#EBECF0',
      300: '#DFE1E6',
      400: '#C1C7D0',
      500: '#A5ADBA',
      600: '#6B778C',
      700: '#505F79',
      800: '#344563',
      900: '#172B4D',
    },
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    xxl: '32px',
  },
  radius: {
    sm: '2px',
    md: '4px',
    lg: '8px',
  },
  typography: {
    fontFamily: "'Inter', -apple-system, sans-serif",
    sizes: {
      xs: '11px',
      sm: '12px',
      md: '14px',
      lg: '16px',
      xl: '20px',
      xxl: '24px',
    },
  },
}
```

---

## Development Ergonomics

### 1. Streamable UI Architecture (Rapid Iteration)

**Principle**: Every component is independently testable and hot-reloadable.

```
libs/domains/{feature}/
├── src/
│   ├── components/
│   │   ├── MyComponent.tsx      # Component
│   │   ├── MyComponent.stories.tsx  # Storybook story
│   │   └── MyComponent.test.tsx     # Unit test
│   ├── __dev__/
│   │   └── MockData.ts          # Dev-only mock data
│   └── index.ts
```

**Key Patterns**:
- **Lazy Loading**: All route components use `React.lazy()` for code splitting
- **Suspense Boundaries**: Each page wrapped in `<Suspense fallback={<PageSkeleton />}>`
- **Mock Mode**: `VITE_MOCK=true` flag enables MSW for offline development
- **Feature Flags**: `VITE_FF_*` flags to toggle features during iteration

```typescript
// routes.tsx - Lazy loading for fast iteration
const ProcessExplorer = lazy(() => import('./pages/explorer/ProcessExplorerPage'));
const Analytics = lazy(() => import('./pages/analytics/AnalyticsPage'));

// Each page is independently deployable/testable
```

### 2. File-Based Logging (No Browser Console)

**Location**: `frontend/dev-logs/` (gitignored)

```typescript
// libs/shared/dev-tools/src/logger.ts
import fs from 'fs';
import path from 'path';

const LOG_DIR = path.join(process.cwd(), 'dev-logs');

export const devLog = {
  info: (context: string, message: string, data?: any) => {
    writeLog('INFO', context, message, data);
  },
  error: (context: string, message: string, error?: any) => {
    writeLog('ERROR', context, message, error);
  },
  api: (method: string, url: string, status: number, duration: number) => {
    writeLog('API', 'request', `${method} ${url} → ${status} (${duration}ms)`);
  },
  render: (component: string, props: any) => {
    writeLog('RENDER', component, JSON.stringify(props));
  },
  state: (store: string, action: string, payload: any) => {
    writeLog('STATE', store, `${action}: ${JSON.stringify(payload)}`);
  },
};

function writeLog(level: string, context: string, message: string, data?: any) {
  if (process.env.NODE_ENV !== 'development') return;

  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] [${level}] [${context}] ${message}${data ? '\n' + JSON.stringify(data, null, 2) : ''}\n`;

  const logFile = path.join(LOG_DIR, `${new Date().toISOString().split('T')[0]}.log`);
  fs.appendFileSync(logFile, logLine);
}
```

**Usage in Components**:
```typescript
// ProcessMap.tsx
import { devLog } from '@lumina/dev-tools';

export function ProcessMap({ logId }: Props) {
  const { data } = useDFG(logId);

  useEffect(() => {
    devLog.render('ProcessMap', { logId, nodeCount: data?.nodes.length });
  }, [data]);

  // ...
}
```

**Log File Structure**:
```
frontend/dev-logs/
├── 2024-12-30.log              # Today's logs
├── 2024-12-29.log              # Yesterday's logs
├── api-requests.log            # API-only log
├── state-changes.log           # Zustand state changes
└── render-trace.log            # Component render trace
```

**Sample Log Output** (`dev-logs/2024-12-30.log`):
```
[2024-12-30T10:15:32.123Z] [API] [request] GET /api/v1/logs → 200 (45ms)
[2024-12-30T10:15:32.200Z] [RENDER] [LogList] {"count":12,"loading":false}
[2024-12-30T10:15:33.100Z] [STATE] [filters] setActivity: ["Create","Approve"]
[2024-12-30T10:15:33.150Z] [API] [request] GET /api/v1/visualization/dfg/abc123 → 200 (120ms)
[2024-12-30T10:15:33.300Z] [RENDER] [ProcessMap] {"logId":"abc123","nodeCount":15}
```

### 3. Development Aids

**a) Component Playground (Storybook)**
```bash
nx run lumina:storybook    # Component explorer at :6006
```

**b) API Inspector (MSW + DevTools)**
```typescript
// libs/shared/dev-tools/src/msw-handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/v1/logs', () => {
    devLog.api('GET', '/api/v1/logs', 200, 0);
    return HttpResponse.json(mockLogs);
  }),
  // ... other handlers
];
```

**c) State Inspector**
```typescript
// Zustand devtools integration
import { devtools } from 'zustand/middleware';

export const useUIStore = create<UIStore>()(
  devtools(
    (set) => ({
      sidebarCollapsed: false,
      toggleSidebar: () => {
        devLog.state('ui', 'toggleSidebar', {});
        set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed }));
      },
    }),
    { name: 'ui-store' }
  )
);
```

**d) Render Tracker HOC**
```typescript
// libs/shared/dev-tools/src/track-render.tsx
export function trackRender<P extends object>(
  Component: React.FC<P>,
  name: string
): React.FC<P> {
  return (props: P) => {
    useEffect(() => {
      devLog.render(name, props);
    });
    return <Component {...props} />;
  };
}

// Usage
export const ProcessMap = trackRender(_ProcessMap, 'ProcessMap');
```

### 4. Iteration-Friendly File Structure

```
apps/lumina/src/
├── pages/
│   ├── explorer/
│   │   ├── ProcessExplorerPage.tsx      # Thin page shell
│   │   ├── ProcessExplorerPage.stories.tsx
│   │   └── __mocks__/
│   │       └── dfg-data.json            # Mock data for this page
│   └── ...
├── __dev__/
│   ├── DevPanel.tsx                     # Floating dev panel
│   ├── MockProvider.tsx                 # Wraps app in mock mode
│   └── fixtures/                        # Shared test fixtures
└── ...
```

**DevPanel Component** (only in dev mode):
```typescript
// __dev__/DevPanel.tsx - Floating panel for quick actions
export function DevPanel() {
  if (process.env.NODE_ENV !== 'development') return null;

  return (
    <div className="fixed bottom-4 right-4 bg-gray-900 text-white p-3 rounded-lg shadow-xl z-50">
      <div className="text-xs font-mono mb-2">DEV TOOLS</div>
      <button onClick={() => openLogFile()}>📋 View Logs</button>
      <button onClick={() => clearCache()}>🗑️ Clear Cache</button>
      <button onClick={() => toggleMock()}>🔄 Toggle Mock</button>
      <button onClick={() => triggerError()}>💥 Test Error</button>
    </div>
  );
}
```

### 5. Rapid Iteration Scripts

```json
// package.json scripts
{
  "scripts": {
    "dev": "nx serve lumina",
    "dev:mock": "VITE_MOCK=true nx serve lumina",
    "dev:logs": "tail -f dev-logs/$(date +%Y-%m-%d).log",
    "dev:clear": "rm -rf dev-logs/* && echo 'Logs cleared'",
    "test:watch": "nx test lumina --watch",
    "story": "nx run lumina:storybook",
    "gen:component": "nx g @nx/react:component --project=lumina",
    "gen:domain": "nx g @nx/react:library --directory=libs/domains"
  }
}
```

### 6. Environment Configuration

```bash
# apps/lumina/.env.development
VITE_API_URL=http://localhost:8001
VITE_MOCK=false                    # Set to true for offline dev
VITE_LOG_LEVEL=debug               # debug | info | warn | error
VITE_LOG_TO_FILE=true              # Enable file logging
VITE_DEV_PANEL=true                # Show floating dev panel
VITE_FF_PREDICTIONS=true           # Feature flag: predictions
VITE_FF_SIMULATION=false           # Feature flag: simulation
```

---

## Key Files to Create

### Foundation (Phase 1)
1. `libs/shared/design-system/src/theme/tokens.ts` - Design tokens
2. `libs/shared/design-system/src/theme/antd-theme.ts` - Ant Design theme
3. `libs/shared/design-system/src/components/layout/AppShell.tsx` - Main layout
4. `libs/shared/data-access/src/sdk-provider.tsx` - SDK context
5. `libs/shared/data-access/src/query-client.ts` - React Query config
6. `libs/shared/dev-tools/src/logger.ts` - File-based logger
7. `libs/shared/dev-tools/src/track-render.tsx` - Render tracker
8. `apps/lumina/src/__dev__/DevPanel.tsx` - Dev tools panel
9. `apps/lumina/src/app/routes.tsx` - All routes with lazy loading

### Domain Libraries (Phase 2+)
10. `libs/domains/data-hub/src/components/LogList.tsx`
11. `libs/domains/data-hub/src/components/UploadWizard.tsx`
12. `libs/domains/process-explorer/src/components/ProcessMap.tsx`
13. `libs/domains/analytics/src/components/KPIDashboard.tsx`
14. `libs/domains/conformance/src/components/ConformanceScore.tsx`
15. `libs/domains/predictions/src/components/ModelTrainer.tsx`
