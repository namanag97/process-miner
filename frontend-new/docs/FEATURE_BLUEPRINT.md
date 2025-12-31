# Feature Blueprint

This document provides templates and patterns for creating new features in the frontend.

## Quick Start

```bash
# Generate a new feature
npx ts-node scripts/generate-feature.ts my-feature
```

This creates:
```
src/features/my-feature/
├── index.ts              # Public exports + feature config
├── types.ts              # TypeScript types
├── routes.tsx            # Route configuration
├── hooks/
│   └── index.ts          # Data fetching hooks
├── pages/
│   ├── MyFeatureListPage.tsx
│   └── MyFeatureDetailPage.tsx
└── components/
    └── MyFeatureCard.tsx
```

## Feature Module Structure

### index.ts - Feature Entry Point

```typescript
// Feature configuration
export const FEATURE_ID = 'my-feature';
export const FEATURE_CONFIG = {
  id: 'my-feature',
  name: 'My Feature',
  version: '1.0.0',
  icon: 'AppstoreOutlined',
  navPath: '/my-feature',
  navOrder: 10,
};

// Page exports (lazy-loadable)
export { MyFeatureListPage } from './pages/MyFeatureListPage';
export { MyFeatureDetailPage } from './pages/MyFeatureDetailPage';

// Hook exports (for cross-feature use)
export { useMyFeatureList, useMyFeatureDetail } from './hooks';

// Type exports
export type { MyFeature, MyFeatureDetail } from './types';
```

### types.ts - Type Definitions

```typescript
// Base entity (list view)
export interface MyFeature {
  id: string;
  name: string;
  status: 'draft' | 'active' | 'archived';
  createdAt: string;
  updatedAt: string;
}

// Detailed entity (detail view)
export interface MyFeatureDetail extends MyFeature {
  metadata?: Record<string, unknown>;
}

// Input types (mutations)
export interface MyFeatureCreateInput {
  name: string;
  description?: string;
}

// Query options
export interface MyFeatureListOptions {
  page?: number;
  pageSize?: number;
  search?: string;
}
```

### hooks/index.ts - Data Hooks

```typescript
import { createQueryHook, createMutationHook } from '@/core';

// Query hook (5 lines instead of 20+)
export const useMyFeatureList = createQueryHook({
  queryKey: (options) => ['my-feature', 'list', options],
  queryFn: (sdk, options) => sdk.myFeature.list(options),
});

export const useMyFeatureDetail = createQueryHook({
  queryKey: (id) => ['my-feature', 'detail', id],
  queryFn: (sdk, id) => sdk.myFeature.get(id),
  enabled: (id) => !!id,
});

// Mutation hook with automatic cache invalidation
export const useCreateMyFeature = createMutationHook({
  mutationFn: (sdk, input) => sdk.myFeature.create(input),
  invalidateKeys: [['my-feature', 'list']],
  onSuccessMessage: 'Created successfully',
});
```

### pages/MyFeatureListPage.tsx - List Page

```typescript
import { FeaturePage, PageSection } from '@/core';
import { useMyFeatureList } from '../hooks';

export function MyFeatureListPage() {
  const { data, isLoading, error, refetch } = useMyFeatureList();

  return (
    <FeaturePage
      title="My Features"
      description="Manage your features"
      breadcrumb={[{ label: 'My Features' }]}
      isLoading={isLoading}
      error={error}
      onRetry={refetch}
      isEmpty={!data?.items.length}
      emptyState={{
        title: 'No features yet',
        description: 'Create your first feature',
        actionLabel: 'Create',
        onAction: () => navigate('/my-feature/new'),
      }}
      actions={<Button type="primary">Create</Button>}
    >
      <PageSection>
        <Table dataSource={data?.items} columns={columns} />
      </PageSection>
    </FeaturePage>
  );
}
```

## Hook Factory Reference

### createQueryHook

```typescript
const useData = createQueryHook<ResponseType, ParamsType>({
  queryKey: (params) => ['domain', params],  // Required
  queryFn: (sdk, params) => sdk.module.method(params),  // Required
  staleTime: 5 * 60 * 1000,  // Optional, default 5 min
  gcTime: 10 * 60 * 1000,    // Optional, default 10 min
  enabled: (params) => !!params,  // Optional
  select: (data) => data.items,   // Optional
});

// Usage
const { data, isLoading, error, refetch } = useData(params);
```

### createMutationHook

```typescript
const useMutate = createMutationHook<ResponseType, InputType>({
  mutationFn: (sdk, input) => sdk.module.method(input),  // Required
  invalidateKeys: [['domain', 'list']],  // Optional
  onSuccessMessage: 'Success!',          // Optional
  onErrorMessage: 'Failed',              // Optional
  onSuccess: (data) => {},               // Optional
  onError: (error) => {},                // Optional
});

// Usage
const mutation = useMutate();
await mutation.mutateAsync(input);
```

## FeaturePage Component

Handles loading, error, and empty states consistently:

```typescript
<FeaturePage
  // Header
  title="Page Title"                    // Required
  description="Page description"        // Optional
  breadcrumb={[                         // Optional
    { label: 'Home', href: '/' },
    { label: 'Current' }
  ]}
  actions={<Button>Action</Button>}     // Optional

  // States
  isLoading={isLoading}                 // Shows skeleton
  error={error}                         // Shows error with retry
  onRetry={refetch}                     // Retry callback
  isEmpty={!data}                       // Shows empty state
  emptyState={{                         // Empty state config
    title: 'Nothing here',
    description: 'Get started by...',
    actionLabel: 'Create',
    onAction: () => navigate('/new'),
  }}

  // Options
  auditCategory="my-feature"            // For audit logging
  noPadding={false}                     // Remove content padding
  maxWidth={1200}                       // Max content width
>
  {/* Your content */}
</FeaturePage>
```

## Feature Registration

For dynamic routing via FeatureRegistry:

```typescript
// In feature index.ts
import { FeatureRegistry } from '@/core';

FeatureRegistry.register({
  id: 'my-feature',
  name: 'My Feature',
  version: '1.0.0',
  icon: 'AppstoreOutlined',
  navPath: '/my-feature',
  navOrder: 10,
  routes: [
    { path: '/my-feature', element: <MyFeatureListPage /> },
    { path: '/my-feature/:id', element: <MyFeatureDetailPage /> },
  ],
});
```

## Checklist for New Features

- [ ] Generate feature scaffold: `npx ts-node scripts/generate-feature.ts <name>`
- [ ] Update types.ts with actual entity types
- [ ] Implement hooks with real SDK methods
- [ ] Connect pages to hooks
- [ ] Add routes to App.tsx or FeatureRegistry
- [ ] Add navigation entry if needed
- [ ] Update PAGE_MAP.md documentation
