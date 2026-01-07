/**
 * useAdaptivePolling - Smart polling hook with visibility detection and backoff
 *
 * Features:
 * - Adaptive intervals based on elapsed time (fast initially, slower over time)
 * - Pauses when tab is hidden (saves bandwidth)
 * - Exponential backoff on errors
 * - Automatic stop on terminal states
 *
 * Polling Strategy:
 * ┌─────────────────────────────────────────────────┐
 * │ Phase          │ Interval │ Reason              │
 * ├─────────────────────────────────────────────────┤
 * │ Just started   │ 2s       │ Quick feedback      │
 * │ Running 10s+   │ 5s       │ Normal progress     │
 * │ Running 60s+   │ 10s      │ Slow operation      │
 * │ Running 5min+  │ 30s      │ Long running        │
 * │ Tab hidden     │ PAUSE    │ No point polling    │
 * │ Error/timeout  │ Backoff  │ Server might be down│
 * │ Terminal state │ STOP     │ No more changes     │
 * └─────────────────────────────────────────────────┘
 */

import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { useState, useCallback, useEffect, useRef } from 'react';

export interface AdaptivePollingOptions<TData, TError = Error> {
  /** Query key for TanStack Query */
  queryKey: unknown[];
  /** Function to fetch data */
  queryFn: () => Promise<TData>;
  /** Function to determine if polling should stop (terminal state) */
  isTerminal: (data: TData) => boolean;
  /** Enable/disable the query */
  enabled?: boolean;

  // Interval configuration (in ms)
  /** Interval for first 10 seconds (default: 2000ms) */
  initialInterval?: number;
  /** Interval for 10s - 60s (default: 5000ms) */
  normalInterval?: number;
  /** Interval for 60s - 5min (default: 10000ms) */
  slowInterval?: number;
  /** Interval for 5min+ (default: 30000ms) */
  longRunningInterval?: number;

  // Error handling
  /** Max retries before stopping (default: 5) */
  maxRetries?: number;
  /** Backoff multiplier for errors (default: 2) */
  backoffMultiplier?: number;
  /** Max backoff interval (default: 60000ms) */
  maxBackoffInterval?: number;

  // TanStack Query options
  /** Stale time in ms (default: 1000ms) */
  staleTime?: number;
  /** Additional query options */
  queryOptions?: Partial<UseQueryOptions<TData, TError>>;
}

export interface AdaptivePollingResult<TData, TError = Error> {
  /** Query data */
  data: TData | undefined;
  /** Loading state */
  isLoading: boolean;
  /** Fetching state (includes refetches) */
  isFetching: boolean;
  /** Error object */
  error: TError | null;
  /** Whether query has errored */
  isError: boolean;
  /** Whether query was successful */
  isSuccess: boolean;
  /** Whether polling is currently active */
  isPolling: boolean;
  /** Number of consecutive errors */
  errorCount: number;
  /** Current polling interval (or null if stopped) */
  currentInterval: number | null;
  /** Elapsed time since polling started */
  elapsedTime: number;
  /** Whether tab is visible */
  isVisible: boolean;
  /** Force refetch */
  refetch: () => Promise<unknown>;
  /** Manually stop polling */
  stopPolling: () => void;
  /** Manually resume polling */
  resumePolling: () => void;
}

export function useAdaptivePolling<TData, TError = Error>({
  queryKey,
  queryFn,
  isTerminal,
  enabled = true,
  initialInterval = 2000,
  normalInterval = 5000,
  slowInterval = 10000,
  longRunningInterval = 30000,
  maxRetries = 5,
  backoffMultiplier = 2,
  maxBackoffInterval = 60000,
  staleTime = 1000,
  queryOptions,
}: AdaptivePollingOptions<TData, TError>): AdaptivePollingResult<TData, TError> {
  // Track when polling started
  const [startTime] = useState(() => Date.now());
  const [elapsedTime, setElapsedTime] = useState(0);

  // Track errors for backoff
  const [errorCount, setErrorCount] = useState(0);

  // Track tab visibility
  const [isVisible, setIsVisible] = useState(() =>
    typeof document !== 'undefined' ? !document.hidden : true
  );

  // Manual polling control
  const [manualStop, setManualStop] = useState(false);

  // Track if we've reached terminal state
  const isTerminalRef = useRef(false);

  // Update elapsed time periodically
  useEffect(() => {
    if (!enabled || manualStop) return;

    const timer = setInterval(() => {
      setElapsedTime(Date.now() - startTime);
    }, 1000);

    return () => clearInterval(timer);
  }, [enabled, manualStop, startTime]);

  // Track tab visibility changes
  useEffect(() => {
    if (typeof document === 'undefined') return;

    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  // Calculate current interval based on state
  const getInterval = useCallback(
    (data: TData | undefined): number | false => {
      // Stop if manually stopped
      if (manualStop) return false;

      // Stop if we've reached terminal state
      if (data && isTerminal(data)) {
        isTerminalRef.current = true;
        return false;
      }

      // Pause if tab is hidden (save bandwidth)
      if (!isVisible) return false;

      // Backoff on errors
      if (errorCount > 0) {
        if (errorCount >= maxRetries) {
          // Too many errors, stop polling
          return false;
        }
        // Exponential backoff
        const backoffInterval = Math.min(
          initialInterval * Math.pow(backoffMultiplier, errorCount),
          maxBackoffInterval
        );
        return backoffInterval;
      }

      // Adaptive interval based on elapsed time
      const elapsed = Date.now() - startTime;
      if (elapsed < 10000) return initialInterval; // First 10 seconds
      if (elapsed < 60000) return normalInterval; // 10s - 60s
      if (elapsed < 300000) return slowInterval; // 60s - 5min
      return longRunningInterval; // 5min+
    },
    [
      isVisible,
      errorCount,
      manualStop,
      startTime,
      isTerminal,
      initialInterval,
      normalInterval,
      slowInterval,
      longRunningInterval,
      maxRetries,
      backoffMultiplier,
      maxBackoffInterval,
    ]
  );

  // Main query with adaptive polling
  const query = useQuery<TData, TError>({
    queryKey,
    queryFn: async () => {
      try {
        const result = await queryFn();
        // Reset error count on success
        setErrorCount(0);
        return result;
      } catch (error) {
        // Increment error count for backoff
        setErrorCount((c) => c + 1);
        throw error;
      }
    },
    enabled: enabled && !manualStop,
    refetchInterval: (query) => getInterval(query.state.data),
    refetchIntervalInBackground: false, // Never poll when tab is hidden
    retry: false, // We handle retries via interval backoff
    staleTime,
    ...queryOptions,
  });

  // Calculate current interval for display
  const currentInterval = enabled && !manualStop ? getInterval(query.data) || null : null;

  // Control methods
  const stopPolling = useCallback(() => {
    setManualStop(true);
  }, []);

  const resumePolling = useCallback(() => {
    setManualStop(false);
    setErrorCount(0); // Reset errors on manual resume
  }, []);

  return {
    data: query.data,
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    error: query.error,
    isError: query.isError,
    isSuccess: query.isSuccess,
    isPolling: !!currentInterval && !query.isError,
    errorCount,
    currentInterval: typeof currentInterval === 'number' ? currentInterval : null,
    elapsedTime,
    isVisible,
    refetch: query.refetch,
    stopPolling,
    resumePolling,
  };
}
