/**
 * Explorer Feature Hooks
 *
 * Data fetching hooks using the createFeatureHook factory.
 */

import { queryKeys } from '@lumina/design-system';
import { createQueryHook } from '../../../core/hooks/createFeatureHook';

// ============================================
// Query Hooks
// ============================================

/**
 * Hook to fetch DFG (Directly-Follows Graph) for a log
 */
export const useDFG = createQueryHook({
  queryKey: ({ logId, options }: { logId: string; options?: { includePerformance?: boolean } }) =>
    queryKeys.dfg.data(logId, options as any),
  queryFn: async (sdk, { logId, options }: { logId: string; options?: { includePerformance?: boolean } }) => {
    const result = await sdk.discovery.buildDFG(logId, {
      includePerformance: options?.includePerformance ?? true,
    });
    return result;
  },
  enabled: ({ logId }: { logId: string }) => !!logId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch variants for a log
 */
export const useVariants = createQueryHook({
  queryKey: ({ logId, options }: { logId: string; options?: { topN?: number } }) =>
    queryKeys.variants.list(logId, options as any),
  queryFn: async (sdk, { logId, options }: { logId: string; options?: { topN?: number } }) => {
    const result = await sdk.discovery.getVariants(logId, {
      topN: options?.topN ?? 50,
    });
    return result;
  },
  enabled: ({ logId }: { logId: string }) => !!logId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch activities for a log
 */
export const useActivities = createQueryHook({
  queryKey: (logId: string) => queryKeys.activities.list(logId),
  queryFn: async (sdk, logId: string) => {
    // Use DFG to get activity information since getActivityStats may not exist
    const dfg = await sdk.discovery.buildDFG(logId);
    // Transform nodes to activity details
    return dfg.nodes.map((node: { id: string; label: string; frequency: number; isStart?: boolean; isEnd?: boolean }) => ({
      id: node.id,
      name: node.label,
      frequency: node.frequency,
      frequencyPercent: 0,
      avgDuration: null,
      minDuration: null,
      maxDuration: null,
      isStart: node.isStart || false,
      isEnd: node.isEnd || false,
      resources: [],
    }));
  },
  enabled: (logId: string) => !!logId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch log details
 */
export const useLogDetail = createQueryHook({
  queryKey: (logId: string) => queryKeys.processes.detail(logId),
  queryFn: async (sdk, logId: string) => {
    const result = await sdk.processes.get(logId);
    return result;
  },
  enabled: (logId: string) => !!logId,
  staleTime: 2 * 60 * 1000,
});

/**
 * Hook to fetch event logs list for explorer index
 */
export const useEventLogsList = createQueryHook<
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
