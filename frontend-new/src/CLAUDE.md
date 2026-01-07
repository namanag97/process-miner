# Frontend Source Code CLAUDE.md

## Overview
React 19 application source code with feature-based architecture.

## Directory Structure

```
src/
├── App.tsx              # Root component with providers
├── main.tsx             # Application entry point
├── routes.tsx           # Route definitions
├── navigation.ts        # Navigation configuration
├── features/            # Feature modules
│   ├── ai/              # AI Assistant feature
│   ├── analytics/       # Analytics dashboards
│   ├── discovery/       # Process discovery
│   ├── explorer/        # Data explorer
│   ├── kpi/             # KPI management
│   └── platform/        # Platform features (settings, projects, upload)
├── shared/              # Shared components and utilities
│   ├── components/      # Reusable UI components
│   ├── core/            # Core utilities
│   └── hooks/           # Shared React hooks
├── api/                 # API client configuration
├── stores/              # Global state management
├── hooks/               # App-level hooks
├── config/              # Environment configuration
└── styles.css           # Global styles
```

## Feature Module Pattern

Each feature follows this structure:
```
features/
└── {feature}/
    ├── index.ts         # Public exports
    ├── pages/           # Page components
    ├── components/      # Feature-specific components
    ├── hooks/           # Feature-specific hooks
    ├── api/             # API queries/mutations
    └── types.ts         # TypeScript types
```

## Key Patterns

### API Queries (TanStack Query)
```typescript
import { useQuery } from '@tanstack/react-query';
import { api } from '@/api';

export function useDataset(id: string) {
  return useQuery({
    queryKey: ['dataset', id],
    queryFn: () => api.datasets.getDataset(id),
  });
}
```

### Page Component
```typescript
export function DatasetListPage() {
  const { data, isLoading } = useDatasets();

  if (isLoading) return <PageSkeleton />;

  return <DatasetTable data={data} />;
}
```

## Import Conventions

- Use `@/` alias for src imports: `import { Button } from '@/shared/components'`
- Features should not import from other features
- Shared components are in `shared/components/`
