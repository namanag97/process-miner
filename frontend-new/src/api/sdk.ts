/**
 * Process Mining SDK
 *
 * Unified API client for all backend endpoints.
 * Uses axios with interceptors for auth and error handling.
 *
 * @example
 * ```typescript
 * import { sdk } from '@/api/sdk';
 *
 * // Fetch datasets
 * const datasets = await sdk.datasets.list();
 *
 * // Run discovery
 * const job = await sdk.discovery.discover({ datasetId: '123', minerType: 'inductive' });
 * ```
 */

import apiClient from './client';

// ============================================
// Types
// ============================================

export interface PaginationParams {
    page?: number;
    pageSize?: number;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    pageSize: number;
    pages: number;
}

// Dataset types
export interface Dataset {
    id: string;
    name: string;
    status: string;
    sourceFormat?: string;
    totalCases?: number;
    totalEvents?: number;
    totalActivities?: number;
    createdAt: string;
    projectId?: string;
}

export interface DatasetColumn {
    name: string;
    dtype: string;
    sampleValues?: string[];
}

export interface ColumnMapping {
    caseId: string;
    activity: string;
    timestamp: string;
    resource?: string;
    cost?: string;
}

// Discovery types
export interface DiscoveryRequest {
    datasetId: string;
    minerType: 'alpha' | 'inductive' | 'heuristic' | 'split';
    modelName?: string;
    parameters?: Record<string, unknown>;
}

export interface DiscoveryResponse {
    jobId: string;
    modelId?: string;
    status: string;
}

export type ModelFormat =
    | 'petri_net'
    | 'process_tree'
    | 'dfg'
    | 'performance_dfg'
    | 'bpmn'
    | 'powl'
    | 'declare'
    | 'log_skeleton'
    | 'temporal_profile'
    | 'prefix_tree'
    | 'transition_system'
    | 'batches';

export type MinerType =
    | 'alpha'
    | 'alpha_plus'
    | 'inductive'
    | 'inductive_infrequent'
    | 'heuristics'
    | 'dfg'
    | 'performance_dfg'
    | 'ilp'
    | 'powl'
    | 'bpmn_inductive'
    | 'declare'
    | 'log_skeleton'
    | 'temporal_profile'
    | 'prefix_tree'
    | 'transition_system';

export interface ProcessModel {
    id: string;
    name: string;
    type: string;
    datasetId: string;
    minerType?: MinerType;
    modelFormat?: ModelFormat;
    fitness?: number;
    precision?: number;
    createdAt: string;
    // Visualization data (varies by model type)
    data?: unknown;
}

// DFG types
export interface DFGNode {
    id: string;
    label: string;
    frequency: number;
    isStart?: boolean;
    isEnd?: boolean;
}

export interface DFGEdge {
    source: string;
    target: string;
    frequency: number;
    avgDuration?: number;
}

export interface DFGResponse {
    nodes: DFGNode[];
    edges: DFGEdge[];
    startActivities?: Record<string, number>;
    endActivities?: Record<string, number>;
}

// Variant types
export interface Variant {
    key: string;
    activities: string[];
    caseCount: number;
    frequencyPercent: number;
    avgDuration?: number;
}

// Analytics types
export interface BottleneckResponse {
    bottlenecks: Array<{
        activity: string;
        avgWaitingTime: number;
        medianWaitingTime?: number;
        caseCount: number;
        severity: 'low' | 'medium' | 'high';
    }>;
}

export interface CycleTimeResponse {
    avgSeconds: number;
    medianSeconds: number;
    minSeconds: number;
    maxSeconds: number;
    p75Seconds?: number;
    p95Seconds?: number;
}

export interface ThroughputResponse {
    casesPerDay: number;
    casesPerWeek?: number;
    casesPerMonth?: number;
    totalCases: number;
}

// Job types
export type JobStatus = 'queued' | 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface Job {
    id: string;
    type: string;
    jobType?: string; // Alias for type
    status: JobStatus;
    progress?: number;
    stage?: string;
    entityType?: string;
    entityId?: string;
    result?: unknown;
    error?: string;
    createdAt: string;
    startedAt?: string;
    completedAt?: string;
}

// Explorer types
export interface ExplorerData {
    dfg: DFGResponse;
    variants: Variant[];
    activities: Array<{
        name: string;
        frequency: number;
        avgDuration?: number;
    }>;
    statistics: {
        totalCases: number;
        totalEvents: number;
        totalActivities: number;
        avgCaseDuration?: number;
    };
}

// Analysis types
export interface Analysis {
    id: string;
    name: string;
    type: string;
    status: string;
    datasetId: string;
    createdAt: string;
    completedAt?: string;
}

// ============================================
// SDK Implementation
// ============================================

// Note: apiClient.baseURL already includes /api/v1, so we don't need a prefix here

export const sdk = {
    // ========================================
    // Health
    // ========================================
    health: {
        check: async (): Promise<boolean> => {
            try {
                const response = await apiClient.get('/health');
                return response.status === 200;
            } catch {
                return false;
            }
        },

        detailed: async () => {
            const { data } = await apiClient.get('/health/detailed');
            return data;
        },
    },

    // ========================================
    // Auth
    // ========================================
    auth: {
        login: async (email: string, password: string) => {
            const { data } = await apiClient.post(`/auth/login`, { email, password });
            return data;
        },

        register: async (params: { email: string; password: string; name?: string; orgName?: string }) => {
            const { data } = await apiClient.post(`/auth/register`, params);
            return data;
        },

        logout: async () => {
            const { data } = await apiClient.post(`/auth/logout`);
            return data;
        },

        refresh: async (refreshToken: string) => {
            const { data } = await apiClient.post(`/auth/refresh`, { refresh_token: refreshToken });
            return data;
        },

        me: async () => {
            const { data } = await apiClient.get(`/auth/me`);
            return data;
        },

        updateProfile: async (params: { name?: string }) => {
            const { data } = await apiClient.put(`/auth/me`, null, { params });
            return data;
        },

        changePassword: async (currentPassword: string, newPassword: string) => {
            const { data } = await apiClient.post(`/auth/change-password`, {
                current_password: currentPassword,
                new_password: newPassword,
            });
            return data;
        },
    },

    // ========================================
    // Organizations
    // ========================================
    organizations: {
        list: async (params?: PaginationParams) => {
            const { data } = await apiClient.get(`/organizations/`, { params });
            return data;
        },

        get: async (orgId: string) => {
            const { data } = await apiClient.get(`/organizations/${orgId}`);
            return data;
        },

        create: async (params: { name: string; plan?: string }) => {
            const { data } = await apiClient.post(`/organizations/`, params);
            return data;
        },

        update: async (orgId: string, params: { name?: string }) => {
            const { data } = await apiClient.put(`/organizations/${orgId}`, params);
            return data;
        },

        delete: async (orgId: string) => {
            await apiClient.delete(`/organizations/${orgId}`);
        },
    },

    // ========================================
    // Workspaces
    // ========================================
    workspaces: {
        list: async (params?: PaginationParams & { orgId?: string }) => {
            const { data } = await apiClient.get(`/workspaces`, { params });
            return data;
        },

        get: async (workspaceId: string) => {
            const { data } = await apiClient.get(`/workspaces/${workspaceId}`);
            return data;
        },

        create: async (orgId: string, params: { name: string; description?: string }) => {
            const { data } = await apiClient.post(`/workspaces`, params, { params: { org_id: orgId } });
            return data;
        },

        update: async (workspaceId: string, params: { name?: string; description?: string }) => {
            const { data } = await apiClient.put(`/workspaces/${workspaceId}`, params);
            return data;
        },

        delete: async (workspaceId: string) => {
            await apiClient.delete(`/workspaces/${workspaceId}`);
        },

        members: {
            list: async (workspaceId: string) => {
                const { data } = await apiClient.get(`/workspaces/${workspaceId}/members`);
                return data;
            },

            add: async (workspaceId: string, userId: string, role?: string) => {
                const { data } = await apiClient.post(`/workspaces/${workspaceId}/members`, {
                    user_id: userId,
                    role: role || 'viewer',
                });
                return data;
            },

            remove: async (workspaceId: string, userId: string) => {
                await apiClient.delete(`/workspaces/${workspaceId}/members/${userId}`);
            },
        },
    },

    // ========================================
    // Projects
    // ========================================
    projects: {
        list: async (workspaceId: string, params?: PaginationParams) => {
            const { data } = await apiClient.get(`/projects/`, {
                params: { workspace_id: workspaceId, ...params },
            });
            return data;
        },

        get: async (projectId: string) => {
            const { data } = await apiClient.get(`/projects/${projectId}`);
            return data;
        },

        create: async (workspaceId: string, params: { name: string; description?: string }) => {
            const { data } = await apiClient.post(`/projects/`, {
                ...params,
                workspace_id: workspaceId,
            });
            return data;
        },

        update: async (projectId: string, params: { name?: string; description?: string }) => {
            const { data } = await apiClient.put(`/projects/${projectId}`, params);
            return data;
        },

        delete: async (projectId: string) => {
            await apiClient.delete(`/projects/${projectId}`);
        },
    },

    // ========================================
    // Datasets
    // ========================================
    datasets: {
        list: async (params?: PaginationParams & { projectId?: string }) => {
            const queryParams: Record<string, unknown> = { ...params };
            if (params?.projectId) {
                queryParams.project_id = params.projectId;
                delete queryParams.projectId;
            }
            const { data } = await apiClient.get(`/datasets/`, { params: queryParams });
            return data;
        },

        get: async (datasetId: string): Promise<Dataset> => {
            const { data } = await apiClient.get(`/datasets/${datasetId}`);
            return data;
        },

        upload: async (params: {
            projectId: string;
            file: File;
            name?: string;
            asyncStore?: boolean;
            signal?: AbortSignal;
        }): Promise<Dataset> => {
            const formData = new FormData();
            formData.append('file', params.file);
            formData.append('project_id', params.projectId);
            if (params.name) formData.append('name', params.name);
            if (params.asyncStore) formData.append('async_store', 'true');

            const { data } = await apiClient.post(`/datasets/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                signal: params.signal,
            });
            return data;
        },

        delete: async (datasetId: string) => {
            await apiClient.delete(`/datasets/${datasetId}`);
        },

        // Column detection and mapping
        getColumns: async (datasetId: string): Promise<DatasetColumn[]> => {
            const { data } = await apiClient.get(`/datasets/${datasetId}/columns`);
            return data;
        },

        getMapping: async (datasetId: string): Promise<ColumnMapping | null> => {
            const { data } = await apiClient.get(`/datasets/${datasetId}/column-mapping`);
            return data;
        },

        setMapping: async (datasetId: string, mapping: ColumnMapping) => {
            const { data } = await apiClient.post(`/datasets/${datasetId}/column-mapping`, mapping);
            return data;
        },

        // Ingestion
        ingest: async (datasetId: string) => {
            const { data } = await apiClient.post(`/datasets/${datasetId}/ingest`);
            return data;
        },

        // Preview (for upload wizard)
        getPreview: async (datasetId: string, rows = 10) => {
            const { data } = await apiClient.get(`/datasets/${datasetId}/preview`, {
                params: { rows },
            });
            return data;
        },

        // Sheets (for Excel/multi-sheet files)
        getSheets: async (datasetId: string) => {
            const { data } = await apiClient.get(`/datasets/${datasetId}/sheets`);
            return data;
        },

        // Presigned upload URL (for S3 direct upload)
        getPresignedUrl: async (params: {
            filename: string;
            fileSizeBytes: number;
            projectId: string;
            contentType?: string;
        }) => {
            const { data } = await apiClient.post(`/datasets/presign`, {
                filename: params.filename,
                file_size_bytes: params.fileSizeBytes,
                project_id: params.projectId,
                content_type: params.contentType,
            });
            return data;
        },

        // Trigger validation after S3 upload
        triggerValidation: async (datasetId: string) => {
            const { data } = await apiClient.post(`/datasets/${datasetId}/uploaded`);
            return data;
        },
    },

    // ========================================
    // Discovery
    // ========================================
    discovery: {
        discover: async (request: DiscoveryRequest): Promise<DiscoveryResponse> => {
            const { data } = await apiClient.post(`/discovery/discover`, {
                dataset_id: request.datasetId,
                miner_type: request.minerType,
                model_name: request.modelName,
                parameters: request.parameters,
            });
            return data;
        },

        listModels: async (datasetId: string): Promise<ProcessModel[]> => {
            const { data } = await apiClient.get(`/discovery/models`, {
                params: { dataset_id: datasetId },
            });
            return data;
        },

        getModel: async (modelId: string): Promise<ProcessModel> => {
            const { data } = await apiClient.get(`/discovery/models/${modelId}`);
            return data;
        },

        // Visualization endpoints
        buildDFG: async (datasetId: string, options?: { includePerformance?: boolean }): Promise<DFGResponse> => {
            const { data } = await apiClient.get(`/visualization/dfg/${datasetId}`, {
                params: { include_performance: options?.includePerformance },
            });
            return data;
        },

        getVariants: async (datasetId: string, options?: { topN?: number }): Promise<Variant[]> => {
            const { data } = await apiClient.get(`/discovery/datasets/${datasetId}/variants`, {
                params: { top_n: options?.topN },
            });
            return data;
        },

        getActivityStats: async (datasetId: string) => {
            const { data } = await apiClient.get(`/discovery/datasets/${datasetId}/activities`);
            return data;
        },

        // Unified explorer data endpoint
        getExplorerData: async (datasetId: string, options?: {
            includePerformance?: boolean;
            includeComplexity?: boolean;
            topVariants?: number;
        }): Promise<ExplorerData> => {
            const { data } = await apiClient.get(`/discovery/datasets/${datasetId}/explorer`, {
                params: {
                    include_performance: options?.includePerformance,
                    include_complexity: options?.includeComplexity,
                    top_variants: options?.topVariants,
                },
            });
            return data;
        },
    },

    // ========================================
    // Analytics
    // ========================================
    analytics: {
        getBottlenecks: async (datasetId: string): Promise<BottleneckResponse> => {
            const { data } = await apiClient.get(`/analytics/datasets/${datasetId}/bottlenecks`);
            return data;
        },

        getCycleTime: async (datasetId: string): Promise<CycleTimeResponse> => {
            const { data } = await apiClient.get(`/analytics/datasets/${datasetId}/cycle-time`);
            return data;
        },

        getThroughput: async (datasetId: string): Promise<ThroughputResponse> => {
            const { data } = await apiClient.get(`/analytics/datasets/${datasetId}/throughput`);
            return data;
        },

        getRework: async (datasetId: string) => {
            const { data } = await apiClient.get(`/analytics/datasets/${datasetId}/rework`);
            return data;
        },

        getPerformance: async (datasetId: string) => {
            const { data } = await apiClient.get(`/analytics/datasets/${datasetId}/performance`);
            return data;
        },
    },

    // ========================================
    // Conformance
    // ========================================
    conformance: {
        check: async (datasetId: string, modelId: string) => {
            const { data } = await apiClient.post(`/conformance/check`, {
                dataset_id: datasetId,
                model_id: modelId,
            });
            return data;
        },

        tokenReplay: async (datasetId: string, modelId: string) => {
            const { data } = await apiClient.post(`/conformance/token-replay`, {
                dataset_id: datasetId,
                model_id: modelId,
            });
            return data;
        },

        alignments: async (datasetId: string, modelId: string) => {
            const { data } = await apiClient.get(`/conformance/alignments`, {
                params: { dataset_id: datasetId, model_id: modelId },
            });
            return data;
        },
    },

    // ========================================
    // Predictions
    // ========================================
    predictions: {
        listPredictors: async (datasetId: string) => {
            const { data } = await apiClient.get(`/predictions/datasets/${datasetId}/predictors`);
            return data;
        },

        createPredictor: async (datasetId: string, params: {
            name: string;
            type: 'next_activity' | 'remaining_time';
            config?: Record<string, unknown>;
        }) => {
            const { data } = await apiClient.post(`/predictions/datasets/${datasetId}/predictors`, params);
            return data;
        },

        getPredictor: async (predictorId: string) => {
            const { data } = await apiClient.get(`/predictions/predictors/${predictorId}`);
            return data;
        },

        predict: async (predictorId: string, caseData: unknown) => {
            const { data } = await apiClient.post(`/predictions/predictors/${predictorId}/predict`, {
                case_data: caseData,
            });
            return data;
        },
    },

    // ========================================
    // Analyses (Stored Results)
    // ========================================
    analyses: {
        list: async (datasetId: string, params?: PaginationParams): Promise<PaginatedResponse<Analysis>> => {
            const { data } = await apiClient.get(`/analyses/`, {
                params: { dataset_id: datasetId, ...params },
            });
            return data;
        },

        get: async (analysisId: string): Promise<Analysis> => {
            const { data } = await apiClient.get(`/analyses/${analysisId}`);
            return data;
        },

        create: async (datasetId: string, params: {
            name: string;
            analysisType: string;
            config?: Record<string, unknown>;
        }) => {
            const { data } = await apiClient.post(`/analyses/`, {
                dataset_id: datasetId,
                name: params.name,
                analysis_type: params.analysisType,
                config: params.config,
            });
            return data;
        },

        delete: async (analysisId: string) => {
            await apiClient.delete(`/analyses/${analysisId}`);
        },

        getMetadata: async () => {
            const { data } = await apiClient.get(`/analyses/metadata`);
            return data;
        },
    },

    // ========================================
    // Jobs
    // ========================================
    jobs: {
        get: async (jobId: string): Promise<Job> => {
            const { data } = await apiClient.get(`/jobs/${jobId}`);
            return data;
        },

        list: async (params?: { status?: string; type?: string } & PaginationParams) => {
            const { data } = await apiClient.get(`/jobs/`, { params });
            return data;
        },

        cancel: async (jobId: string) => {
            const { data } = await apiClient.post(`/jobs/${jobId}/cancel`);
            return data;
        },
    },

    // ========================================
    // KPI / Quality Metrics
    // ========================================
    kpi: {
        getAutomation: async (datasetId: string) => {
            const { data } = await apiClient.get(`/quality-metrics/datasets/${datasetId}/automation`);
            return data;
        },

        getDeadlines: async (datasetId: string) => {
            const { data } = await apiClient.get(`/quality-metrics/datasets/${datasetId}/deadlines`);
            return data;
        },

        getUnwantedActivities: async (datasetId: string) => {
            const { data } = await apiClient.get(`/quality-metrics/datasets/${datasetId}/unwanted-activities`);
            return data;
        },
    },

    // ========================================
    // Filtering
    // ========================================
    filtering: {
        apply: async (datasetId: string, filters: unknown) => {
            const { data } = await apiClient.post(`/filtering/datasets/${datasetId}/apply`, filters);
            return data;
        },

        getOptions: async (datasetId: string) => {
            const { data } = await apiClient.get(`/filtering/datasets/${datasetId}/options`);
            return data;
        },
    },

    // ========================================
    // OCPM (Object-Centric Process Mining)
    // ========================================
    ocpm: {
        getObjectTypes: async (datasetId: string) => {
            const { data } = await apiClient.get(`/ocpm/datasets/${datasetId}/object-types`);
            return data;
        },

        getObjectGraph: async (datasetId: string, objectType?: string) => {
            const { data } = await apiClient.get(`/ocpm/datasets/${datasetId}/object-graph`, {
                params: { object_type: objectType },
            });
            return data;
        },
    },

    // ========================================
    // Audit Logs
    // ========================================
    audit: {
        list: async (params?: { startDate?: string; endDate?: string } & PaginationParams) => {
            const { data } = await apiClient.get(`/audit/logs`, { params });
            return data;
        },
    },

    // ========================================
    // Processes (Legacy/Compatibility)
    // ========================================
    processes: {
        list: async (options?: { pageSize?: number }) => {
            // Maps to datasets list for backward compatibility
            const { data } = await apiClient.get(`/datasets/`, {
                params: { page_size: options?.pageSize },
            });
            return data;
        },

        get: async (id: string) => {
            // Maps to dataset get for backward compatibility
            const { data } = await apiClient.get(`/datasets/${id}`);
            return data;
        },

        analyze: async (id: string) => {
            // Trigger analysis for backward compatibility
            const { data } = await apiClient.post(`/analyses/`, {
                dataset_id: id,
                name: 'Quick Analysis',
                analysis_type: 'discovery',
            });
            return data;
        },

        getProcessSummary: async (id: string) => {
            // Get summary via analytics for backward compatibility
            const { data } = await apiClient.get(`/analytics/datasets/${id}/summary`);
            return data;
        },
    },
};

// Export types
export type SDK = typeof sdk;

export default sdk;
