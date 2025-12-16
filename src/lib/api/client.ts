/**
 * API Client for Process Mining Backend
 * 
 * Provides typed functions for all API endpoints.
 * Handles authentication, error handling, and response parsing.
 */

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

    // Inject User ID header
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

    const response = await fetch(url, {
        ...options,
        headers,
    });

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
// Types (matching backend schemas)
// ============================================================================

export interface ColumnMetadata {
    name: string;
    detected_type: 'string' | 'number' | 'datetime' | 'boolean';
    sample_values: string[];
    null_percentage: number;
    unique_count: number;
    detected_format?: string;
}

export interface UploadResponse {
    upload_id: string;
    filename: string;
    file_size_bytes: number;
    row_count: number;
    columns: ColumnMetadata[];
    created_at: string;
}

export interface MappingCreate {
    case_id_column: string;
    activity_column: string;
    timestamp_column: string;
    timestamp_format?: string;
    resource_column?: string;
    cost_column?: string;
}

export interface MappingResponse {
    mapping_id: string;
    upload_id: string;
    case_id_column: string;
    activity_column: string;
    timestamp_column: string;
    timestamp_format?: string;
    resource_column?: string;
    cost_column?: string;
    created_at: string;
}

export interface ValidationError {
    field: string;
    message: string;
    sample_bad_values?: string[];
}

export interface ValidationWarning {
    field: string;
    message: string;
    suggestion?: string;
}

export interface ValidationStats {
    total_rows: number;
    valid_rows: number;
    case_count: number;
    activity_count: number;
    date_range_start?: string;
    date_range_end?: string;
}

export interface ValidationResult {
    is_valid: boolean;
    errors: ValidationError[];
    warnings: ValidationWarning[];
    stats?: ValidationStats;
}

export interface JobResponse {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    progress: number;
    progress_message?: string;
    dataset_id?: string;
    error?: string;
    created_at: string;
    completed_at?: string;
}

export interface ActivityNodeData {
    label: string;
    frequency: number;
    isStart: boolean;
    isEnd: boolean;
    avgDuration: number;
    maxFrequency: number;
}

export interface DFGNode {
    id: string;
    type: string;
    position: { x: number; y: number };
    data: ActivityNodeData;
}

export interface DFGEdge {
    id: string;
    source: string;
    target: string;
    type: string;
    data: {
        frequency: number;
        avgDuration: number;
    };
}

export interface DFGSummary {
    totalCases: number;
    totalEvents: number;
    totalActivities: number;
    totalVariants: number;
}

export interface DFGResponse {
    nodes: DFGNode[];
    edges: DFGEdge[];
    summary: DFGSummary;
}

export interface VariantItem {
    id: string;
    sequence: string[];
    trace_display: string;
    case_count: number;
    percentage: number;
    avg_duration_ms: number;
    is_happy_path: boolean;
    case_ids: string[];
}

export interface VariantsResponse {
    total: number;
    variants: VariantItem[];
}

export interface ProcessStats {
    total_cases: number;
    total_events: number;
    total_activities: number;
    total_variants: number;
    avg_case_duration_ms: number;
    median_case_duration_ms: number;
    start_activities: string[];
    end_activities: string[];
}

export interface DatasetSummary {
    dataset_id: string;
    stats: ProcessStats;
    created_at: string;
}

export interface Deviation {
    type: 'rework' | 'skip' | 'unusual_path';
    description: string;
    affected_cases: string[];
    frequency: number;
}

export interface FullAnalysisResponse {
    dataset_id: string;
    dfg: DFGResponse;
    variants: VariantsResponse;
    stats: ProcessStats;
    deviations: Deviation[];
    created_at: string;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Upload a file for process mining
 */
export async function uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/api/uploads`, {
        method: 'POST',
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

/**
 * Get upload details
 */
export async function getUpload(uploadId: string): Promise<UploadResponse> {
    return apiFetch(`/api/uploads/${uploadId}`);
}

/**
 * Get columns for an upload
 */
export async function getUploadColumns(uploadId: string): Promise<{ columns: ColumnMetadata[] }> {
    return apiFetch(`/api/uploads/${uploadId}/columns`);
}

/**
 * Delete an upload
 */
export async function deleteUpload(uploadId: string): Promise<void> {
    await apiFetch(`/api/uploads/${uploadId}`, { method: 'DELETE' });
}

/**
 * Create a column mapping
 */
export async function createMapping(
    uploadId: string,
    mapping: MappingCreate
): Promise<MappingResponse> {
    return apiFetch(`/api/mappings/uploads/${uploadId}/mappings`, {
        method: 'POST',
        body: JSON.stringify(mapping),
    });
}

/**
 * Get mapping details
 */
export async function getMapping(mappingId: string): Promise<MappingResponse> {
    return apiFetch(`/api/mappings/${mappingId}`);
}

/**
 * Validate a mapping
 */
export async function validateMapping(mappingId: string): Promise<ValidationResult> {
    return apiFetch(`/api/mappings/${mappingId}/validate`, {
        method: 'POST',
    });
}

/**
 * Start processing a mapped file
 */
export async function startProcessing(mappingId: string): Promise<JobResponse> {
    return apiFetch(`/api/processing/mappings/${mappingId}/process`, {
        method: 'POST',
    });
}

/**
 * Get job status
 */
export async function getJobStatus(jobId: string): Promise<JobResponse> {
    return apiFetch(`/api/processing/jobs/${jobId}`);
}

/**
 * Poll job until complete
 */
export async function waitForJob(
    jobId: string,
    onProgress?: (progress: number, message?: string) => void,
    pollIntervalMs = 1000
): Promise<JobResponse> {
    while (true) {
        const job = await getJobStatus(jobId);

        if (onProgress) {
            onProgress(job.progress, job.progress_message ?? undefined);
        }

        if (job.status === 'completed' || job.status === 'failed') {
            return job;
        }

        await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
    }
}

/**
 * Get DFG for a dataset
 */
export async function getDFG(datasetId: string): Promise<DFGResponse> {
    return apiFetch(`/api/datasets/${datasetId}/dfg`);
}

/**
 * Get variants for a dataset
 */
export async function getVariants(
    datasetId: string,
    limit = 50,
    offset = 0
): Promise<VariantsResponse> {
    return apiFetch(
        `/api/datasets/${datasetId}/variants?limit=${limit}&offset=${offset}`
    );
}

/**
 * Get summary statistics for a dataset
 */
export async function getSummary(datasetId: string): Promise<DatasetSummary> {
    return apiFetch(`/api/datasets/${datasetId}/summary`);
}

/**
 * Get full analysis in one request
 */
export async function getFullAnalysis(datasetId: string): Promise<FullAnalysisResponse> {
    return apiFetch(`/api/datasets/${datasetId}/full`);
}

/**
 * Get deviations for a dataset
 */
export async function getDeviations(datasetId: string): Promise<{ deviations: Deviation[] }> {
    return apiFetch(`/api/datasets/${datasetId}/deviations`);
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string }> {
    return apiFetch('/api/health');
}

/**
 * Create a new user
 */
export async function createUser(): Promise<{ id: string }> {
    return apiFetch('/api/users', { method: 'POST' });
}

/**
 * Verify current user
 */
export async function getCurrentUser(userId: string): Promise<{ id: string; created_at: string }> {
    // We pass userId manually here usually, or let the header handle it.
    // The endpoint expects ?user_id= query param for now based on my implementation 
    // Wait, let's check routers/users.py implementation:
    // @router.get("/me") async def get_current_user_info(user_id: str
    return apiFetch(`/api/users/me?user_id=${userId}`);
}
