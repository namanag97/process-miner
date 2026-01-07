# Frontend Architecture

> **Architecture Overview**: Feature-based React Application with Plugin System

**Last Updated**: 2026-01-07  
**Pattern**: Feature-Sliced Design + Plugin Architecture  
**Framework**: React 19 + TypeScript + Nx

---

## 🎯 Architecture Overview

### High-Level Structure

```
┌─────────────────────────────────────────────────────┐
│                   App Shell                         │
│  (AppShell, BrowserRouter, Global Providers)        │
└─────────────────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
   │Feature 1│   │Feature 2│   │Feature N│
   │(Plugin) │   │(Plugin) │   │(Plugin) │
   └─────────┘   └─────────┘   └─────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
            ┌──────────▼─────────┐
            │   Shared Layer     │
            │ (Design System,    │
            │  Context, Hooks)   │
            └────────────────────┘
                       │
            ┌──────────▼─────────┐
            │    API Layer       │
            │ (Auto-gen SDK +    │
            │  TanStack Query)   │
            └────────────────────┘
                       │
                   Backend
```

---

## 📁 Layer Architecture

### 1. Application Layer

**Location**: `src/App.tsx`, `src/main.tsx`

**Responsibilities**:
- Bootstrap React application
- Configure routing (React Router)
- Set up global providers (Query Client, Contexts, Theme)
- Initialize error boundaries
- Register dev tools (DevConsole)

**Key Files**:
- [`src/main.tsx`](file:///Users/namanagarwal/system/frontend-new/src/main.tsx) - React root
- [`src/App.tsx`](file:///Users/namanagarwal/system/frontend-new/src/App.tsx) - App shell with providers
- [`src/index.html`](file:///Users/namanagarwal/system/frontend-new/src/index.html) - HTML entry point

### 2. Feature Layer

**Location**: `src/features/*`

**Responsibilities**:
- Self-contained feature modules
- Auto-register routes via FeatureRegistry
- Feature-specific components, hooks, and logic
- Isolated from other features (communicate via shared layer)

**Structure**:
```
src/features/
├── index.ts                    # Registers all features
├── platform/                   # Platform features
│   ├── workspace/
│   │   ├── index.ts            # Feature registration
│   │   ├── WorkspacePage.tsx   # Main page component
│   │   ├── components/         # Feature-specific components
│   │   └── hooks/              # Feature-specific hooks
│   └── settings/
├── explorer/                   # Process explorer
├── analytics/                  # Analytics dashboard
├── ai/                         # AI insights
├── discovery/                  # Process discovery
└── kpi/                        # KPI dashboard
```

**Registration Pattern**:
```typescript
// src/features/analytics/index.ts
import { registerFeature } from '@/shared/core/plugins/FeatureRegistry';

registerFeature({
  id: 'analytics',
  name: 'Analytics',
  routes: [{ path: '/analytics', element: <AnalyticsPage /> }],
  navConfig: { icon: 'BarChartOutlined', label: 'Analytics', order: 3 },
});
```

### 3. Shared Layer

**Location**: `src/shared/*`

**Responsibilities**:
- Reusable components and utilities
- Design system (theme, components)
- Shared contexts (User, Notifications, Health)
- Common hooks (useAuth, useDataset, etc.)
- Core infrastructure (FeatureRegistry, routing)

**Structure**:
```
src/shared/
├── design-system.ts           # Central export for UI components
├── components.tsx             # Shared components
├── context/                   # React contexts
│   ├── UserContext.tsx
│   ├── NotificationContext.tsx
│   └── BackendHealthContext.tsx
├── core/                      # Core infrastructure
│   ├── plugins/               # FeatureRegistry
│   └── router/                # Routing utilities
├── hooks/                     # Custom hooks
├── lib/                       # Utilities (logger, formatters)
└── ui/                        # Shared UI components
    ├── DevConsole.tsx
    ├── GlobalErrorBoundary.tsx
    └── PageLoader.tsx
```

### 4. API Layer

**Location**: `src/api/*`

**Responsibilities**:
- Auto-generated TypeScript SDK from OpenAPI spec
- TanStack Query hooks for data fetching
- API client configuration
- Request/response type definitions

**Structure**:
```
src/api/
├── client/                    # Auto-generated from OpenAPI
│   ├── index.ts
│   ├── models.ts              # TypeScript types
│   └── api.ts                 # API functions
└── hooks/                     # TanStack Query hooks
    ├── useDatasets.ts
    ├── useAnalytics.ts
    └── usePredictions.ts
```

**Generation**:
```bash
npm run generate:api          # Runs orval to generate client
```

**Configuration**: [`orval.config.ts`](file:///Users/namanagarwal/system/frontend-new/orval.config.ts)

---

## 🔄 Data Flow

### Request Flow

```
User Interaction (Button Click)
  ↓
Component Event Handler
  ↓
TanStack Query Hook (mutation)
  ↓
Auto-generated API Function
  ↓
HTTP Request (Axios)
  ↓
Backend API
```

### Response Flow

```
Backend API Response
  ↓
TanStack Query Cache Update
  ↓
React Component Re-render
  ↓
UI Updates Automatically
```

### Example Flow

```typescript
// 1. Component calls hook
function AnalyticsPage() {
  const { data, isLoading } = useBottlenecks(datasetId);
  // ...
}

// 2. Hook uses auto-generated client
// src/api/hooks/useAnalytics.ts
export function useBottlenecks(datasetId: number) {
  return useQuery({
    queryKey: ['bottlenecks', datasetId],
    queryFn: () => analyticsApi.getBottlenecks(datasetId), // Auto-generated
  });
}

// 3. Auto-generated client makes HTTP request
// src/api/client/api.ts
export const analyticsApi = {
  getBottlenecks: (datasetId: number) => 
    axios.get(`/api/v1/analytics/logs/${datasetId}/bottlenecks`),
};
```

---

## 🧩 Plugin Architecture

### FeatureRegistry Pattern

**Purpose**: Decouple features from the core app, enable dynamic registration

**Benefits**:
- Add/remove features without modifying `App.tsx`
- Each feature is self-contained
- Routes auto-register
- Navigation auto-updates

**Implementation**:

```typescript
// src/shared/core/plugins/FeatureRegistry.ts
interface FeatureConfig {
  id: string;
  name: string;
  routes: RouteObject[];
  navConfig?: {
    icon: string;
    label: string;
    order: number;
  };
}

const features: FeatureConfig[] = [];

export function registerFeature(config: FeatureConfig) {
  features.push(config);
}

export function useFeatureRoutes() {
  return useMemo(() => 
    features.flatMap(f => f.routes), 
    []
  );
}
```

### Feature Lifecycle

1. **Import**: `src/features/index.ts` imports feature
2. **Register**: Feature's `index.ts` calls `registerFeature()`
3. **Discovery**: `App.tsx` calls `useFeatureRoutes()` hook
4. **Rendering**: Routes rendered dynamically in `<Routes>`

---

## 🎨 Design System

### Theme Configuration

```typescript
// src/shared/design-system.ts
import { theme } from 'antd';

export const luminaTheme = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 8,
    // ... other tokens
  },
  algorithm: theme.darkAlgorithm, // or theme.defaultAlgorithm
};
```

### Component Architecture

**Pattern**: Import from single design-system.ts file

```typescript
// ✅ Recommended
import { Button, Card, Table } from '@/shared/design-system';

// ❌ Avoid
import { Button } from 'antd';
import Card from 'antd/es/card';
```

**Benefits**:
- Single source of truth
- Easier to swap component library
- Consistent theming
- Tree-shaking optimized

---

## 🔐 State Management

### Server State (TanStack Query)

**Purpose**: Manage server data (fetching, caching, synchronization)

**Features**:
- Automatic caching
- Background refetching
- Optimistic updates
- Request deduplication

**Example**:
```typescript
// Fetch data
const { data, isLoading, error } = useQuery({
  queryKey: ['datasets'],
  queryFn: () => datasetsApi.getAll(),
  staleTime: 5 * 60 * 1000, // 5min cache
});

// Mutate data
const mutation = useMutation({
  mutationFn: (id) => datasetsApi.delete(id),
  onSuccess: () => {
    queryClient.invalidateQueries(['datasets']); // Refetch
  },
});
```

### Global State (React Context)

**Purpose**: Share app-wide state (user, notifications, health)

**Contexts**:
- **UserContext**: Current user info
- **NotificationContext**: Global notifications
- **BackendHealthContext**: Backend connectivity status

**Example**:
```typescript
// src/shared/context/UserContext.tsx
export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}

// Usage
const { user } = useUser();
```

### Local State (React Hooks)

**Purpose**: Component-specific state

**Patterns**:
```typescript
// Simple state
const [count, setCount] = useState(0);

// Complex state
const [state, dispatch] = useReducer(reducer, initialState);

// Derived state
const filteredData = useMemo(() => 
  data.filter(item => item.active),
  [data]
);
```

---

## 🛣️ Routing Architecture

### Route Registration

**Dynamic Routes** (via FeatureRegistry):
```typescript
registerFeature({
  routes: [
    {
      path: '/analytics',
      element: <AnalyticsLayout />,
      children: [
        { path: 'bottlenecks', element: <BottlenecksPage /> },
        { path: 'performance', element: <PerformancePage /> },
      ],
    },
  ],
});
```

**Static Routes** (in `App.tsx`):
```typescript
<Routes>
  {/* Dynamic feature routes */}
  {featureRoutes.map((route, i) => renderRouteObject(route, i))}
  
  {/* Static redirects */}
  <Route path="/" element={<Navigate to="/workspace" />} />
  <Route path="/home" element={<Navigate to="/workspace" />} />
</Routes>
```

### Navigation

```typescript
// Programmatic navigation
import { useNavigate } from 'react-router-dom';
const navigate = useNavigate();
navigate('/analytics/bottlenecks');

// Link navigation
import { Link } from 'react-router-dom';
<Link to="/analytics">Analytics</Link>
```

---

## 📦 Build Architecture

### Bundler: Rspack

**Why Rspack?** 10x faster than Webpack, Webpack-compatible

**Configuration**: [`rspack.config.js`](file:///Users/namanagarwal/system/frontend-new/rspack.config.js)

**Features**:
- Code splitting
- Tree shaking
- Hot module replacement (HMR)
- CSS extraction

### Monorepo: Nx

**Why Nx?** Fast builds, caching, code generation

**Configuration**: [`nx.json`](file:///Users/namanagarwal/system/frontend-new/nx.json)

**Features**:
- Affected builds (only rebuild changed code)
- Computation caching
- Task orchestration

---

## 🔒 Security Architecture

### XSS Protection

- React auto-escapes values
- Use `dangerouslySetInnerHTML` sparingly
- Sanitize user input

### CSRF Protection

- SameSite cookies
- Backend CSRF tokens (when auth enabled)

### API Security

- HTTPS in production
- CORS configured on backend
- JWT tokens (when auth enabled)

---

## 🚀 Deployment Architecture

### Development

```bash
npm run start               # Dev server on :4200
# - Hot reloading
# - Source maps
# - DevConsole enabled
```

### Production Build

```bash
npm run build               # Output to dist/
# - Minification
# - Tree shaking
# - Code splitting
# - Asset optimization
```

### Environment Configuration

```typescript
// src/config/env.ts
export const env = {
  apiBaseUrl: process.env.VITE_API_BASE_URL || 'http://localhost:8001',
  isDev: process.env.NODE_ENV === 'development',
  // ...
};
```

---

## 📊 Performance Patterns

### Code Splitting

```typescript
// Lazy load features
const AnalyticsPage = lazy(() => import('./AnalyticsPage'));

// Use Suspense for loading state
<Suspense fallback={<PageLoader />}>
  <AnalyticsPage />
</Suspense>
```

### Memoization

```typescript
// Expensive computations
const expensiveValue = useMemo(() => 
  computeExpensiveValue(data),
  [data]
);

// Component memoization
const MemorizedComponent = memo(MyComponent);
```

### Query Optimization

```typescript
// Prefetch data
queryClient.prefetchQuery(['dataset', id], () => fetchDataset(id));

// Optimistic updates
mutate(newData, {
  onMutate: async (newData) => {
    await queryClient.cancelQueries(['datasets']);
    queryClient.setQueryData(['datasets'], old => [...old, newData]);
  },
});
```

---

## 🔗 Related Documentation

- **[AI Agent Guide](file:///Users/namanagarwal/system/frontend-new/AI_AGENT_GUIDE.md)** - Development workflows and patterns
- **[Backend Architecture](file:///Users/namanagarwal/system/backend/ARCHITECTURE.md)** - Backend architecture overview
- **[System Overview](file:///Users/namanagarwal/system/SYSTEM_OVERVIEW.md)** - Full-stack architecture

---

**Last Updated**: 2026-01-07
