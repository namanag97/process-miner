/**
 * Discovery Hooks - React Query hooks for process model discovery
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSDK } from '../../../../apps/lumina/src/context/SDKContext';
import type { DiscoverModelOptions, ProcessModel } from 'process-mining-sdk';

// Query key factory for discovery
export const discoveryKeys = {
  all: ['discovery'] as const,
  miners: () => [...discoveryKeys.all, 'miners'] as const,
  models: (logId: string) => [...discoveryKeys.all, 'models', logId] as const,
  model: (modelId: string) => [...discoveryKeys.all, 'model', modelId] as const,
  quality: (modelId: string) => [...discoveryKeys.all, 'quality', modelId] as const,
};

/**
 * Fetch available mining algorithms
 */
export function useMiners() {
  const sdk = useSDK();

  return useQuery({
    queryKey: discoveryKeys.miners(),
    queryFn: () => sdk.discovery.listMiners(),
    staleTime: Infinity, // Miners list is static
  });
}

/**
 * Discover a process model from an event log
 */
export function useDiscoverModel() {
  const sdk = useSDK();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (options: DiscoverModelOptions) => sdk.discovery.discover(options),
    onSuccess: (result, variables) => {
      // Invalidate models list for the source log
      queryClient.invalidateQueries({ queryKey: discoveryKeys.models(variables.logId) });
    },
  });
}

/**
 * Evaluate model quality metrics
 */
export function useModelQuality(modelId: string, logId?: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: [...discoveryKeys.quality(modelId), logId],
    queryFn: () => sdk.discovery.evaluateQuality(modelId, logId),
    enabled: !!modelId,
  });
}

/**
 * Get detailed DFG from discovery endpoint
 */
export function useDetailedDFG(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: [...discoveryKeys.all, 'dfg-detailed', logId],
    queryFn: () => sdk.discovery.buildDFG(logId),
    enabled: !!logId,
  });
}
