/// <reference types="jest" />
import React, { ReactElement } from 'react';
import { render, RenderOptions, RenderResult, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { SDKProvider, luminaTheme } from '@/src/shared/design-system';
import { UserProvider } from '../shared/context/UserContext';
import { NotificationProvider } from '../shared/context/NotificationContext';
import { BackendHealthProvider } from '../shared/context/BackendHealthContext';

/**
 * Create a fresh QueryClient for each test
 */
export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

interface WrapperProps {
  children: React.ReactNode;
}

/**
 * Options for creating a test wrapper
 */
interface TestWrapperOptions {
  queryClient?: QueryClient;
  initialEntries?: string[];
  withRouter?: boolean;
  withUser?: boolean; // MVP: Always includes UserProvider by default
}

/**
 * Create test providers with fresh QueryClient
 */
function createTestWrapper(options: TestWrapperOptions = {}) {
  const {
    queryClient,
    initialEntries = ['/'],
    withRouter = true,
    withUser = true,
  } = options;
  const client = queryClient || createTestQueryClient();

  return function TestWrapper({ children }: WrapperProps) {
    const content = (
      <ConfigProvider theme={luminaTheme}>
        <QueryClientProvider client={client}>
          <SDKProvider baseUrl="http://localhost:8001">
            <BackendHealthProvider>
              {withUser ? (
                <UserProvider>
                  <NotificationProvider>{children}</NotificationProvider>
                </UserProvider>
              ) : (
                children
              )}
            </BackendHealthProvider>
          </SDKProvider>
        </QueryClientProvider>
      </ConfigProvider>
    );

    if (withRouter) {
      return <MemoryRouter initialEntries={initialEntries}>{content}</MemoryRouter>;
    }

    return content;
  };
}

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient;
  initialRoute?: string;
  initialEntries?: string[];
  withRouter?: boolean;
  withUser?: boolean;
}

/**
 * Custom render function with all providers
 */
export function renderWithProviders(
  ui: ReactElement,
  options: CustomRenderOptions = {}
): RenderResult & { queryClient: QueryClient } {
  const {
    queryClient,
    initialRoute,
    initialEntries,
    withRouter = true,
    withUser = true,
    ...renderOptions
  } = options;

  const entries = initialRoute ? [initialRoute] : initialEntries;

  const client = queryClient || createTestQueryClient();
  const Wrapper = createTestWrapper({
    queryClient: client,
    initialEntries: entries,
    withRouter,
    withUser,
  });

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient: client,
  };
}

/**
 * Wait for loading states to resolve
 */
export async function waitForLoadingToFinish() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

/**
 * Create a mock SDK for testing
 */
export function createMockSDK() {
  return {
    processes: {
      list: jest.fn().mockResolvedValue({ items: [], total: 0, page: 1, pageSize: 10 }),
      get: jest.fn().mockResolvedValue(null),
      ingest: jest.fn().mockResolvedValue({ id: 'test-id' }),
      delete: jest.fn().mockResolvedValue(undefined),
      detectColumns: jest.fn().mockResolvedValue({ columns: [] }),
      analyze: jest.fn().mockResolvedValue({}),
    },
    projects: {
      list: jest.fn().mockResolvedValue({ items: [], total: 0, page: 1, pageSize: 10 }),
      get: jest.fn().mockResolvedValue(null),
      create: jest.fn().mockResolvedValue({ id: 'new-project-id', name: 'Test' }),
      update: jest.fn().mockResolvedValue({}),
      delete: jest.fn().mockResolvedValue(undefined),
      addProcess: jest.fn().mockResolvedValue(undefined),
      removeProcess: jest.fn().mockResolvedValue(undefined),
    },
    discovery: {
      buildDFG: jest.fn().mockResolvedValue({ nodes: [], edges: [] }),
      getVariants: jest.fn().mockResolvedValue({ items: [] }),
      getActivities: jest.fn().mockResolvedValue({ items: [] }),
    },
    analytics: {
      getPerformance: jest.fn().mockResolvedValue({}),
      getCycleTime: jest.fn().mockResolvedValue({}),
      getThroughput: jest.fn().mockResolvedValue({}),
      getRework: jest.fn().mockResolvedValue({}),
      getBottlenecks: jest.fn().mockResolvedValue({ items: [] }),
      getPatterns: jest.fn().mockResolvedValue({ items: [] }),
      getProcessSummary: jest.fn().mockResolvedValue({}),
      getDeadlines: jest.fn().mockResolvedValue({}),
      getAutomation: jest.fn().mockResolvedValue({}),
      getUnwantedActivities: jest.fn().mockResolvedValue({}),
    },
    conformance: {
      check: jest.fn().mockResolvedValue({}),
      getDiagnostics: jest.fn().mockResolvedValue({}),
    },
    organizational: {
      getSocialNetwork: jest.fn().mockResolvedValue({}),
      getNetworkMetrics: jest.fn().mockResolvedValue({}),
      getRoles: jest.fn().mockResolvedValue({ items: [] }),
      getResourceProfile: jest.fn().mockResolvedValue({}),
      getWorkloadDistribution: jest.fn().mockResolvedValue({}),
    },
    predictions: {
      list: jest.fn().mockResolvedValue({ items: [] }),
      train: jest.fn().mockResolvedValue({}),
      predict: jest.fn().mockResolvedValue({}),
      getHistory: jest.fn().mockResolvedValue({ items: [] }),
    },
    ai: {
      getInsights: jest.fn().mockResolvedValue({ insights: [] }),
      getPredictors: jest.fn().mockResolvedValue({ items: [] }),
    },
    simulation: {
      playOut: jest.fn().mockResolvedValue({}),
      getResults: jest.fn().mockResolvedValue({}),
      getCapacityAnalysis: jest.fn().mockResolvedValue({}),
    },
    audit: {
      list: jest.fn().mockResolvedValue([]),
      create: jest.fn().mockResolvedValue({}),
    },
    checkHealth: jest.fn().mockResolvedValue({ status: 'healthy' }),
    isHealthy: jest.fn().mockResolvedValue(true),
  };
}

// ============================================
// Test Assertions & Helpers
// ============================================
// Note: These helpers use @testing-library/jest-dom matchers
// which are only available in test files with proper setup

/**
 * Assert that an element has specific text content
 */
export function expectTextContent(element: HTMLElement, text: string) {
  expect(element.textContent).toContain(text);
}

/**
 * Find a loading indicator (returns element or null)
 */
export async function findLoadingState() {
  return screen.queryByRole('status');
}

/**
 * Find an error message (returns element or null)
 */
export async function findErrorMessage(message?: string | RegExp) {
  if (message) {
    return screen.queryByText(message);
  }
  return screen.queryByRole('alert');
}

/**
 * Wait for loading to finish (query state to settle)
 */
export async function waitForQueryToSettle() {
  // Wait for any pending state updates to flush
  await waitFor(() => {
    const loadingIndicator = screen.queryByRole('status');
    if (loadingIndicator) {
      throw new Error('Still loading');
    }
  });
}

/**
 * Mock localStorage for tests
 */
export function mockLocalStorage() {
  const store: Record<string, string> = {};

  const mockStorage = {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      Object.keys(store).forEach((key) => delete store[key]);
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: jest.fn((index: number) => Object.keys(store)[index] || null),
  };

  Object.defineProperty(window, 'localStorage', { value: mockStorage });

  return mockStorage;
}

/**
 * Mock sessionStorage for tests
 */
export function mockSessionStorage() {
  const store: Record<string, string> = {};

  const mockStorage = {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      Object.keys(store).forEach((key) => delete store[key]);
    }),
    get length() {
      return Object.keys(store).length;
    },
    key: jest.fn((index: number) => Object.keys(store)[index] || null),
  };

  Object.defineProperty(window, 'sessionStorage', { value: mockStorage });

  return mockStorage;
}

/**
 * Create a mock user for testing
 */
export function createMockUser(overrides = {}) {
  return {
    id: 'test-user-1',
    name: 'Test User',
    email: 'test@example.com',
    role: 'admin' as const,
    ...overrides,
  };
}

/**
 * Create a mock guest user for testing
 */
export function createMockGuestUser() {
  return {
    id: 'guest_test-session',
    name: 'Guest User',
    email: 'guest@local.session',
    role: 'guest' as const,
    isGuest: true,
    sessionId: 'test-session',
  };
}

/**
 * Create a mock process for testing
 */
export function createMockProcess(overrides = {}) {
  return {
    id: 'process-1',
    name: 'Test Process',
    status: 'ready' as const,
    caseCount: 100,
    eventCount: 1000,
    activityCount: 10,
    uploadedAt: new Date().toISOString(),
    ...overrides,
  };
}

/**
 * Create a mock project for testing
 */
export function createMockProject(overrides = {}) {
  return {
    id: 'project-1',
    name: 'Test Project',
    description: 'A test project',
    processIds: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

// Re-export testing library utilities
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
