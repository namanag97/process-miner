# Error Handling Guide

This document describes error handling patterns and strategies used in the frontend.

## Overview

The frontend uses a layered error handling approach:

1. **API Client Level** - Network errors, retries, validation
2. **Query/Mutation Level** - React Query error states
3. **Component Level** - Error boundaries, error UI
4. **Global Level** - Unhandled errors, crash reporting

## API Client Errors

### Error Types

```typescript
// API errors from backend
interface APIError {
  status: number;        // HTTP status code
  title: string;         // Error title
  detail: string;        // Detailed message
  type?: string;         // Error type URI
  instance?: string;     // Request identifier
}

// Network errors
interface NetworkError {
  message: string;
  isNetworkError: true;
}
```

### Retry Logic

The API client automatically retries failed requests:

- **Max Retries**: 3
- **Retry Window**: 30 seconds
- **Backoff**: Exponential (1s, 2s, 4s)
- **Retryable Errors**: Network errors, 5xx, 408, 429

```typescript
// In client.ts
const RETRY_CONFIG = {
  maxRetries: 3,
  maxRetryWindow: 30000,
  baseDelay: 1000,
  retryableCodes: [408, 429, 500, 502, 503, 504],
};
```

## Query Error Handling

### With FeaturePage

The `FeaturePage` component handles errors automatically:

```typescript
function MyPage() {
  const { data, isLoading, error, refetch } = useMyData();

  return (
    <FeaturePage
      title="My Page"
      isLoading={isLoading}
      error={error}        // Shows error UI with retry button
      onRetry={refetch}    // Called when user clicks retry
    >
      <Content data={data} />
    </FeaturePage>
  );
}
```

### Manual Error Handling

```typescript
function MyComponent() {
  const { data, error, refetch } = useMyData();

  if (error) {
    return (
      <Result
        status="error"
        title="Failed to load"
        subTitle={error.message}
        extra={<Button onClick={() => refetch()}>Try Again</Button>}
      />
    );
  }

  return <Content data={data} />;
}
```

## Mutation Error Handling

### With createMutationHook

```typescript
// Automatic toast on error
const useCreateItem = createMutationHook({
  mutationFn: (sdk, input) => sdk.items.create(input),
  onErrorMessage: 'Failed to create item',  // Shows error toast
});
```

### Custom Error Handling

```typescript
const mutation = useCreateItem();

const handleSubmit = async (data) => {
  try {
    await mutation.mutateAsync(data);
    navigate('/items');
  } catch (error) {
    // Handle specific errors
    if (error.status === 409) {
      form.setError('name', { message: 'Name already exists' });
    }
  }
};
```

## Error Boundary

Global error boundary catches unhandled React errors:

```typescript
// In App.tsx
<GlobalErrorBoundary onError={handleGlobalError}>
  <App />
</GlobalErrorBoundary>

// Error handler
function handleGlobalError(report: ErrorReport) {
  console.error('Global error:', report);
  // Send to error tracking service
}
```

## Toast Notifications

For user feedback on errors:

```typescript
import { toast } from '@lumina/design-system';

// Error toast
toast.error('Failed to save changes');

// Success toast
toast.success('Changes saved');

// With custom duration
toast.error('Network error', { duration: 5000 });
```

## Common Error Patterns

### Network Connectivity

```typescript
function useNetworkAwareQuery(options) {
  const isOnline = useOnlineStatus();

  return useQuery({
    ...options,
    enabled: isOnline && options.enabled,
    meta: {
      showOfflineWarning: true,
    },
  });
}
```

### Validation Errors

```typescript
// Form validation with Zod
const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
});

// In component
try {
  const data = schema.parse(formData);
  await mutation.mutateAsync(data);
} catch (error) {
  if (error instanceof z.ZodError) {
    error.errors.forEach((e) => {
      form.setError(e.path[0], { message: e.message });
    });
  }
}
```

### 404 Not Found

```typescript
function DetailPage() {
  const { id } = useParams();
  const { data, error } = useItemDetail(id);

  if (error?.status === 404) {
    return (
      <Result
        status="404"
        title="Not Found"
        subTitle="The item you're looking for doesn't exist"
        extra={<Button onClick={() => navigate(-1)}>Go Back</Button>}
      />
    );
  }

  return <ItemDetails data={data} />;
}
```

### Permission Errors

```typescript
function ProtectedAction() {
  const { user } = useUser();
  const mutation = useDeleteItem();

  if (user.role !== 'admin') {
    return <Tooltip title="Admin only"><Button disabled>Delete</Button></Tooltip>;
  }

  return (
    <Button
      danger
      onClick={() => mutation.mutate(id)}
      loading={mutation.isPending}
    >
      Delete
    </Button>
  );
}
```

## Error Recovery

### Optimistic Updates with Rollback

```typescript
const mutation = useMutation({
  mutationFn: updateItem,
  onMutate: async (newData) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries(['items', id]);

    // Snapshot previous value
    const previous = queryClient.getQueryData(['items', id]);

    // Optimistically update
    queryClient.setQueryData(['items', id], newData);

    return { previous };
  },
  onError: (err, newData, context) => {
    // Rollback on error
    queryClient.setQueryData(['items', id], context.previous);
    toast.error('Failed to save, changes reverted');
  },
  onSettled: () => {
    queryClient.invalidateQueries(['items', id]);
  },
});
```

## Best Practices

1. **Always show feedback** - Use toast for mutations, inline errors for forms
2. **Provide recovery options** - Retry buttons, back navigation
3. **Be specific** - "Failed to save project" not "Something went wrong"
4. **Log for debugging** - Console in dev, error service in prod
5. **Handle offline** - Show appropriate UI when network is unavailable
6. **Validate early** - Client-side validation before API calls
