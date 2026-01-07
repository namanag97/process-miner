/**
 * Operations Hooks - Unified Temporal Operations API
 *
 * TanStack Query hooks for the new Temporal-native operations endpoint.
 * This replaces dual-polling of /jobs and /workflows endpoints.
 *
 * Use these hooks for v2 Temporal workflows. Legacy jobs should still use useJobs.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from './queryKeys';
import apiClient from '../client';

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
 * Fetch operation status by workflow ID.
 * Polls every 2 seconds while operation is running.
 */
export function useOperationStatus(
    workflowId: string | null,
    options?: {
        enabled?: boolean;
        refetchInterval?: number | false;
    }
) {
    return useQuery({
        queryKey: [...queryKeys.jobs.all, 'operations', workflowId],
        queryFn: () => operationsApi.get(workflowId!),
        enabled: !!workflowId && (options?.enabled ?? true),
        refetchInterval: (query) => {
            if (options?.refetchInterval !== undefined) {
                return options.refetchInterval;
            }
            // Auto-poll while running
            const data = query.state.data;
            if (data && data.status === 'RUNNING') {
                return 2000;
            }
            return false;
        },
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
    pollingInterval?: number;
    onComplete?: (operation: OperationStatus) => void;
    onError?: (operation: OperationStatus) => void;
    enabled?: boolean;
}

/**
 * Poll operation status until completion or failure.
 * Automatically stops polling when operation finishes.
 */
export function useOperationPolling(
    workflowId: string | null,
    options: UseOperationPollingOptions = {}
) {
    const {
        pollingInterval = 2000,
        onComplete,
        onError,
        enabled = true,
    } = options;

    const query = useQuery({
        queryKey: [...queryKeys.jobs.all, 'operations', 'polling', workflowId],
        queryFn: () => operationsApi.get(workflowId!),
        enabled: !!workflowId && enabled,
        refetchInterval: (query) => {
            const data = query.state.data;
            if (!data) return pollingInterval;

            // Stop polling when complete
            if (data.status === 'COMPLETED') {
                onComplete?.(data);
                return false;
            }

            // Stop polling on failure
            if (data.status === 'FAILED' || data.status === 'CANCELLED' || data.status === 'TIMED_OUT') {
                onError?.(data);
                return false;
            }

            // Continue polling
            return pollingInterval;
        },
        staleTime: 500,
    });

    return {
        ...query,
        isPolling: query.data?.status === 'RUNNING' || query.data?.status === 'PENDING',
        isComplete: query.data?.status === 'COMPLETED',
        isFailed: query.data?.status === 'FAILED' || query.data?.status === 'CANCELLED' || query.data?.status === 'TIMED_OUT',
        progress: query.data?.progress ?? 0,
        currentStep: query.data?.current_step,
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
