/**
 * Analytics Feature Hooks
 *
 * Re-exports and custom hooks for analytics feature.
 */

import { createQueryHook } from '../../../core/hooks/createFeatureHook';

// ============================================
// Query Hooks
// ============================================

/**
 * Hook to fetch performance analytics data
 */
export const useAnalyticsPerformance = createQueryHook({
  queryKey: (logId: string) => ['analytics', 'performance', logId],
  queryFn: async (sdk, logId: string) => {
    const result = await sdk.analytics.getPerformance(logId);
    return result;
  },
  enabled: (logId: string) => !!logId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch rework analytics data
 */
export const useAnalyticsRework = createQueryHook({
  queryKey: (logId: string) => ['analytics', 'rework', logId],
  queryFn: async (sdk, logId: string) => {
    const result = await sdk.analytics.getRework(logId);
    return result;
  },
  enabled: (logId: string) => !!logId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch event logs list
 */
export const useEventLogs = createQueryHook<
  { items: Array<{ id: string; name: string; totalCases: number; totalEvents: number }>; total: number },
  { pageSize?: number } | undefined
>({
  queryKey: (options) => ['processes', 'list', options],
  queryFn: async (sdk, options) => {
    const result = await sdk.processes.list({ pageSize: options?.pageSize ?? 50 });
    return result;
  },
  staleTime: 2 * 60 * 1000,
});
