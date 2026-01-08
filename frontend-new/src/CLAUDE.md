# Frontend Source Code CLAUDE.md

## Overview

React 19 application source code with feature-based architecture, TanStack Query for server state, and Ant Design for UI components.

## Directory Structure

```
src/
├── App.tsx              # App shell, providers, routing setup
├── main.tsx             # Application entry point
├── routes.tsx           # All route definitions (single source of truth)
├── navigation.ts        # Navigation items and route mappings
│
├── features/            # Feature modules (self-contained)
│   ├── platform/        # Workspace, projects, settings, upload wizard
│   ├── explorer/        # Process visualization (DFG, variants)
│   ├── analytics/       # Performance analytics dashboards
│   ├── discovery/       # Process discovery UI
│   ├── ai/              # AI predictions and chat
│   ├── kpi/             # KPI management and dashboards
│   ├── auth/            # Login, authentication pages
│   └── landing/         # Landing page
│
├── shared/              # Shared components and utilities
│   ├── design-system.ts # UI component exports (ALWAYS import from here)
│   ├── context/         # UserContext, NotificationContext, BackendHealthContext
│   ├── core/            # Core utilities, base components
│   ├── hooks/           # Shared React hooks (useQueryWithErrorHandling, etc.)
│   ├── lib/             # Utilities (logger, formatters, validators)
│   └── ui/              # DevConsole, ErrorBoundary, PageSkeleton
│
├── api/                 # API integration
│   ├── client/          # OpenAPI SDK client configuration
│   └── hooks/           # TanStack Query hooks for API calls
│
├── stores/              # Global state stores
├── hooks/               # App-level hooks
├── config/              # Environment configuration (env.ts)
└── styles.css           # Global styles
```

## Key Files

### routes.tsx
All application routes are defined here. Uses React.lazy() for code splitting:

```typescript
const ExplorerPage = lazy(() => import('./features/explorer/pages/ExplorerPage'));

export const routes: RouteObject[] = [
  { path: '/explorer', element: page(<ExplorerPage />, 'Explorer') },
  // ...
];
```

### navigation.ts
Navigation items for sidebar/header, mapping to routes.

### shared/design-system.ts
Central export for all UI components. Always import from here:

```typescript
// CORRECT
import { Button, Card, Table, PageHeader } from '@/shared/design-system';

// WRONG - don't import directly
import { Button } from 'antd';
```

## Feature Module Pattern

Each feature is self-contained:

```
features/{feature}/
├── index.ts              # Public exports
├── pages/                # Route page components
│   ├── {Feature}ListPage.tsx
│   └── {Feature}DetailPage.tsx
├── components/           # Feature-specific UI components
├── hooks/                # TanStack Query hooks + business logic
└── types/                # TypeScript types
```

## Key Patterns

### API Queries (TanStack Query)

```typescript
import { useQuery } from '@tanstack/react-query';
import { DatasetsService } from '@/libs/openapi-sdk';

export function useDataset(id: string) {
  return useQuery({
    queryKey: ['dataset', id],
    queryFn: () => DatasetsService.getDataset({ datasetId: id }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

### Error Boundary Pattern

```typescript
import { ComponentErrorBoundary } from '@/shared/ui';

<ComponentErrorBoundary componentName="Process Graph" variant="card">
  <CytoscapeCanvas data={graphData} />
</ComponentErrorBoundary>
```

### DevConsole Logging

```typescript
import { devLog } from '@/shared/lib/logger';

devLog.action('Upload', 'File selected', { filename });
devLog.apiRequest('POST', '/api/v1/datasets', data);
devLog.apiResponse('POST', '/api/v1/datasets', 201, duration, response);
devLog.error('Upload', 'Failed to upload', { error: error.message });
```

Toggle DevConsole with backtick (`) key in development.

## Import Conventions

- Use `@/` alias for src imports: `import { Button } from '@/shared/design-system'`
- Features should NOT import from other features
- Shared components are in `@/shared/`
- API hooks are in `@/api/hooks/` or feature-specific `features/{feature}/hooks/`

## State Management

1. **Server State**: TanStack Query (caching, refetching)
2. **Global State**: React Context (UserContext, NotificationContext)
3. **Local State**: `useState`, `useReducer`
4. **URL State**: React Router (filters, pagination)

No Redux - deliberate choice for simplicity.
