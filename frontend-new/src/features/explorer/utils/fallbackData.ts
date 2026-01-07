/**
 * Fallback Data Utilities
 *
 * Utilities for gracefully falling back to mock data when backend fails.
 * Includes error logging to DevConsole and determination logic.
 */

import { useMemo, useEffect } from 'react';
import { logError } from '@/src/shared/design-system';

// ============================================
// Error Classification
// ============================================

/**
 * Determines if an error should trigger fallback to mock data
 */
export function shouldUseFallback(error: unknown): boolean {
  if (!error) return false;

  const errorMessage = error instanceof Error ? error.message : String(error);
  const lowerMessage = errorMessage.toLowerCase();

  // Network errors
  if (
    lowerMessage.includes('network') ||
    lowerMessage.includes('failed to fetch') ||
    lowerMessage.includes('unable to reach') ||
    lowerMessage.includes('timeout') ||
    lowerMessage.includes('connection')
  ) {
    return true;
  }

  // Server errors (5xx)
  if (
    lowerMessage.includes('500') ||
    lowerMessage.includes('502') ||
    lowerMessage.includes('503') ||
    lowerMessage.includes('504') ||
    lowerMessage.includes('internal server error')
  ) {
    return true;
  }

  // Not found errors (404)
  if (
    lowerMessage.includes('404') ||
    lowerMessage.includes('not found')
  ) {
    return true;
  }

  // Malformed response errors
  if (
    lowerMessage.includes('unexpected token') ||
    lowerMessage.includes('json parse') ||
    lowerMessage.includes('invalid json')
  ) {
    return true;
  }

  return false;
}

// ============================================
// Error Logging
// ============================================

/**
 * Logs data fetching error to DevConsole with context
 */
export function logDataError(
  source: string,
  error: unknown,
  context: {
    usingFallback: boolean;
    hookType?: string;
    datasetId?: string;
    endpoint?: string;
  }
): void {
  const errorObj = error instanceof Error ? error : new Error(String(error));

  logError(source, errorObj, {
    ...context,
    timestamp: new Date().toISOString(),
    fallbackStrategy: context.usingFallback ? 'mock-data' : 'none',
  });

  // Also log to console in development for immediate visibility
  if (process.env.NODE_ENV === 'development') {
    console.error(
      `[${source}] Data fetch failed:`,
      errorObj,
      context.usingFallback ? '→ Using mock data' : '→ No fallback'
    );
  }
}

// ============================================
// Fallback Hook
// ============================================

export interface UseFallbackDataOptions {
  /** Name of the data source for logging */
  source: string;
  /** Hook type for logging context */
  hookType?: string;
  /** Log ID for logging context */
  datasetId?: string;
  /** Endpoint being called */
  endpoint?: string;
  /** Disable fallback even on error */
  disableFallback?: boolean;
}

/**
 * Hook that returns real data if available, otherwise falls back to mock data
 * and logs the error to DevConsole
 *
 * @example
 * const { data, error } = useDFG({ datasetId });
 * const dfgData = useFallbackData(data, error, mockOrderToCashDFG, {
 *   source: 'ExplorerDetailPage',
 *   hookType: 'useDFG',
 *   datasetId,
 * });
 */
export function useFallbackData<T>(
  data: T | undefined,
  error: unknown,
  mockData: T,
  options: UseFallbackDataOptions
): T {
  const { source, hookType, datasetId, endpoint, disableFallback = false } = options;

  // Determine if we should use fallback
  const useFallback = !disableFallback && shouldUseFallback(error);

  // Log error when it occurs
  useEffect(() => {
    if (error && useFallback) {
      logDataError(source, error, {
        usingFallback: true,
        hookType,
        datasetId,
        endpoint,
      });
    } else if (error && !useFallback) {
      // Log error without fallback (e.g., validation errors)
      logDataError(source, error, {
        usingFallback: false,
        hookType,
        datasetId,
        endpoint,
      });
    }
  }, [error, useFallback, source, hookType, datasetId, endpoint]);

  // Return real data if available, otherwise mock data if fallback is enabled
  return useMemo(() => {
    if (data !== undefined) {
      return data;
    }

    if (useFallback) {
      return mockData;
    }

    // If no data and no fallback, return empty/default based on type
    // This handles the case where data is still loading
    return data as T;
  }, [data, useFallback, mockData]);
}

// ============================================
// Error Message Extraction
// ============================================

/**
 * Extracts user-friendly error messages from multiple errors
 */
export function extractErrorMessages(
  errors: Array<unknown | undefined | null>
): string {
  const messages = errors
    .filter((err) => err !== undefined && err !== null)
    .map((err) => {
      if (err instanceof Error) {
        return err.message;
      }
      return String(err);
    });

  if (messages.length === 0) {
    return 'Unknown error occurred';
  }

  if (messages.length === 1) {
    return messages[0];
  }

  // Multiple errors: show first 3
  return messages.slice(0, 3).join(' | ');
}

/**
 * Determines error severity for UI display
 */
export function getErrorSeverity(error: unknown): 'error' | 'warning' | 'info' {
  if (!error) return 'info';

  const message = error instanceof Error ? error.message : String(error);
  const lower = message.toLowerCase();

  // Network/server errors are critical
  if (
    lower.includes('network') ||
    lower.includes('500') ||
    lower.includes('unable to reach')
  ) {
    return 'error';
  }

  // Not found is a warning
  if (lower.includes('404') || lower.includes('not found')) {
    return 'warning';
  }

  // Default to error
  return 'error';
}

// ============================================
// Fallback Status Helper
// ============================================

/**
 * Returns status information about data fallback
 */
export interface FallbackStatus {
  usingFallback: boolean;
  reason: string | null;
  severity: 'error' | 'warning' | 'info';
}

export function getFallbackStatus(
  error: unknown,
  disableFallback = false
): FallbackStatus {
  if (!error) {
    return {
      usingFallback: false,
      reason: null,
      severity: 'info',
    };
  }

  const useFallback = !disableFallback && shouldUseFallback(error);
  const message = error instanceof Error ? error.message : String(error);

  return {
    usingFallback: useFallback,
    reason: message,
    severity: getErrorSeverity(error),
  };
}
