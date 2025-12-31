# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
# Development
npx nx serve frontend-new     # Dev server (http://localhost:4200)
npx nx build frontend-new     # Production build
npx nx test frontend-new      # Run tests

# Storybook
npm run storybook             # Component development (port 6006)
npm run build-storybook       # Build static Storybook

# Quality
npx nx lint frontend-new      # ESLint
npx nx graph                  # Visualize project dependencies
```

## Architecture

Process mining frontend built with React 19 + TypeScript in an Nx monorepo. Communicates with FastAPI backend (sibling directory `../backend` on port 8001).

**Core Structure:**
- `src/pages/` - Feature-organized pages (ai, analytics, explorer, logs, projects, settings)
- `src/context/` - React Context providers (Auth, Notification, BackendHealth)
- `libs/shared/design-system/` - Shared components, SDK client, utilities
- `libs/shared/design-system/src/api/` - ProcessMiningSdk with 11 modules
- `/docs/` - Comprehensive architecture documentation (see below)

**Tech Stack:**
Nx + React 19 + TypeScript + Ant Design 5 + TanStack Query v5 + React Router v6 + React Flow + Rspack (bundler)

**State Philosophy:**
Server-first. 90% of data lives in TanStack Query cache, 10% local state for UI transients. See STATE_ARCHITECTURE.md.

## SDK & Backend Communication

All API calls go through `ProcessMiningSdk` exposed via `SDKContext`. Never call `fetch` directly.

```tsx
import { useSDK } from '@lumina/design-system';
import { useQuery } from '@tanstack/react-query';

const sdk = useSDK();
const { data } = useQuery({
  queryKey: ['processes', processId],
  queryFn: () => sdk.processes.get(processId),
});
```

**SDK Modules (11):**
processes, discovery, analytics, conformance, organizational, simulation, predictions, ai, projects, workflows, notifications

**Query Key Pattern:**
```tsx
['domain', entityId, options]  // Hierarchical
// Examples:
['processes']                         // All processes
['processes', { status: 'active' }]   // Filtered
['dfg', processId, { threshold: 80 }] // DFG with options
```

See SDK_INTEGRATION.md for complete module reference.

## Key Patterns

**Error Handling:**
```tsx
if (error) {
  return <EmptyState icon={<WarningOutlined />} title="Failed to load"
                     description={error.message} actionLabel="Retry" onAction={refetch} />;
}
```

**Loading States:**
```tsx
if (isLoading) return <Skeleton active />;
// or for metrics: <MetricCard loading={true} />
```

**Optimistic Updates:**
```tsx
onMutate: async (id) => {
  await queryClient.cancelQueries(['logs']);
  const previous = queryClient.getQueryData(['logs']);
  queryClient.setQueryData(['logs'], old => old.filter(l => l.id !== id));
  return { previous };
},
onError: (err, id, ctx) => queryClient.setQueryData(['logs'], ctx.previous),
onSettled: () => queryClient.invalidateQueries(['logs'])
```

**URL State (for shareable filters):**
```tsx
const [params, setParams] = useSearchParams();
const variant = params.get('variant');
```

**Protected Routes:**
All routes except `/login` wrapped in `ProtectedRoute` (checks `useAuth().isAuthenticated`)

See PATTERNS.md for 10+ implementation patterns.

## Module Organization

**Design System Exports (`@lumina/design-system`):**
- Components: `AppShell`, `MetricCard`, `EmptyState`, `PageHeader`, `SkeletonCard`
- SDK: `useSDK()`, `SDKProvider`, `ProcessMiningSdk`
- Context: `AuthContext`, `NotificationContext`, `BackendHealthContext`
- Utils: `toast`, `notify`, `formatDuration`, `formatCompactNumber`, `logAction`
- Theme: `luminaTheme`, `tokens`

**Component Location Strategy:**
- Shared/reusable → `libs/shared/design-system/src/components/`
- Feature-specific → `src/pages/{feature}/components/`
- Export from design system if used across 2+ pages

**Import Alias:**
```tsx
import { AppShell, useSDK, toast } from '@lumina/design-system';
```

## Adding Features

**New Page:**
1. Create in `src/pages/{feature}/NewPage.tsx`
2. Add route in `src/app/App.tsx`
3. Use SDK: `const sdk = useSDK()`
4. Wrap with `useQuery` for data fetching
5. Follow PageHeader + EmptyState patterns
6. Update PAGE_MAP.md

**New API Integration:**
1. Add method to SDK module: `libs/shared/design-system/src/api/modules/{module}.ts`
2. Define types in same file or `api/types.ts`
3. Create custom hook pattern:
```tsx
export function useProcesses(filters?: ListProcessesOptions) {
  const sdk = useSDK();
  return useQuery({
    queryKey: ['processes', filters],
    queryFn: () => sdk.processes.list(filters),
    staleTime: 5 * 60 * 1000,
  });
}
```
4. Invalidate cache in mutations: `queryClient.invalidateQueries({ queryKey: ['processes'] })`

**New Component:**
1. Determine scope (shared vs feature-specific)
2. Create with TypeScript interface for props
3. Add to COMPONENT_CATALOG.md if shared
4. Export from design-system `index.ts` if shared

**Backend Changes:**
Backend is in sibling directory `../backend`. After backend API changes:
1. Restart backend: `uvicorn src.api.main:app --reload --port 8001` (from backend dir)
2. Update SDK types manually or regenerate if SDK generation is configured

## Documentation

Comprehensive docs in `/docs/`:

| File                      | Purpose                                          |
| ------------------------- | ------------------------------------------------ |
| STATE_ARCHITECTURE.md     | Data flow, query keys, state categories          |
| SDK_INTEGRATION.md        | All 11 SDK modules with methods and types        |
| PAGE_MAP.md               | Every route, component, SDK call mapping         |
| COMPONENT_CATALOG.md      | All 12+ components with props reference          |
| PATTERNS.md               | 10 implementation patterns (empty, error, etc.)  |
| UI_FLOW_DIAGRAM.md        | User journeys with Mermaid diagram               |
| DESIGN_TOKENS.md          | Colors, spacing, typography tokens               |
| CHANGELOG.md              | Version history and feature tracking             |

**Read docs before:**
- Adding routes (PAGE_MAP.md)
- Creating components (COMPONENT_CATALOG.md, PATTERNS.md)
- Integrating backend (SDK_INTEGRATION.md, STATE_ARCHITECTURE.md)

## Config & Environment

**Backend URL:**
Set in `SDKContext` provider (`libs/shared/design-system/src/context/SDKContext.tsx`):
```tsx
<SDKProvider baseUrl="http://localhost:8001">
```

**TanStack Query Config:**
- `staleTime`: 5 min (reduce API calls)
- `gcTime`: 10 min (cache for back navigation)
- `retry`: 2 for queries, 1 for mutations
- `refetchOnWindowFocus`: false

**TypeScript:**
- Strict mode enabled
- Target: ES2020
- Config: `tsconfig.json`, `tsconfig.app.json`

## Process Mining Domain

**Event Log Structure:**
Required: Case ID, Activity, Timestamp | Optional: Resource, additional attributes

**Supported Formats:**
CSV, XES

**Key Concepts:**
- **DFG (Directly-Follows Graph)**: Node = activity, Edge = sequence
- **Variant**: Unique activity sequence (e.g., A→B→C vs A→C→B)
- **Conformance**: Process execution vs expected model
- **Organizational Mining**: Resource interactions, handovers, workload

**PM4Py Backend:**
Backend wraps PM4Py algorithms (Alpha, Inductive, Heuristics miners). Frontend visualizes results.
