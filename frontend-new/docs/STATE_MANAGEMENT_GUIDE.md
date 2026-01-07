# State Management Guide

> **Version:** 1.0
> **Last Updated:** 2026-01-07
> **Purpose:** Complete guide to state management patterns and best practices

---

## Table of Contents

1. [Overview](#overview)
2. [The Three Layers](#the-three-layers)
3. [Server State (TanStack Query)](#server-state-tanstack-query)
4. [Client State (React Context)](#client-state-react-context)
5. [URL State (React Router)](#url-state-react-router)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)
8. [Migration Guide](#migration-guide)

---

## Overview

Our application uses **3 distinct layers** of state management, each optimized for its specific use case:

| Layer | Technology | Purpose | Examples |
|-------|-----------|---------|----------|
| **Server State** | TanStack Query | Backend data, caching, synchronization | Datasets, projects, analytics |
| **Client State** | React Context | UI-only state, user preferences | Sidebar open, theme, DevConsole |
| **URL State** | React Router | Shareable filters, pagination | Search params, active tab |

**Key Principle:** Use the right tool for the job. Don't over-centralize state.

---

## The Three Layers

### When to Use Which Layer?

```
Is the data from the API?
  └─ YES → Server State (TanStack Query)

Is it UI-only state shared across components?
  └─ YES → Client State (React Context)

Should it be shareable via URL?
  └─ YES → URL State (React Router)

Is it local to one component?
  └─ YES → useState in component
```

### Decision Tree

```
Data Source Question
│
├─ From Backend API?
│  └─ Server State (TanStack Query)
│     Examples: Datasets, Projects, Analytics, Models
│
├─ UI Preference (persists across sessions)?
│  └─ localStorage + Context
│     Examples: Theme, sidebar collapsed, dev console settings
│
├─ Should be shareable via URL?
│  └─ URL State (useSearchParams)
│     Examples: Filters, pagination, active tab, sort order
│
└─ Local to one component?
   └─ Component State (useState)
      Examples: Modal open, form draft, hover state
```

---

## Server State (TanStack Query)

### Overview

TanStack Query (formerly React Query) manages **all server data** with automatic:
- **Caching** - Reduces API calls
- **Revalidation** - Keeps data fresh
- **Background refetching** - Updates stale data
- **Optimistic updates** - Instant UI feedback
- **Retry logic** - Handles transient failures

### Query Keys

Queries are identified by **hierarchical keys**:

```typescript
// Pattern: [domain, ...identifiers, ...filters]

// List queries
['datasets']                          // All datasets
['datasets', { status: 'ready' }]    // Filtered datasets
['projects', workspaceId]             // Workspace projects

// Detail queries
['dataset', datasetId]                // Single dataset
['project', projectId]                // Single project
['model', modelId]                    // Single model

// Nested queries
['dataset', datasetId, 'statistics']  // Dataset stats
['project', projectId, 'datasets']    // Project datasets
```

**Naming Convention:**
- Singular for detail: `['dataset', id]`
- Plural for lists: `['datasets']`
- Filters as object: `['datasets', { status: 'ready' }]`

### Basic Query Pattern

```typescript
import { useQuery } from '@tanstack/react-query';
import { devLog } from '@/shared/ui';

export function useDatasets(options: { status?: string; page?: number } = {}) {
  return useQuery({
    // Unique key for this query
    queryKey: ['datasets', options],

    // Fetch function
    queryFn: async () => {
      devLog.apiRequest('GET', '/api/v1/datasets', options);
      const start = Date.now();

      const params = new URLSearchParams();
      if (options.status) params.set('status', options.status);
      if (options.page) params.set('page', String(options.page));

      const response = await fetch(`/api/v1/datasets?${params}`);
      const duration = Date.now() - start;

      if (!response.ok) {
        const error = await response.json();
        devLog.apiResponse('GET', '/api/v1/datasets', response.status, duration, error);
        throw new Error(error.message || 'Failed to fetch datasets');
      }

      const data = await response.json();
      devLog.apiResponse('GET', '/api/v1/datasets', 200, duration, { count: data.length });
      return data;
    },

    // Cache for 5 minutes
    staleTime: 5 * 60 * 1000,

    // Retry failed requests 3 times
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

    // Only run if we have required params
    enabled: true,
  });
}

// Usage in component
function DatasetList() {
  const { data, isLoading, error, refetch } = useDatasets({ status: 'ready' });

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState error={error} onRetry={refetch} />;

  return <List data={data} />;
}
```

### Mutation Pattern

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import { devLog } from '@/shared/ui';

export function useCreateDataset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (dataset: { name: string; file: File }) => {
      devLog.action('Datasets', 'Creating dataset', { name: dataset.name });
      devLog.apiRequest('POST', '/api/v1/datasets', { name: dataset.name });

      const formData = new FormData();
      formData.append('name', dataset.name);
      formData.append('file', dataset.file);

      const start = Date.now();
      const response = await fetch('/api/v1/datasets', {
        method: 'POST',
        body: formData,
      });

      const duration = Date.now() - start;
      const data = await response.json();

      if (!response.ok) {
        devLog.apiResponse('POST', '/api/v1/datasets', response.status, duration, data);
        throw new Error(data.message || 'Failed to create dataset');
      }

      devLog.apiResponse('POST', '/api/v1/datasets', 201, duration, data);
      devLog.state('Datasets', 'Dataset created', { datasetId: data.id });
      return data;
    },

    // Optimistic update
    onMutate: async (newDataset) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['datasets'] });

      // Snapshot previous value
      const previousDatasets = queryClient.getQueryData(['datasets']);

      // Optimistically update
      queryClient.setQueryData(['datasets'], (old: any) => [
        ...(old || []),
        { id: 'temp-id', name: newDataset.name, status: 'pending' }
      ]);

      return { previousDatasets };
    },

    // On error, rollback
    onError: (error, newDataset, context) => {
      queryClient.setQueryData(['datasets'], context?.previousDatasets);

      devLog.error('Datasets', 'Failed to create dataset', {
        error: error.message,
        datasetName: newDataset.name,
      });

      message.error(`Failed to create dataset: ${error.message}`);
    },

    // On success, refetch and show success
    onSuccess: (data) => {
      message.success('Dataset created successfully!');

      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
      queryClient.invalidateQueries({ queryKey: ['projects', data.project_id] });
    },
  });
}
```

### Invalidation Strategies

When data changes, **invalidate related queries**:

```typescript
// After creating a dataset
queryClient.invalidateQueries({ queryKey: ['datasets'] });
queryClient.invalidateQueries({ queryKey: ['projects', projectId] });

// After deleting a dataset
queryClient.invalidateQueries({ queryKey: ['datasets'] });
queryClient.removeQueries({ queryKey: ['dataset', datasetId] });

// After updating a dataset
queryClient.invalidateQueries({ queryKey: ['dataset', datasetId] });
queryClient.invalidateQueries({ queryKey: ['datasets'] });
```

### Dependent Queries

Load data that depends on other data:

```typescript
function DatasetDetails({ datasetId }: { datasetId: string }) {
  // First query: Get dataset
  const { data: dataset } = useQuery({
    queryKey: ['dataset', datasetId],
    queryFn: () => fetchDataset(datasetId),
  });

  // Second query: Get dataset statistics (depends on dataset)
  const { data: stats } = useQuery({
    queryKey: ['dataset', datasetId, 'statistics'],
    queryFn: () => fetchDatasetStatistics(datasetId),
    enabled: !!dataset && dataset.status === 'ready', // Only run if dataset is ready
  });

  return (
    <div>
      <h1>{dataset?.name}</h1>
      {stats && <StatsPanel stats={stats} />}
    </div>
  );
}
```

---

## Client State (React Context)

### Overview

Use React Context for **UI-only state** that:
- Doesn't come from the backend
- Is shared across multiple components
- Doesn't belong in the URL

**Examples:**
- Sidebar open/collapsed
- Theme (light/dark)
- DevConsole visibility
- User preferences (language, timezone)

### Context Pattern

```typescript
// src/shared/context/SidebarContext.tsx

import { createContext, useContext, useState, ReactNode } from 'react';

interface SidebarContextValue {
  isCollapsed: boolean;
  toggle: () => void;
  collapse: () => void;
  expand: () => void;
}

const SidebarContext = createContext<SidebarContextValue | undefined>(undefined);

export function SidebarProvider({ children }: { children: ReactNode }) {
  const [isCollapsed, setIsCollapsed] = useState(() => {
    // Load from localStorage
    const saved = localStorage.getItem('sidebar-collapsed');
    return saved ? JSON.parse(saved) : false;
  });

  const toggle = () => {
    setIsCollapsed(prev => {
      const next = !prev;
      localStorage.setItem('sidebar-collapsed', JSON.stringify(next));
      devLog.action('Sidebar', next ? 'Collapsed' : 'Expanded', { collapsed: next });
      return next;
    });
  };

  const collapse = () => {
    setIsCollapsed(true);
    localStorage.setItem('sidebar-collapsed', 'true');
    devLog.action('Sidebar', 'Collapsed programmatically', {});
  };

  const expand = () => {
    setIsCollapsed(false);
    localStorage.setItem('sidebar-collapsed', 'false');
    devLog.action('Sidebar', 'Expanded programmatically', {});
  };

  return (
    <SidebarContext.Provider value={{ isCollapsed, toggle, collapse, expand }}>
      {children}
    </SidebarContext.Provider>
  );
}

export function useSidebar() {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error('useSidebar must be used within SidebarProvider');
  }
  return context;
}
```

### Usage

```typescript
// In App.tsx
function App() {
  return (
    <SidebarProvider>
      <AppShell>
        <Routes />
      </AppShell>
    </SidebarProvider>
  );
}

// In Sidebar component
function Sidebar() {
  const { isCollapsed, toggle } = useSidebar();

  return (
    <aside className={isCollapsed ? 'collapsed' : 'expanded'}>
      <button onClick={toggle}>Toggle</button>
      {/* sidebar content */}
    </aside>
  );
}

// In any other component
function SomeFeature() {
  const { collapse } = useSidebar();

  const handleFullscreen = () => {
    collapse(); // Collapse sidebar for more space
  };

  return <button onClick={handleFullscreen}>Fullscreen</button>;
}
```

### When NOT to Use Context

❌ **Don't use Context for:**
- Server data (use TanStack Query)
- URL-shareable state (use URL params)
- Local component state (use useState)
- Frequently changing values (causes re-renders)

✅ **Do use Context for:**
- Theme
- Auth user (cached from server)
- UI preferences
- Feature flags
- Global UI state (modals, toasts managed by library)

---

## URL State (React Router)

### Overview

Store state in URL for:
- **Shareability** - Users can bookmark/share the exact view
- **Navigation** - Back/forward works correctly
- **Persistence** - Survives page refresh

**Examples:**
- Search queries
- Filters
- Pagination (page, page size)
- Active tab
- Sort order

### useSearchParams Pattern

```typescript
import { useSearchParams } from 'react-router-dom';
import { devLog } from '@/shared/ui';

function useExplorerFilters() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Parse filters from URL
  const filters = {
    minFrequency: Number(searchParams.get('minFreq')) || 0,
    maxDuration: searchParams.get('maxDur')
      ? Number(searchParams.get('maxDur'))
      : undefined,
    activities: searchParams.getAll('activity'),
    dateRange: searchParams.get('from') && searchParams.get('to')
      ? [searchParams.get('from')!, searchParams.get('to')!]
      : undefined,
  };

  // Update filters (merges with existing params)
  const setFilters = (newFilters: Partial<typeof filters>) => {
    devLog.action('ExplorerFilters', 'Filters updated', newFilters);

    setSearchParams(params => {
      // Merge new filters
      if (newFilters.minFrequency !== undefined) {
        params.set('minFreq', String(newFilters.minFrequency));
      }
      if (newFilters.maxDuration !== undefined) {
        params.set('maxDur', String(newFilters.maxDuration));
      }
      if (newFilters.activities) {
        params.delete('activity'); // Clear existing
        newFilters.activities.forEach(a => params.append('activity', a));
      }
      if (newFilters.dateRange) {
        params.set('from', newFilters.dateRange[0]);
        params.set('to', newFilters.dateRange[1]);
      }
      return params;
    });
  };

  // Clear all filters
  const clearFilters = () => {
    devLog.action('ExplorerFilters', 'Filters cleared', {});
    setSearchParams({});
  };

  return { filters, setFilters, clearFilters };
}

// Usage
function ExplorerPage() {
  const { filters, setFilters, clearFilters } = useExplorerFilters();

  return (
    <div>
      <FilterPanel
        filters={filters}
        onChange={setFilters}
        onClear={clearFilters}
      />
      <ProcessGraph filters={filters} />
    </div>
  );
}
```

### URL Format Examples

```
# No filters
/explorer/ds-123

# With filters
/explorer/ds-123?minFreq=5&activity=Submit&activity=Approve&from=2024-01-01&to=2024-12-31

# Pagination
/datasets?page=2&pageSize=20

# Active tab
/analytics?tab=performance

# Sort
/projects?sortBy=name&sortOrder=asc
```

### Benefits

1. **Shareable Links** - Users can share exact view
2. **Bookmarkable** - Save specific filtered view
3. **Back/Forward** - Browser navigation works
4. **Refresh-Safe** - State survives page reload
5. **Deep Linking** - Navigate directly to filtered view

---

## Best Practices

### 1. Choose the Right State Layer

```typescript
// ✅ GOOD: Server state for API data
const { data: datasets } = useQuery({
  queryKey: ['datasets'],
  queryFn: fetchDatasets,
});

// ❌ BAD: useState for API data
const [datasets, setDatasets] = useState([]);
useEffect(() => {
  fetchDatasets().then(setDatasets);
}, []);

// ✅ GOOD: URL state for filters
const [searchParams] = useSearchParams();
const search = searchParams.get('search') || '';

// ❌ BAD: useState for shareable filters
const [search, setSearch] = useState('');

// ✅ GOOD: Context for UI preferences
const { theme } = useTheme();

// ❌ BAD: Prop drilling for theme
<DeepComponent theme={theme} />
```

### 2. Keep Queries Simple

```typescript
// ✅ GOOD: Simple, focused query
function useDataset(id: string) {
  return useQuery({
    queryKey: ['dataset', id],
    queryFn: () => fetchDataset(id),
  });
}

// ❌ BAD: Complex query with side effects
function useDataset(id: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // ...too much logic
}
```

### 3. Invalidate Efficiently

```typescript
// ✅ GOOD: Invalidate specific queries
queryClient.invalidateQueries({ queryKey: ['datasets'] });
queryClient.invalidateQueries({ queryKey: ['dataset', datasetId] });

// ❌ BAD: Invalidate everything
queryClient.invalidateQueries();

// ✅ GOOD: Remove deleted items
queryClient.removeQueries({ queryKey: ['dataset', deletedId] });

// ❌ BAD: Leave deleted items in cache
// (stale data might reappear)
```

### 4. Use Optimistic Updates Wisely

```typescript
// ✅ GOOD: Optimistic update for instant feedback
onMutate: async (newItem) => {
  await queryClient.cancelQueries({ queryKey: ['items'] });
  const previous = queryClient.getQueryData(['items']);
  queryClient.setQueryData(['items'], (old) => [...old, newItem]);
  return { previous };
},
onError: (err, newItem, context) => {
  queryClient.setQueryData(['items'], context.previous);
},

// ❌ BAD: Optimistic update without rollback
onMutate: async (newItem) => {
  queryClient.setQueryData(['items'], (old) => [...old, newItem]);
  // No error handling!
},
```

### 5. Avoid Over-Abstraction

```typescript
// ✅ GOOD: Direct, clear hook
function useDatasets() {
  return useQuery({
    queryKey: ['datasets'],
    queryFn: fetchDatasets,
  });
}

// ❌ BAD: Over-engineered abstraction
function useGenericResource<T>(
  resource: string,
  transformer: (data: any) => T,
  options: UseQueryOptions<T>
) {
  // Too generic, hard to understand
}
```

---

## Common Patterns

### Pattern 1: List + Detail

```typescript
// List query
function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: fetchProjects,
  });
}

// Detail query
function useProject(id: string) {
  return useQuery({
    queryKey: ['project', id],
    queryFn: () => fetchProject(id),
    enabled: !!id,
  });
}

// Usage
function ProjectsPage() {
  const { data: projects } = useProjects();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const { data: project } = useProject(selectedId!);

  return (
    <div>
      <ProjectList projects={projects} onSelect={setSelectedId} />
      {project && <ProjectDetails project={project} />}
    </div>
  );
}
```

### Pattern 2: Filters + Data

```typescript
function useFilteredDatasets() {
  const [searchParams] = useSearchParams();
  const status = searchParams.get('status') || 'all';

  return useQuery({
    queryKey: ['datasets', { status }],
    queryFn: () => fetchDatasets({ status }),
  });
}

function DatasetsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { data, isLoading } = useFilteredDatasets();

  const handleFilterChange = (newStatus: string) => {
    setSearchParams({ status: newStatus });
  };

  return (
    <div>
      <FilterBar status={searchParams.get('status')} onChange={handleFilterChange} />
      <DatasetList data={data} loading={isLoading} />
    </div>
  );
}
```

### Pattern 3: Pagination

```typescript
function usePaginatedDatasets() {
  const [searchParams] = useSearchParams();
  const page = Number(searchParams.get('page')) || 1;
  const pageSize = Number(searchParams.get('pageSize')) || 20;

  return useQuery({
    queryKey: ['datasets', { page, pageSize }],
    queryFn: () => fetchDatasets({ page, pageSize }),
    keepPreviousData: true, // Show old data while loading new page
  });
}

function DatasetsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { data, isPreviousData } = usePaginatedDatasets();

  const goToPage = (newPage: number) => {
    setSearchParams(params => {
      params.set('page', String(newPage));
      return params;
    });
  };

  return (
    <div>
      <DatasetList data={data?.items} loading={isPreviousData} />
      <Pagination
        current={Number(searchParams.get('page')) || 1}
        total={data?.total}
        onChange={goToPage}
      />
    </div>
  );
}
```

---

## Migration Guide

### From useState to TanStack Query

**Before:**
```typescript
function DatasetList() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetchDatasets()
      .then(setDatasets)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;
  if (error) return <Error error={error} />;
  return <List data={datasets} />;
}
```

**After:**
```typescript
function DatasetList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['datasets'],
    queryFn: fetchDatasets,
  });

  if (isLoading) return <Loading />;
  if (error) return <Error error={error} />;
  return <List data={data} />;
}
```

### From Prop Drilling to Context

**Before:**
```typescript
function App() {
  const [theme, setTheme] = useState('light');
  return <Layout theme={theme} setTheme={setTheme}>
    <Page theme={theme} />
  </Layout>;
}

function Layout({ theme, setTheme, children }) {
  return <Header theme={theme} setTheme={setTheme}>
    {children}
  </Header>;
}

function Header({ theme, setTheme }) {
  return <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
    Toggle Theme
  </button>;
}
```

**After:**
```typescript
function App() {
  return (
    <ThemeProvider>
      <Layout>
        <Page />
      </Layout>
    </ThemeProvider>
  );
}

function Header() {
  const { theme, toggle } = useTheme();
  return <button onClick={toggle}>Toggle Theme</button>;
}
```

---

## Summary

| Layer | Technology | Purpose | Key Features |
|-------|-----------|---------|--------------|
| **Server State** | TanStack Query | Backend data | Caching, revalidation, optimistic updates |
| **Client State** | React Context | UI preferences | Global UI state, persists in localStorage |
| **URL State** | React Router | Shareable state | Filters, pagination, bookmarkable |
| **Component State** | useState | Local state | Form inputs, modal visibility, hover |

**Golden Rules:**
1. **Server data → TanStack Query** (always)
2. **UI preferences → Context** (when shared)
3. **Shareable state → URL** (filters, pagination)
4. **Local state → useState** (when possible)

**Next Steps:**
- Review existing code for state management anti-patterns
- Migrate useState API calls to TanStack Query
- Move filters to URL params for shareability
- Extract UI preferences to Context providers

