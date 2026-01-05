import React, { createContext, useContext, useMemo, useCallback, useEffect } from 'react';
import { QueryClient, QueryClientProvider, QueryCache, MutationCache } from '@tanstack/react-query';
import { ApiClient } from '../api/client';
import { logQuery, logMutation } from '../utils/devLogger';
import { configureOpenAPISDK } from '../api/sdk-bridge';
import {
  createProcessesModule,
  createProjectsModule,
  createDiscoveryModule,
  createAnalyticsModule,
  createConformanceModule,
  createAIModule,
  createPredictionsModule,
  createSimulationModule,
  createOrganizationalModule,
  createAuditModule,
  createOCPMModule,
  type ProcessesModule,
  type ProjectsModule,
  type DiscoveryModule,
  type AnalyticsModule,
  type ConformanceModule,
  type AIModule,
  type PredictionsModule,
  type SimulationModule,
  type OrganizationalModule,
  type AuditModule,
  type OCPMModule,
} from '../api/modules';

// SDK type - properly typed with real modules
interface ProcessMiningSdk {
  processes: ProcessesModule;
  projects: ProjectsModule;
  discovery: DiscoveryModule;
  analytics: AnalyticsModule;
  conformance: ConformanceModule;
  ai: AIModule;
  predictions: PredictionsModule;
  simulation: SimulationModule;
  organizational: OrganizationalModule;
  audit: AuditModule;
  ocpm: OCPMModule;
  visualization: {
    getDFG: (logId: string) => Promise<unknown>;
  };
  /** Check backend health */
  checkHealth: () => Promise<boolean>;
  /** Get cached health status */
  isHealthy: () => boolean;
}

// Create SDK context
const SDKContext = createContext<ProcessMiningSdk | null>(null);

// Query cache with logging for all query events
const queryCache = new QueryCache({
  onSuccess: (data, query) => {
    const key = Array.isArray(query.queryKey) ? query.queryKey.join('/') : String(query.queryKey);
    logQuery(key, 'success', {
      dataPreview: typeof data === 'object' ? Object.keys(data as object).slice(0, 5) : typeof data,
      fetchStatus: query.state.fetchStatus,
    });
  },
  onError: (error, query) => {
    const key = Array.isArray(query.queryKey) ? query.queryKey.join('/') : String(query.queryKey);
    logQuery(key, 'error', { error: error instanceof Error ? error.message : String(error) });
  },
});

// Mutation cache with logging for all mutation events
const mutationCache = new MutationCache({
  onSuccess: (data, variables, _context, mutation) => {
    const key = mutation.options.mutationKey
      ? Array.isArray(mutation.options.mutationKey)
        ? mutation.options.mutationKey.join('/')
        : String(mutation.options.mutationKey)
      : 'anonymous';
    logMutation(key, 'success', {
      dataPreview: typeof data === 'object' ? Object.keys(data as object).slice(0, 5) : typeof data,
      variables: typeof variables === 'object' ? Object.keys(variables as object) : typeof variables,
    });
  },
  onError: (error, variables, _context, mutation) => {
    const key = mutation.options.mutationKey
      ? Array.isArray(mutation.options.mutationKey)
        ? mutation.options.mutationKey.join('/')
        : String(mutation.options.mutationKey)
      : 'anonymous';
    logMutation(key, 'error', {
      error: error instanceof Error ? error.message : String(error),
      variables: typeof variables === 'object' ? Object.keys(variables as object) : typeof variables,
    });
  },
  onMutate: (variables, mutation) => {
    const key = mutation.options.mutationKey
      ? Array.isArray(mutation.options.mutationKey)
        ? mutation.options.mutationKey.join('/')
        : String(mutation.options.mutationKey)
      : 'anonymous';
    logMutation(key, 'start', {
      variables: typeof variables === 'object' ? Object.keys(variables as object) : typeof variables,
    });
  },
});

// Query client configuration with logging caches
export const queryClient = new QueryClient({
  queryCache,
  mutationCache,
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

  // Configure the OpenAPI-generated SDK with same config
  useEffect(() => {
    configureOpenAPISDK({
      baseUrl,
      getAuthToken: memoizedGetAuthToken,
    });
  }, [baseUrl, memoizedGetAuthToken]);

  // Create SDK with real API modules
  const sdk = useMemo<ProcessMiningSdk>(() => {
    const client = new ApiClient({
      baseUrl,
      getAuthToken: memoizedGetAuthToken,
    });

    const processesModule = createProcessesModule(client);
    const projectsModule = createProjectsModule(client);
    const discoveryModule = createDiscoveryModule(client);
    const analyticsModule = createAnalyticsModule(client);
    const conformanceModule = createConformanceModule(client);
    const aiModule = createAIModule(client);
    const predictionsModule = createPredictionsModule(client);
    const simulationModule = createSimulationModule(client);
    const organizationalModule = createOrganizationalModule(client);
    const auditModule = createAuditModule(client);
    const ocpmModule = createOCPMModule(client);

    return {
      processes: processesModule,
      projects: projectsModule,
      discovery: discoveryModule,
      analytics: analyticsModule,
      conformance: conformanceModule,
      ai: aiModule,
      predictions: predictionsModule,
      simulation: simulationModule,
      organizational: organizationalModule,
      audit: auditModule,
      ocpm: ocpmModule,
      // Visualization is an alias to discovery.buildDFG for backward compatibility
      visualization: {
        getDFG: (logId: string) => discoveryModule.buildDFG(logId),
      },
      // Health check methods
      checkHealth: () => client.checkHealth(),
      isHealthy: () => client.getHealthStatus(),
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
