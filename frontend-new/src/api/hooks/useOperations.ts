/**
 * Operations Hooks - Unified Temporal Operations API
 *
 * TanStack Query hooks for the new Temporal-native operations endpoint.
 * This replaces dual-polling of /jobs and /workflows endpoints.
 *
 * UPDATED: Now uses adaptive polling with visibility detection and error backoff.
 *
 * Use these hooks for v2 Temporal workflows. Legacy jobs should still use useJobs.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useCallback, useRef } from 'react';
import { queryKeys } from './queryKeys';
import apiClient from '../client';
import { useAdaptivePolling } from '@/hooks';

const API_PREFIX = '/api/v1';

// ============================================
// Types
// ============================================

export interface OperationStatus {
    workflow_id: string;
    status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'TIMED_OUT';
    progress: number;
    current_step: string | null;
    started_at: string | null;
    completed_at: string | null;
    error_message: string | null;
    entity_type: string | null;
    entity_id: string | null;
    operation_type: string | null;
}

export interface OperationListResponse {
    items: OperationStatus[];
    total: number;
}

export interface OperationResult {
    workflow_id: string;
    status: string;
    result: Record<string, unknown>;
}

// Terminal statuses for operations
const TERMINAL_STATUSES = ['COMPLETED', 'FAILED', 'CANCELLED', 'TIMED_OUT'];

// ============================================
// SDK Functions
// ============================================

const operationsApi = {
    get: async (workflowId: string): Promise<OperationStatus> => {
        const { data } = await apiClient.get(`${API_PREFIX}/operations/${workflowId}`);
        return data;
    },

    list: async (params?: {
        entity_type?: string;
        entity_id?: string;
        status?: string;
        limit?: number;
        offset?: number;
    }): Promise<OperationListResponse> => {
        const { data } = await apiClient.get(`${API_PREFIX}/operations`, { params });
        return data;
    },

    cancel: async (workflowId: string): Promise<{ workflow_id: string; status: string }> => {
        const { data } = await apiClient.post(`${API_PREFIX}/operations/${workflowId}/cancel`);
        return data;
    },

    getResult: async (workflowId: string): Promise<OperationResult> => {
        const { data } = await apiClient.get(`${API_PREFIX}/operations/${workflowId}/result`);
        return data;
    },
};

// ============================================
// Query Hooks
// ============================================

/**
 * Fetch operation status by workflow ID with adaptive polling.
 *
 * Features:
 * - Adaptive polling (fast at start, slower over time)
 * - Pauses when browser tab is hidden
 * - Error backoff on failures
 * - Auto-stops on terminal states
 */
export function useOperationStatus(
    workflowId: string | null,
    options?: {
        enabled?: boolean;
        /** @deprecated Use adaptive intervals instead */
        refetchInterval?: number | false;
    }
) {
    const isTerminal = useCallback((data: OperationStatus): boolean => {
        return TERMINAL_STATUSES.includes(data.status);
    }, []);

    return useAdaptivePolling<OperationStatus, Error>({
        queryKey: [...queryKeys.jobs.all, 'operations', workflowId],
        queryFn: () => operationsApi.get(workflowId!),
        isTerminal,
        enabled: !!workflowId && (options?.enabled ?? true),
        // Adaptive intervals: 2s -> 5s -> 10s -> 30s
        initialInterval: 2000,
        normalInterval: 5000,
        slowInterval: 10000,
        longRunningInterval: 30000,
        staleTime: 1000,
    });
}

/**
 * Fetch list of operations.
 */
export function useOperations(params?: {
    entity_type?: string;
    entity_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
}) {
    return useQuery({
        queryKey: [...queryKeys.jobs.all, 'operations', 'list', params],
        queryFn: () => operationsApi.list(params),
    });
}

/**
 * Fetch operation result (for completed operations).
 */
export function useOperationResult(workflowId: string | null) {
    return useQuery({
        queryKey: [...queryKeys.jobs.all, 'operations', workflowId, 'result'],
        queryFn: () => operationsApi.getResult(workflowId!),
        enabled: !!workflowId,
    });
}

// ============================================
// Polling Hook (similar to useJobStatus)
// ============================================

export interface UseOperationPollingOptions {
    /** @deprecated Interval is now adaptive. Ignored. */
    pollingInterval?: number;
    onComplete?: (operation: OperationStatus) => void;
    onError?: (operation: OperationStatus) => void;
    enabled?: boolean;
    // Adaptive interval overrides
    initialInterval?: number;
    normalInterval?: number;
    slowInterval?: number;
    longRunningInterval?: number;
}

export interface UseOperationPollingResult {
    data: OperationStatus | undefined;
    isLoading: boolean;
    isFetching: boolean;
    error: Error | null;
    isError: boolean;
    refetch: () => Promise<unknown>;
    isPolling: boolean;
    isComplete: boolean;
    isFailed: boolean;
    progress: number;
    currentStep: string | null;
    stopPolling: () => void;
    resumePolling: () => void;
    errorCount: number;
    isVisible: boolean;
    elapsedTime: number;
    currentInterval: number | null;
}

/**
 * Poll operation status with adaptive intervals until completion or failure.
 *
 * Features:
 * - Adaptive polling (fast at start, slower over time)
 * - Pauses when browser tab is hidden (saves bandwidth)
 * - Error backoff (exponential delay, stops after 5 failures)
 * - Automatically stops on terminal states
 */
export function useOperationPolling(
    workflowId: string | null,
    options: UseOperationPollingOptions = {}
): UseOperationPollingResult {
    const {
        onComplete,
        onError,
        enabled = true,
        initialInterval = 2000,
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

    const isTerminal = useCallback((data: OperationStatus): boolean => {
        return TERMINAL_STATUSES.includes(data.status);
    }, []);

    const result = useAdaptivePolling<OperationStatus, Error>({
        queryKey: [...queryKeys.jobs.all, 'operations', 'polling', workflowId],
        queryFn: () => operationsApi.get(workflowId!),
        isTerminal,
        enabled: enabled && !!workflowId,
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

        if (currentStatus === 'COMPLETED') {
            onCompleteRef.current?.(result.data);
        } else if (['FAILED', 'CANCELLED', 'TIMED_OUT'].includes(currentStatus)) {
            onErrorRef.current?.(result.data);
        }
    }, [result.data]);

    return {
        data: result.data,
        isLoading: result.isLoading,
        isFetching: result.isFetching,
        error: result.error,
        isError: result.isError,
        refetch: result.refetch,
        isPolling: result.isPolling,
        isComplete: result.data?.status === 'COMPLETED',
        isFailed: result.data?.status === 'FAILED' || result.data?.status === 'CANCELLED' || result.data?.status === 'TIMED_OUT',
        progress: result.data?.progress ?? 0,
        currentStep: result.data?.current_step ?? null,
        stopPolling: result.stopPolling,
        resumePolling: result.resumePolling,
        errorCount: result.errorCount,
        isVisible: result.isVisible,
        elapsedTime: result.elapsedTime,
        currentInterval: result.currentInterval,
    };
}

// ============================================
// Mutation Hooks
// ============================================

/**
 * Cancel a running operation.
 */
export function useCancelOperation() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (workflowId: string) => operationsApi.cancel(workflowId),
        onSuccess: (_data, workflowId) => {
            // Invalidate the operation status
            queryClient.invalidateQueries({
                queryKey: [...queryKeys.jobs.all, 'operations', workflowId],
            });
            // Invalidate the operations list
            queryClient.invalidateQueries({
                queryKey: [...queryKeys.jobs.all, 'operations', 'list'],
            });
        },
    });
}
