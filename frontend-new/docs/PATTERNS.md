# PATTERNS.md — How We Do Things Here

> [!NOTE]
> This document captures recurring patterns used across the codebase. Each pattern includes when to use it, implementation example, and gotchas.

---

## 1. Empty State Pattern

**When:** No data available (first load, search with no results, deleted items)

```tsx
import { EmptyState } from '@lumina/design-system';

if (data.length === 0) {
  return (
    <EmptyState
      icon={<FolderOutlined />}
      title="No event logs yet"
      description="Upload your first event log to start analyzing."
      actionLabel="Upload File"
      onAction={() => navigate('/logs/upload')}
    />
  );
}
```

**Gotchas:**

- Always provide a clear action to resolve the empty state
- Distinguish between "no data exists" vs "no results for filter"

---

## 2. Loading State Pattern

**When:** Data is being fetched

```tsx
const { data, isLoading } = useQuery({...});

if (isLoading) {
  return <Skeleton active paragraph={{ rows: 6 }} />;
}
```

**Variants:**

- Full page: `<Spin size="large" />` centered
- Card content: `<Skeleton active />`
- MetricCard: `<MetricCard loading={true} />`

---

## 3. Error Handling Pattern

**When:** Query or mutation fails

```tsx
const { data, error, refetch } = useQuery({...});

if (error) {
  return (
    <EmptyState
      icon={<WarningOutlined />}
      title="Failed to load"
      description={error.message}
      actionLabel="Retry"
      onAction={refetch}
    />
  );
}
```

**Levels:**
| Level | Mechanism | Use Case |
|-------|-----------|----------|
| Page | EmptyState | Query fails |
| Action | Toast | Mutation fails |
| Global | Error boundary | Crash recovery |

---

## 4. Optimistic Update Pattern

**When:** User actions should feel instant (delete, rename)

```tsx
const mutation = useMutation({
  mutationFn: (id) => sdk.logs.delete(id),
  onMutate: async (id) => {
    await queryClient.cancelQueries(['logs']);
    const previous = queryClient.getQueryData(['logs']);
    queryClient.setQueryData(['logs'], (old) =>
      old.filter((log) => log.id !== id),
    );
    return { previous };
  },
  onError: (err, id, context) => {
    queryClient.setQueryData(['logs'], context.previous);
    toast.error('Delete failed');
  },
  onSettled: () => {
    queryClient.invalidateQueries(['logs']);
  },
});
```

**Gotchas:**

- Always cancel in-flight queries before optimistic update
- Keep `previous` data for rollback
- Invalidate on settled (not just success)

---

## 5. URL State Pattern

**When:** State should persist across refresh/share

```tsx
import { useSearchParams } from 'react-router-dom';

function FilterableList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const variant = searchParams.get('variant');

  const handleVariantChange = (v: string) => {
    setSearchParams({ ...Object.fromEntries(searchParams), variant: v });
  };

  return <VariantSelector value={variant} onChange={handleVariantChange} />;
}
```

**Use For:**

- Filter selections
- Sort order
- Selected items (if shareable)
- Tab selection

---

## 6. Tab Navigation Pattern

**When:** Page has multiple views/tabs

```tsx
function SettingsPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const activeTab = location.pathname.split('/').pop() || 'profile';

  const handleTabChange = (key: string) => {
    navigate(`/settings/${key}`);
  };

  return (
    <Tabs activeKey={activeTab} onChange={handleTabChange} items={tabItems} />
  );
}
```

**Route Setup:**

```tsx
<Route path="/settings/*" element={<SettingsPage />} />
```

---

## 7. Logger Pattern

**When:** Need debugging info in dev

```tsx
import { createLogger } from '../utils/logger';

const log = createLogger('ComponentName');

function MyComponent() {
  log.debug('Rendering', { props });
  log.info('User action', { action: 'click' });
  log.warn('Potential issue', { value });
  log.error('Failed operation', { error });
}
```

**Gotchas:**

- Use component name as logger scope
- `debug` for verbose dev info
- `info` for user actions
- `error` for failures

---

## 8. Mock Data Pattern

**When:** Backend not ready, need realistic UI

```tsx
// Define at top of file, outside component
const mockLogs = [
  { id: '1', name: 'Orders_2024.csv', cases: 1250 },
  { id: '2', name: 'Claims.xes', cases: 890 },
];

function EventLogsPage() {
  // TODO: Replace with useQuery when backend ready
  const data = mockLogs;

  return <Table dataSource={data} />;
}
```

**Gotchas:**

- Mark with `// TODO: Replace with useQuery`
- Keep mock data structure identical to expected API response
- Place mocks in dedicated `mock*.ts` files for larger datasets

---

## 9. Protected Route Pattern

**When:** Route requires authentication

```tsx
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <Spin />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return <>{children}</>;
}

// Usage in App.tsx
<Route
  path="/*"
  element={
    <ProtectedRoute>
      <AppLayout />
    </ProtectedRoute>
  }
/>;
```

---

## 10. Page Header Pattern

**When:** Standard page layout

```tsx
<PageHeader
  title="Event Logs"
  description="Manage your uploaded event log files"
  breadcrumb={[{ label: 'Home', href: '/' }, { label: 'Logs' }]}
  actions={<Button type="primary">Upload</Button>}
/>
```

Always include:

- Clear title
- Brief description
- Primary action (if applicable)
