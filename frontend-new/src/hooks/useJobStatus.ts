/**
 * useJobStatus - Smart job status polling with adaptive intervals
 *
 * Features:
 * - Adaptive polling (fast at start, slower over time)
 * - Pauses when tab is hidden
 * - Error backoff
 * - Type-safe job status handling
 * - Callbacks for completion/failure
 *
 * Usage:
 * ```typescript
 * const { data, isPolling, progress } = useJobStatus(jobId, {
 *   onComplete: (job) => message.success('Done!'),
 *   onError: (job) => message.error(job.error),
 * });
 * ```
 */

import { useCallback, useRef, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAdaptivePolling } from './useAdaptivePolling';
import { sdk, Job, JobStatus } from '@/api/sdk';

// Terminal states that should stop polling
const TERMINAL_STATUSES: JobStatus[] = ['completed', 'failed', 'cancelled'];

export interface UseJobStatusOptions {
  /** Enable/disable polling (default: true) */
  enabled?: boolean;
  /** Called when job completes successfully */
  onComplete?: (job: Job) => void;
  /** Called when job fails or is cancelled */
  onError?: (job: Job) => void;
  /** Called on each progress update */
  onProgress?: (job: Job) => void;

  // Custom interval overrides (optional)
  /** Initial interval in ms (default: 1500 for quick start) */
  initialInterval?: number;
  /** Normal interval in ms (default: 3000) */
  normalInterval?: number;
  /** Slow interval in ms (default: 8000) */
  slowInterval?: number;
  /** Long-running interval in ms (default: 15000) */
  longRunningInterval?: number;
}

export interface UseJobStatusResult {
  /** Job data */
  job: Job | undefined;
  /** Loading state */
  isLoading: boolean;
  /** Error object */
  error: Error | null;
  /** Whether polling is active */
  isPolling: boolean;
  /** Whether job completed successfully */
  isComplete: boolean;
  /** Whether job failed */
  isFailed: boolean;
  /** Whether job is still running */
  isRunning: boolean;
  /** Job progress (0-100) */
  progress: number;
  /** Current step/stage */
  currentStep: string | undefined;
  /** Consecutive error count */
  errorCount: number;
  /** Whether tab is visible */
  isVisible: boolean;
  /** Elapsed time since polling started */
  elapsedTime: number;
  /** Force refetch */
  refetch: () => Promise<unknown>;
  /** Stop polling manually */
  stopPolling: () => void;
  /** Resume polling manually */
  resumePolling: () => void;
}

export function useJobStatus(
  jobId: string | null,
  options: UseJobStatusOptions = {}
): UseJobStatusResult {
  const {
    enabled = true,
    onComplete,
    onError,
    onProgress,
    initialInterval = 1500,
    normalInterval = 3000,
    slowInterval = 8000,
    longRunningInterval = 15000,
  } = options;

  const queryClient = useQueryClient();

  // Use refs to avoid stale closures in callbacks
  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);
  const onProgressRef = useRef(onProgress);
  const lastStatusRef = useRef<string | null>(null);

  useEffect(() => {
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
    onProgressRef.current = onProgress;
  }, [onComplete, onError, onProgress]);

  // Function to check if job is in terminal state
  const isTerminal = useCallback((job: Job): boolean => {
    return TERMINAL_STATUSES.includes(job.status);
  }, []);

  // Use adaptive polling
  const {
    data: job,
    isLoading,
    error,
    isPolling,
    errorCount,
    isVisible,
    elapsedTime,
    refetch,
    stopPolling,
    resumePolling,
  } = useAdaptivePolling<Job, Error>({
    queryKey: ['jobs', jobId],
    queryFn: () => sdk.jobs.get(jobId!),
    isTerminal,
    enabled: enabled && !!jobId,
    initialInterval,
    normalInterval,
    slowInterval,
    longRunningInterval,
  });

  // Handle status changes and callbacks
  useEffect(() => {
    if (!job) return;

    const currentStatus = job.status;
    const previousStatus = lastStatusRef.current;

    // Skip if status hasn't changed
    if (currentStatus === previousStatus) return;
    lastStatusRef.current = currentStatus;

    // Call appropriate callbacks
    if (currentStatus === 'completed') {
      onCompleteRef.current?.(job);
      // Invalidate related queries
      if (job.entityType && job.entityId) {
        queryClient.invalidateQueries({ queryKey: [job.entityType, job.entityId] });
      }
    } else if (currentStatus === 'failed' || currentStatus === 'cancelled') {
      onErrorRef.current?.(job);
    } else if (currentStatus === 'running') {
      onProgressRef.current?.(job);
    }
  }, [job, queryClient]);

  // Derived state
  const isComplete = job?.status === 'completed';
  const isFailed = job?.status === 'failed' || job?.status === 'cancelled';
  const isRunning = job?.status === 'running' || job?.status === 'pending' || job?.status === 'queued';

  return {
    job,
    isLoading,
    error,
    isPolling,
    isComplete,
    isFailed,
    isRunning,
    progress: job?.progress ?? 0,
    currentStep: job?.stage,
    errorCount,
    isVisible,
    elapsedTime,
    refetch,
    stopPolling,
    resumePolling,
  };
}

// ============================================
// Convenience hook for operations (Temporal workflows)
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

const TERMINAL_OPERATION_STATUSES = ['COMPLETED', 'FAILED', 'CANCELLED', 'TIMED_OUT'];

export interface UseOperationStatusOptions {
  enabled?: boolean;
  onComplete?: (operation: OperationStatus) => void;
  onError?: (operation: OperationStatus) => void;
}

export function useOperationStatus(
  workflowId: string | null,
  options: UseOperationStatusOptions = {}
) {
  const { enabled = true, onComplete, onError } = options;

  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);
  const lastStatusRef = useRef<string | null>(null);

  useEffect(() => {
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
  }, [onComplete, onError]);

  const isTerminal = useCallback((op: OperationStatus): boolean => {
    return TERMINAL_OPERATION_STATUSES.includes(op.status);
  }, []);

  const fetchOperation = useCallback(async (): Promise<OperationStatus> => {
    const response = await fetch(`/api/v1/operations/${workflowId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch operation: ${response.status}`);
    }
    return response.json();
  }, [workflowId]);

  const result = useAdaptivePolling<OperationStatus, Error>({
    queryKey: ['operations', workflowId],
    queryFn: fetchOperation,
    isTerminal,
    enabled: enabled && !!workflowId,
    initialInterval: 2000,
    normalInterval: 5000,
    slowInterval: 10000,
    longRunningInterval: 30000,
  });

  // Handle status changes
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
    ...result,
    operation: result.data,
    isComplete: result.data?.status === 'COMPLETED',
    isFailed: ['FAILED', 'CANCELLED', 'TIMED_OUT'].includes(result.data?.status ?? ''),
    progress: result.data?.progress ?? 0,
    currentStep: result.data?.current_step,
  };
}
