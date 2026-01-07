/**
 * Discovery Hooks
 *
 * TanStack Query hooks for process discovery operations.
 * Uses normalized entity store for models and jobs.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useCallback, useRef } from 'react';
import { sdk, type DiscoveryRequest } from '../sdk';
import { queryKeys } from './queryKeys';
import {
    useEntityStore,
    useModelsById,
    useModel as useModelFromStore,
    useJob as useJobFromStore,
    transformModel,
    transformJob,
    type NormalizedJob,
} from '@/stores';

// ============================================
// Query Hooks
// ============================================

/**
 * Fetch DFG (Directly-Follows Graph) for a dataset
 * Note: DFG data is not normalized as it's visualization-specific
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
 * Note: Variants are not normalized as they're query-specific data
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
 * Note: Activity stats are not normalized as they're query-specific data
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
 * Note: Explorer data is not normalized as it's visualization-specific
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
 * Normalizes response into entity store
 * Note: This endpoint returns ProcessModel[] directly, not paginated
 */
export function useDiscoveredModels(datasetId: string | null) {
    const setModels = useEntityStore((s) => s.setModels);

    const query = useQuery({
        queryKey: queryKeys.discovery.models(datasetId ?? ''),
        queryFn: async (): Promise<string[]> => {
            const response = await sdk.discovery.listModels(datasetId!);
            // Response is ProcessModel[] array directly
            const models = Array.isArray(response) ? response : [];
            // Normalize: store models in entity store
            const normalized = models.map((m: unknown) => ({
                ...transformModel(m),
                datasetId: datasetId!, // Ensure FK reference
            }));
            setModels(normalized);
            // Return IDs
            return models.map((m: { id: string }) => m.id);
        },
        enabled: !!datasetId,
    });

    // Select entities from store using IDs
    const models = useModelsById(query.data ?? []);

    return {
        ...query,
        data: models,
    };
}

/**
 * Fetch a specific process model
 * Normalizes response into entity store
 */
export function useProcessModel(modelId: string | null) {
    const setModel = useEntityStore((s) => s.setModel);

    useQuery({
        queryKey: queryKeys.discovery.model(modelId ?? ''),
        queryFn: async () => {
            const response = await sdk.discovery.getModel(modelId!);
            // Normalize: store model
            const normalized = transformModel(response);
            setModel(normalized);
            return response.id;
        },
        enabled: !!modelId,
    });

    // Select from entity store
    return useModelFromStore(modelId);
}

/**
 * Fetch analysis metadata (available algorithms, etc.)
 * Note: Metadata is not normalized as it's configuration data
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
 * Invalidates model cache on success
 */
export function useDiscoveryMutation() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (request: DiscoveryRequest) => sdk.discovery.discover(request),
        onSuccess: (_data, variables) => {
            // Invalidate models list after discovery completes
            // The actual model will be fetched when the list is refetched
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
    onComplete?: (job: NormalizedJob) => void;
    onError?: (error: Error) => void;
}

/**
 * Poll job status with auto-stop on completion
 * Normalizes job data into entity store
 */
export function useJobStatus(jobId: string | null, options: UseJobStatusOptions = {}) {
    const { pollInterval = 2000, enabled = true, onComplete, onError } = options;

    const [isPolling, setIsPolling] = useState(true);
    const onCompleteRef = useRef(onComplete);
    const onErrorRef = useRef(onError);
    const setJob = useEntityStore((s) => s.setJob);

    // Update refs to avoid stale closures
    useEffect(() => {
        onCompleteRef.current = onComplete;
        onErrorRef.current = onError;
    }, [onComplete, onError]);

    const query = useQuery({
        queryKey: queryKeys.jobs.detail(jobId ?? ''),
        queryFn: async () => {
            const response = await sdk.jobs.get(jobId!);
            // Normalize: store job in entity store
            const normalized = transformJob(response);
            setJob(normalized);
            return response.id;
        },
        enabled: enabled && !!jobId && isPolling,
        refetchInterval: isPolling ? pollInterval : false,
    });

    // Select job from entity store
    const job = useJobFromStore(jobId);

    // Handle completion/failure
    useEffect(() => {
        if (job) {
            const { status } = job;
            if (status === 'completed' || status === 'failed' || status === 'cancelled') {
                setIsPolling(false);

                if (status === 'completed') {
                    onCompleteRef.current?.(job);
                } else if (status === 'failed') {
                    onErrorRef.current?.(new Error(job.error || 'Job failed'));
                }
            }
        }
    }, [job]);

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
        data: job,
        isPolling,
        stopPolling,
    };
}

// ============================================
// Re-export types for convenience
// ============================================

export type { NormalizedModel as Model, NormalizedJob as Job } from '@/stores/entityStore.types';
