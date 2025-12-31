/**
 * AI Feature Hooks
 *
 * Data fetching hooks for AI Assistant, Insights, and Predictions.
 * Uses createFeatureHook factory for standardized patterns.
 */

import { createQueryHook } from '../../../core/hooks/createFeatureHook';
import type { ProcessSummaryData } from '@lumina/design-system';
import type { Predictor } from '@lumina/design-system/api/modules/predictions';

// ============================================
// Types
// ============================================

interface ProcessListItem {
  id: string;
  name: string;
  totalCases: number;
  totalActivities: number;
  sourceFormat: string;
}

interface ProcessListResponse {
  items: ProcessListItem[];
  total: number;
}

// ============================================
// Query Hooks
// ============================================

/**
 * Hook to fetch available processes for AI features
 */
export const useAIProcesses = createQueryHook<
  ProcessListResponse,
  { pageSize?: number } | undefined
>({
  queryKey: (options) => ['ai', 'processes', options],
  queryFn: async (sdk, options) => {
    const result = await sdk.processes.list({ pageSize: options?.pageSize ?? 100 });
    return result;
  },
  staleTime: 2 * 60 * 1000,
});

/**
 * Hook to fetch process summary for AI context
 * Provides performance metrics, bottlenecks, and patterns for AI analysis
 */
export const useAIProcessSummary = createQueryHook<ProcessSummaryData, string>({
  queryKey: (logId) => ['ai', 'summary', logId],
  queryFn: async (sdk, logId) => {
    const result = await sdk.analytics.getProcessSummary(logId);
    return result;
  },
  enabled: (logId) => !!logId && logId.length > 0,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch predictors for a process
 * Returns array of Predictor objects from SDK
 */
export const useAIPredictors = createQueryHook<Predictor[], string>({
  queryKey: (logId) => ['ai', 'predictors', logId],
  queryFn: async (sdk, logId) => {
    return sdk.predictions.listPredictors(logId);
  },
  enabled: (logId) => !!logId && logId.length > 0,
  staleTime: 5 * 60 * 1000,
});
