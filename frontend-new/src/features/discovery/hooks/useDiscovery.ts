/**
 * Discovery Feature - API Hooks
 *
 * React Query hooks for discovery operations with proper job polling.
 *
 * UPDATED: Now uses adaptive polling with visibility detection and error backoff.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useCallback, useRef } from 'react';
import {
    sdk,
    Job as SDKJob,
    DiscoveryRequest as SDKDiscoveryRequest,
    DiscoveryResponse as SDKDiscoveryResponse,
} from '@/api/sdk';
import { useAdaptivePolling } from '@/hooks/useAdaptivePolling';
import type { Job, DiscoveryRequest, DiscoveredModel, AnalysisMetadata } from '../types';

// Terminal job statuses
const TERMINAL_STATUSES = ['completed', 'failed', 'cancelled'];

// Convert SDK Job to local Job type
function toLocalJob(sdkJob: SDKJob): Job {
    return {
        id: sdkJob.id,
        jobType: sdkJob.type || sdkJob.jobType || 'unknown',
        status: sdkJob.status as Job['status'],
        progress: sdkJob.progress ?? 0,
        stage: sdkJob.stage,
        entityType: sdkJob.entityType,
        entityId: sdkJob.entityId,
        error: sdkJob.error,
        createdAt: sdkJob.createdAt,
        startedAt: sdkJob.startedAt,
        completedAt: sdkJob.completedAt,
    };
}

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

    return useMutation<SDKDiscoveryResponse, Error, DiscoveryRequest>({
        mutationFn: async (request) => {
            // Cast to SDK type (local type is more permissive)
            return sdk.discovery.discover(request as unknown as SDKDiscoveryRequest);
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
// useJobStatus - Poll job status with adaptive intervals
// ============================================

interface UseJobStatusOptions {
    /** @deprecated Interval is now adaptive. Use initialInterval instead. */
    pollInterval?: number;
    enabled?: boolean;
    onComplete?: (job: Job) => void;
    onError?: (error: Error) => void;
    // Adaptive interval overrides
    initialInterval?: number;
    normalInterval?: number;
    slowInterval?: number;
    longRunningInterval?: number;
}

interface UseJobStatusResult {
    data: Job | undefined;
    isLoading: boolean;
    isFetching: boolean;
    error: Error | null;
    isError: boolean;
    refetch: () => Promise<unknown>;
    isPolling: boolean;
    stopPolling: () => void;
    errorCount: number;
    isVisible: boolean;
    elapsedTime: number;
    currentInterval: number | null;
    resumePolling: () => void;
}

/**
 * Poll job status with adaptive intervals.
 *
 * Features:
 * - Adaptive polling (fast at start, slower over time)
 * - Pauses when browser tab is hidden (saves bandwidth)
 * - Error backoff (slows down if server is unresponsive)
 * - Automatically stops on terminal states
 */
export function useJobStatus(jobId: string | null, options: UseJobStatusOptions = {}): UseJobStatusResult {
    const {
        pollInterval, // deprecated
        enabled = true,
        onComplete,
        onError,
        initialInterval = pollInterval ?? 2000,
        normalInterval = 4000,
        slowInterval = 8000,
        longRunningInterval = 15000,
    } = options;

    const onCompleteRef = useRef(onComplete);
    const onErrorRef = useRef(onError);
    const lastStatusRef = useRef<string | null>(null);

    // Update refs to avoid stale closures
    useEffect(() => {
        onCompleteRef.current = onComplete;
        onErrorRef.current = onError;
    }, [onComplete, onError]);

    const isTerminal = useCallback((job: Job): boolean => {
        return TERMINAL_STATUSES.includes(job.status);
    }, []);

    const result = useAdaptivePolling<Job, Error>({
        queryKey: [...discoveryQueryKeys.job(jobId || '')],
        queryFn: async (): Promise<Job> => {
            if (!jobId) throw new Error('No job ID');
            const sdkJob = await sdk.jobs.get(jobId);
            return toLocalJob(sdkJob);
        },
        isTerminal,
        enabled: enabled && !!jobId,
        initialInterval,
        normalInterval,
        slowInterval,
        longRunningInterval,
    });

    // Handle status changes and callbacks
    useEffect(() => {
        if (!result.data) return;

        const currentStatus = result.data.status;
        const previousStatus = lastStatusRef.current;

        if (currentStatus === previousStatus) return;
        lastStatusRef.current = currentStatus;

        if (currentStatus === 'completed') {
            onCompleteRef.current?.(result.data);
        } else if (currentStatus === 'failed' || currentStatus === 'cancelled') {
            onErrorRef.current?.(new Error(result.data.error || 'Job failed'));
        }
    }, [result.data]);

    // Handle query errors
    useEffect(() => {
        if (result.error) {
            onErrorRef.current?.(result.error);
        }
    }, [result.error]);

    return {
        data: result.data,
        isLoading: result.isLoading,
        isFetching: result.isFetching,
        error: result.error,
        isError: result.isError,
        refetch: result.refetch,
        isPolling: result.isPolling,
        stopPolling: result.stopPolling,
        // Additional adaptive polling info
        errorCount: result.errorCount,
        isVisible: result.isVisible,
        elapsedTime: result.elapsedTime,
        currentInterval: result.currentInterval,
        resumePolling: result.resumePolling,
    };
}

// ============================================
// useDiscoveredModels - List models for dataset
// ============================================

export function useDiscoveredModels(datasetId: string) {
    return useQuery<DiscoveredModel[], Error>({
        queryKey: discoveryQueryKeys.models(datasetId),
        queryFn: async (): Promise<DiscoveredModel[]> => {
            const result = await sdk.discovery.listModels(datasetId);
            return result as DiscoveredModel[];
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
