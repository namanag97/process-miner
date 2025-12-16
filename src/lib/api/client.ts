/**
 * API Client for Process Mining Backend
 * 
 * Thin fetch wrapper with error handling.
 * Types are imported from ./types.ts
 */

import type {
    UploadResponse,
    MappingCreate,
    MappingResponse,
    ValidationResult,
    JobResponse,
    DFGResponse,
    VariantsResponse,
    DatasetSummary,
    FullAnalysisResponse,
    Deviation,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const USER_ID_KEY = 'process_miner_user_id';

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
    constructor(
        public status: number,
        message: string,
        public detail?: string
    ) {
        super(message);
        this.name = 'ApiError';
    }
}

/**
 * Base fetch wrapper with error handling and auth injection
 */
async function apiFetch<T>(
    path: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_URL}${path}`;

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    } as Record<string, string>;

    if (typeof window !== 'undefined') {
        const userId = localStorage.getItem(USER_ID_KEY);
        if (userId) {
            headers['X-User-ID'] = userId;
        }
    }

    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new ApiError(
            response.status,
            errorBody.error || `API error: ${response.status}`,
            errorBody.detail
        );
    }

    return response.json();
}

// ============================================================================
// Upload API
// ============================================================================

export async function uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    // Get user ID from localStorage for authentication
    const headers: Record<string, string> = {};
    if (typeof window !== 'undefined') {
        const userId = localStorage.getItem(USER_ID_KEY);
        if (userId) {
            headers['X-User-ID'] = userId;
        }
    }

    const response = await fetch(`${API_URL}/api/uploads`, {
        method: 'POST',
        headers,
        body: formData,
    });

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new ApiError(
            response.status,
            errorBody.detail || `Upload failed: ${response.status}`,
            errorBody.detail
        );
    }

    return response.json();
}

export async function getUpload(uploadId: string): Promise<UploadResponse> {
    return apiFetch(`/api/uploads/${uploadId}`);
}

export async function deleteUpload(uploadId: string): Promise<void> {
    await apiFetch(`/api/uploads/${uploadId}`, { method: 'DELETE' });
}

// ============================================================================
// Mapping API
// ============================================================================

export async function createMapping(
    uploadId: string,
    mapping: MappingCreate
): Promise<MappingResponse> {
    return apiFetch(`/api/mappings/uploads/${uploadId}/mappings`, {
        method: 'POST',
        body: JSON.stringify(mapping),
    });
}

export async function getMapping(mappingId: string): Promise<MappingResponse> {
    return apiFetch(`/api/mappings/${mappingId}`);
}

export async function validateMapping(mappingId: string): Promise<ValidationResult> {
    return apiFetch(`/api/mappings/${mappingId}/validate`, { method: 'POST' });
}

// ============================================================================
// Processing API
// ============================================================================

export async function startProcessing(mappingId: string): Promise<JobResponse> {
    return apiFetch(`/api/processing/mappings/${mappingId}/process`, { method: 'POST' });
}

export async function getJobStatus(jobId: string): Promise<JobResponse> {
    return apiFetch(`/api/processing/jobs/${jobId}`);
}

export async function waitForJob(
    jobId: string,
    onProgress?: (progress: number, message?: string) => void,
    pollIntervalMs = 1000
): Promise<JobResponse> {
    while (true) {
        const job = await getJobStatus(jobId);
        onProgress?.(job.progress, job.progress_message ?? undefined);

        if (job.status === 'completed' || job.status === 'failed') {
            return job;
        }

        await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
    }
}

// ============================================================================
// Analysis API
// ============================================================================

export async function getDFG(datasetId: string): Promise<DFGResponse> {
    return apiFetch(`/api/datasets/${datasetId}/dfg`);
}

export async function getVariants(
    datasetId: string,
    limit = 50,
    offset = 0
): Promise<VariantsResponse> {
    return apiFetch(`/api/datasets/${datasetId}/variants?limit=${limit}&offset=${offset}`);
}

export async function getSummary(datasetId: string): Promise<DatasetSummary> {
    return apiFetch(`/api/datasets/${datasetId}/summary`);
}

export async function getFullAnalysis(datasetId: string): Promise<FullAnalysisResponse> {
    return apiFetch(`/api/datasets/${datasetId}/full`);
}

export async function getDeviations(datasetId: string): Promise<{ deviations: Deviation[] }> {
    return apiFetch(`/api/datasets/${datasetId}/deviations`);
}

// ============================================================================
// User API
// ============================================================================

export async function healthCheck(): Promise<{ status: string }> {
    return apiFetch('/api/health');
}

export async function createUser(): Promise<{ id: string }> {
    return apiFetch('/api/users', { method: 'POST' });
}

export async function getCurrentUser(userId: string): Promise<{ id: string; created_at: string }> {
    return apiFetch(`/api/users/me?user_id=${userId}`);
}
