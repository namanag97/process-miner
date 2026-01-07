/**
 * useAnalyzeDataset - Hooks for column detection and dataset analysis
 *
 * Provides hooks for:
 * - Detecting columns from uploaded CSV file
 * - Starting analysis (triggering /ingest endpoint)
 * - Polling job status with adaptive intervals
 *
 * UPDATED: Now uses adaptive polling with visibility detection and error backoff.
 *
 * BUG-043 FIX: Added auth header injection
 * BUG-045 FIX: Added AbortController support for cancellation
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect, useRef } from 'react';
import { message } from 'antd';
import { queryKeys, instrumentedFetch } from '@lumina/design-system';
import { useAdaptivePolling } from '@/hooks';
import { env } from '../../../../config/env';

// ============================================
// Types
// ============================================

export interface ColumnMapping {
    case_id_column: string;
    activity_column: string;
    timestamp_column: string;
    resource_column?: string;
}

export interface ColumnDetectionResponse {
    columns: string[];
    suggestions: {
        case_id?: string;
        activity?: string;
        timestamp?: string;
        resource?: string;
    };
    sample_rows: Record<string, unknown>[];
    row_count?: number;
}

export interface AnalyzeResponse {
    id: string;
    job_type: string;
    status: string;
    progress?: number;
}

export interface JobStatus {
    id: string;
    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
    progress?: number;
    error?: string;
    result?: Record<string, unknown>;
}

// Terminal statuses
const TERMINAL_STATUSES = ['completed', 'failed', 'cancelled'];

// ============================================
// BUG-043 FIX: Auth Header Helper
// ============================================

function getAuthHeaders(): Record<string, string> {
    // Get token from localStorage (set by auth context)
    const token = localStorage.getItem('auth_token');
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

// ============================================
// Column Detection
// ============================================

async function detectColumns(
    datasetId: string,
    signal?: AbortSignal
): Promise<ColumnDetectionResponse> {
    const apiUrl = `${env.API_BASE_URL}/api/v1/datasets/${datasetId}/detect-columns`;
    console.log('[AnalyzeDataset] Detecting columns:', apiUrl);

    // BUG-043 & BUG-045 FIX: Add auth headers and abort signal
    // Using instrumentedFetch for DevConsole visibility
    const response = await instrumentedFetch(apiUrl, {
        headers: getAuthHeaders(),
        signal,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to detect columns' }));
        throw new Error(error.detail || 'Failed to detect columns');
    }

    return response.json();
}

export function useDetectColumns(datasetId: string | null) {
    return useQuery({
        queryKey: ['datasets', datasetId, 'columns'],
        queryFn: ({ signal }) => detectColumns(datasetId!, signal),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000, // Columns don't change
    });
}

// ============================================
// Start Analysis (Ingestion)
// ============================================

interface StartAnalysisParams {
    datasetId: string;
    mapping: ColumnMapping;
    signal?: AbortSignal;
}

async function startAnalysis({
    datasetId,
    mapping,
    signal,
}: StartAnalysisParams): Promise<AnalyzeResponse> {
    const apiUrl = `${env.API_BASE_URL}/api/v1/datasets/${datasetId}/ingest`;
    console.log('[AnalyzeDataset] Starting analysis:', apiUrl);

    // BUG-043 & BUG-045 FIX: Add auth headers and abort signal
    // Using instrumentedFetch for DevConsole visibility
    const response = await instrumentedFetch(apiUrl, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(mapping),
        signal,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to start analysis' }));
        console.error('[AnalyzeDataset] Error:', error);
        throw new Error(error.detail || 'Failed to start analysis');
    }

    return response.json();
}

export function useStartAnalysis() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: startAnalysis,
        onSuccess: () => {
            message.info('Analysis started. This may take a moment...');
            // Invalidate to refresh dataset status
            queryClient.invalidateQueries({ queryKey: queryKeys.projects.all() });
        },
        onError: (error: Error) => {
            // BUG-045 FIX: Don't show error for aborted requests
            if (error.name === 'AbortError') {
                console.log('[AnalyzeDataset] Request was cancelled');
                return;
            }
            message.error(error.message || 'Failed to start analysis');
        },
    });
}

// ============================================
// Job Status Polling (Adaptive)
// ============================================

async function getJobStatus(jobId: string, signal?: AbortSignal): Promise<JobStatus> {
    const apiUrl = `${env.API_BASE_URL}/api/v1/jobs/${jobId}`;

    // BUG-043 & BUG-045 FIX: Add auth headers and abort signal
    // Using instrumentedFetch for DevConsole visibility
    const response = await instrumentedFetch(apiUrl, {
        headers: getAuthHeaders(),
        signal,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to get job status' }));
        throw new Error(error.detail || 'Failed to get job status');
    }

    return response.json();
}

export interface UseJobStatusOptions {
    /** @deprecated Use adaptive intervals instead */
    refetchInterval?: number;
    enabled?: boolean;
    onComplete?: (job: JobStatus) => void;
    onError?: (error: Error) => void;
    // Adaptive interval overrides
    initialInterval?: number;
    normalInterval?: number;
    slowInterval?: number;
    longRunningInterval?: number;
}

export interface UseJobStatusResult {
    data: JobStatus | undefined;
    isLoading: boolean;
    isFetching: boolean;
    error: Error | null;
    isError: boolean;
    refetch: () => Promise<unknown>;
    isPolling: boolean;
    stopPolling: () => void;
    resumePolling: () => void;
    errorCount: number;
    isVisible: boolean;
    elapsedTime: number;
    currentInterval: number | null;
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
export function useJobStatus(
    jobId: string | null,
    options: UseJobStatusOptions = {}
): UseJobStatusResult {
    const {
        refetchInterval, // deprecated
        enabled = true,
        onComplete,
        onError,
        initialInterval = refetchInterval ?? 2000,
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

    const isTerminal = useCallback((job: JobStatus): boolean => {
        return TERMINAL_STATUSES.includes(job.status);
    }, []);

    const result = useAdaptivePolling<JobStatus, Error>({
        queryKey: ['jobs', jobId],
        queryFn: () => getJobStatus(jobId!),
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
        resumePolling: result.resumePolling,
        errorCount: result.errorCount,
        isVisible: result.isVisible,
        elapsedTime: result.elapsedTime,
        currentInterval: result.currentInterval,
    };
}
