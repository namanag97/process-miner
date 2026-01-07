/**
 * Explorer Feature Hooks
 *
 * Data fetching hooks using the createFeatureHook factory.
 */

import { queryKeys } from '@lumina/design-system';
import { createQueryHook } from '../../../shared/core';

// ============================================
// Query Hooks
// ============================================

/**
 * Hook to fetch unified explorer data (DFG, variants, activities, statistics)
 * This is the recommended hook for the Process Explorer page
 */
export const useExplorerData = createQueryHook({
  queryKey: ({ datasetId, options }: { datasetId: string; options?: { includePerformance?: boolean; includeComplexity?: boolean; topVariants?: number } }) =>
    queryKeys.explorer.data(datasetId, options as any),
  queryFn: async (sdk, { datasetId, options }: { datasetId: string; options?: { includePerformance?: boolean; includeComplexity?: boolean; topVariants?: number } }) => {
    const result = await sdk.discovery.getExplorerData(datasetId, {
      includePerformance: options?.includePerformance ?? true,
      includeComplexity: options?.includeComplexity ?? true,
      topVariants: options?.topVariants ?? 50,
    });
    return result;
  },
  enabled: ({ datasetId }: { datasetId: string }) => !!datasetId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch DFG (Directly-Follows Graph) for a log
 * @deprecated Use useExplorerData instead for better performance
 */
export const useDFG = createQueryHook({
  queryKey: ({ datasetId, options }: { datasetId: string; options?: { includePerformance?: boolean } }) =>
    queryKeys.dfg.data(datasetId, options as any),
  queryFn: async (sdk, { datasetId, options }: { datasetId: string; options?: { includePerformance?: boolean } }) => {
    const result = await sdk.discovery.buildDFG(datasetId, {
      includePerformance: options?.includePerformance ?? true,
    });
    return result;
  },
  enabled: ({ datasetId }: { datasetId: string }) => !!datasetId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch variants for a log
 * @deprecated Use useExplorerData instead for better performance
 */
export const useVariants = createQueryHook({
  queryKey: ({ datasetId, options }: { datasetId: string; options?: { topN?: number } }) =>
    queryKeys.variants.list(datasetId, options as any),
  queryFn: async (sdk, { datasetId, options }: { datasetId: string; options?: { topN?: number } }) => {
    const result = await sdk.discovery.getVariants(datasetId, {
      topN: options?.topN ?? 50,
    });
    return result;
  },
  enabled: ({ datasetId }: { datasetId: string }) => !!datasetId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch activities for a log
 * @deprecated Use useExplorerData instead for better performance
 */
export const useActivities = createQueryHook({
  queryKey: (datasetId: string) => queryKeys.activities.list(datasetId),
  queryFn: async (sdk, datasetId: string) => {
    // Use DFG to get activity information since getActivityStats may not exist
    const dfg = await sdk.discovery.buildDFG(datasetId);
    // Transform nodes to activity details (matching ActivityDetail type)
    return dfg.nodes.map((node: { id: string; label: string; frequency: number; isStart?: boolean; isEnd?: boolean }) => ({
      id: node.id,
      name: node.label,
      frequency: node.frequency,
      frequencyPercent: 0,
      avgDuration: undefined,
      minDuration: undefined,
      maxDuration: undefined,
      isStartActivity: node.isStart || false,
      isEndActivity: node.isEnd || false,
      resources: [] as string[],
    }));
  },
  enabled: (datasetId: string) => !!datasetId,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch log details
 */
export const useLogDetail = createQueryHook({
  queryKey: (datasetId: string) => queryKeys.processes.detail(datasetId),
  queryFn: async (sdk, datasetId: string) => {
    const result = await sdk.processes.get(datasetId);
    return result;
  },
  enabled: (datasetId: string) => !!datasetId,
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

// Process Graph Hook for CytoscapeCanvas
export { useProcessGraph } from './useProcessGraph';
