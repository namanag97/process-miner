# Feature API Layer

This directory contains the API integration layer for this feature, following standardized patterns for data fetching and mutations.

## Structure

```
api/
├── queries.ts       # GET requests (React Query)
├── mutations.ts     # POST/PUT/DELETE (React Query)
├── types.ts         # TypeScript interfaces
├── endpoints.ts     # API endpoint URLs
└── README.md        # This file
```

## Usage

### Fetching Data (Queries)

```tsx
import { useGetFeatureItems, useGetFeatureItem } from './api/queries';

function FeatureList() {
  // List with filters
  const { data, isLoading, error } = useGetFeatureItems({ status: 'active' });

  if (isLoading) return <LoadingState type="table" />;
  if (error) return <QueryError error={error} />;

  return <DataTable data={data.items} columns={columns} />;
}

function FeatureDetail({ id }: { id: string }) {
  // Single item
  const { data } = useGetFeatureItem(id);

  return <FeatureCard item={data.item} />;
}
```

### Modifying Data (Mutations)

```tsx
import { useCreateFeatureItem, useUpdateFeatureItem } from './api/mutations';

function CreateFeatureForm() {
  const createFeature = useCreateFeatureItem();

  const handleSubmit = async (formData) => {
    try {
      const result = await createFeature.mutateAsync(formData);
      toast.success('Created successfully!');
      navigate(`/features/${result.id}`);
    } catch (error) {
      // Error already handled in mutation
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" />
      <Button type="submit" loading={createFeature.isPending}>
        Create
      </Button>
    </form>
  );
}
```

## Patterns

### Query Keys

Query keys follow a hierarchical structure for targeted cache invalidation:

```ts
featureQueryKeys.all            // ['feature']
featureQueryKeys.lists()        // ['feature', 'list']
featureQueryKeys.list(filters)  // ['feature', 'list', filters]
featureQueryKeys.details()      // ['feature', 'detail']
featureQueryKeys.detail(id)     // ['feature', 'detail', id]
```

### Error Handling

Errors are handled at three levels:

1. **Query/Mutation level**: Automatic error state in hook
2. **UI level**: Display with `<QueryError>` component
3. **User feedback**: Toast notifications in mutations

```tsx
// Automatic error handling
const { data, error } = useGetFeatureItems();
if (error) return <QueryError error={error} />;

// Manual error handling
const mutation = useCreateFeatureItem({
  onError: (error) => {
    // Custom handling beyond toast
    logErrorToService(error);
  },
});
```

### Loading States

Use appropriate loading components based on context:

```tsx
// Tables/Lists
if (isLoading) return <TableLoadingState rows={5} />;

// Detail pages
if (isLoading) return <DetailLoadingState />;

// Metrics
if (isLoading) return <MetricsLoadingState />;

// Inline/small
if (isLoading) return <LoadingState type="inline" />;
```

### Optimistic Updates

Mutations can update the UI immediately before the server responds:

```tsx
const updateFeature = useUpdateFeatureItem({
  onMutate: async ({ id, data }) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: featureQueryKeys.detail(id) });

    // Snapshot previous value (for rollback)
    const previous = queryClient.getQueryData(featureQueryKeys.detail(id));

    // Optimistically update
    queryClient.setQueryData(featureQueryKeys.detail(id), (old) => ({
      ...old,
      item: { ...old.item, ...data },
    }));

    return { previous };
  },
  onError: (err, { id }, context) => {
    // Rollback on error
    if (context?.previous) {
      queryClient.setQueryData(featureQueryKeys.detail(id), context.previous);
    }
  },
});
```

### Cache Invalidation

After mutations, invalidate affected queries:

```tsx
// Invalidate all lists (refetch)
queryClient.invalidateQueries({ queryKey: featureQueryKeys.lists() });

// Invalidate specific item
queryClient.invalidateQueries({ queryKey: featureQueryKeys.detail(id) });

// Invalidate entire feature
queryClient.invalidateQueries({ queryKey: featureQueryKeys.all });

// Remove from cache (for deletes)
queryClient.removeQueries({ queryKey: featureQueryKeys.detail(id) });
```

## Best Practices

### DO

✅ Use `instrumentedFetch` for all API calls (logging, error tracking)
✅ Define query keys hierarchically for targeted invalidation
✅ Handle loading and error states in UI
✅ Use optimistic updates for better UX
✅ Provide toast notifications for user feedback
✅ Type all requests and responses
✅ Set appropriate `staleTime` based on data volatility

### DON'T

❌ Don't use `fetch` directly (use `instrumentedFetch`)
❌ Don't hardcode API URLs (use `endpoints.ts`)
❌ Don't ignore error states
❌ Don't use `any` types
❌ Don't invalidate more than necessary
❌ Don't forget to enable/disable queries based on dependencies
❌ Don't mix server state (React Query) with client state (useState)

## Testing

Test queries and mutations with React Query test utilities:

```tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useGetFeatureItems } from './queries';

test('fetches feature items', async () => {
  const queryClient = new QueryClient();
  const wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  const { result } = renderHook(() => useGetFeatureItems(), { wrapper });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));

  expect(result.current.data.items).toHaveLength(3);
});
```

## Migration from Old Pattern

If migrating from existing code:

1. Move API calls from components to `queries.ts` or `mutations.ts`
2. Replace `useState` + `useEffect` with React Query hooks
3. Update imports to use new hooks
4. Remove manual loading/error state management
5. Remove manual cache management

**Before:**
```tsx
function FeatureList() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/v1/features')
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return 'Loading...';
  if (error) return 'Error!';
  return <div>{data.items.length} items</div>;
}
```

**After:**
```tsx
import { useGetFeatureItems } from './api/queries';

function FeatureList() {
  const { data, isLoading, error } = useGetFeatureItems();

  if (isLoading) return <LoadingState type="table" />;
  if (error) return <QueryError error={error} />;
  return <div>{data.items.length} items</div>;
}
```

## References

- [TanStack Query Docs](https://tanstack.com/query/latest/docs/react/overview)
- [React Query Best Practices](https://tkdodo.eu/blog/practical-react-query)
- [Design System API Utilities](/libs/shared/design-system/src/api/)
