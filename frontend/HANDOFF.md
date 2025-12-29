# Frontend Handoff - Lumina Process Mining Platform

## Current Status: Phases 1-3 COMPLETE

### What's Done
- **Phase 1**: Foundation & Shell (100%)
- **Phase 2**: Data Hub (100%)
- **Phase 3**: Process Discovery & Visualization (100%)

### What's Next
- **Phase 4**: Variant Analysis
- **Phase 5**: Performance Analytics
- **Phase 6**: Conformance Checking

## Key Files
- **Full Plan**: `/Users/namanagarwal/system/frontend/FEPLAN.md`
- **Business Use Cases**: `/Users/namanagarwal/system/docs/businessusecase.md`
- **Backend API**: `http://localhost:8001/docs`
- **SDK**: `/Users/namanagarwal/system/sdk/`

## Tech Stack
- React 19, TypeScript 5.9, Rspack/Rsbuild
- Ant Design 6 (compact algorithm), TanStack Query
- @xyflow/react v12 (process graphs)
- Tailwind CSS, Inter font, #0052CC primary

---

## Completed Implementation

### Domain Libraries Created

#### `@lumina/data-hub` (`libs/domains/data-hub/`)
**Hooks:**
- `useLogs()` - Paginated log list with search/sort
- `useLog(logId)` - Single log details
- `useLogStatistics(logId)` - Detailed statistics
- `useLogQuality(logId)` - Quality assessment
- `useLogVariants(logId)` - Process variants
- `useLogActivities(logId)` - Unique activities
- `useDeleteLog()` - Mutation to delete log
- `useUploadWizard()` - Multi-step upload state machine

**Components:**
- `LogList` - Table with search, sort, pagination, delete modal
- `LogDetail` - Full log view with tabs (Overview, Variants, Quality)
- `UploadWizard` - 4-step wizard (Upload → Map Columns → Validate → Confirm)
- `QualityReport` - Quality scores with issue table

#### `@lumina/process-explorer` (`libs/domains/process-explorer/`)
**Hooks:**
- `useDFG(logId)` - DFG nodes/edges
- `usePetriNet(modelId)` - Petri net structure
- `useFootprints(logId)` - Behavioral footprints
- `useMiners()` - Available mining algorithms
- `useDiscoverModel()` - Discover process model
- `useFilterOptions(logId)` - Filter options (activities, time, variants)
- `useApplyFilter()` / `usePreviewFilter()` - Filter operations

**Components:**
- `ProcessMap` - ReactFlow DFG visualization with:
  - Dagre-like auto-layout
  - Frequency/performance color modes
  - Zoom, pan, minimap
  - Node/edge click handlers
- `ActivityNode` - Custom node with frequency coloring
- `TransitionEdge` - Custom edge with frequency labels
- `FilterPanel` - Collapsible filter sidebar (activities, time, variants, duration)
- `ActivityDetails` - Activity info panel with incoming/outgoing transitions

### Updated Pages (using domain components)
- `apps/lumina/src/pages/data/EventLogsPage.tsx` → uses `LogList`
- `apps/lumina/src/pages/data/UploadPage.tsx` → uses `UploadWizard`
- `apps/lumina/src/pages/data/LogDetailPage.tsx` → uses `LogDetail`
- `apps/lumina/src/pages/explorer/ProcessExplorerPage.tsx` → uses `ProcessMap`, `FilterPanel`, `ActivityDetails`

---

## Architecture Reference

```
apps/lumina/                     # Main SPA (port 4300)
├── src/
│   ├── main.tsx                 # Entry with providers
│   ├── app/
│   │   ├── App.tsx              # AppShell + Router
│   │   └── routes.tsx           # Lazy-loaded routes
│   ├── context/
│   │   ├── AuthContext.tsx      # Mock auth
│   │   └── SDKContext.tsx       # SDK + React Query
│   ├── pages/                   # Route pages (thin wrappers)
│   └── __dev__/
│       └── DevPanel.tsx         # Dev tools overlay

libs/shared/design-system/       # @lumina/design-system
├── src/
│   ├── theme/                   # tokens.ts, antd-theme.ts
│   ├── components/              # AppShell, MetricCard, DataGrid
│   ├── patterns/                # DashboardPage, ResourceListPage
│   └── utils/                   # formatDuration, formatCompactNumber

libs/domains/data-hub/           # @lumina/data-hub
├── src/
│   ├── hooks/                   # use-logs.ts, use-upload.ts
│   ├── components/              # LogList, UploadWizard, LogDetail, QualityReport
│   └── index.ts

libs/domains/process-explorer/   # @lumina/process-explorer
├── src/
│   ├── hooks/                   # use-dfg.ts, use-discovery.ts, use-filter.ts
│   ├── components/              # ProcessMap, FilterPanel, ActivityDetails
│   └── index.ts
```

---

## Commands

```bash
cd /Users/namanagarwal/system/frontend

# Development
npx nx serve lumina              # Dev server on :4300
npx nx build lumina              # Production build

# Backend (required for SDK to work)
cd ../backend && make dev        # API on :8001
```

---

## Next Phase Tasks (Phase 4: Variant Analysis)

Create `libs/domains/variants/` with:

**Hooks:**
- `useVariants(logId)` - Get variant list with stats
- `useVariantComparison(logId, variantIds)` - Compare variants

**Components:**
- `VariantList` - Sortable table (frequency, duration, happy path)
- `VariantComparison` - Side-by-side comparison view
- `VariantTrace` - Single variant visualization
- `HappyPathBadge` - Tag for happy path variant

**Page Updates:**
- `apps/lumina/src/pages/explorer/VariantExplorerPage.tsx` - Use new components

---

## SDK Reference (already available)

```typescript
// All SDK clients available via useSDK() hook:
sdk.logs.*          // Event log operations
sdk.visualization.* // DFG, Petri net, footprints
sdk.discovery.*     // Mining algorithms
sdk.filtering.*     // Filter operations
sdk.analytics.*     // Performance metrics
sdk.conformance.*   // Compliance checking
sdk.predictions.*   // ML predictions
sdk.org.*           // Organizational mining
sdk.simulation.*    // What-if scenarios
```

---

## Path Aliases (tsconfig.base.json)

```json
{
  "@lumina/design-system": ["libs/shared/design-system/src/index.ts"],
  "@lumina/data-hub": ["libs/domains/data-hub/src/index.ts"],
  "@lumina/process-explorer": ["libs/domains/process-explorer/src/index.ts"]
}
```

Add new domain aliases as you create them.
