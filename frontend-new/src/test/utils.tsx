/**
 * Test Utilities
 *
 * Provides helper functions and custom render methods for testing.
 * All tests should use these utilities for consistent provider wrapping.
 *
 * @example
 * import { render, screen, userEvent } from '@/test/utils';
 *
 * test('renders button', async () => {
 *   render(<MyComponent />);
 *   const button = screen.getByRole('button');
 *   await userEvent.click(button);
 * });
 */

import { type ReactElement, type ReactNode } from 'react';
import { render, type RenderOptions, type RenderResult } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, MemoryRouter, type MemoryRouterProps } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { luminaTheme, SDKProvider } from '@lumina/design-system';

// Re-export everything from testing-library
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';

// ============================================
// Query Client Factory
// ============================================

/**
 * Create a new QueryClient configured for testing
 */
export function createTestQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Disable retries in tests for faster failures
        retry: false,
        // Disable garbage collection during tests
        gcTime: Infinity,
        // Disable stale time checks
        staleTime: Infinity,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

// ============================================
// Provider Wrapper
// ============================================

interface TestWrapperProps {
  children: ReactNode;
  /** Initial URL path for MemoryRouter */
  initialPath?: string;
  /** Initial entries for MemoryRouter */
  initialEntries?: MemoryRouterProps['initialEntries'];
  /** Use BrowserRouter instead of MemoryRouter */
  useBrowserRouter?: boolean;
  /** Custom QueryClient instance */
  queryClient?: QueryClient;
}

/**
 * Wrapper component that provides all necessary context providers for testing
 */
export function TestWrapper({
  children,
  initialPath = '/',
  initialEntries,
  useBrowserRouter = false,
  queryClient,
}: TestWrapperProps): ReactElement {
  const client = queryClient ?? createTestQueryClient();

  const Router = useBrowserRouter ? BrowserRouter : MemoryRouter;
  const routerProps = useBrowserRouter
    ? {}
    : {
        initialEntries: initialEntries ?? [initialPath],
      };

  return (
    <QueryClientProvider client={client}>
      <ConfigProvider theme={luminaTheme}>
        <SDKProvider baseUrl="/api/v1">
          <Router {...routerProps}>{children}</Router>
        </SDKProvider>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

// ============================================
// Custom Render Functions
// ============================================

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  /** Initial URL path for routing */
  initialPath?: string;
  /** Initial route entries */
  initialEntries?: MemoryRouterProps['initialEntries'];
  /** Use BrowserRouter instead of MemoryRouter */
  useBrowserRouter?: boolean;
  /** Custom QueryClient instance */
  queryClient?: QueryClient;
}

/**
 * Custom render function that wraps component with all providers
 *
 * @example
 * const { getByText } = renderWithProviders(<MyComponent />);
 */
export function renderWithProviders(
  ui: ReactElement,
  options: CustomRenderOptions = {}
): RenderResult & { queryClient: QueryClient } {
  const {
    initialPath,
    initialEntries,
    useBrowserRouter,
    queryClient = createTestQueryClient(),
    ...renderOptions
  } = options;

  const Wrapper = ({ children }: { children: ReactNode }) => (
    <TestWrapper
      initialPath={initialPath}
      initialEntries={initialEntries}
      useBrowserRouter={useBrowserRouter}
      queryClient={queryClient}
    >
      {children}
    </TestWrapper>
  );

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
  };
}

// ============================================
// Hook Testing Utilities
// ============================================

interface HookWrapperProps {
  children: ReactNode;
}

/**
 * Create a wrapper for testing hooks with renderHook
 *
 * @example
 * const { result } = renderHook(() => useMyHook(), {
 *   wrapper: createHookWrapper(),
 * });
 */
export function createHookWrapper(options: Omit<CustomRenderOptions, 'container'> = {}) {
  return function HookWrapper({ children }: HookWrapperProps) {
    return <TestWrapper {...options}>{children}</TestWrapper>;
  };
}

// ============================================
// Assertion Helpers
// ============================================

/**
 * Wait for a condition to be true
 *
 * @example
 * await waitForCondition(() => result.current.isSuccess);
 */
export async function waitForCondition(
  condition: () => boolean,
  timeout = 5000,
  interval = 50
): Promise<void> {
  const startTime = Date.now();

  while (!condition()) {
    if (Date.now() - startTime > timeout) {
      throw new Error(`Condition not met within ${timeout}ms`);
    }
    await new Promise((resolve) => setTimeout(resolve, interval));
  }
}

/**
 * Create a deferred promise for async testing
 *
 * @example
 * const deferred = createDeferred<string>();
 * deferred.resolve('test');
 * await deferred.promise;
 */
export function createDeferred<T>(): {
  promise: Promise<T>;
  resolve: (value: T) => void;
  reject: (reason?: unknown) => void;
} {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;

  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });

  return { promise, resolve, reject };
}

// ============================================
// Mock Helpers
// ============================================

/**
 * Create a mock function that resolves after a delay
 *
 * @example
 * const mockFn = createDelayedMock(100, 'result');
 * const result = await mockFn();
 */
export function createDelayedMock<T>(delay: number, value: T): jest.Mock<Promise<T>> {
  return jest.fn().mockImplementation(
    () =>
      new Promise((resolve) => {
        setTimeout(() => resolve(value), delay);
      })
  );
}

/**
 * Create a mock that rejects after a delay
 *
 * @example
 * const mockFn = createDelayedRejectMock(100, new Error('Failed'));
 */
export function createDelayedRejectMock(delay: number, error: Error): jest.Mock<Promise<never>> {
  return jest.fn().mockImplementation(
    () =>
      new Promise((_, reject) => {
        setTimeout(() => reject(error), delay);
      })
  );
}
