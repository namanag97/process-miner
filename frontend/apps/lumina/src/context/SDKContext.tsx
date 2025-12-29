import React, { createContext, useContext, useMemo } from 'react';
import { ProcessMiningSdk } from 'process-mining-sdk';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

interface SDKContextValue {
  sdk: ProcessMiningSdk;
}

const SDKContext = createContext<SDKContextValue | null>(null);

// Query client with sensible defaults for enterprise app
const queryClient = new QueryClient({
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

export const SDKProvider: React.FC<SDKProviderProps> = ({
  children,
  baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001',
}) => {
  const sdk = useMemo(() => {
    return new ProcessMiningSdk({ baseUrl });
  }, [baseUrl]);

  return (
    <SDKContext.Provider value={{ sdk }}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </SDKContext.Provider>
  );
};

export const useSDK = (): ProcessMiningSdk => {
  const context = useContext(SDKContext);
  if (!context) {
    throw new Error('useSDK must be used within an SDKProvider');
  }
  return context.sdk;
};

export { queryClient };
