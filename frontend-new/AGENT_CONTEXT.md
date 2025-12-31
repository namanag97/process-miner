# Process Mining Frontend - Agent Context

> **Copy this document into each new Claude chat to provide context without re-searching the codebase.**

---

## Tech Stack
- React 19 + TypeScript + Nx Monorepo
- Ant Design 5 + TanStack Query v5 + React Router v6 + React Flow
- Bundler: Rspack
- Backend: FastAPI on port 8001

---

## Key File Locations

| Category | Path |
|----------|------|
| Pages | `src/pages/` |
| Design System | `libs/shared/design-system/src/` |
| SDK Client | `libs/shared/design-system/src/api/` |
| Zod Schemas | `libs/shared/design-system/src/api/schemas/` |
| Components | `libs/shared/design-system/src/components/` |
| Hooks (Design System) | `libs/shared/design-system/src/hooks/` |
| Hooks (App) | `src/hooks/` |
| Contexts | `src/context/` + `libs/shared/design-system/src/context/` |
| Query Keys | `libs/shared/design-system/src/api/queryKeys.ts` |
| Testing | `src/testing/` |

---

## SDK Usage Pattern

```tsx
import { useSDK } from '@lumina/design-system';

function MyComponent() {
  const sdk = useSDK();

  // Use with TanStack Query
  const { data } = useQuery({
    queryKey: queryKeys.processes.all(),
    queryFn: () => sdk.processes.list(),
  });
}
```

---

## Query Hook Pattern

```tsx
import { useProcesses, useDFG, useProject } from '@lumina/design-system';

// Automatically handles loading, error, caching
const { data, isLoading, error } = useProcesses();
const { data: dfg } = useDFG(logId);
```

---

## Query Keys

```tsx
import { queryKeys } from '@lumina/design-system';

queryKeys.projects.all()              // ['projects']
queryKeys.projects.detail(id)         // ['projects', id]
queryKeys.processes.all()             // ['processes']
queryKeys.processes.detail(id)        // ['processes', id]
queryKeys.dfg.data(logId)             // ['dfg', logId]
queryKeys.variants.list(logId)        // ['variants', logId]
queryKeys.analytics.performance(logId) // ['analytics', 'performance', logId]
queryKeys.analytics.rework(logId)      // ['analytics', 'rework', logId]
queryKeys.audit.logs()                 // ['audit']
```

---

## Zod Validation

All API responses are validated at runtime using Zod schemas.

```tsx
import { validateResponse, ProcessResponseSchema } from '@lumina/design-system';

// In SDK modules - validation happens automatically
const data = validateResponse(ProcessResponseSchema, apiResponse);
```

**Schema Files:**
- `schemas/common.ts` - PaginatedResponse, APIError, validateResponse()
- `schemas/processes.ts` - EventLog, ColumnDetection, Statistics
- `schemas/discovery.ts` - DFGNode, DFGEdge, Variant, Activity
- `schemas/analytics.ts` - Performance, Rework, Bottleneck, CycleTime
- `schemas/organizational.ts` - SocialNetwork, ResourceProfile, Workload
- `schemas/projects.ts` - Project, ProjectDetail, CreateProject
- `schemas/predictions.ts` - Predictor, Prediction, Conformance, Insight

---

## Component Library

| Component | Purpose | Import |
|-----------|---------|--------|
| `AppShell` | Main layout with sidebar | `@lumina/design-system` |
| `PageHeader` | Page title + breadcrumb + actions | `@lumina/design-system` |
| `MetricCard` | KPI display with trend | `@lumina/design-system` |
| `EmptyState` | No data feedback with action | `@lumina/design-system` |
| `LoadingState` | Consistent loading (skeleton/spinner) | `@lumina/design-system` |
| `QueryError` | Error display with retry | `@lumina/design-system` |
| `ErrorBoundary` | Crash recovery wrapper | `@lumina/design-system` |
| `DataTable` | Reusable table with search/sort | `@lumina/design-system` |
| `ProcessQuestion` | Question card with icon | `@lumina/design-system` |
| `DataSourceCard` | Data source display card | `@lumina/design-system` |

---

## User Flow (Primary)

```
Home
  └─→ Workspace Tab
        └─→ Projects Table
              └─→ Add Project (modal)
                    └─→ Project Detail Page
                          └─→ Upload Data (wizard)
                                └─→ Back to Project
                                      └─→ Click "Explore" on data
                                            └─→ Process Questions Page
                                                  ├─→ Process Explorer (DFG)
                                                  ├─→ KPI Page (metrics)
                                                  └─→ Audit Logs
```

---

## Route Structure

```tsx
/login                                    → LoginPage
/home                                     → HomePage (Overview | Workspace tabs)
/projects/:projectId                      → ProjectDetailPage
/projects/:projectId/upload               → UploadWizardPage
/projects/:projectId/data/:logId/questions → ProcessQuestionsPage
/projects/:projectId/data/:logId/explorer  → ProcessExplorerPage
/projects/:projectId/data/:logId/kpi       → KPIPage
/audit                                    → AuditLogsPage
```

---

## Page Structure

```
src/pages/
├── home/
│   ├── HomePage.tsx           # Tab container (Overview | Workspace)
│   ├── OverviewTab.tsx        # Metrics overview
│   └── WorkspaceTab.tsx       # Projects table + create modal
│
├── projects/
│   ├── ProjectDetailPage.tsx  # Single project + data sources
│   └── components/
│       └── DataSourcesList.tsx
│
├── questions/
│   ├── ProcessQuestionsPage.tsx  # 6 question cards
│   └── questionsData.ts          # Question definitions
│
├── kpi/
│   ├── KPIPage.tsx               # Tab container for metrics
│   └── tabs/
│       ├── PerformanceTab.tsx
│       ├── DeadlinesTab.tsx
│       ├── UnwantedActivitiesTab.tsx
│       └── AutomationTab.tsx
│
├── explorer/                     # Process DFG visualization
├── analytics/                    # Analytics tabs
├── ai/                          # AI assistant pages
├── logs/                        # Upload wizard, log detail
└── settings/                    # User settings
```

---

## Design Tokens

Always use tokens from `@lumina/design-system` - never hardcode colors/spacing.

```tsx
import { tokens } from '@lumina/design-system';

const style = {
  backgroundColor: tokens.colors.primary[50],
  padding: tokens.spacing[4],
  borderRadius: tokens.radius.md,
};
```

---

## Process Questions (6 Cards)

| Question | Route |
|----------|-------|
| What does your process look like? | `/projects/:projectId/data/:logId/explorer` |
| How long does your process take? | `/projects/:projectId/data/:logId/kpi?tab=performance` |
| Are you meeting your deadlines? | `/projects/:projectId/data/:logId/kpi?tab=deadlines` |
| How many unwanted activities? | `/projects/:projectId/data/:logId/kpi?tab=unwanted` |
| How automated is your process? | `/projects/:projectId/data/:logId/kpi?tab=automation` |
| Want to look into something else? | Feedback modal |

---

## Backend API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/processes` | GET | List all event logs |
| `/processes/:id` | GET | Get single event log |
| `/processes/upload` | POST | Upload CSV/XES file |
| `/processes/:id` | DELETE | Delete event log |
| `/projects` | GET/POST | List/Create projects |
| `/projects/:id` | GET/PUT/DELETE | Project CRUD |
| `/visualization/:id/dfg` | GET | Get DFG data |
| `/visualization/:id/variants` | GET | Get variants |
| `/analytics/logs/:id/performance` | GET | Performance metrics |
| `/analytics/logs/:id/rework` | GET | Rework analysis |
| `/analytics/logs/:id/deadlines` | GET | Deadline metrics |
| `/analytics/logs/:id/automation` | GET | Automation metrics |
| `/conformance/logs/:id/check` | POST | Conformance check |
| `/audit/logs` | GET/POST | Audit log entries |

---

## Current Implementation Phase

**Phase 1: Foundation** (COMPLETED)
- [x] Zod schemas created (7 schema files in `api/schemas/`)
- [x] HTTP client refactor (retry extraction, AbortController, timeout)
- [x] Query key constants (`api/queryKeys.ts`)
- [x] Error handling components (ErrorBoundary, QueryError, LoadingState)

**Phase 2: Components & Hooks** (COMPLETED)
- [x] Query hooks (useProcesses, useDFG, useProjects, useAnalytics, etc.)
- [x] State hooks (useURLState, useExplorerState, useAuditLogger)
- [x] New shared components (ProcessQuestion, DataTable, DataSourceCard)

**Phase 3: Page Restructure** (COMPLETED)
- [x] HomePage with Overview/Workspace tabs
- [x] ProjectDetailPage with data source cards
- [x] ProcessQuestionsPage with 6 question cards
- [x] KPIPage with 4 metric tabs
- [x] Route updates in App.tsx

**Phase 4: Polish & Integration** (COMPLETED)
- [x] Remove mock data from AuditLogsPage (uses real API)
- [x] Audit logging integrated in key pages
- [x] Testing infrastructure set up (`src/testing/`)

**REMAINING WORK:**
- [ ] Write unit tests (85% coverage target)
- [ ] Remove mock data from AIAssistantPage (needs LLM integration)
- [ ] Remove mock data from other AI pages
- [ ] Connect authentication to real backend
- [ ] Production deployment configuration

---

## Testing Infrastructure

```tsx
import { renderWithProviders, createMockSDK, createMockProject } from '../testing';

// Render with all providers
const { getByText } = renderWithProviders(<MyComponent />);

// Create mock data
const project = createMockProject({ name: 'Test' });
const dfg = createMockDFG();
```

**Test Files Location:**
- `src/testing/utils.tsx` - renderWithProviders, createMockSDK
- `src/testing/mocks/projects.ts` - Project/Process factories
- `src/testing/mocks/dfg.ts` - DFG/Variant factories

---

## Audit Logging

```tsx
import { useAuditLogger, useKPIAuditLogger } from '../hooks';

// General logging
const auditLog = useAuditLogger();
auditLog('project.created', { projectId: '123', name: 'My Project' });

// Specialized loggers
const kpiAudit = useKPIAuditLogger();
kpiAudit.logView(processId, 'performance', projectId);
```

---

## Commands

```bash
# Development
npx nx serve frontend-new     # Dev server (http://localhost:4200)
npx nx build frontend-new     # Production build
npx nx test frontend-new      # Run tests

# Storybook
npm run storybook             # Component dev (port 6006)

# Quality
npx nx lint frontend-new      # ESLint
npx nx graph                  # Dependency visualization
```

---

## Key Files for Common Tasks

| Task | Files to Modify |
|------|-----------------|
| Add new API endpoint | `api/modules/*.ts`, `api/schemas/*.ts`, `api/queryKeys.ts` |
| Add new page | `src/pages/`, `src/App.tsx`, `src/pages/index.ts` |
| Add shared component | `design-system/components/`, `design-system/index.ts` |
| Add query hook | `design-system/hooks/`, `design-system/index.ts` |
| Modify routing | `src/App.tsx` |
| Update design tokens | `design-system/theme.ts` |
| Add test | `src/testing/`, component `__tests__/` folder |

---

## Important Patterns

1. **Never use `fetch` directly** - Always use SDK via `useSDK()`
2. **Always validate API responses** - Use Zod schemas
3. **Use query keys from constants** - Never hardcode query key strings
4. **Handle all states** - Loading, Error, Empty, Success
5. **Use URL state for shareable filters** - `useSearchParams()`
6. **Memoize list items** - Use `React.memo()` for list components
7. **Extract hooks for data fetching** - Don't inline `useQuery` in components
8. **Log important actions** - Use audit logger hooks for tracking
