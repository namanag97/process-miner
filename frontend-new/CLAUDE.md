# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

React 19 + TypeScript frontend for a Process Mining SaaS Platform. Uses Nx monorepo with Rspack bundling, TanStack Query for server state, and Ant Design for UI components.

**See also:** [Root CLAUDE.md](../CLAUDE.md) for full-stack context and backend commands.

## Essential Commands

```bash
# Development
npm run start              # Dev server on port 4200
npm run build              # Production build
npm run test               # Jest tests
npx nx typecheck           # TypeScript check

# API Client Generation
npm run generate:sdk       # Regenerate from OpenAPI spec (backend must be running)

# Code Quality
npm run lint               # ESLint
npx nx lint --fix          # Auto-fix lint issues
```

### Running Single Tests

```bash
npm run test -- --testPathPattern="ProjectCard"     # Match test file name
npm run test -- --testNamePattern="renders card"    # Match test name
npm run test -- src/features/explorer               # Specific directory
```

## Architecture

### Feature Plugin System

Features auto-register via `FeatureRegistry`. Each feature is self-contained:

```
src/features/{feature}/
├── index.ts              # Registers routes via registerFeature()
├── {Feature}Page.tsx     # Main page component
├── components/           # Feature-specific UI
├── hooks/                # Feature-specific hooks
└── types/                # TypeScript types
```

**To add a new feature:**
1. Create directory in `src/features/`
2. Register in feature's `index.ts`:
```typescript
import { registerFeature } from '@/shared/core/plugins/FeatureRegistry';

registerFeature({
  id: 'my-feature',
  name: 'My Feature',
  routes: [{ path: '/my-feature', element: <MyFeaturePage /> }],
  navConfig: { icon: 'AppstoreOutlined', label: 'My Feature', order: 10 },
});
```
3. Export from `src/features/index.ts`

### Layer Structure

```
src/
├── App.tsx                 # App shell, providers, routing
├── features/               # Feature modules (plugin architecture)
│   ├── platform/           # Workspace, projects, settings
│   ├── explorer/           # Process visualization (DFG, Petri nets)
│   ├── analytics/          # Performance analytics
│   ├── ai/                 # AI predictions
│   ├── discovery/          # Process discovery
│   └── kpi/                # KPI dashboards
├── shared/                 # Shared code
│   ├── design-system.ts    # UI components (import from here)
│   ├── context/            # UserContext, NotificationContext, BackendHealthContext
│   ├── core/plugins/       # FeatureRegistry
│   ├── hooks/              # Shared custom hooks
│   ├── lib/                # Utilities (logger, formatters)
│   └── ui/                 # DevConsole, ErrorBoundary
├── api/                    # API integration
│   ├── client/             # Auto-generated SDK
│   └── hooks/              # TanStack Query hooks
└── libs/                   # Monorepo libraries
    └── openapi-sdk/        # Generated TypeScript API client
```

### State Management

- **Server State**: TanStack Query (caching, refetching, optimistic updates)
- **Global State**: React Context (User, Notifications, BackendHealth)
- **Local State**: `useState`, `useReducer`
- **No Redux** - deliberate choice for simplicity

### Data Flow Pattern

```typescript
// 1. Create query hook
function useDatasets() {
  return useQuery({
    queryKey: ['datasets'],
    queryFn: () => datasetsApi.getAll(),
    staleTime: 5 * 60 * 1000, // 5 min cache
  });
}

// 2. Use in component
function DatasetsPage() {
  const { data, isLoading, error } = useDatasets();
  if (isLoading) return <Spin />;
  if (error) return <Alert type="error" message={error.message} />;
  return <DatasetList datasets={data} />;
}
```

## Key Patterns

### Design System Imports

Always import UI components from the design system:

```typescript
// Correct
import { Button, Card, Table, PageHeader } from '@/shared/design-system';

// Avoid
import { Button } from 'antd';
```

### Error Handling

```typescript
// Query errors handled declaratively
const { data, error, isError } = useQuery({...});
if (isError) return <ErrorAlert error={error} />;

// Imperative errors
try {
  await api.deleteDataset(id);
  message.success('Deleted');
} catch (error) {
  message.error(`Failed: ${error.message}`);
}
```

### DevConsole Logging

```typescript
import { devLog } from '@/shared/lib/logger';

devLog.action('UserAction', 'Clicked button', { buttonId });
devLog.apiRequest('POST', '/api/v1/datasets', data);
devLog.apiResponse('POST', '/api/v1/datasets', 201, duration, response);
devLog.error('FeatureName', 'Error message', { details });
```

Toggle DevConsole with backtick (`) key in development.

### TypeScript Conventions

- **No `any`**: Use `unknown` with type guards
- **Props interfaces**: `interface MyComponentProps { ... }`
- **Hooks prefix**: `useCamelCase`
- **Files**: `PascalCase.tsx` for components, `camelCase.ts` for utilities

```typescript
// Error handling pattern
catch (err: unknown) {
  const error = err instanceof Error ? err : new Error(String(err));
  devLog.error('Feature', error.message);
}
```

## Development Workflow

### Adding API Integration

1. Ensure backend is running on port 8001
2. Run `npm run generate:sdk` to regenerate types
3. Create query hook in `src/api/hooks/`
4. Use hook in component

### Testing

```bash
npm run test                           # All tests
npm run test -- --watch                # Watch mode
npm run test -- --coverage             # Coverage report
npm run test -- --testPathPattern=explorer  # Specific feature
```

Test files are co-located: `Component.tsx` + `Component.test.tsx`

## Environment Variables

Create `.env` from `.env.example`:

```bash
VITE_API_URL=http://localhost:8001
VITE_ENABLE_DEV_CONSOLE=true
```

Access via `src/config/env.ts`:
```typescript
import { env } from '@/config/env';
const apiUrl = env.apiBaseUrl;
```

## Troubleshooting

**TypeScript errors after API changes:**
```bash
npm run generate:sdk
# Restart TypeScript server in IDE
```

**Module not found:**
```bash
rm -rf node_modules package-lock.json
npm install
npx nx reset  # Clear Nx cache
```

**API calls failing:**
```bash
curl http://localhost:8001/health/live  # Check backend
# Open DevConsole (backtick key) to see detailed logs
```
