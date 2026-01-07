/**
 * useQueryWithErrorHandling - TanStack Query wrapper with centralized error handling
 *
 * Provides automatic error notifications and logging for queries.
 * Use this instead of useQuery when you want automatic error feedback to users.
 *
 * Usage:
 * ```tsx
 * const { data, isLoading } = useQueryWithErrorHandling({
 *   queryKey: ['datasets'],
 *   queryFn: () => api.getDatasets(),
 *   errorMessage: 'Failed to load datasets',
 *   showNotification: true, // default
 * });
 * ```
 */
import {
  useQuery,
  UseQueryOptions,
  UseQueryResult,
  QueryKey,
} from '@tanstack/react-query';
import { notification, message } from 'antd';
import { useEffect, useRef } from 'react';
import { devLog } from '../ui/DevConsole';

// ============================================
// Types
// ============================================

export interface UseQueryWithErrorHandlingOptions<
  TQueryFnData = unknown,
  TError = Error,
  TData = TQueryFnData,
  TQueryKey extends QueryKey = QueryKey
> extends Omit<UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>, 'onError'> {
  /** Custom error message to display to the user */
  errorMessage?: string;
  /** Show notification on error (default: true) */
  showNotification?: boolean;
  /** Notification type: 'notification' for persistent, 'message' for toast (default: 'notification') */
  notificationType?: 'notification' | 'message';
  /** Custom error handler callback */
  onError?: (error: TError) => void;
  /** Feature/component name for logging */
  featureName?: string;
  /** Suppress error UI entirely (still logs) */
  suppressErrorUI?: boolean;
}

// ============================================
// Hook Implementation
// ============================================

export function useQueryWithErrorHandling<
  TQueryFnData = unknown,
  TError = Error,
  TData = TQueryFnData,
  TQueryKey extends QueryKey = QueryKey
>(
  options: UseQueryWithErrorHandlingOptions<TQueryFnData, TError, TData, TQueryKey>
): UseQueryResult<TData, TError> {
  const {
    errorMessage = 'Failed to load data',
    showNotification = true,
    notificationType = 'notification',
    onError,
    featureName,
    suppressErrorUI = false,
    ...queryOptions
  } = options;

  // Track if we've shown the error notification to avoid duplicates
  const hasShownErrorRef = useRef(false);

  // Use standard useQuery
  const result = useQuery<TQueryFnData, TError, TData, TQueryKey>(queryOptions);

  // Handle error effects
  useEffect(() => {
    if (result.error && !hasShownErrorRef.current) {
      hasShownErrorRef.current = true;

      // Extract error details
      const error = result.error;
      const errorDetails =
        error instanceof Error
          ? error.message
          : typeof error === 'object' && error !== null
            ? JSON.stringify(error)
            : String(error);

      // Log to DevConsole
      const logContext = featureName || String(queryOptions.queryKey?.[0] || 'Query');
      devLog.error(`Query:${logContext}`, `${errorMessage}: ${errorDetails}`, {
        queryKey: queryOptions.queryKey,
        error: errorDetails,
        timestamp: new Date().toISOString(),
      });

      // Show notification unless suppressed
      if (showNotification && !suppressErrorUI) {
        if (notificationType === 'message') {
          message.error(errorMessage);
        } else {
          notification.error({
            message: errorMessage,
            description:
              import.meta.env.DEV && error instanceof Error
                ? error.message
                : 'Please try again or contact support if the issue persists.',
            duration: 5,
          });
        }
      }

      // Call custom error handler
      onError?.(error);
    }

    // Reset error tracking when query succeeds
    if (result.isSuccess) {
      hasShownErrorRef.current = false;
    }
  }, [
    result.error,
    result.isSuccess,
    errorMessage,
    showNotification,
    notificationType,
    onError,
    featureName,
    suppressErrorUI,
    queryOptions.queryKey,
  ]);

  return result;
}

// ============================================
// Convenience Variants
// ============================================

/**
 * useQueryWithToast - Query with toast-style error messages
 * Less intrusive than notifications, auto-dismisses quickly
 */
export function useQueryWithToast<
  TQueryFnData = unknown,
  TError = Error,
  TData = TQueryFnData,
  TQueryKey extends QueryKey = QueryKey
>(
  options: Omit<
    UseQueryWithErrorHandlingOptions<TQueryFnData, TError, TData, TQueryKey>,
    'notificationType'
  >
): UseQueryResult<TData, TError> {
  return useQueryWithErrorHandling({
    ...options,
    notificationType: 'message',
  });
}

/**
 * useSilentQuery - Query that logs errors but doesn't show UI
 * Use when errors are expected or handled elsewhere
 */
export function useSilentQuery<
  TQueryFnData = unknown,
  TError = Error,
  TData = TQueryFnData,
  TQueryKey extends QueryKey = QueryKey
>(
  options: Omit<
    UseQueryWithErrorHandlingOptions<TQueryFnData, TError, TData, TQueryKey>,
    'showNotification' | 'suppressErrorUI'
  >
): UseQueryResult<TData, TError> {
  return useQueryWithErrorHandling({
    ...options,
    suppressErrorUI: true,
  });
}

export default useQueryWithErrorHandling;
