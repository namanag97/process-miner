# Testing Guide

> **Version:** 1.0
> **Last Updated:** 2026-01-07
> **Purpose:** Complete guide to testing patterns, tools, and best practices

---

## Table of Contents

1. [Overview](#overview)
2. [Testing Philosophy](#testing-philosophy)
3. [Test Setup](#test-setup)
4. [Unit Tests](#unit-tests)
5. [Component Tests](#component-tests)
6. [Integration Tests](#integration-tests)
7. [Testing with TanStack Query](#testing-with-tanstack-query)
8. [Mocking](#mocking)
9. [Best Practices](#best-practices)

---

## Overview

Our testing strategy focuses on **confidence over coverage**:

| Test Type | Tool | Purpose | Coverage Goal |
|-----------|------|---------|---------------|
| **Unit Tests** | Jest | Pure functions, utils | >80% |
| **Component Tests** | React Testing Library | User interactions, rendering | >50% |
| **Integration Tests** | RTL + MSW | Feature flows, API integration | Critical paths |
| **E2E Tests** | (Future: Playwright) | Full user journeys | Key scenarios |

**Current Status:**
- ✅ Jest configured with TypeScript
- ✅ React Testing Library available
- ⚠️ MSW setup needed (Mock Service Worker)
- ❌ E2E tests (planned for future)

---

## Testing Philosophy

### Write Tests That:

✅ **Test Behavior, Not Implementation**
```typescript
// ✅ GOOD: Test what the user sees
test('shows success message after form submit', async () => {
  render(<CreateProjectForm />);
  await userEvent.type(screen.getByLabelText('Project Name'), 'New Project');
  await userEvent.click(screen.getByRole('button', { name: /create/i }));
  expect(await screen.findByText('Project created')).toBeInTheDocument();
});

// ❌ BAD: Test implementation details
test('calls handleSubmit when button clicked', () => {
  const handleSubmit = jest.fn();
  render(<CreateProjectForm onSubmit={handleSubmit} />);
  // Testing internal prop passing, not user behavior
});
```

✅ **Give Confidence**
```typescript
// ✅ GOOD: Test critical user flow
test('user can upload, map, and analyze dataset', async () => {
  // Full integration test of upload wizard
});

// ❌ BAD: Test trivial things
test('button has correct class name', () => {
  // Low value test
});
```

✅ **Are Maintainable**
```typescript
// ✅ GOOD: Use semantic queries
screen.getByRole('button', { name: /submit/i });
screen.getByLabelText('Email');

// ❌ BAD: Use brittle selectors
container.querySelector('.btn-primary');
container.querySelector('#email-input');
```

### Test Pyramid

```
      /\
     /E2E\        10% - Full user journeys
    /------\
   /Integration\ 20% - Feature flows with API
  /------------\
 / Component   \ 30% - UI interactions
/--------------\
/  Unit Tests  \  40% - Pure functions, utils
```

---

## Test Setup

### Project Structure

```
src/
├── features/
│   └── projects/
│       ├── components/
│       │   ├── ProjectCard.tsx
│       │   └── __tests__/
│       │       └── ProjectCard.test.tsx
│       ├── hooks/
│       │   ├── useProjects.ts
│       │   └── __tests__/
│       │       └── useProjects.test.ts
│       └── utils/
│           ├── formatters.ts
│           └── __tests__/
│               └── formatters.test.ts
└── test/
    ├── utils.tsx         # Test utilities
    ├── setup.ts          # Jest setup
    └── mocks/
        ├── handlers.ts    # MSW request handlers
        └── server.ts      # MSW server
```

### Test Utilities Setup

**Create:** `src/test/utils.tsx`
```typescript
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { ReactElement } from 'react';

// Create a test QueryClient with no retries
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Don't retry in tests
        cacheTime: 0, // Don't cache
      },
      mutations: {
        retry: false,
      },
    },
  });
}

// Custom render with all providers
export function renderWithProviders(
  ui: ReactElement,
  {
    queryClient = createTestQueryClient(),
    ...renderOptions
  }: RenderOptions & { queryClient?: QueryClient } = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </QueryClientProvider>
    );
  }

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
  };
}

// Re-export everything from React Testing Library
export * from '@testing-library/react';
export { renderWithProviders as render };
```

### MSW Setup (Mock Service Worker)

**Install:**
```bash
npm install -D msw
```

**Create:** `src/test/mocks/handlers.ts`
```typescript
import { rest } from 'msw';

export const handlers = [
  // Projects
  rest.get('/api/v1/projects', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        items: [
          { id: 'proj-1', name: 'Test Project 1', created_at: '2024-01-01' },
          { id: 'proj-2', name: 'Test Project 2', created_at: '2024-01-02' },
        ],
        total: 2,
      })
    );
  }),

  rest.get('/api/v1/projects/:id', (req, res, ctx) => {
    const { id } = req.params;
    return res(
      ctx.status(200),
      ctx.json({
        id,
        name: `Project ${id}`,
        created_at: '2024-01-01',
      })
    );
  }),

  rest.post('/api/v1/projects', async (req, res, ctx) => {
    const body = await req.json();
    return res(
      ctx.status(201),
      ctx.json({
        id: 'proj-new',
        ...body,
        created_at: new Date().toISOString(),
      })
    );
  }),

  // Datasets
  rest.get('/api/v1/datasets', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        items: [],
        total: 0,
      })
    );
  }),
];
```

**Create:** `src/test/mocks/server.ts`
```typescript
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

**Create:** `src/test/setup.ts`
```typescript
import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Start MSW server before all tests
beforeAll(() => server.listen());

// Reset handlers after each test
afterEach(() => server.resetHandlers());

// Clean up after all tests
afterAll(() => server.close());
```

**Update:** `jest.config.js`
```javascript
module.exports = {
  setupFilesAfterEnv: ['<rootDir>/src/test/setup.ts'],
  testEnvironment: 'jsdom',
  // ... other config
};
```

---

## Unit Tests

### Pure Functions

**Example:** `src/shared/utils/__tests__/formatters.test.ts`
```typescript
import { formatDuration, formatPercentage, formatNumber } from '../formatters';

describe('formatDuration', () => {
  it('formats milliseconds correctly', () => {
    expect(formatDuration(500)).toBe('500ms');
    expect(formatDuration(1500)).toBe('1.5s');
    expect(formatDuration(65000)).toBe('1m 5s');
    expect(formatDuration(3665000)).toBe('1h 1m 5s');
  });

  it('handles zero', () => {
    expect(formatDuration(0)).toBe('0ms');
  });

  it('handles negative values', () => {
    expect(formatDuration(-1000)).toBe('-1s');
  });
});

describe('formatPercentage', () => {
  it('formats percentages with default precision', () => {
    expect(formatPercentage(0.1234)).toBe('12.34%');
    expect(formatPercentage(0.5)).toBe('50.00%');
    expect(formatPercentage(1)).toBe('100.00%');
  });

  it('formats with custom precision', () => {
    expect(formatPercentage(0.1234, 0)).toBe('12%');
    expect(formatPercentage(0.1234, 3)).toBe('12.340%');
  });

  it('handles edge cases', () => {
    expect(formatPercentage(0)).toBe('0.00%');
    expect(formatPercentage(2)).toBe('200.00%');
  });
});

describe('formatNumber', () => {
  it('formats numbers with thousand separators', () => {
    expect(formatNumber(1000)).toBe('1,000');
    expect(formatNumber(1234567)).toBe('1,234,567');
  });

  it('handles decimals', () => {
    expect(formatNumber(1234.56)).toBe('1,234.56');
  });
});
```

### Business Logic

**Example:** `src/features/explorer/utils/__tests__/filterLogic.test.ts`
```typescript
import { applyActivityFilter, applyDurationFilter } from '../filterLogic';

describe('applyActivityFilter', () => {
  const traces = [
    { id: '1', activities: ['A', 'B', 'C'] },
    { id: '2', activities: ['A', 'C'] },
    { id: '3', activities: ['B', 'C'] },
  ];

  it('filters traces containing activity', () => {
    const result = applyActivityFilter(traces, { type: 'include', activities: ['B'] });
    expect(result).toHaveLength(2);
    expect(result.map(t => t.id)).toEqual(['1', '3']);
  });

  it('filters traces not containing activity', () => {
    const result = applyActivityFilter(traces, { type: 'exclude', activities: ['B'] });
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe('2');
  });

  it('filters with multiple activities (OR)', () => {
    const result = applyActivityFilter(traces, { type: 'include', activities: ['A', 'B'] });
    expect(result).toHaveLength(3); // All traces have A or B
  });
});

describe('applyDurationFilter', () => {
  const traces = [
    { id: '1', duration: 1000 },
    { id: '2', duration: 5000 },
    { id: '3', duration: 10000 },
  ];

  it('filters by min duration', () => {
    const result = applyDurationFilter(traces, { min: 3000 });
    expect(result).toHaveLength(2);
    expect(result.map(t => t.id)).toEqual(['2', '3']);
  });

  it('filters by max duration', () => {
    const result = applyDurationFilter(traces, { max: 7000 });
    expect(result).toHaveLength(2);
    expect(result.map(t => t.id)).toEqual(['1', '2']);
  });

  it('filters by range', () => {
    const result = applyDurationFilter(traces, { min: 2000, max: 8000 });
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe('2');
  });
});
```

---

## Component Tests

### Simple Component

**Example:** `src/features/projects/components/__tests__/ProjectCard.test.tsx`
```typescript
import { render, screen } from '@/test/utils';
import { ProjectCard } from '../ProjectCard';

describe('ProjectCard', () => {
  const project = {
    id: 'proj-123',
    name: 'Test Project',
    description: 'Test description',
    created_at: '2024-01-01T00:00:00Z',
    dataset_count: 5,
  };

  it('renders project information', () => {
    render(<ProjectCard project={project} />);

    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
    expect(screen.getByText('5 datasets')).toBeInTheDocument();
  });

  it('shows formatted creation date', () => {
    render(<ProjectCard project={project} />);

    // Check for date in any format
    expect(screen.getByText(/Jan|January/i)).toBeInTheDocument();
  });

  it('calls onSelect when clicked', async () => {
    const onSelect = jest.fn();
    const { user } = render(<ProjectCard project={project} onSelect={onSelect} />);

    await user.click(screen.getByRole('article'));

    expect(onSelect).toHaveBeenCalledWith(project.id);
  });

  it('shows actions menu', async () => {
    const { user } = render(<ProjectCard project={project} />);

    await user.click(screen.getByLabelText('More actions'));

    expect(screen.getByText('Edit')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });
});
```

### Component with User Interactions

**Example:** `src/features/projects/components/__tests__/CreateProjectForm.test.tsx`
```typescript
import { render, screen, waitFor } from '@/test/utils';
import { CreateProjectForm } from '../CreateProjectForm';
import userEvent from '@testing-library/user-event';

describe('CreateProjectForm', () => {
  it('renders form fields', () => {
    render(<CreateProjectForm />);

    expect(screen.getByLabelText(/project name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create/i })).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();
    render(<CreateProjectForm />);

    const submitButton = screen.getByRole('button', { name: /create/i });
    await user.click(submitButton);

    expect(await screen.findByText(/name is required/i)).toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    const onSuccess = jest.fn();
    render(<CreateProjectForm onSuccess={onSuccess} />);

    await user.type(screen.getByLabelText(/project name/i), 'New Project');
    await user.type(screen.getByLabelText(/description/i), 'Test description');
    await user.click(screen.getByRole('button', { name: /create/i }));

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith(expect.objectContaining({
        name: 'New Project',
        description: 'Test description',
      }));
    });
  });

  it('shows error message on API failure', async () => {
    // Override MSW handler to return error
    server.use(
      rest.post('/api/v1/projects', (req, res, ctx) => {
        return res(ctx.status(400), ctx.json({ message: 'Name already exists' }));
      })
    );

    const user = userEvent.setup();
    render(<CreateProjectForm />);

    await user.type(screen.getByLabelText(/project name/i), 'Existing Project');
    await user.click(screen.getByRole('button', { name: /create/i }));

    expect(await screen.findByText(/name already exists/i)).toBeInTheDocument();
  });

  it('disables submit button while loading', async () => {
    const user = userEvent.setup();
    render(<CreateProjectForm />);

    await user.type(screen.getByLabelText(/project name/i), 'New Project');
    const submitButton = screen.getByRole('button', { name: /create/i });
    await user.click(submitButton);

    expect(submitButton).toBeDisabled();
  });
});
```

---

## Integration Tests

### Feature Flow with API

**Example:** `src/features/projects/__tests__/ProjectsListPage.integration.test.tsx`
```typescript
import { render, screen, waitFor } from '@/test/utils';
import { ProjectsListPage } from '../pages/ProjectsListPage';
import userEvent from '@testing-library/user-event';

describe('ProjectsListPage Integration', () => {
  it('loads and displays projects', async () => {
    render(<ProjectsListPage />);

    // Shows loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Shows projects after loading
    expect(await screen.findByText('Test Project 1')).toBeInTheDocument();
    expect(screen.getByText('Test Project 2')).toBeInTheDocument();
  });

  it('creates new project', async () => {
    const user = userEvent.setup();
    render(<ProjectsListPage />);

    // Wait for list to load
    await screen.findByText('Test Project 1');

    // Open create modal
    await user.click(screen.getByRole('button', { name: /create project/i }));

    // Fill form
    await user.type(screen.getByLabelText(/project name/i), 'New Project');
    await user.type(screen.getByLabelText(/description/i), 'Test description');

    // Submit
    await user.click(screen.getByRole('button', { name: /create/i }));

    // Verify success message
    expect(await screen.findByText(/project created successfully/i)).toBeInTheDocument();

    // Verify new project appears in list
    expect(await screen.findByText('New Project')).toBeInTheDocument();
  });

  it('deletes project', async () => {
    const user = userEvent.setup();
    server.use(
      rest.delete('/api/v1/projects/:id', (req, res, ctx) => {
        return res(ctx.status(204));
      })
    );

    render(<ProjectsListPage />);

    await screen.findByText('Test Project 1');

    // Open actions menu
    await user.click(screen.getAllByLabelText('More actions')[0]);

    // Click delete
    await user.click(screen.getByText(/delete/i));

    // Confirm deletion
    await user.click(screen.getByRole('button', { name: /confirm/i }));

    // Verify project removed
    await waitFor(() => {
      expect(screen.queryByText('Test Project 1')).not.toBeInTheDocument();
    });
  });

  it('searches projects', async () => {
    const user = userEvent.setup();
    render(<ProjectsListPage />);

    await screen.findByText('Test Project 1');

    // Type in search
    await user.type(screen.getByPlaceholderText(/search/i), 'Project 1');

    // Verify filtered results
    expect(screen.getByText('Test Project 1')).toBeInTheDocument();
    expect(screen.queryByText('Test Project 2')).not.toBeInTheDocument();
  });
});
```

---

## Testing with TanStack Query

### Custom Hooks

**Example:** `src/features/projects/hooks/__tests__/useProjects.test.ts`
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useProjects } from '../useProjects';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

describe('useProjects', () => {
  it('fetches projects successfully', async () => {
    const { result } = renderHook(() => useProjects(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual({
      items: [
        expect.objectContaining({ id: 'proj-1', name: 'Test Project 1' }),
        expect.objectContaining({ id: 'proj-2', name: 'Test Project 2' }),
      ],
      total: 2,
    });
  });

  it('handles API errors', async () => {
    server.use(
      rest.get('/api/v1/projects', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ message: 'Server error' }));
      })
    );

    const { result } = renderHook(() => useProjects(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeTruthy();
  });
});
```

---

## Mocking

### Mocking API Responses

```typescript
// Override specific endpoint
server.use(
  rest.get('/api/v1/datasets/:id', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: req.params.id,
        name: 'Mocked Dataset',
        status: 'ready',
      })
    );
  })
);

// Simulate error
server.use(
  rest.post('/api/v1/datasets', (req, res, ctx) => {
    return res(
      ctx.status(400),
      ctx.json({ message: 'Validation failed' })
    );
  })
);

// Simulate network delay
server.use(
  rest.get('/api/v1/datasets', (req, res, ctx) => {
    return res(
      ctx.delay(2000), // 2 second delay
      ctx.status(200),
      ctx.json({ items: [], total: 0 })
    );
  })
);
```

### Mocking External Libraries

```typescript
// Mock logger
jest.mock('@/shared/lib/logger', () => ({
  createLogger: () => ({
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
  }),
}));

// Mock router
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
  useParams: () => ({ id: 'test-id' }),
}));
```

---

## Best Practices

### 1. Test User Behavior, Not Implementation

```typescript
// ✅ GOOD: Test what the user sees
expect(screen.getByText('Welcome')).toBeInTheDocument();

// ❌ BAD: Test internal state
expect(component.state.isOpen).toBe(true);
```

### 2. Use Semantic Queries

```typescript
// ✅ GOOD: Accessible queries
screen.getByRole('button', { name: /submit/i });
screen.getByLabelText('Email');
screen.getByPlaceholderText('Enter your name');

// ❌ BAD: Implementation detail queries
screen.getByTestId('submit-button');
container.querySelector('.btn-primary');
```

### 3. Wait for Async Updates

```typescript
// ✅ GOOD: Wait for element
expect(await screen.findByText('Success')).toBeInTheDocument();

// ✅ GOOD: Wait for condition
await waitFor(() => {
  expect(screen.getByText('Success')).toBeInTheDocument();
});

// ❌ BAD: Don't wait
expect(screen.getByText('Success')).toBeInTheDocument(); // Fails if async
```

### 4. Clean Up After Tests

```typescript
// Reset MSW handlers
afterEach(() => {
  server.resetHandlers();
});

// Clear timers
afterEach(() => {
  jest.clearAllTimers();
});
```

### 5. Keep Tests Focused

```typescript
// ✅ GOOD: One assertion per test
test('shows project name', () => {
  render(<ProjectCard project={project} />);
  expect(screen.getByText(project.name)).toBeInTheDocument();
});

test('shows dataset count', () => {
  render(<ProjectCard project={project} />);
  expect(screen.getByText('5 datasets')).toBeInTheDocument();
});

// ❌ BAD: Testing multiple things
test('renders project card', () => {
  // Tests 10 different things
});
```

---

## Running Tests

```bash
# Run all tests
npm run test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm run test -- ProjectCard.test.tsx

# Run tests matching pattern
npm run test -- --testNamePattern="renders project"
```

---

## Summary

**Testing Priorities:**
1. **Critical user flows** - Upload wizard, dataset analysis
2. **Business logic** - Filtering, calculations, transformations
3. **Shared utilities** - Formatters, validators, parsers
4. **Complex components** - Forms, data tables, graphs

**Coverage Goals:**
- Utilities: >80%
- Business logic: >70%
- Components: >50%
- Integration: Critical paths

**Next Steps:**
1. Set up MSW for API mocking
2. Write tests for shared utilities
3. Add tests for critical user flows
4. Document testing patterns as you go

