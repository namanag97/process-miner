# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
# Development
npx nx serve frontend-new     # Dev server (http://localhost:4200)
npx nx build frontend-new     # Production build
npx nx test frontend-new      # Run tests

# Generate new feature
npx ts-node scripts/generate-feature.ts <feature-name>

# Storybook
npm run storybook             # Component development (port 6006)

# Quality
npx nx lint frontend-new      # ESLint
npx tsc --noEmit              # Type check
```

## Architecture

Process mining & business automation SaaS frontend built with React 19 + TypeScript in an Nx monorepo.

**Core Structure:**
```
src/
├── core/                    # Core infrastructure (NEW)
│   ├── hooks/               # createFeatureHook factory
│   ├── components/          # FeaturePage, PageSection
│   └── plugins/             # FeatureRegistry
├── features/                # Feature modules (NEW)
│   └── _template/           # Scaffold for new features
├── pages/                   # Legacy pages (being migrated)
├── context/                 # UserContext, Notification, BackendHealth
└── components/              # App-level components

libs/shared/design-system/   # Shared components, SDK, utilities
```

**Tech Stack:**
Nx + React 19 + TypeScript + Ant Design 5 + TanStack Query v5 + React Router v6 + React Flow + Rspack

**State Philosophy:**
Server-first. 90% TanStack Query cache, 10% local state for UI. See STATE_ARCHITECTURE.md.

## MVP Mode (No Authentication)

Authentication is disabled for MVP. All users have full access.

```tsx
import { useUser } from './context/UserContext';

const { user } = useUser();
// user is always authenticated with role: 'admin'
```

## Feature Module System (NEW)

### Creating New Features

```bash
npx ts-node scripts/generate-feature.ts my-feature
```

Creates a complete feature module:
```
src/features/my-feature/
├── index.ts              # Exports + config
├── types.ts              # TypeScript types
├── routes.tsx            # Route config
├── hooks/index.ts        # Data hooks
├── pages/                # Page components
└── components/           # UI components
```

### Hook Factory (60% Less Boilerplate)

```tsx
import { createQueryHook, createMutationHook } from '@/core';

// Query hook - 5 lines instead of 20+
export const useProjectList = createQueryHook({
  queryKey: (options) => ['projects', 'list', options],
  queryFn: (sdk, options) => sdk.projects.list(options),
});

// Mutation with auto cache invalidation + toast
export const useDeleteProject = createMutationHook({
  mutationFn: (sdk, id) => sdk.projects.delete(id),
  invalidateKeys: [['projects', 'list']],
  onSuccessMessage: 'Project deleted',
});
```

### FeaturePage Component

Standardized page wrapper with loading/error/empty states:

```tsx
import { FeaturePage, PageSection } from '@/core';

function MyPage() {
  const { data, isLoading, error, refetch } = useMyData();

  return (
    <FeaturePage
      title="Page Title"
      breadcrumb={[{ label: 'Home', href: '/' }, { label: 'Current' }]}
      isLoading={isLoading}
      error={error}
      onRetry={refetch}
      isEmpty={!data}
      emptyState={{
        title: 'No data',
        description: 'Create something',
        actionLabel: 'Create',
        onAction: () => navigate('/new'),
      }}
      actions={<Button>Action</Button>}
    >
      <PageSection title="Section">
        <Content data={data} />
      </PageSection>
    </FeaturePage>
  );
}
```

## SDK & Backend Communication

All API calls go through `ProcessMiningSdk` via `SDKContext`.

```tsx
import { useSDK } from '@lumina/design-system';

const sdk = useSDK();
const result = await sdk.processes.list();
```

**SDK Modules (11):**
processes, discovery, analytics, conformance, organizational, simulation, predictions, ai, projects, workflows, notifications

See SDK_INTEGRATION.md for complete reference.

## Key Patterns

**Standard Query Pattern:**
```tsx
const { data, isLoading, error } = useMyFeatureList(options);
```

**Loading States:**
```tsx
<FeaturePage isLoading={isLoading}>  // Auto skeleton
// or manually:
if (isLoading) return <Skeleton active />;
```

**Error Handling:**
```tsx
<FeaturePage error={error} onRetry={refetch}>  // Auto error UI
// or manually:
if (error) return <QueryError error={error} />;
```

**URL State (shareable filters):**
```tsx
const [params, setParams] = useSearchParams();
const filter = params.get('status');
```

See PATTERNS.md and ERROR_HANDLING_GUIDE.md for more.

## Module Organization

**Core Infrastructure (`src/core/`):**
- `createQueryHook`, `createMutationHook` - Hook factories
- `FeaturePage`, `PageSection` - Page components
- `FeatureRegistry` - Plugin system

**Design System (`@lumina/design-system`):**
- Components: `AppShell`, `MetricCard`, `EmptyState`, `PageHeader`
- SDK: `useSDK()`, `SDKProvider`
- Utils: `toast`, `formatDuration`, `logAction`
- Theme: `luminaTheme`, `tokens`

**Import Aliases:**
```tsx
import { AppShell, useSDK, toast } from '@lumina/design-system';
import { FeaturePage, createQueryHook } from '@/core';
```

## Adding Features

### New Feature Module (Recommended)

1. Generate scaffold: `npx ts-node scripts/generate-feature.ts my-feature`
2. Update `types.ts` with entity types
3. Implement hooks with actual SDK methods
4. Connect pages to hooks
5. Add routes to App.tsx
6. Update PAGE_MAP.md

### New Page (Legacy Pattern)

1. Create in `src/pages/{feature}/NewPage.tsx`
2. Add route in `src/App.tsx`
3. Use FeaturePage wrapper
4. Use SDK hooks for data

### New API Integration

1. Add method to SDK module: `libs/shared/design-system/src/api/modules/{module}.ts`
2. Create hook with `createQueryHook` or `createMutationHook`
3. Export from feature's `hooks/index.ts`

## Documentation

| File                      | Purpose                                          |
| ------------------------- | ------------------------------------------------ |
| FEATURE_BLUEPRINT.md      | Feature module templates and patterns (NEW)      |
| ERROR_HANDLING_GUIDE.md   | Error handling strategies (NEW)                  |
| STATE_ARCHITECTURE.md     | Data flow, query keys, state categories          |
| SDK_INTEGRATION.md        | All 11 SDK modules with methods and types        |
| PAGE_MAP.md               | Every route, component, SDK call mapping         |
| COMPONENT_CATALOG.md      | All components with props reference              |
| PATTERNS.md               | Implementation patterns                          |

## Config & Environment

**Backend URL:**
```tsx
<SDKProvider baseUrl="http://localhost:8001">
```

**TanStack Query Config:**
- `staleTime`: 5 min
- `gcTime`: 10 min
- `retry`: 2 for queries, 1 for mutations

**TypeScript:** Strict mode, ES2020 target

## Process Mining Domain

**Event Log:** Case ID, Activity, Timestamp (required) + Resource, attributes (optional)

**Formats:** CSV, XES

**Concepts:**
- **DFG**: Directly-Follows Graph (nodes = activities, edges = sequences)
- **Variant**: Unique activity sequence
- **Conformance**: Execution vs expected model
- **Organizational**: Resource interactions, workload

**Backend:** FastAPI + PM4Py (../backend, port 8001)
