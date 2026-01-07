/**
 * AI Feature Hooks
 *
 * Data fetching hooks for AI Assistant, Insights, and Predictions.
 * Uses createFeatureHook factory for standardized patterns.
 */

import { createQueryHook } from '../../../shared/core';
import type { ProcessSummaryData } from '@lumina/design-system';
import type { Predictor } from '@lumina/design-system/api/modules/predictions';

// ============================================
// Types
// ============================================

export interface TrainPredictorRequest {
  targetType: string;
  algorithm?: string;
  outcomeAttribute?: string;
}

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
  queryKey: (datasetId) => ['ai', 'summary', datasetId],
  queryFn: async (sdk, datasetId) => {
    const result = await sdk.analytics.getProcessSummary(datasetId);
    return result;
  },
  enabled: (datasetId) => !!datasetId && datasetId.length > 0,
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch predictors for a process
 * Returns array of Predictor objects from SDK
 */
export const useAIPredictors = createQueryHook<Predictor[], string>({
  queryKey: (datasetId) => ['ai', 'predictors', datasetId],
  queryFn: async (sdk, datasetId) => {
    return sdk.predictions.listPredictors(datasetId);
  },
  enabled: (datasetId) => !!datasetId && datasetId.length > 0,
  staleTime: 5 * 60 * 1000,
});

// ============================================
// Mutation Hooks
// ============================================

// AI Chat mutation hook
export { useSendAIMessage } from '../api/mutations';
export type {
  AIChatMessage,
  AIChatRequest,
  AIChatResponse,
  AIInsight,
} from '../api/mutations';

/**
 * Hook to train a new predictor
 * TODO: Implement train() method in predictions module
 */
// export const useTrainPredictor = createMutationHook<
//   Predictor,
//   { datasetId: string; request: TrainPredictorRequest }
// >({
//   mutationFn: async (sdk, { datasetId, request }) => {
//     return sdk.predictions.train(datasetId, request);
//   },
//   invalidateKeys: (data, { datasetId }) => [['ai', 'predictors', datasetId]],
//   onSuccessMessage: 'Predictor training started successfully',
// });

/**
 * Hook to delete a predictor
 * TODO: Implement delete() method in predictions module
 */
// export const useDeletePredictor = createMutationHook<void, string>({
//   mutationFn: async (sdk, predictorId) => {
//     return sdk.predictions.delete(predictorId);
//   },
//   invalidateKeys: [['ai', 'predictors']], // Invalidate all predictor lists
//   onSuccessMessage: 'Predictor deleted successfully',
// });
