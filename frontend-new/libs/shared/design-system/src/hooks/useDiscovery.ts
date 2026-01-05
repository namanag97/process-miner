/**
 * Discovery Hooks - React Query hooks for process discovery and visualization
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSDK } from '../context/SDKContext';
import { queryKeys } from '../api/queryKeys';
import { toast } from '../utils';
import type { DFGOptions, VariantOptions } from '../api/modules/discovery';

/**
 * Get DFG (Directly Follows Graph) for a process
 */
export function useDFG(datasetId: string, options?: DFGOptions) {
  const sdk = useSDK();

  return useQuery({
    queryKey: queryKeys.dfg.data(datasetId, options),
    queryFn: () => sdk.discovery.buildDFG(datasetId, options),
    enabled: !!datasetId,
    staleTime: 10 * 60 * 1000, // 10 minutes - DFG is expensive to compute
  });
}

/**
 * Get process variants
 */
export function useVariants(datasetId: string, options?: VariantOptions) {
  const sdk = useSDK();

  return useQuery({
    queryKey: queryKeys.variants.list(datasetId, options as Parameters<typeof queryKeys.variants.list>[1]),
    queryFn: () => sdk.discovery.getVariants(datasetId, options),
    enabled: !!datasetId,
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Get activity details for a process
 */
export function useActivities(datasetId: string, sortBy?: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: queryKeys.activities.list(datasetId),
    queryFn: () => sdk.discovery.getActivities(datasetId, sortBy),
    enabled: !!datasetId,
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Discover a process model (run miner)
 */
export function useDiscoverProcess() {
  const sdk = useSDK();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (options: { datasetId: string; minerType?: string; modelName?: string }) =>
      sdk.discovery.discover(options),
    onSuccess: (_result, variables) => {
      // Invalidate DFG to show new model
      queryClient.invalidateQueries({ queryKey: queryKeys.dfg.data(variables.datasetId) });
      toast.success('Process model discovered successfully');
    },
    onError: (error: Error) => {
      toast.error(`Discovery failed: ${error.message}`);
    },
  });
}

/**
 * Combined hook for all explorer data (DFG, variants, activities)
 * Fetches in parallel for better performance
 */
export function useExplorerData(datasetId: string, options?: { includePerformance?: boolean }) {
  const dfgQuery = useDFG(datasetId, { includePerformance: options?.includePerformance });
  const variantsQuery = useVariants(datasetId);
  const activitiesQuery = useActivities(datasetId);

  return {
    dfg: dfgQuery.data,
    variants: variantsQuery.data,
    activities: activitiesQuery.data,
    isLoading: dfgQuery.isLoading || variantsQuery.isLoading || activitiesQuery.isLoading,
    isError: dfgQuery.isError || variantsQuery.isError || activitiesQuery.isError,
    error: dfgQuery.error || variantsQuery.error || activitiesQuery.error,
    refetch: () => {
      dfgQuery.refetch();
      variantsQuery.refetch();
      activitiesQuery.refetch();
    },
  };
}
