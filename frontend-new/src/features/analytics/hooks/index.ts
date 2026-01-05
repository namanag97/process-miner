/**
 * Analytics Feature Hooks
 *
 * Re-exports and custom hooks for analytics feature.
 */

import { queryKeys } from '@lumina/design-system';
import { createQueryHook } from '../../../core/hooks/createFeatureHook';

// ============================================
// Query Hooks
// ============================================

/**
 * Hook to fetch performance analytics data
 */
export const useAnalyticsPerformance = createQueryHook({
  queryKey: (datasetId: string) => queryKeys.analytics.performance(datasetId),
  queryFn: async (sdk, datasetId: string) => {
    const result = await sdk.analytics.getPerformance(datasetId);
    return result;
  },
  enabled: (datasetId: string) => !!datasetId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch rework analytics data
 */
export const useAnalyticsRework = createQueryHook({
  queryKey: (datasetId: string) => queryKeys.analytics.rework(datasetId),
  queryFn: async (sdk, datasetId: string) => {
    const result = await sdk.analytics.getRework(datasetId);
    return result;
  },
  enabled: (datasetId: string) => !!datasetId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch event logs list
 */
export const useEventLogs = createQueryHook<
  { items: Array<{ id: string; name: string; totalCases: number; totalEvents: number }>; total: number },
  { pageSize?: number } | undefined
>({
  queryKey: (options) => queryKeys.processes.list(options as any),
  queryFn: async (sdk, options) => {
    const result = await sdk.processes.list({ pageSize: options?.pageSize ?? 50 });
    return result;
  },
  staleTime: 2 * 60 * 1000,
});
