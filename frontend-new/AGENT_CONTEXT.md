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
| Hooks | `libs/shared/design-system/src/hooks/` |
| Contexts | `src/context/` + `libs/shared/design-system/src/context/` |
| Query Keys | `libs/shared/design-system/src/api/queryKeys.ts` |

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
| `DataTable` | Reusable table | `@lumina/design-system` |
| `ProcessQuestion` | Question card with icon | `@lumina/design-system` |

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
| What does your process look like? | `/explorer` |
| How long does your process take? | `/kpi?tab=performance` |
| Are you meeting your deadlines? | `/kpi?tab=deadlines` |
| How many unwanted activities? | `/kpi?tab=unwanted` |
| How automated is your process? | `/kpi?tab=automation` |
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
| `/conformance/logs/:id/check` | POST | Conformance check |
| `/audit/logs` | GET | Audit log entries |

---

## Current Implementation Phase

**Phase 1: Foundation** (IN PROGRESS)
- [x] Zod schemas created
- [ ] HTTP client refactor (retry extraction, AbortController)
- [ ] Query key constants
- [ ] Error handling components
- [ ] Test infrastructure

**Phase 2: Components & Hooks**
- [ ] Query hooks (useProcesses, useDFG, etc.)
- [ ] State hooks (useURLState, useExplorerState)
- [ ] New shared components

**Phase 3: Page Restructure**
- [ ] HomePage with Overview/Workspace tabs
- [ ] ProjectDetailPage
- [ ] ProcessQuestionsPage
- [ ] Route updates

**Phase 4: Polish & Testing**
- [ ] Remove mock data
- [ ] Audit logging
- [ ] 85% test coverage

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
| Add new page | `src/pages/`, `src/App.tsx` |
| Add shared component | `design-system/components/`, `design-system/index.ts` |
| Add query hook | `design-system/hooks/`, `design-system/index.ts` |
| Modify routing | `src/App.tsx` |
| Update design tokens | `design-system/theme.ts` |

---

## Important Patterns

1. **Never use `fetch` directly** - Always use SDK via `useSDK()`
2. **Always validate API responses** - Use Zod schemas
3. **Use query keys from constants** - Never hardcode query key strings
4. **Handle all states** - Loading, Error, Empty, Success
5. **Use URL state for shareable filters** - `useSearchParams()`
6. **Memoize list items** - Use `React.memo()` for list components
7. **Extract hooks for data fetching** - Don't inline `useQuery` in components
