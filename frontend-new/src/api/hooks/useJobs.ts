/**
 * Jobs Hooks
 *
 * TanStack Query hooks for job operations.
 * Uses normalized entity store for consistent job data across the app.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sdk } from '../sdk';
import { queryKeys } from './queryKeys';
import {
    useEntityStore,
    useJobsById,
    useJob as useJobFromStore,
    transformJob,
} from '@/stores';

// ============================================
// Query Hooks
// ============================================

/**
 * Job list query result with pagination metadata
 */
export interface JobListResult {
    ids: string[];
    total: number;
    page: number;
    pageSize: number;
    pages: number;
}

/**
 * Fetch list of jobs
 * Normalizes response into entity store, returns IDs
 */
export function useJobs(params?: { status?: string; type?: string; page?: number; pageSize?: number }) {
    const setJobs = useEntityStore((s) => s.setJobs);

    const query = useQuery({
        queryKey: queryKeys.jobs.list(params),
        queryFn: async (): Promise<JobListResult> => {
            const response = await sdk.jobs.list(params) as {
                items: Array<{ id: string }>;
                total: number;
                page: number;
                page_size: number;
                pages: number;
            };
            // Normalize: store jobs in entity store
            const normalized = response.items.map((item: unknown) => transformJob(item));
            setJobs(normalized);
            // Return IDs and pagination metadata
            return {
                ids: response.items.map((j: { id: string }) => j.id),
                total: response.total,
                page: response.page,
                pageSize: response.page_size,
                pages: response.pages,
            };
        },
    });

    // Select entities from store using IDs
    const jobs = useJobsById(query.data?.ids ?? []);

    return {
        ...query,
        data: jobs,
        // Expose pagination metadata
        pagination: query.data
            ? {
                  total: query.data.total,
                  page: query.data.page,
                  pageSize: query.data.pageSize,
                  pages: query.data.pages,
              }
            : undefined,
    };
}

/**
 * Fetch single job by ID
 * Normalizes response into entity store
 */
export function useJob(jobId: string | null) {
    const setJob = useEntityStore((s) => s.setJob);

    useQuery({
        queryKey: queryKeys.jobs.detail(jobId ?? ''),
        queryFn: async () => {
            const response = await sdk.jobs.get(jobId!);
            // Normalize: store job in entity store
            const normalized = transformJob(response);
            setJob(normalized);
            return response.id;
        },
        enabled: !!jobId,
    });

    // Select from entity store
    return useJobFromStore(jobId);
}

// ============================================
// Mutation Hooks
// ============================================

/**
 * Cancel a running job
 * Updates entity store with optimistic update
 */
export function useCancelJob() {
    const queryClient = useQueryClient();
    const updateJob = useEntityStore((s) => s.updateJob);

    return useMutation({
        mutationFn: (jobId: string) => sdk.jobs.cancel(jobId),
        // Optimistic update: set status to cancelled
        onMutate: async (jobId) => {
            const previous = useEntityStore.getState().jobs[jobId];
            updateJob(jobId, { status: 'cancelled' });
            return { previous, jobId };
        },
        onSuccess: (_data, jobId) => {
            // Update from server response if needed
            // Invalidate the job detail for fresh data
            queryClient.invalidateQueries({
                queryKey: queryKeys.jobs.detail(jobId),
            });
            // Invalidate the jobs list
            queryClient.invalidateQueries({
                queryKey: queryKeys.jobs.all,
            });
        },
        onError: (_error, _jobId, context) => {
            // Rollback on error
            if (context?.previous) {
                updateJob(context.jobId, { status: context.previous.status });
            }
        },
    });
}

// ============================================
// Re-export types for convenience
// ============================================

export type { NormalizedJob as Job } from '@/stores/entityStore.types';
