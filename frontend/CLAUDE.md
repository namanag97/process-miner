# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

**Current Phase**: Phase 3 Complete (Foundation, Data Hub, Process Explorer)
**Next Phase**: Phase 4 - Variant Analysis
**Overall Goals**: 16 screens, 7 core capabilities, 237 business activities

**Completed**:
- Phase 1: Foundation (Design system, AppShell, routing, auth context)
- Phase 2: Data Hub (`@lumina/data-hub` - event log management, upload wizard, quality reports)
- Phase 3: Process Discovery (`@lumina/process-explorer` - DFG visualization, discovery algorithms, filtering)

**In Progress**:
- Phase 4: Variant Analysis (`@lumina/variants` - variant explorer, comparison, happy path identification)

**Upcoming**:
- Phase 5: Performance Analytics (bottlenecks, cycle time, throughput)
- Phase 6: Conformance Checking (compliance, deviations, fitness metrics)

See `FEPLAN.md` for complete implementation plan and `HANDOFF.md` for detailed status.

## Commands

```bash
# Lumina (new enterprise app - port 4300)
npx nx serve lumina               # Dev server
npx nx build lumina               # Production build
npx nx test lumina                # Tests
npx nx lint lumina                # Lint
npx nx typecheck lumina           # Type check

# Process Mining (legacy app - port 4200)
npx nx serve process-mining       # Dev server
npx nx build process-mining       # Production build

# Utilities
npx nx graph                      # View dependency graph
npx nx affected:test              # Test affected projects
npx nx reset                      # Clear Nx cache
```

## Architecture

**Nx monorepo** with React 19, Rsbuild (Rspack-based bundler), TanStack Query for server state.

### Applications

**`apps/lumina/`** - New enterprise process mining platform (primary development)
- Domain-driven design with vertical slice architecture
- Ant Design 6 with compact algorithm
- Pages are thin wrappers that compose domain components
- Port 4300 in development

**`apps/process-mining/`** - Legacy app (maintenance mode)
- Original SPA with mixed concerns
- Port 4200 in development

### Library Structure

**Shared Libraries:**
- `libs/shared/design-system/` (`@lumina/design-system`) - Theme, tokens, reusable components (AppShell, MetricCard, DataGrid)
- `libs/api/` (`@frontend/api`) - React Query hooks wrapping SDK (legacy)
- `libs/ui/` (`@frontend/ui`) - Legacy shared components
- `libs/process-graph/` (`@frontend/process-graph`) - ReactFlow visualization utilities

**Domain Libraries** (Vertical Slices - Feature-Complete Modules):
- `libs/domains/data-hub/` (`@lumina/data-hub`) - Event log management, upload wizard, quality reports
- `libs/domains/process-explorer/` (`@lumina/process-explorer`) - DFG visualization, discovery, filtering
- `libs/domains/variants/` (`@lumina/variants`) - Variant analysis and comparison
- `libs/domains/analytics/` (`@lumina/analytics`) - Performance metrics, bottlenecks, KPIs
- Each domain exports hooks + components for its feature area

**Key Dependencies:**
- `process-mining-sdk` - TypeScript SDK from `../sdk` (linked via `file:../sdk` in package.json)
- SDK is auto-generated from backend OpenAPI spec using openapi-typescript-codegen

## Design System Quick Reference

**Theme**: Celonis-inspired with Ant Design 6 compact algorithm for high-density enterprise UIs

**Design Tokens** (`libs/shared/design-system/src/theme.ts`):
- **Primary Color**: `#0066FF` (Celonis blue)
- **Semantic Colors**: Success `#36B37E`, Warning `#FAAD14`, Error `#DE350B`
- **Spacing Scale**: 8-12-16-24px (xs, sm, base, lg)
- **Typography**: Inter font, 14px base size
- **Border Radius**: 6px default (softer, modern)
- **Text Colors**: Primary `#172B4D`, Secondary `#5E6C84`, Tertiary `#97A0AF`

**Core Components**:
- `AppShell` - Main layout with collapsible sidebar (dark: `#1B2838`), header, footer
- `MetricCard` - Compact stat card with trend indicators and status colors
- `KPICard` - Full-featured KPI with progress bar, trend, and breakdown
- `StatCard` - Inline statistic display for headers/tables
- `DataGrid` - High-density table with search, export, density control

**Page Patterns**:
- `DashboardPage` - Standardized dashboard with header, date range, KPI row, tabs, grid
- `ResourceListPage` - List page with filters, data grid, bulk actions, row actions

**Utilities**:
- `formatDuration(ms)` - Human-readable duration (e.g., "2d 3h 15m")
- `formatCompactNumber(num)` - Compact notation (e.g., "1.5K", "2.3M")
- `formatPercentage(value, decimals)` - Percentage with precision
- `toast.success/error/warning/info(message)` - Toast notifications
- `notify.success/error/warning/info({ title, description })` - Persistent notifications

**Import**:
```typescript
import { AppShell, MetricCard, KPICard, DataGrid, theme, toast } from '@lumina/design-system'
```

## SDK Integration

**Critical:** Frontend depends on locally linked SDK from `../sdk`.

### SDK Architecture

The SDK uses a **business verb pattern** (CodeOpinion guidance) with 16 domain clients. Use business-focused method names, not CRUD operations.

**Accessing SDK in Components**:
```typescript
import { useSDK } from '@lumina/design-system'

const sdk = useSDK() // Returns ProcessMiningSdk instance
```

**16 Domain Clients** (see `../sdk/src/index.ts` for complete reference):

```typescript
// Event Logs
sdk.logs.ingest(file, metadata)           // Not "upload"
sdk.logs.analyze(logId)                   // Not "getStats"
sdk.logs.assessQuality(logId)             // Not "checkQuality"
sdk.logs.listVariants(logId)

// Process Discovery
sdk.discovery.discover({ logId, minerType })
sdk.discovery.buildDFG(logId, options)
sdk.discovery.extractPetriNet(logId)

// Visualization
sdk.visualization.getDFG(logId)
sdk.visualization.getPetriNet(modelId)
sdk.visualization.getFootprints(logId)

// Conformance
sdk.conformance.check({ logId, modelId })
sdk.conformance.measureFitness(logId, modelId)
sdk.conformance.computeAlignments(logId, modelId)

// Performance & Analytics
sdk.performance.analyze(logId)
sdk.performance.findBottlenecks(logId)
sdk.analytics.getBottlenecks(logId)
sdk.analytics.getRework(logId)
sdk.analytics.getServiceTimes(logId)

// Predictions
sdk.predictions.trainPredictor(config)
sdk.predictions.predict(logId, caseId)
sdk.predictions.predictBatch(logId, caseIds)

// Filtering
sdk.filtering.applyFilter(logId, filterSpec)
sdk.filtering.previewFilter(logId, filterSpec)

// Other clients: auth, ocpm, org, models, workflows, simulation, notifications, integrations
```

**SDK Context**: SDK is initialized in `SDKProvider` from `@lumina/design-system` with React Query client. The provider wraps the app in `apps/lumina/src/main.tsx`.

### Regenerating SDK After Backend Changes

**CRITICAL**: Backend must be running on port 8001 before regeneration!

```bash
# 1. Start backend on port 8001
cd ../backend && source .venv/bin/activate && uvicorn src.api.main:app --reload --port 8001

# 2. Generate and build SDK
cd ../sdk && npm run generate && npm run build

# 3. Clear Nx cache and restart frontend
cd ../frontend && npx nx reset && npx nx serve lumina
```

**Troubleshooting**:
- SDK changes not reflecting: `cd ../sdk && npm run build && npx nx reset`
- Type errors after regeneration: Update domain hooks to match new SDK types

## React Query Patterns

Domain libraries follow consistent conventions for React Query integration.

### Query Key Factory Convention

Each domain exports a query key factory for type-safe cache management:

```typescript
// Example: libs/domains/data-hub/src/hooks/use-logs.ts
export const logsKeys = {
  all: ['logs'] as const,
  list: (params?: ListLogsOptions) => [...logsKeys.all, 'list', params] as const,
  detail: (id: string) => [...logsKeys.all, id] as const,
  statistics: (id: string) => [...logsKeys.all, id, 'statistics'] as const,
  quality: (id: string) => [...logsKeys.all, id, 'quality'] as const,
}
```

**Benefits**: Type-safe keys, easy invalidation, clear hierarchy

### Hook Naming Convention

- `use{Resource}` (plural) - List query (e.g., `useLogs()`)
- `use{Resource}` (singular) - Detail query (e.g., `useLog(id)`)
- `use{Action}{Resource}` - Mutation (e.g., `useDeleteLog()`, `useUploadLog()`)
- `use{Resource}{Aspect}` - Sub-resource query (e.g., `useLogStatistics(id)`)

### Standard Hook Pattern

```typescript
export function useLogs(options?: ListLogsOptions) {
  const sdk = useSDK()
  return useQuery({
    queryKey: logsKeys.list(options),
    queryFn: () => sdk.logs.list(options),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export function useLog(id: string) {
  const sdk = useSDK()
  return useQuery({
    queryKey: logsKeys.detail(id),
    queryFn: () => sdk.logs.get(id),
    enabled: !!id,
  })
}

export function useDeleteLog() {
  const sdk = useSDK()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => sdk.logs.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: logsKeys.all })
    },
  })
}
```

**Query Client Config** (in SDKProvider):
- Stale Time: 5 minutes
- GC Time: 10 minutes
- Retry: 2 for queries, 1 for mutations
- No refetch on window focus

## Path Aliases (Import Patterns)

Domain libraries use scoped imports defined in `tsconfig.base.json`:

```typescript
// Design system (theme, components, SDK context)
import { AppShell, MetricCard, theme, useSDK, SDKProvider } from '@lumina/design-system'

// Domain libraries
import { LogList, useLogs } from '@lumina/data-hub'
import { ProcessMap, useDFG } from '@lumina/process-explorer'
import { VariantList, useVariants } from '@lumina/variants'
import { KPIDashboard, usePerformance } from '@lumina/analytics'

// Legacy libraries (process-mining app)
import { Button } from '@frontend/ui'
import { useProcesses } from '@frontend/api'
```

## Working with Domain Libraries

Domain libraries follow a **vertical slice architecture** - each domain is self-contained with:
- **Hooks** (`hooks/use-*.ts`) - React Query wrappers for SDK calls
- **Components** (`components/*.tsx`) - UI components specific to that domain
- **Exports** (`index.ts`) - Public API of the domain

**Example: Creating a new page using domains**
```typescript
// apps/lumina/src/pages/analytics/AnalyticsPage.tsx
import { KPIDashboard, usePerformance } from '@lumina/analytics'

export default function AnalyticsPage() {
  const { data } = usePerformance(logId)
  return <KPIDashboard data={data} />
}
```

**Adding a new domain library:**
```bash
npx nx g @nx/react:library --name=my-domain --directory=libs/domains/my-domain --importPath=@lumina/my-domain
```

Then add to `tsconfig.base.json`:
```json
"@lumina/my-domain": ["libs/domains/my-domain/src/index.ts"],
"@lumina/my-domain/*": ["libs/domains/my-domain/src/*"]
```

## Authentication

**Process Mining app**: Mock auth at `apps/process-mining/src/context/AuthContext.tsx`

**Lumina app**: Mock auth at `apps/lumina/src/context/AuthContext.tsx`
- Accepts any credentials (username/password)
- Stores mock token in localStorage
- Protected routes check for token presence
- No backend integration yet

## Development Workflow

1. Start backend: `cd ../backend && make dev` (runs on :8001)
2. Start frontend: `npx nx serve lumina` (runs on :4300)
3. Access:
   - Lumina app: http://localhost:4300
   - Process Mining app: `npx nx serve process-mining` → http://localhost:4200 (legacy, maintenance mode)
   - Backend API docs: http://localhost:8001/docs

## Project Documentation

- `FEPLAN.md` - Comprehensive frontend implementation plan for Lumina (16 screens, 237 business activities)
- `HANDOFF.md` - Current implementation status and next steps
- `../CONTRIBUTING.md` - Git workflow (two-branch: `dev` → `main`)
- `../sdk/` - TypeScript SDK source (auto-generated from backend OpenAPI)
