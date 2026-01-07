import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { useSDK } from '@/src/shared/design-system';

interface BackendHealthContextType {
  isBackendDown: boolean;
  errorMessage: string | null;
  checkHealth: () => Promise<boolean>;
  setBackendDown: (message: string) => void;
  clearError: () => void;
}

const BackendHealthContext = createContext<BackendHealthContextType | undefined>(undefined);

interface BackendHealthProviderProps {
  children: ReactNode;
}

export function BackendHealthProvider({ children }: BackendHealthProviderProps) {
  const sdk = useSDK();
  const [isBackendDown, setIsBackendDown] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const checkHealth = useCallback(async (): Promise<boolean> => {
    try {
      const isHealthy = await sdk.checkHealth();
      if (isHealthy) {
        setIsBackendDown(false);
        setErrorMessage(null);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }, [sdk]);

  const setBackendDown = useCallback((message: string) => {
    setIsBackendDown(true);
    setErrorMessage(message);
  }, []);

  const clearError = useCallback(() => {
    setIsBackendDown(false);
    setErrorMessage(null);
  }, []);

  // Auto-retry health check periodically when backend is down
  useEffect(() => {
    if (!isBackendDown) return;

    const interval = setInterval(async () => {
      const isHealthy = await checkHealth();
      if (isHealthy) {
        clearInterval(interval);
      }
    }, 30000); // Retry every 30 seconds

    return () => clearInterval(interval);
  }, [isBackendDown, checkHealth]);

  return (
    <BackendHealthContext.Provider
      value={{
        isBackendDown,
        errorMessage,
        checkHealth,
        setBackendDown,
        clearError,
      }}
    >
      {children}
    </BackendHealthContext.Provider>
  );
}

export function useBackendHealth() {
  const context = useContext(BackendHealthContext);
  if (context === undefined) {
    throw new Error('useBackendHealth must be used within a BackendHealthProvider');
  }
  return context;
}

export default BackendHealthContext;
