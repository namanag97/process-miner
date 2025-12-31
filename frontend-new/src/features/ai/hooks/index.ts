/**
 * AI Feature Hooks
 *
 * Re-exports and custom hooks for AI feature.
 */

import { createQueryHook } from '../../../core/hooks/createFeatureHook';

// ============================================
// Query Hooks
// ============================================

/**
 * Hook to fetch available processes for AI
 */
export const useAIProcesses = createQueryHook<
  { items: Array<{ id: string; name: string; totalCases: number; totalActivities: number; sourceFormat: string }>; total: number },
  { pageSize?: number } | undefined
>({
  queryKey: (options) => ['ai', 'processes', options],
  queryFn: async (sdk, options) => {
    const result = await sdk.processes.list({ pageSize: options?.pageSize ?? 100 });
    return result;
  },
  staleTime: 2 * 60 * 1000,
});

// Note: Additional AI-specific hooks can be added here
// The predictions module hooks are not yet implemented in SDK
