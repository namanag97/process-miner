import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { SDKProvider, luminaTheme } from '@lumina/design-system';
import { AuthProvider } from '../context/AuthContext';
import { NotificationProvider } from '../context/NotificationContext';

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
 * Create test providers with fresh QueryClient
 */
function createTestWrapper(queryClient?: QueryClient) {
  const client = queryClient || createTestQueryClient();

  return function TestWrapper({ children }: WrapperProps) {
    return (
      <ConfigProvider theme={luminaTheme}>
        <QueryClientProvider client={client}>
          <SDKProvider baseUrl="http://localhost:8001">
            <AuthProvider>
              <NotificationProvider>
                <BrowserRouter>{children}</BrowserRouter>
              </NotificationProvider>
            </AuthProvider>
          </SDKProvider>
        </QueryClientProvider>
      </ConfigProvider>
    );
  };
}

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient;
  initialRoute?: string;
}

/**
 * Custom render function with all providers
 */
export function renderWithProviders(
  ui: ReactElement,
  options: CustomRenderOptions = {}
) {
  const { queryClient, initialRoute, ...renderOptions } = options;

  if (initialRoute) {
    window.history.pushState({}, 'Test page', initialRoute);
  }

  const Wrapper = createTestWrapper(queryClient);

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient: queryClient || createTestQueryClient(),
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

// Re-export testing library utilities
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
