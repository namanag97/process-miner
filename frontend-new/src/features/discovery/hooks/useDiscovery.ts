/**
 * Discovery Feature - API Hooks
 * 
 * React Query hooks for discovery operations with proper job polling.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useCallback, useRef } from 'react';
import { sdk } from '@/api/sdk';
import type { Job, DiscoveryRequest, DiscoveryResponse, DiscoveredModel, AnalysisMetadata } from '../types';

// ============================================
// Query Keys
// ============================================

export const discoveryQueryKeys = {
    all: ['discovery'] as const,
    models: (datasetId: string) => ['discovery', 'models', datasetId] as const,
    model: (modelId: string) => ['discovery', 'model', modelId] as const,
    job: (jobId: string) => ['jobs', jobId] as const,
    metadata: () => ['analyses', 'metadata'] as const,
};

// ============================================
// useAnalysisMetadata - Fetch available algorithms
// ============================================

export function useAnalysisMetadata() {
    return useQuery<AnalysisMetadata>({
        queryKey: discoveryQueryKeys.metadata(),
        queryFn: async () => {
            return sdk.analyses.getMetadata();
        },
        staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    });
}

// ============================================
// useDiscoveryMutation - Trigger discovery
// ============================================

export function useDiscoveryMutation() {
    const queryClient = useQueryClient();

    return useMutation<DiscoveryResponse, Error, DiscoveryRequest>({
        mutationFn: async (request) => {
            return sdk.discovery.discover(request);
        },
        onSuccess: (_data, variables) => {
            // Invalidate models list after discovery
            queryClient.invalidateQueries({
                queryKey: discoveryQueryKeys.models(variables.datasetId)
            });
        },
    });
}

// ============================================
// useJobStatus - Poll job status with auto-stop
// ============================================

interface UseJobStatusOptions {
    pollInterval?: number;
    enabled?: boolean;
    onComplete?: (job: Job) => void;
    onError?: (error: Error) => void;
}

export function useJobStatus(jobId: string | null, options: UseJobStatusOptions = {}) {
    const {
        pollInterval = 2000,
        enabled = true,
        onComplete,
        onError
    } = options;

    const [isPolling, setIsPolling] = useState(true);
    const onCompleteRef = useRef(onComplete);
    const onErrorRef = useRef(onError);

    // Update refs to avoid stale closures
    useEffect(() => {
        onCompleteRef.current = onComplete;
        onErrorRef.current = onError;
    }, [onComplete, onError]);

    const query = useQuery<Job>({
        queryKey: discoveryQueryKeys.job(jobId || ''),
        queryFn: async () => {
            if (!jobId) throw new Error('No job ID');
            return sdk.jobs.get(jobId);
        },
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
            onErrorRef.current?.(query.error);
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

// ============================================
// useDiscoveredModels - List models for dataset
// ============================================

export function useDiscoveredModels(datasetId: string) {
    return useQuery<DiscoveredModel[]>({
        queryKey: discoveryQueryKeys.models(datasetId),
        queryFn: async () => {
            return sdk.discovery.listModels(datasetId);
        },
        enabled: !!datasetId,
    });
}

// ============================================
// useModelVisualization - Get model for rendering
// ============================================

export function useModelVisualization(modelId: string) {
    return useQuery({
        queryKey: discoveryQueryKeys.model(modelId),
        queryFn: async () => {
            return sdk.discovery.getModel(modelId);
        },
        enabled: !!modelId,
    });
}
