/**
 * useAnalyzeDataset - Hooks for column detection and dataset analysis
 *
 * Provides hooks for:
 * - Detecting columns from uploaded CSV file
 * - Starting analysis (triggering /ingest endpoint)
 * - Polling job status
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import { queryKeys } from '@lumina/design-system';

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
}

export interface AnalyzeResponse {
    job_id: string;
    status: string;
    dataset_id: string;
}

export interface JobStatus {
    id: string;
    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
    progress?: number;
    error?: string;
    result?: Record<string, unknown>;
}

// ============================================
// Column Detection
// ============================================

async function detectColumns(datasetId: string): Promise<ColumnDetectionResponse> {
    const response = await fetch(`/api/v1/datasets/${datasetId}/detect-columns`);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to detect columns' }));
        throw new Error(error.detail || 'Failed to detect columns');
    }

    return response.json();
}

export function useDetectColumns(datasetId: string | null) {
    return useQuery({
        queryKey: ['datasets', datasetId, 'columns'],
        queryFn: () => detectColumns(datasetId!),
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
}

async function startAnalysis({
    datasetId,
    mapping,
}: StartAnalysisParams): Promise<AnalyzeResponse> {
    const response = await fetch(`/api/v1/datasets/${datasetId}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mapping),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to start analysis' }));
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
            message.error(error.message || 'Failed to start analysis');
        },
    });
}

// ============================================
// Job Status Polling
// ============================================

async function getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await fetch(`/api/v1/jobs/${jobId}`);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to get job status' }));
        throw new Error(error.detail || 'Failed to get job status');
    }

    return response.json();
}

export function useJobStatus(jobId: string | null, options?: { refetchInterval?: number }) {
    return useQuery({
        queryKey: ['jobs', jobId],
        queryFn: () => getJobStatus(jobId!),
        enabled: !!jobId,
        refetchInterval: (query) => {
            // Stop polling when job is complete
            const status = query.state.data?.status;
            if (status === 'completed' || status === 'failed' || status === 'cancelled') {
                return false;
            }
            return options?.refetchInterval ?? 2000; // Poll every 2 seconds
        },
    });
}
