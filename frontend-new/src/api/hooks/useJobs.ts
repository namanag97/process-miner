/**
 * Jobs Hooks
 *
 * TanStack Query hooks for job operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sdk } from '../sdk';
import { queryKeys } from './queryKeys';

// ============================================
// Query Hooks
// ============================================

/**
 * Fetch list of jobs
 */
export function useJobs(params?: { status?: string; type?: string; page?: number; pageSize?: number }) {
    return useQuery({
        queryKey: queryKeys.jobs.list(params),
        queryFn: () => sdk.jobs.list(params),
    });
}

/**
 * Fetch single job by ID
 */
export function useJob(jobId: string | null) {
    return useQuery({
        queryKey: queryKeys.jobs.detail(jobId ?? ''),
        queryFn: () => sdk.jobs.get(jobId!),
        enabled: !!jobId,
    });
}

// ============================================
// Mutation Hooks
// ============================================

/**
 * Cancel a running job
 */
export function useCancelJob() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (jobId: string) => sdk.jobs.cancel(jobId),
        onSuccess: (_data, jobId) => {
            // Invalidate the job detail
            queryClient.invalidateQueries({
                queryKey: queryKeys.jobs.detail(jobId),
            });
            // Invalidate the jobs list
            queryClient.invalidateQueries({
                queryKey: queryKeys.jobs.all,
            });
        },
    });
}
