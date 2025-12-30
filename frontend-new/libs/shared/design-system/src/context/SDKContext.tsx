import React, { createContext, useContext, useMemo, useCallback } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ApiClient } from '../api/client';
import {
  createLogsModule,
  createDiscoveryModule,
  createAnalyticsModule,
  createConformanceModule,
  createAIModule,
  type LogsModule,
  type DiscoveryModule,
  type AnalyticsModule,
  type ConformanceModule,
  type AIModule,
} from '../api/modules';

// SDK type - properly typed with real modules
interface ProcessMiningSdk {
  logs: LogsModule;
  discovery: DiscoveryModule;
  analytics: AnalyticsModule;
  conformance: ConformanceModule;
  ai: AIModule;
  visualization: {
    getDFG: (logId: string) => Promise<unknown>;
  };
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
  getAuthToken?: () => string | null;
}

/**
 * SDKProvider - Wraps app with SDK and React Query contexts
 */
export function SDKProvider({ 
  children, 
  baseUrl = 'http://localhost:8001',
  getAuthToken,
}: SDKProviderProps) {
  // Memoize the auth token getter
  const memoizedGetAuthToken = useCallback(() => {
    if (getAuthToken) {
      return getAuthToken();
    }
    // Default: try localStorage
    return localStorage.getItem('auth_token');
  }, [getAuthToken]);

  // Create SDK with real API modules
  const sdk = useMemo<ProcessMiningSdk>(() => {
    const client = new ApiClient({ 
      baseUrl, 
      getAuthToken: memoizedGetAuthToken,
    });

    const logsModule = createLogsModule(client);
    const discoveryModule = createDiscoveryModule(client);
    const analyticsModule = createAnalyticsModule(client);
    const conformanceModule = createConformanceModule(client);
    const aiModule = createAIModule(client);

    return {
      logs: logsModule,
      discovery: discoveryModule,
      analytics: analyticsModule,
      conformance: conformanceModule,
      ai: aiModule,
      // Visualization is an alias to discovery.buildDFG for backward compatibility
      visualization: {
        getDFG: (logId: string) => discoveryModule.buildDFG(logId),
      },
    };
  }, [baseUrl, memoizedGetAuthToken]);

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

// Re-export types for convenience
export type { ProcessMiningSdk };
