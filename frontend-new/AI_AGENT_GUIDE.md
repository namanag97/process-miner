# AI Agent Guide: Frontend Codebase

> **Quick Start for AI Agents**: Your comprehensive guide to navigating, understanding, and contributing to the Process Mining SaaS frontend.

**Last Updated**: 2026-01-07  
**Tech Stack**: React 19 + TypeScript + Nx + Rspack + TanStack Query + Ant Design  
**Architecture**: Feature-based with Plugin Architecture

---

## 🎯 Quick Context

### What This System Does
A **modern React SPA** for Process Mining analytics - users upload event logs, visualize process flows (DFG/Petri nets), analyze performance, detect bottlenecks, and get AI-powered insights. Think "interactive dashboard for business process analysis."

### System Scale
- **6 Major Features**: Workspace, Explorer, Analytics, AI, Discovery, Platform
- **Plugin Architecture**: Auto-registering features via FeatureRegistry
- **~40K Lines of TypeScript**: Well-typed, component-based
- **Design System**: Custom Lumina theme with Ant Design components

---

## 📁 Navigation Map

### Critical Files (Start Here)

| File | Purpose | When to Read |
|------|---------|--------------|
| [`README.md`](file:///Users/namanagarwal/system/frontend-new/README.md) | Project overview, setup | First time setup |
| [`package.json`](file:///Users/namanagarwal/system/frontend-new/package.json) | Dependencies, scripts | Understanding dependencies |
| [`src/App.tsx`](file:///Users/namanagarwal/system/frontend-new/src/App.tsx) | App shell, routing, providers | Understanding app structure |
| [`src/features/index.ts`](file:///Users/namanagarwal/system/frontend-new/src/features/index.ts) | Feature registration | Adding new features |
| [`src/shared/design-system.ts`](file:///Users/namanagarwal/system/frontend-new/src/shared/design-system.ts) | Design system exports | UI components |

### Folder Structure

```
frontend-new/
├── src/
│   ├── App.tsx                    # 🏠 Main app component
│   ├── main.tsx                   # Entry point, React root
│   ├── index.html                 # HTML template
│   │
│   ├── features/                  # 🎯 Feature Modules (plugin-based)
│   │   ├── index.ts               # Auto-registers all features
│   │   ├── platform/              # Platform features (workspace, projects)
│   │   │   ├── workspace/         # Workspace management
│   │   │   ├── projects/          # Project CRUD
│   │   │   └── settings/          # User settings
│   │   ├── explorer/              # Process explorer (DFG, Petri nets)
│   │   ├── analytics/             # Performance analytics
│   │   ├── ai/                    # AI insights & predictions
│   │   ├── discovery/             # Process discovery
│   │   └── kpi/                   # KPI dashboard
│   │
│   ├── shared/                    # 🔄 Shared Code
│   │   ├── design-system.ts       # Design system (components, theme)
│   │   ├── components.tsx         # Shared UI components
│   │   ├── context/               # React contexts (User, Notifications, Health)
│   │   ├── core/                  # Core infrastructure
│   │   │   ├── plugins/           # FeatureRegistry for auto-registration
│   │   │   └── router/            # Routing utilities
│   │   ├── lib/                   # Utilities (logger, formatters)
│   │   ├── hooks/                 # Custom React hooks
│   │   └── ui/                    # Shared UI (DevConsole, ErrorBoundary)
│   │
│   ├── api/                       # 🌐 API Integration
│   │   ├── client/                # Auto-generated SDK from OpenAPI
│   │   └── hooks/                 # TanStack Query hooks
│   │
│   ├── config/                    # ⚙️ Configuration
│   │   └── env.ts                 # Environment variables
│   │
│   ├── testing/                   # 🧪 Test Utilities
│   │   └── test-utils.tsx         # Testing library setup
│   │
│   └── styles.css                 # Global CSS
│
├── public/                        # Static assets
├── dist/                          # Build output (gitignored)
├── rspack.config.js               # Rspack bundler config
├── tsconfig.json                  # TypeScript config
├── jest.config.cts                # Jest config
├── eslint.config.mjs              # ESLint config
└── orval.config.ts                # API client generator config
```

---

## 🏗️ Architecture Principles

### Feature Plugin Architecture

All features auto-register via `FeatureRegistry`:

```typescript
// src/features/analytics/index.ts
import { registerFeature } from '@/shared/core/plugins/FeatureRegistry';
import { AnalyticsPage } from './AnalyticsPage';

registerFeature({
  id: 'analytics',
  name: 'Analytics',
  routes: [
    {
      path: '/analytics',
      element: <AnalyticsPage />,
    },
  ],
  navConfig: {
    icon: 'BarChartOutlined',
    label: 'Analytics',
    order: 3,
  },
});
```

### Data Flow

```
User Action
  ↓
React Component
  ↓
TanStack Query Hook (src/api/hooks/)
  ↓
Auto-generated SDK (src/api/client/)
  ↓
Backend API (FastAPI)
  ↓
Response → React Query Cache → UI Updates
```

### State Management

- **Server State**: TanStack Query (caching, refetching, optimistic updates)
- **Global State**: React Context (UserContext, NotificationContext, BackendHealthContext)
- **Local State**: `useState`, `useReducer` in components
- **No Redux**: Deliberate choice for simplicity

---

## 🛠️ Common Development Tasks

### 1. Add a New Page/Feature

```bash
# Step 1: Create feature directory
mkdir -p src/features/my-feature

# Step 2: Create component
# src/features/my-feature/MyFeaturePage.tsx
import { PageHeader } from '@/shared/design-system';

export function MyFeaturePage() {
  return (
    <div>
      <PageHeader title="My Feature" />
      {/* Your content */}
    </div>
  );
}

# Step 3: Register feature
# src/features/my-feature/index.ts
import { registerFeature } from '@/shared/core/plugins/FeatureRegistry';
import { MyFeaturePage } from './MyFeaturePage';

registerFeature({
  id: 'my-feature',
  name: 'My Feature',
  routes: [
    {
      path: '/my-feature',
      element: <MyFeaturePage />,
    },
  ],
  navConfig: {
    icon: 'AppstoreOutlined',
    label: 'My Feature',
    order: 10,
  },
});

# Step 4: Export from features/index.ts
# src/features/index.ts
import './my-feature';
```

### 2. Create a Component with Design System

```tsx
// src/features/analytics/components/MetricCard.tsx
import { Card, Statistic } from '@/shared/design-system';

interface MetricCardProps {
  title: string;
  value: number;
  precision?: number;
  suffix?: string;
}

export function MetricCard({ title, value, precision = 0, suffix }: MetricCardProps) {
  return (
    <Card size="small">
      <Statistic
        title={title}
        value={value}
        precision={precision}
        suffix={suffix}
      />
    </Card>
  );
}
```

### 3. Add API Integration with TanStack Query

```typescript
// Step 1: Generate types from OpenAPI
npm run generate:api  // Runs orval to generate client

// Step 2: Create query hook
// src/api/hooks/useAnalytics.ts
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/api/client';

export function useBottlenecks(datasetId: number) {
  return useQuery({
    queryKey: ['bottlenecks', datasetId],
    queryFn: () => analyticsApi.getBottlenecks(datasetId),
    enabled: !!datasetId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Step 3: Use in component
// src/features/analytics/AnalyticsPage.tsx
import { useBottlenecks } from '@/api/hooks/useAnalytics';
import { LoadingState, ErrorAlert } from '@/shared/design-system';

export function AnalyticsPage({ datasetId }: { datasetId: number }) {
  const { data, isLoading, error } = useBottlenecks(datasetId);

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorAlert error={error} />;

  return (
    <div>
      {data?.map(bottleneck => (
        <MetricCard key={bottleneck.activity} {...bottleneck} />
      ))}
    </div>
  );
}
```

### 4. Add Routing with React Router

```typescript
// src/features/analytics/index.ts
import { lazy } from 'react';
import { registerFeature } from '@/shared/core/plugins/FeatureRegistry';

const AnalyticsPage = lazy(() => import('./AnalyticsPage'));
const BottlenecksPage = lazy(() => import('./BottlenecksPage'));

registerFeature({
  id: 'analytics',
  name: 'Analytics',
  routes: [
    {
      path: '/analytics',
      element: <AnalyticsPage />,
      children: [
        { path: 'bottlenecks', element: <BottlenecksPage /> },
        { path: 'performance', element: <PerformancePage /> },
      ],
    },
  ],
});
```

### 5. Style Components

```tsx
// Option 1: Inline styles (for dynamic values)
<div style={{ padding: 24, backgroundColor: token.colorBgContainer }}>

// Option 2: CSS Modules (for complex styles)
import styles from './MyComponent.module.css';
<div className={styles.container}>

// Option 3: Ant Design theme tokens
import { theme } from 'antd';
const { token } = theme.useToken();
<div style={{ color: token.colorPrimary }}>
```

---

## 🧪 Testing Strategy

### Test Structure

```
src/
├── features/
│   └── analytics/
│       ├── AnalyticsPage.tsx
│       └── AnalyticsPage.spec.tsx  # Co-located tests
├── shared/
│   └── components.tsx
│       └── components.spec.tsx
└── testing/
    └── test-utils.tsx              # Testing utilities
```

### Running Tests

```bash
npm test                    # Run all tests
npm run test:watch          # Watch mode
npm run test:coverage       # With coverage

# Nx commands
npx nx test                 # Run tests
npx nx test --watch         # Watch mode
```

### Writing Tests

```typescript
// src/features/analytics/AnalyticsPage.spec.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AnalyticsPage } from './AnalyticsPage';

describe('AnalyticsPage', () => {
  it('renders bottlenecks when data loads', async () => {
    const queryClient = new QueryClient();
    
    render(
      <QueryClientProvider client={queryClient}>
        <AnalyticsPage datasetId={1} />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Bottlenecks')).toBeInTheDocument();
    });
  });
});
```

---

## 🎨 Design System

### Available Components

Import from `@/shared/design-system`:

```typescript
import {
  // Layout
  AppShell, PageHeader, PageLayout, Card, Space, Divider,
  
  // Data Display
  Table, Statistic, Tag, Badge, Avatar, Tooltip, Popover,
  
  // Forms
  Form, Input, Button, Select, DatePicker, Switch, Checkbox, Radio,
  
  // Feedback
  Message, Notification, Modal, Drawer, Spin, Alert,
  
  // Navigation
  Menu, Tabs, Breadcrumb, Steps, Pagination,
  
  // Theme
  luminaTheme, useToken,
  
  // Icons (from @ant-design/icons)
  BellOutlined, UserOutlined, SettingOutlined, // ... etc
} from '@/shared/design-system';
```

### Theme Tokens

```typescript
import { theme } from 'antd';

function MyComponent() {
  const { token } = theme.useToken();
  
  return (
    <div style={{
      padding: token.padding,
      borderRadius: token.borderRadius,
      backgroundColor: token.colorBgContainer,
      color: token.colorText,
    }}>
      Themed content
    </div>
  );
}
```

---

## 🔍 Code Patterns & Conventions

### Naming Conventions

- **Files**: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Components**: `PascalCase`
- **Hooks**: `useCamelCase`
- **Types/Interfaces**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`

### TypeScript Patterns

```typescript
// Component props interface
interface MyComponentProps {
  title: string;
  count?: number;
  onAction: (id: number) => void;
}

// Component with typed props
export function MyComponent({ title, count = 0, onAction }: MyComponentProps) {
  return <div>{title}: {count}</div>;
}

// Generic type for API responses
type ApiResponse<T> = {
  data: T;
  status: number;
  message?: string;
};
```

### Error Handling

```typescript
// Global error boundary catches render errors
// See src/shared/ui/GlobalErrorBoundary.tsx

// Query errors
const { data, error, isError } = useQuery({...});
if (isError) {
  return <ErrorAlert error={error} />;
}

// Try-catch for imperative code
try {
  await api.deleteDataset(id);
  message.success('Deleted successfully');
} catch (error) {
  message.error(`Failed: ${error.message}`);
  console.error('Delete failed:', error);
}
```

### Logging

```typescript
import { createLogger, devLog } from '@/shared/lib/logger';

const log = createLogger('MyFeature');

// Structured logging
log.info('Data fetched', { datasetId, rowCount });
log.error('Fetch failed', { error, datasetId });

// Dev console logging (visible in UI during dev)
devLog.action('User clicked button', { buttonId: 'submit' });
devLog.error ('API call failed', { endpoint: '/api/datasets' });
```

---

## 🚀 Development Workflow

### Daily Workflow

```bash
# 1. Start development server
cd frontend-new
npm run start               # or: npx nx serve

# 2. Make changes to code (auto-reloads on save)

# 3. Lint & format
npm run lint                # ESLint
npm run format              # Prettier (if configured)

# 4. Run tests
npm test

# 5. Build for production (when needed)
npm run build
```

### Available Scripts

| Script | Description |
|--------|-------------|
| `npm run start` | Start dev server (http://localhost:4200) |
| `npm run build` | Production build |
| `npm test` | Run tests |
| `npm run lint` | Run ESLint |
| `npm run generate:api` | Generate API client from OpenAPI spec |

### Environment Variables

```bash
# .env files (.env, .env.local)
VITE_API_BASE_URL=http://localhost:8001
VITE_ENABLE_DEV_CONSOLE=true
VITE_MOCK_API=false
```

Access in code:
```typescript
import { env } from '@/config/env';

const apiUrl = env.apiBaseUrl;  // Type-safe access
```

---

## 📚 Key Documentation

### Must-Read Files

1. **[App.tsx](file:///Users/namanagarwal/system/frontend-new/src/App.tsx)** - App structure, routing
2. **[features/index.ts](file:///Users/namanagarwal/system/frontend-new/src/features/index.ts)** - Feature registration
3. **[design-system.ts](file:///Users/namanagarwal/system/frontend-new/src/shared/design-system.ts)** - UI components
4. **[package.json](file:///Users/namanagarwal/system/frontend-new/package.json)** - Dependencies

### External Documentation

- **React 19**: https://react.dev
- **TypeScript**: https://www.typescriptlang.org/docs
- **TanStack Query**: https://tanstack.com/query/latest
- **Ant Design**: https://ant.design/components/overview
- **React Router**: https://reactrouter.com
- **Nx**: https://nx.dev

---

## 🐛 Debugging & Troubleshooting

### Common Issues

**Issue**: TypeScript errors after API generation
- **Fix**: Run `npm run generate:api` to regenerate types
- **Fix**: Restart TypeScript server in IDE

**Issue**: Component not rendering / white screen
- **Check**: Browser console for errors
- **Check**: Network tab for API failures
- **Check**: React DevTools component tree

**Issue**: API calls failing with CORS errors
- **Fix**: Ensure backend is running on correct port (8001)
- **Fix**: Check backend CORS configuration
- **Fix**: Verify `VITE_API_BASE_URL` in .env

**Issue**: Build fails with module not found
- **Fix**: Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- **Fix**: Clear Nx cache: `npx nx reset`

### Dev Console

Built-in dev console (development only):
- Press `` ` `` (backtick) to toggle
- Shows logs, actions, errors in real-time
- See `src/shared/ui/DevConsole.tsx`

### React DevTools

Install React DevTools browser extension:
- Inspect component tree
- View props and state
- Profile performance

---

## 🎓 Learning Path

### Week 1: Foundations
1. Read [App.tsx](file:///Users/namanagarwal/system/frontend-new/src/App.tsx) to understand structure
2. Explore `src/features/` to see feature examples
3. Run dev server and navigate the UI
4. Read `src/shared/design-system.ts` for available components

### Week 2: Deep Dive
1. Study Feature Registry pattern (`src/shared/core/plugins`)
2. Learn TanStack Query patterns (`src/api/hooks`)
3. Understand Context providers (`src/shared/context`)
4. Write a simple component test

### Week 3: Contribute
1. Add a new page to an existing feature
2. Create a new API hook
3. Style with design system
4. Run tests and linting

---

## 🔗 Related Resources

- **Backend AI Agent Guide**: [`../backend/AI_AGENT_GUIDE.md`](file:///Users/namanagarwal/system/backend/AI_AGENT_GUIDE.md)
- **System Overview**: [`../SYSTEM_OVERVIEW.md`](file:///Users/namanagarwal/system/SYSTEM_OVERVIEW.md)
- **API Documentation**: http://localhost:8001/docs (backend Swagger UI)

---

## 📊 Key Metrics & Stats

- **Bundle Size**: Optimized with Rspack (faster than Webpack)
- **Code Splitting**: Lazy loading for features
- **Type Safety**: 100% TypeScript
- **Component Library**: Ant Design 5.x
- **State Management**: TanStack Query + React Context

---

**Ready to contribute?** Start by adding a simple component or page. Use the design system for consistency, TanStack Query for data, and test your changes! 🚀
