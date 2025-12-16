/**
 * Analysis API Hooks
 * 
 * React Query hooks for fetching analysis data (DFG, variants, stats).
 */

import { useQuery } from '@tanstack/react-query';
import {
    getDFG,
    getVariants,
    getSummary,
    getFullAnalysis,
    getDeviations,
} from '../client';
import type {
    DFGResponse,
    VariantsResponse,
    DatasetSummary,
    FullAnalysisResponse,
    Deviation,
} from '../types';

// =============================================================================
// Query Keys
// =============================================================================

export const analysisKeys = {
    all: ['analysis'] as const,
    dataset: (datasetId: string) => [...analysisKeys.all, datasetId] as const,
    dfg: (datasetId: string) => [...analysisKeys.dataset(datasetId), 'dfg'] as const,
    variants: (datasetId: string) => [...analysisKeys.dataset(datasetId), 'variants'] as const,
    summary: (datasetId: string) => [...analysisKeys.dataset(datasetId), 'summary'] as const,
    full: (datasetId: string) => [...analysisKeys.dataset(datasetId), 'full'] as const,
    deviations: (datasetId: string) => [...analysisKeys.dataset(datasetId), 'deviations'] as const,
};

// =============================================================================
// Hooks
// =============================================================================

/**
 * Query hook for fetching DFG (Directly-Follows Graph).
 */
export function useDatasetDFG(datasetId: string | null) {
    return useQuery({
        queryKey: datasetId ? analysisKeys.dfg(datasetId) : ['analysis', 'none'],
        queryFn: () => getDFG(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    });
}

/**
 * Query hook for fetching variants with pagination.
 */
export function useDatasetVariants(
    datasetId: string | null,
    options?: { limit?: number; offset?: number }
) {
    const limit = options?.limit ?? 50;
    const offset = options?.offset ?? 0;

    return useQuery({
        queryKey: datasetId
            ? [...analysisKeys.variants(datasetId), { limit, offset }]
            : ['analysis', 'none'],
        queryFn: () => getVariants(datasetId!, limit, offset),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Query hook for fetching dataset summary stats.
 */
export function useDatasetSummary(datasetId: string | null) {
    return useQuery({
        queryKey: datasetId ? analysisKeys.summary(datasetId) : ['analysis', 'none'],
        queryFn: () => getSummary(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Query hook for fetching full analysis (DFG + variants + stats + deviations).
 * This is the most commonly used hook as it returns everything in one call.
 */
export function useFullAnalysis(datasetId: string | null) {
    return useQuery({
        queryKey: datasetId ? analysisKeys.full(datasetId) : ['analysis', 'none'],
        queryFn: () => getFullAnalysis(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Query hook for fetching deviations.
 */
export function useDeviations(datasetId: string | null) {
    return useQuery({
        queryKey: datasetId ? analysisKeys.deviations(datasetId) : ['analysis', 'none'],
        queryFn: () => getDeviations(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}
