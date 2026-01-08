# Process Mining SaaS - Frontend

> **Version:** 2.0
> **Tech Stack:** React 19, TypeScript, Nx, Rspack, TanStack Query
> **Status:** ✅ Production-Ready

A modern, type-safe React application for process mining analytics, built with best practices for performance, testability, and developer experience.

---

## Quick Start

```bash
# Install dependencies
npm install

# Start development server (port 4200)
npm run start

# Build for production
npm run build

# Run tests
npm run test

# Type check
npm run typecheck

# Lint
npm run lint
```

**Development Server:** http://localhost:4200
**Backend API:** http://localhost:8001
**API Docs:** http://localhost:8001/docs

---

## Features

### 7 Core Domains

1. **Explorer** - Process exploration and filtering
2. **Discovery** - Automated process model discovery
3. **Analytics** - Performance analytics and bottlenecks
4. **AI** - Predictive analytics and ML insights
5. **KPI** - Custom KPI dashboards
6. **Projects** - Workspace and project management
7. **Upload Wizard** - Dataset upload with schema mapping

### Key Capabilities

- ✅ **Process Visualization** - Interactive process graphs with Cytoscape.js
- ✅ **Advanced Filtering** - Activity, time, duration, resource filters
- ✅ **Real-time Analytics** - Live performance metrics
- ✅ **AI Predictions** - Next activity, remaining time forecasts
- ✅ **Multi-tenant** - Organization and workspace isolation
- ✅ **DevConsole** - In-app debugging with importance scoring

---

## Project Structure

```
frontend-new/
├── src/                        # Main application source
│   ├── App.tsx                # App shell, providers, routing
│   ├── routes.tsx             # Explicit route definitions (all routes here)
│   ├── navigation.ts          # Navigation config and route mappings
│   ├── main.tsx               # Application entry point
│   │
│   ├── features/              # Feature modules
│   │   ├── platform/          # Workspace, projects, settings
│   │   ├── explorer/          # Process visualization (DFG, variants)
│   │   ├── analytics/         # Performance analytics dashboards
│   │   ├── discovery/         # Process discovery UI
│   │   ├── ai/                # AI predictions and chat
│   │   ├── kpi/               # KPI dashboards
│   │   ├── auth/              # Authentication pages
│   │   └── landing/           # Landing page
│   │
│   ├── shared/                # Shared code
│   │   ├── design-system.ts   # UI component exports (import from here!)
│   │   ├── context/           # UserContext, NotificationContext
│   │   ├── hooks/             # Shared custom hooks
│   │   ├── lib/               # Utilities (logger, formatters)
│   │   └── ui/                # DevConsole, ErrorBoundary
│   │
│   ├── api/                   # API integration
│   │   └── hooks/             # TanStack Query hooks
│   │
│   └── stores/                # Global state stores
│
├── libs/                      # Shared libraries
│   └── openapi-sdk/           # Auto-generated TypeScript API client
│
└── docs/                      # Documentation
    ├── API_INTEGRATION_GUIDE.md
    ├── STATE_MANAGEMENT_GUIDE.md
    ├── ERROR_HANDLING_AND_LOGGING_GUIDE.md
    └── TESTING_GUIDE.md
```

---

## Architecture

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | React 19 | UI rendering, hooks, suspense |
| **Language** | TypeScript 5.3 | Type safety (95%+ coverage) |
| **Build** | Nx + Rspack | Monorepo, fast builds |
| **Routing** | React Router v6 | Client-side navigation |
| **State** | TanStack Query v5 | Server state caching |
| **UI** | Ant Design v5 | Component library |
| **Visualization** | Cytoscape.js | Process graphs |
| **Testing** | Jest + RTL | Unit & integration tests |

### State Management (3 Layers)

1. **Server State** (TanStack Query) - Backend data, caching, revalidation
2. **Client State** (React Context) - UI preferences, sidebar, theme
3. **URL State** (React Router) - Filters, pagination, shareable state

See [STATE_MANAGEMENT_GUIDE.md](./docs/STATE_MANAGEMENT_GUIDE.md) for details.

### Error Handling

- **Feature-level error boundaries** in all 7 features
- **4 error classifications**: Transient, Validation, Authorization, Critical
- **DevConsole logging** with importance scoring (1-5)
- **User-friendly fallbacks** with retry options

See [ERROR_HANDLING_AND_LOGGING_GUIDE.md](./docs/ERROR_HANDLING_AND_LOGGING_GUIDE.md) for details.

---

## Development

### Available Scripts

```bash
# Development
npm run start              # Dev server (port 4200)
npm run build              # Production build
npm run preview            # Preview production build

# Code Quality
npm run typecheck          # TypeScript check (0 errors)
npm run lint               # ESLint
npm run lint -- --fix      # Auto-fix lint issues

# Testing
npm run test               # Run all tests
npm run test:watch         # Watch mode
npm run test:coverage      # With coverage report

# API Client Generation
npm run generate:sdk       # Regenerate API client from OpenAPI spec
```

### Development Workflow

1. **Start Backend** (in separate terminal):
   ```bash
   cd ../backend/src
   ../.venv/bin/python -m uvicorn api.main:app --reload --port 8001
   ```

2. **Start Frontend**:
   ```bash
   npm run start
   ```

3. **Open DevConsole**: Press `Ctrl+Shift+D` or click bug icon
   - View logs with importance scoring
   - Track API requests/responses
   - Monitor backend health

4. **Make Changes**: Files hot-reload automatically

5. **Run Type Check**: `npm run typecheck` (should show 0 errors)

6. **Run Tests**: `npm run test`

7. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat: description"
   git push
   ```

---

## Documentation

### Guides

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture, data flow, tech stack
- **[STATE_MANAGEMENT_GUIDE.md](./docs/STATE_MANAGEMENT_GUIDE.md)** - TanStack Query, Context, URL state
- **[ERROR_HANDLING_AND_LOGGING_GUIDE.md](./docs/ERROR_HANDLING_AND_LOGGING_GUIDE.md)** - Error boundaries, DevConsole, importance scoring
- **[TESTING_GUIDE.md](./docs/TESTING_GUIDE.md)** - Unit tests, component tests, MSW setup
- **[API_INTEGRATION_GUIDE.md](./docs/API_INTEGRATION_GUIDE.md)** - Queries, mutations, cache management

### Quick Links

- [API Documentation](http://localhost:8001/docs) - Swagger UI
- [OpenAPI Spec](http://localhost:8001/openapi.json) - API schema
- [Backend README](../backend/README.md) - Backend setup guide
- [Project CLAUDE.md](../CLAUDE.md) - Claude AI assistant instructions

---

## Key Concepts

### Feature Organization

Each feature is self-contained:
```
features/explorer/
├── pages/          # Route components
├── components/     # Feature-specific UI
├── hooks/          # Data fetching, business logic
├── utils/          # Pure functions
├── types/          # TypeScript types
└── routes.tsx      # Route configuration
```

### Query Pattern

```typescript
import { useQuery } from '@tanstack/react-query';

function useDatasets() {
  return useQuery({
    queryKey: ['datasets'],
    queryFn: async () => {
      const response = await fetch('/api/v1/datasets');
      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

### Error Boundary Pattern

```typescript
<ErrorBoundary
  fallbackRender={({ error, resetErrorBoundary }) => (
    <FeatureErrorFallback
      error={error}
      resetError={resetErrorBoundary}
      featureName="Explorer"
    />
  )}
>
  <Routes>{/* feature routes */}</Routes>
</ErrorBoundary>
```

### DevConsole Logging

```typescript
import { devLog } from '@/shared/ui';

// Log user action (importance: 4)
devLog.action('ProjectCreate', 'User clicked create', { projectName });

// Log API request (importance: 2)
devLog.apiRequest('POST', '/api/v1/projects', data);

// Log API response (importance: 3-5 based on status)
devLog.apiResponse('POST', '/api/v1/projects', 201, duration, response);

// Log error (importance: 5)
devLog.error('ProjectCreate', 'Failed to create', { error: error.message });
```

---

## TypeScript

- **Coverage:** 95%+ (only 1 `any` in template code)
- **Strict Mode:** Enabled
- **No Implicit Any:** Enforced
- **Error Handling:** `unknown` with type guards instead of `any`

### Type-Safe Patterns

```typescript
// ✅ GOOD: Type guard for errors
catch (err: unknown) {
  const error = err instanceof Error ? err : new Error(String(err));
  devLog.error('Feature', error.message, { stack: error.stack });
}

// ❌ BAD: Using any
catch (err: any) {
  devLog.error('Feature', err.message);
}
```

---

## Performance

### Optimizations

- ✅ **Code Splitting** - Route-based lazy loading
- ✅ **Memoization** - useMemo for expensive calculations
- ✅ **Web Workers** - ELK graph layout off main thread
- ✅ **Bundle Analysis** - `npm run build -- --analyze`
- ✅ **React Query Caching** - Reduces API calls

### Bundle Size

- **Main Bundle:** ~200KB (gzipped)
- **Vendor Bundle:** ~150KB (React, Ant Design)
- **Feature Bundles:** 20-50KB each (lazy-loaded)

---

## Testing

### Test Structure

```
src/features/projects/
├── components/
│   ├── ProjectCard.tsx
│   └── __tests__/
│       └── ProjectCard.test.tsx
└── hooks/
    ├── useProjects.ts
    └── __tests__/
        └── useProjects.test.ts
```

### Running Tests

```bash
npm run test                    # All tests
npm run test:watch              # Watch mode
npm run test:coverage           # With coverage
npm run test -- ProjectCard     # Specific test
```

### Coverage Goals

- **Utils:** >80%
- **Business Logic:** >70%
- **Components:** >50%
- **Integration:** Critical paths

See [TESTING_GUIDE.md](./docs/TESTING_GUIDE.md) for patterns and examples.

---

## Deployment

### Production Build

```bash
npm run build
# Output: dist/
# - Minified, tree-shaken, code-split
# - Source maps for debugging
```

### Environment Variables

Create `.env` file:
```
VITE_API_URL=http://localhost:8001
VITE_ENV=development
```

### Deploy to Production

```bash
npm run build
# Upload dist/ to CDN or static hosting
# Configure backend CORS for production domain
```

---

## Troubleshooting

### Common Issues

**Q: Dev server won't start**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Q: TypeScript errors**
```bash
# Run type check
npm run typecheck

# Check for any types
grep -r ": any" src/ --include="*.ts" --include="*.tsx"
```

**Q: API calls failing**
```bash
# Check backend is running
curl http://localhost:8001/health/live

# Check DevConsole for detailed logs
# Press Ctrl+Shift+D
```

**Q: Tests failing**
```bash
# Clear jest cache
npm run test -- --clearCache

# Run specific test
npm run test -- --testNamePattern="my test"
```

---

## Contributing

### Code Quality Checklist

Before submitting PR:
- [ ] `npm run typecheck` passes (0 errors)
- [ ] `npm run lint` passes (no warnings)
- [ ] `npm run test` passes (all tests green)
- [ ] New features have tests
- [ ] DevConsole logs added for key actions
- [ ] Error handling with try/catch + devLog.error()
- [ ] No `any` types (use proper types or `unknown`)

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add feature X"

# Push and create PR
git push origin feature/my-feature
gh pr create --base dev
```

---

## Links

- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs
- **Frontend:** http://localhost:4200
- **GitHub:** https://github.com/namanag97/process-miner

---

## License

Proprietary - All Rights Reserved

---

**Built with ❤️ using React 19, TypeScript, and Nx**

