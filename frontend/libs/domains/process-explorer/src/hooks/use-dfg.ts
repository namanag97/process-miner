/**
 * DFG (Directly-Follows Graph) Hooks - React Query hooks for process visualization
 */
import { useQuery } from '@tanstack/react-query';
import { useSDK } from '@lumina/design-system';
import type { DFGResponse } from 'process-mining-sdk';

// Query key factory for visualization
export const visualizationKeys = {
  all: ['visualization'] as const,
  dfg: (logId: string) => [...visualizationKeys.all, 'dfg', logId] as const,
  petriNet: (modelId: string) => [...visualizationKeys.all, 'petri', modelId] as const,
  footprints: (logId: string) => [...visualizationKeys.all, 'footprints', logId] as const,
};

/**
 * Fetch DFG (Directly-Follows Graph) for a log
 */
export function useDFG(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: visualizationKeys.dfg(logId),
    queryFn: () => sdk.visualization.getDFG(logId),
    enabled: !!logId,
    staleTime: 10 * 60 * 1000, // 10 minutes - DFG doesn't change often
  });
}

/**
 * Fetch Petri Net for a model
 */
export function usePetriNet(modelId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: visualizationKeys.petriNet(modelId),
    queryFn: () => sdk.visualization.getPetriNet(modelId),
    enabled: !!modelId,
    staleTime: Infinity, // Models don't change
  });
}

/**
 * Fetch behavioral footprints for a log
 */
export function useFootprints(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: visualizationKeys.footprints(logId),
    queryFn: () => sdk.visualization.getFootprints(logId),
    enabled: !!logId,
    staleTime: 10 * 60 * 1000,
  });
}
