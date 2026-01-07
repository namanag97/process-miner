# API Integration Guide

**Version:** 1.0
**Last Updated:** 2026-01-07
**For:** Process Mining SaaS Platform Frontend

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [Queries (GET)](#queries-get)
5. [Mutations (POST/PUT/DELETE)](#mutations-postputdelete)
6. [Error Handling](#error-handling)
7. [Loading States](#loading-states)
8. [Cache Management](#cache-management)
9. [Best Practices](#best-practices)
10. [Migration Guide](#migration-guide)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This guide establishes standardized patterns for API integration across the frontend application using **TanStack Query (React Query)** for server state management.

### Why React Query?

- **Automatic caching** - No manual cache management needed
- **Background refetching** - Keep data fresh automatically
- **Optimistic updates** - Instant UI feedback
- **Request deduplication** - Multiple components can share queries
- **Built-in loading/error states** - No manual state management
- **DevTools** - Inspect queries and cache in real-time

### When to Use This Guide

- Adding a new API endpoint
- Fetching data from the backend
- Creating, updating, or deleting resources
- Implementing forms with API integration
- Optimizing API performance

---

## Architecture

### Separation of Concerns

```
┌─────────────────────────────────────┐
│  Component (UI)                     │
│  - Renders UI                       │
│  - Handles user interactions        │
└──────────────┬──────────────────────┘
               │ uses
               ↓
┌─────────────────────────────────────┐
│  Hook (Business Logic)              │
│  - Feature-specific logic           │
│  - Data transformations             │
└──────────────┬──────────────────────┘
               │ uses
               ↓
┌─────────────────────────────────────┐
│  API Module (Data Fetching)         │
│  - React Query hooks                │
│  - Request/response handling        │
└──────────────┬──────────────────────┘
               │ calls
               ↓
┌─────────────────────────────────────┐
│  Backend API                        │
│  - FastAPI REST endpoints           │
│  - Business logic & persistence     │
└─────────────────────────────────────┘
```

### Directory Structure

Each feature has a dedicated `api/` directory:

```
src/features/{feature-name}/
├── api/
│   ├── queries.ts        # GET requests
│   ├── mutations.ts      # POST/PUT/DELETE requests
│   ├── types.ts          # Request/response types
│   ├── endpoints.ts      # API URL constants
│   └── README.md         # Feature-specific docs
├── components/           # UI components
├── hooks/                # Feature hooks (use api/)
├── pages/                # Route components
└── routes.tsx            # Route definitions
```

---

## Getting Started

### 1. Create API Directory

```bash
mkdir -p src/features/my-feature/api
```

### 2. Copy Template Files

Use the template as a starting point:

```bash
cp -r src/features/_template/api/* src/features/my-feature/api/
```

### 3. Update Types

Define your feature's types in `types.ts`:

```typescript
// types.ts
export interface MyFeatureItem {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  createdAt: string;
}

export interface CreateMyFeatureRequest {
  name: string;
  status?: 'active' | 'inactive';
}
```

### 4. Update Endpoints

Define API URLs in `endpoints.ts`:

```typescript
// endpoints.ts
const API_BASE = '/api/v1';

export const MY_FEATURE_ENDPOINTS = {
  list: `${API_BASE}/my-feature`,
  detail: (id: string) => `${API_BASE}/my-feature/${id}`,
  create: `${API_BASE}/my-feature`,
  update: (id: string) => `${API_BASE}/my-feature/${id}`,
  delete: (id: string) => `${API_BASE}/my-feature/${id}`,
} as const;
```

### 5. Implement Queries

Create query hooks in `queries.ts`:

```typescript
// queries.ts
import { useQuery } from '@tanstack/react-query';
import { instrumentedFetch } from '@lumina/design-system';
import { MY_FEATURE_ENDPOINTS } from './endpoints';
import type { MyFeatureItem } from './types';

export const myFeatureKeys = {
  all: ['my-feature'] as const,
  lists: () => [...myFeatureKeys.all, 'list'] as const,
  detail: (id: string) => [...myFeatureKeys.all, 'detail', id] as const,
};

export function useGetMyFeatureItems() {
  return useQuery({
    queryKey: myFeatureKeys.lists(),
    queryFn: async () => {
      const response = await instrumentedFetch(MY_FEATURE_ENDPOINTS.list);
      if (!response.ok) throw new Error('Failed to fetch items');
      return response.json() as Promise<MyFeatureItem[]>;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

---

## Queries (GET)

### Basic Query

```typescript
function MyComponent() {
  const { data, isLoading, error } = useGetMyFeatureItems();

  if (isLoading) return <LoadingState type="table" />;
  if (error) return <QueryError error={error} />;

  return <DataTable data={data} />;
}
```

### Query with Filters

```typescript
export function useGetMyFeatureItems(filters?: { status?: string }) {
  return useQuery({
    queryKey: myFeatureKeys.list(filters),
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);

      const url = `${MY_FEATURE_ENDPOINTS.list}?${params}`;
      const response = await instrumentedFetch(url);
      return response.json();
    },
  });
}

// Usage
function FilteredList() {
  const [status, setStatus] = useState('active');
  const { data } = useGetMyFeatureItems({ status });

  return <DataTable data={data} />;
}
```

### Conditional Queries

Use `enabled` to control when queries run:

```typescript
function ItemDetail({ id }: { id: string | null }) {
  const { data } = useGetMyFeatureItem(id, {
    enabled: !!id, // Only fetch when ID exists
  });

  if (!id) return <EmptyState message="Select an item" />;

  return <ItemCard item={data} />;
}
```

### Dependent Queries

Chain queries when one depends on another:

```typescript
function UserProfile({ userId }: { userId: string }) {
  // First query
  const { data: user } = useGetUser(userId);

  // Second query depends on first
  const { data: posts } = useGetUserPosts(user?.id, {
    enabled: !!user?.id,
  });

  return <div>...</div>;
}
```

### Polling (Auto-refetch)

```typescript
export function useGetLiveStatus(id: string) {
  return useQuery({
    queryKey: ['status', id],
    queryFn: () => fetchStatus(id),
    refetchInterval: 5000, // Poll every 5 seconds
    refetchIntervalInBackground: true,
  });
}
```

---

## Mutations (POST/PUT/DELETE)

### Create Mutation

```typescript
function CreateForm() {
  const createItem = useCreateMyFeatureItem();
  const navigate = useNavigate();

  const handleSubmit = async (formData: CreateMyFeatureRequest) => {
    try {
      const result = await createItem.mutateAsync(formData);
      toast.success('Created successfully!');
      navigate(`/my-feature/${result.id}`);
    } catch (error) {
      // Error toast already shown in mutation
      console.error(error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" required />
      <Button type="submit" loading={createItem.isPending}>
        Create
      </Button>
    </form>
  );
}
```

### Update Mutation

```typescript
function EditForm({ id, initialData }: Props) {
  const updateItem = useUpdateMyFeatureItem();

  const handleSave = async (data: UpdateMyFeatureRequest) => {
    await updateItem.mutateAsync({ id, data });
    // Cache automatically updated, UI reflects changes
  };

  return (
    <form onSubmit={handleSave}>
      <input name="name" defaultValue={initialData.name} />
      <Button type="submit" loading={updateItem.isPending}>
        Save
      </Button>
    </form>
  );
}
```

### Delete Mutation

```typescript
function DeleteButton({ id }: { id: string }) {
  const deleteItem = useDeleteMyFeatureItem();
  const navigate = useNavigate();

  const handleDelete = async () => {
    if (!confirm('Are you sure?')) return;

    await deleteItem.mutateAsync(id);
    navigate('/my-feature'); // Redirect after delete
  };

  return (
    <Button
      onClick={handleDelete}
      danger
      loading={deleteItem.isPending}
    >
      Delete
    </Button>
  );
}
```

### Optimistic Updates

Update UI immediately before server confirms:

```typescript
export function useUpdateMyFeatureItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await instrumentedFetch(
        MY_FEATURE_ENDPOINTS.update(id),
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        }
      );
      return response.json();
    },
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: myFeatureKeys.detail(id)
      });

      // Snapshot current value
      const previous = queryClient.getQueryData(
        myFeatureKeys.detail(id)
      );

      // Optimistically update
      queryClient.setQueryData(myFeatureKeys.detail(id), (old: any) => ({
        ...old,
        ...data,
      }));

      return { previous };
    },
    onError: (err, { id }, context) => {
      // Rollback on error
      if (context?.previous) {
        queryClient.setQueryData(
          myFeatureKeys.detail(id),
          context.previous
        );
      }
      toast.error('Update failed');
    },
    onSuccess: (data, { id }) => {
      // Invalidate to refetch latest data
      queryClient.invalidateQueries({
        queryKey: myFeatureKeys.detail(id)
      });
      queryClient.invalidateQueries({
        queryKey: myFeatureKeys.lists()
      });
      toast.success('Updated successfully');
    },
  });
}
```

---

## Error Handling

### Three Levels of Error Handling

#### 1. Query/Mutation Level

Automatic error state in the hook:

```typescript
const { data, error, isError } = useGetMyFeatureItems();

if (isError) {
  return <QueryError error={error} />;
}
```

#### 2. UI Level

Use error boundary components:

```typescript
import { ErrorBoundary } from '@lumina/design-system';

function FeatureRoutes() {
  return (
    <ErrorBoundary fallback={<FeatureErrorFallback />}>
      <Routes>
        <Route path="/" element={<FeatureList />} />
      </Routes>
    </ErrorBoundary>
  );
}
```

#### 3. User Feedback Level

Toast notifications for mutations:

```typescript
export function useCreateMyFeatureItem() {
  return useMutation({
    mutationFn: createItem,
    onSuccess: () => {
      toast.success('Created successfully!');
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to create item');
    },
  });
}
```

### Error Types

**Network Errors:**
```typescript
if (isNetworkError(error)) {
  return <QueryError error={error} retry={() => refetch()} />;
}
```

**Validation Errors (400):**
```typescript
if (error.status === 400) {
  // Show inline form errors
  return <FormErrors errors={error.details} />;
}
```

**Not Found (404):**
```typescript
if (error.status === 404) {
  return <EmptyState message="Item not found" />;
}
```

**Server Errors (500):**
```typescript
if (error.status >= 500) {
  return <QueryError error={error} message="Server error. Please try again." />;
}
```

---

## Loading States

### Query Loading

```typescript
const { data, isLoading, isFetching } = useGetMyFeatureItems();

// isLoading: true on first load
// isFetching: true on background refetch

if (isLoading) {
  return <TableLoadingState rows={5} />;
}

if (isFetching) {
  // Show subtle loading indicator
  return <div><Spin size="small" /> Refreshing...</div>;
}
```

### Loading State Components

Use appropriate loaders from design system:

```typescript
import {
  LoadingState,
  TableLoadingState,
  DetailLoadingState,
  MetricsLoadingState,
  PageLoadingState,
} from '@lumina/design-system';

// Tables
if (isLoading) return <TableLoadingState rows={5} />;

// Detail pages
if (isLoading) return <DetailLoadingState />;

// Metrics/cards
if (isLoading) return <MetricsLoadingState count={4} />;

// Full page
if (isLoading) return <PageLoadingState message="Loading..." />;

// Inline
if (isLoading) return <LoadingState type="inline" />;
```

### Mutation Loading

```typescript
function SubmitButton() {
  const mutation = useCreateMyFeatureItem();

  return (
    <Button type="submit" loading={mutation.isPending}>
      {mutation.isPending ? 'Creating...' : 'Create'}
    </Button>
  );
}
```

---

## Cache Management

### Query Keys

Hierarchical structure enables targeted invalidation:

```typescript
export const myFeatureKeys = {
  all: ['my-feature'] as const,
  lists: () => [...myFeatureKeys.all, 'list'] as const,
  list: (filters) => [...myFeatureKeys.lists(), filters] as const,
  details: () => [...myFeatureKeys.all, 'detail'] as const,
  detail: (id) => [...myFeatureKeys.details(), id] as const,
};
```

### Invalidation

After mutations, invalidate affected queries:

```typescript
// Invalidate all lists (refetch all list queries)
queryClient.invalidateQueries({
  queryKey: myFeatureKeys.lists()
});

// Invalidate specific item (refetch that item)
queryClient.invalidateQueries({
  queryKey: myFeatureKeys.detail(id)
});

// Invalidate entire feature (refetch everything)
queryClient.invalidateQueries({
  queryKey: myFeatureKeys.all
});
```

### Manual Updates

Set query data directly (for optimistic updates):

```typescript
// Update cache with new data
queryClient.setQueryData(myFeatureKeys.detail(id), newData);

// Update cache with function
queryClient.setQueryData(myFeatureKeys.detail(id), (old) => ({
  ...old,
  name: 'Updated Name',
}));
```

### Remove from Cache

For deletions:

```typescript
queryClient.removeQueries({
  queryKey: myFeatureKeys.detail(id)
});
```

### Stale Time

Control how long data stays fresh:

```typescript
useQuery({
  queryKey: ['items'],
  queryFn: fetchItems,
  staleTime: 5 * 60 * 1000, // 5 minutes (common)
  staleTime: 30 * 1000,     // 30 seconds (frequently changing)
  staleTime: 60 * 60 * 1000, // 1 hour (rarely changes)
  staleTime: Infinity,       // Never auto-refetch
});
```

---

## Best Practices

### DO ✅

1. **Use `instrumentedFetch`** for all API calls
   ```typescript
   import { instrumentedFetch } from '@lumina/design-system';
   const response = await instrumentedFetch(url);
   ```

2. **Define hierarchical query keys**
   ```typescript
   const keys = {
     all: ['feature'] as const,
     lists: () => [...keys.all, 'list'] as const,
     detail: (id) => [...keys.all, 'detail', id] as const,
   };
   ```

3. **Handle loading and error states**
   ```typescript
   if (isLoading) return <LoadingState />;
   if (error) return <QueryError error={error} />;
   ```

4. **Use optimistic updates for better UX**
   ```typescript
   onMutate: async ({ id, data }) => {
     await queryClient.cancelQueries({ queryKey: keys.detail(id) });
     const previous = queryClient.getQueryData(keys.detail(id));
     queryClient.setQueryData(keys.detail(id), { ...previous, ...data });
     return { previous };
   },
   ```

5. **Set appropriate `staleTime`**
   ```typescript
   staleTime: 5 * 60 * 1000, // 5 minutes for most data
   ```

6. **Use `enabled` for conditional queries**
   ```typescript
   useQuery({
     queryKey: ['item', id],
     queryFn: () => fetchItem(id),
     enabled: !!id,
   });
   ```

7. **Provide toast notifications**
   ```typescript
   onSuccess: () => toast.success('Success!'),
   onError: (err) => toast.error(err.message),
   ```

### DON'T ❌

1. **Don't use `fetch` directly**
   ```typescript
   ❌ const res = await fetch(url);
   ✅ const res = await instrumentedFetch(url);
   ```

2. **Don't hardcode URLs**
   ```typescript
   ❌ await fetch('/api/v1/items/123');
   ✅ await instrumentedFetch(ENDPOINTS.detail('123'));
   ```

3. **Don't ignore error states**
   ```typescript
   ❌ const { data } = useQuery(...);
   ✅ const { data, isLoading, error } = useQuery(...);
      if (isLoading) return <Loading />;
      if (error) return <Error />;
   ```

4. **Don't use `any` types**
   ```typescript
   ❌ const data: any = await response.json();
   ✅ const data = await response.json() as MyType;
   ```

5. **Don't over-invalidate**
   ```typescript
   ❌ queryClient.invalidateQueries(); // Invalidates EVERYTHING
   ✅ queryClient.invalidateQueries({ queryKey: keys.lists() });
   ```

6. **Don't mix server/client state**
   ```typescript
   ❌ const [items, setItems] = useState([]); // Server data in useState
   ✅ const { data: items } = useGetItems(); // Use React Query
   ```

7. **Don't forget to handle `isPending`**
   ```typescript
   ❌ <Button onClick={handleSubmit}>Submit</Button>
   ✅ <Button onClick={handleSubmit} loading={mutation.isPending}>
   ```

---

## Migration Guide

### From Old Pattern to React Query

**Before (Old Pattern):**
```typescript
function ItemList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/v1/items')
      .then(res => res.json())
      .then(data => {
        setItems(data.items);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  }, []);

  if (loading) return 'Loading...';
  if (error) return 'Error!';
  return <Table data={items} />;
}
```

**After (React Query):**
```typescript
import { useGetItems } from './api/queries';

function ItemList() {
  const { data, isLoading, error } = useGetItems();

  if (isLoading) return <TableLoadingState rows={5} />;
  if (error) return <QueryError error={error} />;
  return <Table data={data.items} />;
}
```

### Migration Steps

1. **Create API directory structure**
2. **Move API calls to `queries.ts` and `mutations.ts`**
3. **Replace `useState` + `useEffect` with React Query hooks**
4. **Update component imports**
5. **Remove manual state management**
6. **Test thoroughly**

---

## Troubleshooting

### Query Not Refetching

**Problem:** Data doesn't update after mutation

**Solution:** Invalidate affected queries
```typescript
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: keys.lists() });
},
```

### Too Many Requests

**Problem:** Query refetches too often

**Solution:** Increase `staleTime`
```typescript
useQuery({
  queryKey: ['items'],
  queryFn: fetchItems,
  staleTime: 5 * 60 * 1000, // 5 minutes
});
```

### Stale Data After Update

**Problem:** UI shows old data after mutation

**Solution:** Use optimistic updates or invalidate cache
```typescript
onSuccess: (newData, { id }) => {
  queryClient.setQueryData(keys.detail(id), newData);
},
```

### TypeScript Errors

**Problem:** Type mismatch in query/mutation

**Solution:** Properly type the hook
```typescript
useQuery<MyType, Error>({
  queryKey: ['items'],
  queryFn: async () => {
    const res = await fetch(url);
    return res.json() as Promise<MyType>;
  },
});
```

### React Query DevTools

Enable DevTools for debugging:

```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

function App() {
  return (
    <>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </>
  );
}
```

---

## References

- [TanStack Query Docs](https://tanstack.com/query/latest/docs/react/overview)
- [React Query Best Practices (TkDodo)](https://tkdodo.eu/blog/practical-react-query)
- [Design System API Utilities](../libs/shared/design-system/src/api/)
- [Template API Structure](../src/features/_template/api/)

---

**Questions?** Reach out to the frontend team or consult the `_template` feature for examples.
