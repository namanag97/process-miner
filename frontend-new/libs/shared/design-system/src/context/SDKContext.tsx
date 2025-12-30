import React, { createContext, useContext, useMemo } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// SDK type - will be properly typed when SDK is built
// For now, using a flexible interface
interface ProcessMiningSdk {
  logs: {
    list: (options?: unknown) => Promise<unknown>;
    get: (id: string) => Promise<unknown>;
    ingest: (file: File, metadata?: unknown) => Promise<unknown>;
    analyze: (logId: string) => Promise<unknown>;
    delete: (id: string) => Promise<void>;
  };
  discovery: {
    discover: (options: { logId: string; minerType?: string }) => Promise<unknown>;
    buildDFG: (logId: string, options?: unknown) => Promise<unknown>;
  };
  visualization: {
    getDFG: (logId: string) => Promise<unknown>;
  };
  // Add more clients as needed
}

// Create SDK context
const SDKContext = createContext<ProcessMiningSdk | null>(null);

// Query client configuration
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 2,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

interface SDKProviderProps {
  children: React.ReactNode;
  baseUrl?: string;
}

/**
 * SDKProvider - Wraps app with SDK and React Query contexts
 */
export function SDKProvider({ children, baseUrl = 'http://localhost:8001' }: SDKProviderProps) {
  // Create mock SDK instance for now
  // Replace with actual SDK initialization when backend is ready
  const sdk = useMemo<ProcessMiningSdk>(() => ({
    logs: {
      list: async () => ({ items: [], total: 0 }),
      get: async (id) => ({ id, name: 'Mock Log' }),
      ingest: async () => ({ id: 'new-log-id' }),
      analyze: async () => ({ cases: 0, events: 0 }),
      delete: async () => {},
    },
    discovery: {
      discover: async () => ({ modelId: 'mock-model' }),
      buildDFG: async () => ({ nodes: [], edges: [] }),
    },
    visualization: {
      getDFG: async () => ({ nodes: [], edges: [] }),
    },
  }), [baseUrl]);

  return (
    <SDKContext.Provider value={sdk}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </SDKContext.Provider>
  );
}

/**
 * Hook to access SDK instance
 */
export function useSDK(): ProcessMiningSdk {
  const sdk = useContext(SDKContext);
  if (!sdk) {
    throw new Error('useSDK must be used within SDKProvider');
  }
  return sdk;
}
