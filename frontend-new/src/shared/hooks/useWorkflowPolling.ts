/**
 * Workflow Polling Hook
 * 
 * Higher-level hook wrapping generated SDK for Temporal workflow status polling.
 * Automatically stops polling when workflow completes or fails.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
    useGetWorkflowApiV1WorkflowsWorkflowIdGet,
    useGetWorkflowTemporalStatusApiV1WorkflowsWorkflowIdStatusGet,
} from '@/src/api/generated';

export type WorkflowStatus =
    | 'pending'
    | 'running'
    | 'completed'
    | 'failed'
    | 'cancelled'
    | 'timed_out';

export interface WorkflowProgress {
    /** Workflow ID */
    workflowId: string;
    /** Current status */
    status: WorkflowStatus;
    /** Progress percentage (0-100) */
    progressPercent: number;
    /** Human-readable current step */
    currentStep: string | null;
    /** Error message if failed */
    errorMessage: string | null;
    /** Whether workflow is still in progress */
    isActive: boolean;
    /** Whether workflow completed successfully */
    isComplete: boolean;
    /** Whether workflow failed */
    isFailed: boolean;
    /** Refetch function */
    refetch: () => void;
}

const TERMINAL_STATUSES: WorkflowStatus[] = ['completed', 'failed', 'cancelled', 'timed_out'];

/**
 * Poll workflow status with automatic stop on completion.
 * 
 * @param workflowId - Workflow ID to track, null to disable
 * @param pollingIntervalMs - Polling interval in ms (default 1000)
 * @returns Workflow progress state
 * 
 * @example
 * ```tsx
 * const { isComplete, progressPercent, currentStep } = useWorkflowPolling(workflowId);
 * 
 * if (isComplete) {
 *   // Workflow finished, fetch results
 * }
 * ```
 */
export function useWorkflowPolling(
    workflowId: string | null,
    pollingIntervalMs: number = 1000
): WorkflowProgress | null {
    const [shouldPoll, setShouldPoll] = useState(true);

    // Fetch workflow details from database
    const { data: workflow, refetch: refetchWorkflow } = useGetWorkflowApiV1WorkflowsWorkflowIdGet(
        workflowId ?? '',
        {
            query: {
                enabled: !!workflowId && shouldPoll,
                refetchInterval: shouldPoll ? pollingIntervalMs : false,
            },
        }
    );

    // Fetch real-time status from Temporal (more accurate for active workflows)
    const { data: temporalStatus, refetch: refetchTemporal } = useGetWorkflowTemporalStatusApiV1WorkflowsWorkflowIdStatusGet(
        workflowId ?? '',
        {
            query: {
                enabled: !!workflowId && shouldPoll,
                refetchInterval: shouldPoll ? pollingIntervalMs : false,
            },
        }
    );

    // Merge status: prefer Temporal for active workflows, database for terminal states
    const mergedStatus = useMemo(() => {
        if (!workflow && !temporalStatus) return null;

        // Temporal provides more accurate real-time progress
        // Note: Temporal endpoint returns `current_activity`, DB returns `current_step`
        const currentStep = temporalStatus?.current_activity ||
            workflow?.current_step || null;

        // Temporal returns `progress` (0-100), DB returns `progress_percent`
        const progressPercent = (temporalStatus?.progress ??
            temporalStatus?.progress_percent ??
            workflow?.progress_percent ?? 0) as number;

        // Normalize Temporal status (RUNNING -> running, COMPLETED -> completed, etc.)
        const rawStatus = (temporalStatus?.status || workflow?.status || 'pending') as string;
        const normalizedStatus = rawStatus.toLowerCase() as WorkflowStatus;

        const errorMessage = (temporalStatus?.error_message ||
            workflow?.error_message || null) as string | null;

        return { status: normalizedStatus, progressPercent, currentStep, errorMessage };
    }, [workflow, temporalStatus]);

    // Stop polling when terminal status reached
    useEffect(() => {
        if (mergedStatus?.status && TERMINAL_STATUSES.includes(mergedStatus.status)) {
            setShouldPoll(false);
        }
    }, [mergedStatus?.status]);

    // Reset polling when workflowId changes
    useEffect(() => {
        setShouldPoll(true);
    }, [workflowId]);

    const handleRefetch = useCallback(() => {
        setShouldPoll(true);
        refetchWorkflow();
        refetchTemporal();
    }, [refetchWorkflow, refetchTemporal]);

    if (!workflowId || !mergedStatus) {
        return null;
    }

    return {
        workflowId,
        status: mergedStatus.status,
        progressPercent: mergedStatus.progressPercent,
        currentStep: (mergedStatus.currentStep as string | null),
        errorMessage: (mergedStatus.errorMessage as string | null),
        isActive: !TERMINAL_STATUSES.includes(mergedStatus.status),
        isComplete: mergedStatus.status === 'completed',
        isFailed: mergedStatus.status === 'failed',
        refetch: handleRefetch,
    };
}

/**
 * Track multiple workflows simultaneously.
 * 
 * @param workflowIds - Array of workflow IDs to track
 * @returns Map of workflow ID to progress
 */
export function useMultipleWorkflowPolling(
    workflowIds: string[]
): Map<string, WorkflowProgress> {
    const results = new Map<string, WorkflowProgress>();

    // Note: This is a simplified implementation.
    // For production, consider using React Query's useQueries for better batching.
    workflowIds.forEach((id) => {
        // eslint-disable-next-line react-hooks/rules-of-hooks
        const progress = useWorkflowPolling(id);
        if (progress) {
            results.set(id, progress);
        }
    });

    return results;
}

export default useWorkflowPolling;
