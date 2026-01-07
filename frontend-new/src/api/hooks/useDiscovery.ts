/**
 * Discovery Hooks
 *
 * TanStack Query hooks for process discovery operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useCallback, useRef } from 'react';
import { sdk, type DiscoveryRequest, type Job } from '../sdk';
import { queryKeys } from './queryKeys';

// ============================================
// Query Hooks
// ============================================

/**
 * Fetch DFG (Directly-Follows Graph) for a dataset
 */
export function useDFG(datasetId: string | null, options?: { includePerformance?: boolean }) {
    return useQuery({
        queryKey: queryKeys.discovery.dfg(datasetId ?? '', options),
        queryFn: () => sdk.discovery.buildDFG(datasetId!, options),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000, // 5 minutes
    });
}

/**
 * Fetch variants for a dataset
 */
export function useVariants(datasetId: string | null, options?: { topN?: number }) {
    return useQuery({
        queryKey: queryKeys.discovery.variants(datasetId ?? '', options),
        queryFn: () => sdk.discovery.getVariants(datasetId!, options),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Fetch activity statistics for a dataset
 */
export function useActivities(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.discovery.activities(datasetId ?? ''),
        queryFn: () => sdk.discovery.getActivityStats(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Fetch unified explorer data (DFG, variants, activities, statistics)
 */
export function useExplorerData(
    datasetId: string | null,
    options?: {
        includePerformance?: boolean;
        includeComplexity?: boolean;
        topVariants?: number;
    }
) {
    return useQuery({
        queryKey: queryKeys.discovery.explorer(datasetId ?? '', options),
        queryFn: () => sdk.discovery.getExplorerData(datasetId!, options),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Fetch discovered models for a dataset
 */
export function useDiscoveredModels(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.discovery.models(datasetId ?? ''),
        queryFn: () => sdk.discovery.listModels(datasetId!),
        enabled: !!datasetId,
    });
}

/**
 * Fetch a specific process model
 */
export function useProcessModel(modelId: string | null) {
    return useQuery({
        queryKey: queryKeys.discovery.model(modelId ?? ''),
        queryFn: () => sdk.discovery.getModel(modelId!),
        enabled: !!modelId,
    });
}

/**
 * Fetch analysis metadata (available algorithms, etc.)
 */
export function useAnalysisMetadata() {
    return useQuery({
        queryKey: queryKeys.analyses.metadata(),
        queryFn: () => sdk.analyses.getMetadata(),
        staleTime: 10 * 60 * 1000, // 10 minutes - rarely changes
    });
}

// ============================================
// Mutation Hooks
// ============================================

/**
 * Trigger process discovery
 */
export function useDiscoveryMutation() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (request: DiscoveryRequest) => sdk.discovery.discover(request),
        onSuccess: (_data, variables) => {
            // Invalidate models list after discovery completes
            queryClient.invalidateQueries({
                queryKey: queryKeys.discovery.models(variables.datasetId),
            });
        },
    });
}

// ============================================
// Job Polling Hook
// ============================================

interface UseJobStatusOptions {
    pollInterval?: number;
    enabled?: boolean;
    onComplete?: (job: Job) => void;
    onError?: (error: Error) => void;
}

/**
 * Poll job status with auto-stop on completion
 */
export function useJobStatus(jobId: string | null, options: UseJobStatusOptions = {}) {
    const { pollInterval = 2000, enabled = true, onComplete, onError } = options;

    const [isPolling, setIsPolling] = useState(true);
    const onCompleteRef = useRef(onComplete);
    const onErrorRef = useRef(onError);

    // Update refs to avoid stale closures
    useEffect(() => {
        onCompleteRef.current = onComplete;
        onErrorRef.current = onError;
    }, [onComplete, onError]);

    const query = useQuery({
        queryKey: queryKeys.jobs.detail(jobId ?? ''),
        queryFn: () => sdk.jobs.get(jobId!),
        enabled: enabled && !!jobId && isPolling,
        refetchInterval: isPolling ? pollInterval : false,
    });

    // Handle completion/failure
    useEffect(() => {
        if (query.data) {
            const { status } = query.data;
            if (status === 'completed' || status === 'failed' || status === 'cancelled') {
                setIsPolling(false);

                if (status === 'completed') {
                    onCompleteRef.current?.(query.data);
                } else if (status === 'failed') {
                    onErrorRef.current?.(new Error(query.data.error || 'Job failed'));
                }
            }
        }
    }, [query.data]);

    // Stop polling on error
    useEffect(() => {
        if (query.error) {
            setIsPolling(false);
            onErrorRef.current?.(query.error as Error);
        }
    }, [query.error]);

    // Reset polling when job ID changes
    useEffect(() => {
        if (jobId) {
            setIsPolling(true);
        }
    }, [jobId]);

    const stopPolling = useCallback(() => {
        setIsPolling(false);
    }, []);

    return {
        ...query,
        isPolling,
        stopPolling,
    };
}
