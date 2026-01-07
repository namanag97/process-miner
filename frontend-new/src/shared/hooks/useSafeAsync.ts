/**
 * useSafeAsync - Safe execution of async operations with error handling
 *
 * Provides a way to safely execute async operations (like in event handlers)
 * with built-in error tracking, loading state, and error UI.
 *
 * Usage:
 * ```tsx
 * function UploadButton() {
 *   const { execute, isLoading, error, clearError } = useSafeAsync({
 *     onError: (err) => message.error(`Upload failed: ${err.message}`),
 *   });
 *
 *   const handleUpload = async (file: File) => {
 *     const result = await execute(api.uploadDataset(file));
 *     if (result) {
 *       navigate(`/datasets/${result.id}`);
 *     }
 *   };
 *
 *   return (
 *     <>
 *       <Button loading={isLoading} onClick={handleUpload}>Upload</Button>
 *       {error && <Alert type="error" message={error.message} closable onClose={clearError} />}
 *     </>
 *   );
 * }
 * ```
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import { notification, message } from 'antd';
import { devLog } from '../ui/DevConsole';

// ============================================
// Types
// ============================================

export interface UseSafeAsyncOptions {
  /** Callback when an error occurs */
  onError?: (error: Error) => void;
  /** Callback when operation succeeds */
  onSuccess?: () => void;
  /** Show notification on error */
  showNotification?: boolean;
  /** Custom error message */
  errorMessage?: string;
  /** Feature/component name for logging */
  featureName?: string;
  /** Reset error automatically after this many ms (0 = never) */
  errorTimeout?: number;
}

export interface UseSafeAsyncReturn {
  /** Execute an async operation safely */
  execute: <T>(promise: Promise<T>) => Promise<T | null>;
  /** Current error (null if no error) */
  error: Error | null;
  /** Whether an operation is in progress */
  isLoading: boolean;
  /** Clear the current error */
  clearError: () => void;
  /** Reset all state */
  reset: () => void;
}

// ============================================
// Hook Implementation
// ============================================

export function useSafeAsync(options: UseSafeAsyncOptions = {}): UseSafeAsyncReturn {
  const {
    onError,
    onSuccess,
    showNotification = false,
    errorMessage,
    featureName = 'Async',
    errorTimeout = 0,
  } = options;

  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Track component mount state to prevent state updates after unmount
  const isMountedRef = useRef(true);
  const errorTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (errorTimeoutRef.current) {
        clearTimeout(errorTimeoutRef.current);
      }
    };
  }, []);

  const clearError = useCallback(() => {
    setError(null);
    if (errorTimeoutRef.current) {
      clearTimeout(errorTimeoutRef.current);
      errorTimeoutRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    setError(null);
    setIsLoading(false);
    if (errorTimeoutRef.current) {
      clearTimeout(errorTimeoutRef.current);
      errorTimeoutRef.current = null;
    }
  }, []);

  const execute = useCallback(
    async <T>(promise: Promise<T>): Promise<T | null> => {
      // Clear any previous error
      setError(null);
      setIsLoading(true);

      try {
        const result = await promise;

        // Only update state if still mounted
        if (isMountedRef.current) {
          setIsLoading(false);
          onSuccess?.();
        }

        return result;
      } catch (err) {
        // Convert to Error if needed
        const error = err instanceof Error ? err : new Error(String(err));

        // Only update state if still mounted
        if (isMountedRef.current) {
          setIsLoading(false);
          setError(error);

          // Log to DevConsole
          devLog.error(`SafeAsync:${featureName}`, error.message, {
            featureName,
            error: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString(),
          });

          // Show notification if enabled
          if (showNotification) {
            notification.error({
              message: errorMessage || 'Operation failed',
              description: import.meta.env.DEV ? error.message : 'Please try again.',
              duration: 5,
            });
          }

          // Call error callback
          onError?.(error);

          // Auto-clear error after timeout
          if (errorTimeout > 0) {
            if (errorTimeoutRef.current) {
              clearTimeout(errorTimeoutRef.current);
            }
            errorTimeoutRef.current = setTimeout(() => {
              if (isMountedRef.current) {
                setError(null);
              }
            }, errorTimeout);
          }
        }

        return null;
      }
    },
    [onError, onSuccess, showNotification, errorMessage, featureName, errorTimeout]
  );

  return {
    execute,
    error,
    isLoading,
    clearError,
    reset,
  };
}

// ============================================
// Convenience Variants
// ============================================

/**
 * useSafeAsyncWithToast - Safe async with automatic toast notifications
 */
export function useSafeAsyncWithToast(
  options: Omit<UseSafeAsyncOptions, 'showNotification'> & {
    successMessage?: string;
  } = {}
): UseSafeAsyncReturn & { executeWithToast: <T>(promise: Promise<T>) => Promise<T | null> } {
  const { successMessage, onSuccess, ...restOptions } = options;

  const safeAsync = useSafeAsync({
    ...restOptions,
    showNotification: false,
  });

  const executeWithToast = useCallback(
    async <T>(promise: Promise<T>): Promise<T | null> => {
      const result = await safeAsync.execute(promise);

      if (result !== null) {
        if (successMessage) {
          message.success(successMessage);
        }
        onSuccess?.();
      } else if (safeAsync.error) {
        message.error(options.errorMessage || safeAsync.error.message);
      }

      return result;
    },
    [safeAsync, successMessage, onSuccess, options.errorMessage]
  );

  return {
    ...safeAsync,
    executeWithToast,
  };
}

/**
 * useMutation-like pattern for async operations with optimistic updates
 */
export function useSafeMutation<TData = unknown, TVariables = void>(options: {
  mutationFn: (variables: TVariables) => Promise<TData>;
  onSuccess?: (data: TData, variables: TVariables) => void;
  onError?: (error: Error, variables: TVariables) => void;
  featureName?: string;
  showNotification?: boolean;
  errorMessage?: string;
}) {
  const {
    mutationFn,
    onSuccess,
    onError,
    featureName = 'Mutation',
    showNotification = false,
    errorMessage,
  } = options;

  const [data, setData] = useState<TData | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const isMountedRef = useRef(true);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const mutate = useCallback(
    async (variables: TVariables): Promise<TData | null> => {
      setError(null);
      setIsLoading(true);

      try {
        const result = await mutationFn(variables);

        if (isMountedRef.current) {
          setData(result);
          setIsLoading(false);
          onSuccess?.(result, variables);
        }

        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));

        if (isMountedRef.current) {
          setError(error);
          setIsLoading(false);

          devLog.error(`Mutation:${featureName}`, error.message, {
            featureName,
            error: error.message,
            timestamp: new Date().toISOString(),
          });

          if (showNotification) {
            notification.error({
              message: errorMessage || 'Operation failed',
              description: import.meta.env.DEV ? error.message : 'Please try again.',
            });
          }

          onError?.(error, variables);
        }

        return null;
      }
    },
    [mutationFn, onSuccess, onError, featureName, showNotification, errorMessage]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    mutate,
    data,
    error,
    isLoading,
    reset,
  };
}

export default useSafeAsync;
