# Frontend Features CLAUDE.md

## Overview

Feature modules implementing the main application functionality. Each feature is self-contained with its own pages, components, hooks, and types.

## Feature Modules

### platform/
Core platform features for workspace and project management.
- **Projects** - Project CRUD, dataset management
- **Upload Wizard** - Multi-step dataset upload with column mapping
- **Settings** - User preferences, workspace settings

### explorer/
Process exploration and visualization.
- **DFG Viewer** - Interactive Directly-Follows Graph with Cytoscape
- **Variant Analysis** - Process variant comparison
- **Case Explorer** - Individual case inspection

### analytics/
Performance analytics dashboards.
- **Bottleneck Analysis** - Identify slow activities
- **Cycle Time** - Duration distribution analysis
- **Throughput** - Volume and trends
- **Rework Detection** - Repeated activity patterns

### discovery/
Process discovery features.
- **Model Discovery** - Alpha, Inductive, Heuristics miners
- **Model Viewer** - Petri net visualization
- **Discovery Settings** - Algorithm configuration

### ai/
AI-powered insights and predictions.
- **Chat Interface** - Natural language interaction
- **Predictions** - Next activity, remaining time
- **Insights** - AI-generated process insights

### kpi/
KPI management and monitoring.
- **KPI Definitions** - Define custom KPIs
- **KPI Dashboard** - Real-time monitoring
- **Targets** - Set and track targets

### auth/
Authentication pages.
- **Login** - Email/password authentication
- **Token Refresh** - Automatic token refresh

### landing/
Public landing page.
- **Hero Section** - Product introduction
- **Features** - Feature showcase

## Feature Structure Pattern

```
{feature}/
├── index.ts              # Public exports
├── pages/                # Route page components
│   ├── {Feature}ListPage.tsx
│   └── {Feature}DetailPage.tsx
├── components/           # Feature-specific UI components
│   ├── {Feature}Card.tsx
│   └── {Feature}Form.tsx
├── hooks/                # TanStack Query hooks + business logic
│   ├── use{Feature}.ts
│   └── use{Feature}Mutation.ts
└── types/                # TypeScript types (optional)
    └── index.ts
```

## Guidelines

### DO
- Keep features self-contained
- Export only public API through `index.ts`
- Use TanStack Query for data fetching
- Import UI components from `@/shared/design-system`
- Add DevConsole logging for key actions
- Handle errors with try/catch + devLog.error()

### DON'T
- Import from other features (use shared instead)
- Use `any` type (use proper types or `unknown`)
- Skip error handling in async operations
- Import directly from `antd` (use design-system)

## Adding a New Feature

1. Create feature directory: `src/features/{feature-name}/`
2. Add pages in `pages/` subdirectory
3. Create hooks in `hooks/` subdirectory
4. Add route in `src/routes.tsx`
5. Add navigation item in `src/navigation.ts` (if needed)

Example:
```typescript
// src/routes.tsx
const MyFeaturePage = lazy(() => import('./features/my-feature/pages/MyFeaturePage'));

export const routes: RouteObject[] = [
  // ...existing routes
  { path: '/my-feature', element: page(<MyFeaturePage />, 'My Feature') },
];
```
