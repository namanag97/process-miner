# ATLAS Implementation Plan
## Detailed Component & Flow Specifications

**Prepared by: Fictive Kin Design Studio**
**Version: 1.0**

---

# Priority Matrix

## P0 - Must Have (Core Product)
These flows are essential for the product to function. Without them, users cannot accomplish the primary use case.

| Flow | Objects Involved | Current Coverage |
|------|-----------------|------------------|
| Event Log Upload | EventLog, DataConnection | 40% |
| Process Discovery | ProcessModel, DFG, PetriNet | 70% |
| Process Exploration | Case, Activity, Variant | 60% |
| Basic Analytics | PerformanceAnalysis, Bottleneck | 50% |

## P1 - Should Have (Complete Analysis)
These flows complete the process mining story and differentiate from competitors.

| Flow | Objects Involved | Current Coverage |
|------|-----------------|------------------|
| Conformance Checking | ConformanceResult, Deviation | 30% |
| Organizational Mining | OrganizationalRole, HandoverNetwork | 10% |
| Advanced Filtering | FilterPreset | 40% |
| Variant Analysis | Variant (detailed) | 40% |

## P2 - Nice to Have (Intelligence)
These flows add predictive and prescriptive capabilities.

| Flow | Objects Involved | Current Coverage |
|------|-----------------|------------------|
| Predictive Analytics | PredictionModel, RiskScore | 30% |
| Root Cause Analysis | RootCauseResult | 0% |
| Simulation | SimulationModel, SimulationRun | 0% |
| OCEL Support | OCELLog, ObjectType | 20% |

## P3 - Future (Automation)
These flows enable operational automation and monitoring.

| Flow | Objects Involved | Current Coverage |
|------|-----------------|------------------|
| Alerting | Alert, ActionDefinition, Trigger | 0% |
| Work Queues | WorkQueue, WorkQueueItem | 0% |
| Recommendations | Recommendation | 0% |
| Custom Dashboards | Dashboard, Widget | 0% |

---

# Component Specifications

## P0 Components

### 1. UploadDropzone

**Purpose:** Drag-and-drop file upload interface with format validation

**File:** `libs/shared/design-system/src/components/UploadDropzone.tsx`

```typescript
interface UploadDropzoneProps {
  // Behavior
  onFileSelect: (file: File) => void;
  onError?: (error: string) => void;

  // Configuration
  acceptedFormats?: ('csv' | 'xes' | 'xlsx' | 'parquet')[];
  maxSizeMB?: number;

  // State
  isUploading?: boolean;
  uploadProgress?: number;

  // Customization
  title?: string;
  description?: string;
  icon?: ReactNode;
}
```

**Visual Spec:**
- 400px height dashed border container
- Primary color on hover/drag-over
- File type icons for accepted formats
- Progress bar overlay during upload
- Error state with red border

**Usage:**
```tsx
<UploadDropzone
  acceptedFormats={['csv', 'xes']}
  maxSizeMB={100}
  onFileSelect={handleFileSelect}
  onError={(err) => toast.error(err)}
  isUploading={uploading}
  uploadProgress={progress}
/>
```

---

### 2. ColumnMapper

**Purpose:** Map source columns to standard event log fields

**File:** `libs/shared/design-system/src/components/ColumnMapper.tsx`

```typescript
interface ColumnMapperProps {
  // Data
  columns: DetectedColumn[];
  sampleData: Record<string, unknown>[];

  // Current mapping
  mapping: ColumnMapping;
  onMappingChange: (mapping: ColumnMapping) => void;

  // Validation
  errors?: Record<string, string>;

  // Actions
  onConfirm: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

interface DetectedColumn {
  name: string;
  dataType: 'string' | 'number' | 'datetime' | 'boolean';
  sampleValues: string[];
  nullCount: number;
  uniqueCount: number;
  suggestedMapping?: 'case_id' | 'activity' | 'timestamp' | 'resource' | 'cost' | 'attribute';
}

interface ColumnMapping {
  caseIdColumn: string;
  activityColumn: string;
  timestampColumn: string;
  timestampFormat?: string;
  resourceColumn?: string;
  costColumn?: string;
  customAttributes: { sourceColumn: string; targetName: string; isCaseLevel: boolean }[];
}
```

**Visual Spec:**
- Two-column layout: Source columns (left), Target fields (right)
- Drag-and-drop or dropdown selection
- Sample data preview for each column
- Required fields marked with asterisk
- Auto-detected suggestions highlighted
- Timestamp format picker when timestamp selected

**Usage:**
```tsx
<ColumnMapper
  columns={detectedColumns}
  sampleData={preview}
  mapping={currentMapping}
  onMappingChange={setMapping}
  errors={validationErrors}
  onConfirm={handleConfirmMapping}
  onCancel={() => navigate(-1)}
  isLoading={processing}
/>
```

---

### 3. StateIndicator

**Purpose:** Visual indicator for object lifecycle states

**File:** `libs/shared/design-system/src/components/StateIndicator.tsx`

```typescript
interface StateIndicatorProps {
  // State
  state: string;
  stateConfig: StateConfig;

  // Display
  variant?: 'badge' | 'dot' | 'pill' | 'timeline';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;

  // Interaction
  onClick?: () => void;
}

interface StateConfig {
  [state: string]: {
    label: string;
    color: 'default' | 'processing' | 'success' | 'warning' | 'error';
    icon?: ReactNode;
  };
}

// Pre-defined configs
export const EVENT_LOG_STATES: StateConfig = {
  uploading: { label: 'Uploading', color: 'processing', icon: <UploadIcon /> },
  validating: { label: 'Validating', color: 'processing', icon: <CheckIcon /> },
  mapping: { label: 'Needs Mapping', color: 'warning', icon: <MapIcon /> },
  processing: { label: 'Processing', color: 'processing', icon: <LoadingIcon /> },
  ready: { label: 'Ready', color: 'success', icon: <CheckCircleIcon /> },
  error: { label: 'Error', color: 'error', icon: <AlertIcon /> },
  archived: { label: 'Archived', color: 'default', icon: <ArchiveIcon /> },
};

export const JOB_STATES: StateConfig = {
  pending: { label: 'Pending', color: 'default' },
  running: { label: 'Running', color: 'processing' },
  completed: { label: 'Completed', color: 'success' },
  failed: { label: 'Failed', color: 'error' },
  cancelled: { label: 'Cancelled', color: 'warning' },
};
```

**Usage:**
```tsx
<StateIndicator
  state={eventLog.status}
  stateConfig={EVENT_LOG_STATES}
  variant="badge"
  size="md"
/>
```

---

### 4. VariantPath

**Purpose:** Visual representation of an activity sequence

**File:** `libs/shared/design-system/src/components/VariantPath.tsx`

```typescript
interface VariantPathProps {
  // Data
  activities: string[];

  // Optional metrics
  frequency?: number;
  percentage?: number;
  duration?: number;

  // Display
  variant?: 'horizontal' | 'vertical' | 'compact';
  maxVisible?: number;
  showMetrics?: boolean;

  // Highlighting
  highlightActivity?: string;
  deviations?: { activity: string; type: 'missing' | 'unexpected' }[];

  // Interaction
  onClick?: () => void;
  onActivityClick?: (activity: string, index: number) => void;
}
```

**Visual Spec:**
- Horizontal: Activities as pills connected by arrows
- Start activity: green left border
- End activity: red right border
- Deviations: dashed border with error color
- Hover shows activity details
- Collapsed view: "A → B → ... → Z (12 steps)"

**Usage:**
```tsx
<VariantPath
  activities={['Submit', 'Review', 'Approve', 'Close']}
  frequency={1250}
  percentage={45.2}
  duration={3600}
  variant="horizontal"
  onClick={() => openVariantDetail(variantId)}
/>
```

---

### 5. FilterBuilder

**Purpose:** Visual filter construction interface

**File:** `libs/shared/design-system/src/components/FilterBuilder.tsx`

```typescript
interface FilterBuilderProps {
  // Current filters
  filters: FilterCondition[];
  onFiltersChange: (filters: FilterCondition[]) => void;

  // Available options (from event log)
  activities: string[];
  resources: string[];
  attributes: { name: string; type: string; values?: string[] }[];
  dateRange: { min: Date; max: Date };
  variants: { key: string; count: number }[];

  // Preview
  previewStats?: {
    originalCases: number;
    filteredCases: number;
    originalEvents: number;
    filteredEvents: number;
  };
  onPreview?: () => void;

  // Actions
  onApply: () => void;
  onClear: () => void;
  onSavePreset?: (name: string) => void;
}

interface FilterCondition {
  id: string;
  type: FilterType;
  operator: 'include' | 'exclude' | 'equals' | 'between' | 'contains';
  parameters: Record<string, unknown>;
}

type FilterType =
  | 'time_range'
  | 'activities'
  | 'variants'
  | 'case_duration'
  | 'case_size'
  | 'resources'
  | 'attribute';
```

**Visual Spec:**
- Filter chips showing active conditions
- "Add filter" dropdown with filter types
- Each filter type has appropriate input (date picker, multi-select, slider)
- Live preview of case/event counts
- Save as preset button

---

## P1 Components

### 6. DeviationList

**Purpose:** Display conformance deviations with filtering and grouping

**File:** `libs/shared/design-system/src/components/DeviationList.tsx`

```typescript
interface DeviationListProps {
  // Data
  deviations: Deviation[];
  totalCount: number;

  // Pagination
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;

  // Filtering
  filters?: {
    types?: DeviationType[];
    activities?: string[];
    severity?: ('low' | 'medium' | 'high')[];
  };
  onFiltersChange?: (filters: typeof filters) => void;

  // Grouping
  groupBy?: 'none' | 'type' | 'activity' | 'case';

  // Selection
  selectedIds?: string[];
  onSelectionChange?: (ids: string[]) => void;

  // Actions
  onDeviationClick?: (deviation: Deviation) => void;
}

interface Deviation {
  id: string;
  caseId: string;
  type: 'missing_activity' | 'unexpected_activity' | 'wrong_order' | 'constraint_violation';
  activity: string;
  expected?: string;
  actual?: string;
  position: number;
  timestamp?: Date;
  severity: 'low' | 'medium' | 'high';
  cost?: number;
}
```

---

### 7. BottleneckCard

**Purpose:** Display identified bottleneck with severity and recommendations

**File:** `libs/shared/design-system/src/components/BottleneckCard.tsx`

```typescript
interface BottleneckCardProps {
  // Data
  bottleneck: Bottleneck;

  // Display
  variant?: 'compact' | 'detailed';

  // Interaction
  onClick?: () => void;
  onDismiss?: () => void;
}

interface Bottleneck {
  id: string;
  type: 'activity' | 'transition' | 'resource';
  location: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  avgDelaySeconds: number;
  totalDelaySeconds: number;
  affectedCaseCount: number;
  affectedCasePercentage: number;
  costImpact?: number;
  recommendation?: string;
}
```

**Visual Spec:**
- Severity color-coded left border (green/yellow/orange/red)
- Location as title with type icon
- Key metrics: delay, cases affected, cost impact
- Expandable recommendation section

---

### 8. PerformanceHeatmap

**Purpose:** Activity duration heatmap visualization

**File:** `libs/shared/design-system/src/components/PerformanceHeatmap.tsx`

```typescript
interface PerformanceHeatmapProps {
  // Data
  data: ActivityDuration[];

  // Configuration
  metric: 'avg_duration' | 'median_duration' | 'max_duration' | 'frequency';
  colorScale?: 'sequential' | 'diverging';

  // Interaction
  onCellClick?: (activity: string) => void;
  selectedActivity?: string;

  // Display
  showValues?: boolean;
  showLegend?: boolean;
}

interface ActivityDuration {
  activity: string;
  avgSeconds: number;
  medianSeconds: number;
  minSeconds: number;
  maxSeconds: number;
  stdDevSeconds: number;
  frequency: number;
}
```

---

### 9. HandoverNetwork

**Purpose:** Resource handover social network visualization

**File:** `libs/shared/design-system/src/components/HandoverNetwork.tsx`

```typescript
interface HandoverNetworkProps {
  // Data
  nodes: HandoverNode[];
  edges: HandoverEdge[];

  // Configuration
  layout?: 'force' | 'circular' | 'hierarchical';
  nodeSize?: 'frequency' | 'centrality' | 'fixed';
  edgeWidth?: 'frequency' | 'fixed';

  // Filtering
  minEdgeFrequency?: number;

  // Interaction
  onNodeClick?: (resource: string) => void;
  onEdgeClick?: (from: string, to: string) => void;
  selectedNode?: string;

  // Display
  showLabels?: boolean;
  showSelfLoops?: boolean;
}

interface HandoverNode {
  resource: string;
  outgoingHandovers: number;
  incomingHandovers: number;
  selfLoops: number;
  role?: string;
}

interface HandoverEdge {
  fromResource: string;
  toResource: string;
  frequency: number;
  percentage: number;
  avgDelaySeconds: number;
}
```

---

## P2 Components

### 10. PredictionCard

**Purpose:** Display ML prediction with confidence

**File:** `libs/shared/design-system/src/components/PredictionCard.tsx`

```typescript
interface PredictionCardProps {
  // Data
  prediction: Prediction;

  // Display
  variant?: 'compact' | 'detailed';
  showConfidence?: boolean;
  showFeatures?: boolean;

  // Interaction
  onClick?: () => void;
}

interface Prediction {
  id: string;
  type: 'next_activity' | 'remaining_time' | 'outcome' | 'risk_score';
  caseId: string;
  value: string | number;
  confidence: number;
  timestamp: Date;
  features?: { name: string; value: unknown; importance: number }[];
}
```

---

### 11. RiskIndicator

**Purpose:** Visual risk score with threshold indicators

**File:** `libs/shared/design-system/src/components/RiskIndicator.tsx`

```typescript
interface RiskIndicatorProps {
  // Data
  score: number; // 0-1
  thresholds?: { low: number; medium: number; high: number };

  // Display
  variant?: 'gauge' | 'bar' | 'badge' | 'number';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;

  // Interaction
  onClick?: () => void;
}
```

**Visual Spec:**
- Gauge: Semi-circular gauge with needle
- Bar: Horizontal bar with color gradient
- Badge: Colored circle with number
- Number: Large number with color

---

### 12. RecommendationList

**Purpose:** Display actionable recommendations

**File:** `libs/shared/design-system/src/components/RecommendationList.tsx`

```typescript
interface RecommendationListProps {
  // Data
  recommendations: Recommendation[];

  // Filtering
  filters?: {
    types?: RecommendationType[];
    priorities?: Priority[];
    statuses?: RecommendationStatus[];
  };

  // Actions
  onAccept?: (id: string) => void;
  onReject?: (id: string) => void;
  onDetails?: (recommendation: Recommendation) => void;
}

interface Recommendation {
  id: string;
  type: 'next_activity' | 'resource_assignment' | 'escalation' | 'intervention';
  caseId: string;
  action: string;
  reason: string;
  confidence: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'accepted' | 'rejected' | 'expired';
  expiresAt?: Date;
}
```

---

# Page Specifications

## P0 Pages

### 1. UploadPage

**Route:** `/upload`

**Purpose:** Multi-step event log upload wizard

**Components Used:**
- UploadDropzone
- ColumnMapper
- StateIndicator
- MetricCard (for statistics)

**State Flow:**
```
idle → uploading → validating → mapping → processing → complete
                        ↓                      ↓
                      error                  error
```

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ PageHeader: "Upload Event Log"                              │
│ Breadcrumb: Home > Upload                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │              Step Indicator (1-4)                   │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │              Step Content Area                      │   │
│  │                                                     │   │
│  │  Step 1: UploadDropzone                             │   │
│  │  Step 2: ColumnMapper                               │   │
│  │  Step 3: Processing (StateIndicator + Progress)     │   │
│  │  Step 4: Summary (MetricCards + Actions)            │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  [Cancel]                            [Next/Finish]  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 2. ExplorerDetailPage (Enhanced)

**Route:** `/explorer/:logId`

**Purpose:** Interactive process exploration with DFG

**Components Used:**
- ProcessNode (DFG nodes)
- VariantPath (variant list)
- FilterBuilder (filter panel)
- MetricCard (statistics)
- DataTable (cases, activities)
- StateIndicator (log status)

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ PageHeader: "{Log Name}"                                    │
│ Breadcrumb: Home > Explorer > {Log Name}                    │
│ Actions: [Filter] [Export] [Settings]                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────┐  ┌─────────────────────────────────┐│
│  │ Cases   │ 12,450  │  │ Events  │ 156,320  │ Activities ││
│  │ MetricCard        │  │ MetricCard         │ MetricCard ││
│  └───────────────────┘  └─────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                                                         ││
│  │                    DFG Visualization                    ││
│  │                    (React Flow + ProcessNode)           ││
│  │                                                         ││
│  │  Controls: Zoom, Fit, Layout, Performance Toggle        ││
│  │                                                         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Tabs: [Variants] [Activities] [Cases] [Resources]      ││
│  ├─────────────────────────────────────────────────────────┤│
│  │                                                         ││
│  │  Tab Content (DataTable or custom list)                 ││
│  │                                                         ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 3. AnalyticsDetailPage (Enhanced)

**Route:** `/analytics/:logId`

**Purpose:** Comprehensive performance analytics

**Components Used:**
- MetricCard (KPIs)
- BottleneckCard (bottleneck list)
- PerformanceHeatmap (activity durations)
- ThroughputChart (time series)
- DataTable (detailed data)

**Tabs:**
1. **Overview** - Key metrics + bottlenecks
2. **Performance** - Heatmap + duration distributions
3. **Throughput** - Time series + trends
4. **Conformance** - Fitness gauges + deviations
5. **Resources** - Workload + handovers

---

## P1 Pages

### 4. ConformanceDetailPage

**Route:** `/conformance/:resultId`

**Purpose:** Detailed conformance analysis

**Components Used:**
- MetricCard (fitness, precision)
- DeviationList
- VariantPath (with deviations highlighted)
- DataTable (case-level results)

---

### 5. ResourceAnalysisPage

**Route:** `/resources/:logId`

**Purpose:** Organizational mining results

**Components Used:**
- HandoverNetwork
- DataTable (resource list)
- MetricCard (network metrics)

---

## P2 Pages

### 6. PredictionModelPage

**Route:** `/predictions/:modelId`

**Purpose:** ML model details and predictions

**Components Used:**
- MetricCard (model metrics)
- PredictionCard
- DataTable (predictions list)
- Charts (feature importance)

---

### 7. SimulationPage

**Route:** `/simulation/:modelId`

**Purpose:** What-if simulation interface

**Components Used:**
- Parameter forms
- Charts (simulation results)
- Comparison tables

---

# Backend Integration Requirements

## New Endpoints Needed

### P0 - Upload Flow
```
PATCH /processes/{id}/status
  Body: { status: 'validating' | 'mapping' | 'processing' | 'ready' | 'error' }

POST /processes/{id}/validate
  Response: { valid: boolean, errors?: string[], warnings?: string[] }

POST /processes/{id}/mapping
  Body: ColumnMapping
  Response: { success: boolean, statistics?: Statistics }
```

### P1 - Conformance
```
GET /conformance/{resultId}/deviations
  Query: page, pageSize, type?, activity?, severity?
  Response: { items: Deviation[], total: number }
```

### P1 - Organizational
```
GET /organizational/{logId}/roles
  Response: { roles: OrganizationalRole[] }

GET /organizational/{logId}/handovers
  Query: minFrequency?
  Response: { nodes: HandoverNode[], edges: HandoverEdge[] }
```

### P2 - Recommendations
```
GET /recommendations/cases/{caseId}
  Response: { recommendations: Recommendation[] }

POST /recommendations/{id}/action
  Body: { action: 'accept' | 'reject', feedback?: string }
```

### P3 - Automation
```
CRUD /actions - Action definitions
CRUD /triggers - Trigger configurations
CRUD /alerts - Alert management
CRUD /queues - Work queue management
CRUD /dashboards - Dashboard configurations
```

---

# Implementation Checklist

## Sprint 1: Upload Flow (P0)
- [ ] Create UploadDropzone component
- [ ] Create ColumnMapper component
- [ ] Create StateIndicator component
- [ ] Build UploadPage with step flow
- [ ] Add upload hooks (useUploadFile, useColumnDetection, useConfirmMapping)
- [ ] Add backend status endpoints
- [ ] Integration testing

## Sprint 2: Explorer Enhancement (P0)
- [ ] Extract VariantPath component
- [ ] Create FilterBuilder component
- [ ] Enhance DFG with performance toggle
- [ ] Add variant detail drawer
- [ ] Add activity detail drawer
- [ ] Filter integration with backend

## Sprint 3: Analytics Enhancement (P0/P1)
- [ ] Create BottleneckCard component
- [ ] Create PerformanceHeatmap component
- [ ] Create ThroughputChart component
- [ ] Build enhanced AnalyticsDetailPage
- [ ] Add conformance tab content

## Sprint 4: Conformance (P1)
- [ ] Create DeviationList component
- [ ] Build ConformanceDetailPage
- [ ] Add deviation backend endpoint
- [ ] Add case-level conformance view

## Sprint 5: Organizational (P1)
- [ ] Create HandoverNetwork component
- [ ] Build ResourceAnalysisPage
- [ ] Add organizational backend endpoints
- [ ] Add role discovery integration

## Sprint 6: Predictions (P2)
- [ ] Create PredictionCard component
- [ ] Create RiskIndicator component
- [ ] Enhance PredictionsPage
- [ ] Add batch prediction UI

## Sprint 7: Recommendations (P2)
- [ ] Create RecommendationList component
- [ ] Build recommendations integration
- [ ] Add recommendation backend endpoints

## Sprint 8: OCEL (P2)
- [ ] Create ObjectTypeSelector component
- [ ] Create ObjectRelationGraph component
- [ ] Build OCELExplorerPage
- [ ] Enhance OCEL backend

## Sprint 9-12: Automation (P3)
- [ ] AlertCard, AlertsPage
- [ ] WorkQueuePanel, WorkQueuePage
- [ ] TriggerBuilder, ActionDefinitionForm
- [ ] DashboardBuilder, DashboardEditorPage

---

# Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Upload success rate | >95% | Files successfully processed / attempted |
| Time to first insight | <5 min | Upload start to DFG visible |
| Filter performance | <2s | Filter apply to results visible |
| Conformance check time | <30s | Check initiated to results visible |
| Page load time | <3s | P95 initial load time |
| Error rate | <1% | Unhandled errors / total actions |

---

**Document Version:** 1.0
**Last Updated:** December 2024
**Maintainer:** Fictive Kin Design Studio
