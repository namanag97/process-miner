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
export function useDFG(logId: string, options?: DFGOptions) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.dfg.data(logId, options),
    queryFn: () => sdk.discovery.buildDFG(logId, options),
    enabled: !!logId,
    staleTime: 10 * 60 * 1000, // 10 minutes - DFG is expensive to compute
  });
}

/**
 * Get process variants
 */
export function useVariants(logId: string, options?: VariantOptions) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.variants.list(logId, options as Parameters<typeof queryKeys.variants.list>[1]),
    queryFn: () => sdk.discovery.getVariants(logId, options),
    enabled: !!logId,
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Get activity details for a process
 */
export function useActivities(logId: string, sortBy?: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.activities.list(logId),
    queryFn: () => sdk.discovery.getActivities(logId, sortBy),
    enabled: !!logId,
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
    mutationFn: (options: { logId: string; minerType?: string; modelName?: string }) =>
      sdk.discovery.discover(options),
    onSuccess: (result, variables) => {
      // Invalidate DFG to show new model
      queryClient.invalidateQueries({ queryKey: queryKeys.dfg.data(variables.logId) });
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
export function useExplorerData(logId: string, options?: { includePerformance?: boolean }) {
  const dfgQuery = useDFG(logId, { includePerformance: options?.includePerformance });
  const variantsQuery = useVariants(logId);
  const activitiesQuery = useActivities(logId);
  
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
