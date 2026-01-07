/**
 * Entity Store Types
 *
 * Normalized type definitions for the entity cache.
 * These types represent the canonical shape of entities in the store.
 */

// ============================================
// Normalized Entity Types
// ============================================

/**
 * Normalized Dataset entity
 * Uses projectId FK reference instead of nested project object
 */
export interface NormalizedDataset {
    id: string;
    name: string;
    sourceFormat: string;
    totalEvents: number;
    totalCases: number;
    totalActivities: number;
    activities: string[];
    createdAt: string;
    updatedAt?: string | null;
    sourceFile: string | null;
    status?: DatasetStatus;
    errorMessage?: string | null;
    // FK references
    projectId?: string;
    validationJobId?: string | null;
    ingestionJobId?: string | null;
    fileSizeBytes?: number | null;
}

export type DatasetStatus = 'pending' | 'uploading' | 'uploaded' | 'mapping' | 'mapped' | 'ingesting' | 'ready' | 'failed' | 'error';

/**
 * Normalized Project entity
 */
export interface NormalizedProject {
    id: string;
    name: string;
    description: string | null;
    totalFiles: number;
    totalAnalyses: number;
    createdAt: string;
    updatedAt: string | null;
    tags?: string[];
    // FK references - list of dataset IDs in this project
    datasetIds?: string[];
    // Parent reference
    workspaceId?: string;
}

/**
 * Normalized Process Model entity
 * Uses datasetId FK reference
 */
export interface NormalizedModel {
    id: string;
    name: string;
    minerType: string;
    modelFormat: string;
    fitness?: number | null;
    precision?: number | null;
    createdAt: string;
    // FK reference
    datasetId: string | null;
}

/**
 * Normalized Job entity
 */
export interface NormalizedJob {
    id: string;
    jobType: string;
    status: JobStatus;
    progress: number;
    stage?: string | null;
    result?: Record<string, unknown> | null;
    error?: string | null;
    createdAt: string;
    startedAt?: string;
    completedAt?: string;
    // FK references - entity this job operates on
    entityType?: string;
    entityId?: string;
}

export type JobStatus = 'queued' | 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

// ============================================
// Entity Store State & Actions
// ============================================

export interface EntityState {
    // Normalized entity maps
    datasets: Record<string, NormalizedDataset>;
    projects: Record<string, NormalizedProject>;
    models: Record<string, NormalizedModel>;
    jobs: Record<string, NormalizedJob>;

    // Dataset actions
    setDataset: (dataset: NormalizedDataset) => void;
    setDatasets: (datasets: NormalizedDataset[]) => void;
    updateDataset: (id: string, updates: Partial<NormalizedDataset>) => void;
    removeDataset: (id: string) => void;

    // Project actions
    setProject: (project: NormalizedProject) => void;
    setProjects: (projects: NormalizedProject[]) => void;
    updateProject: (id: string, updates: Partial<NormalizedProject>) => void;
    removeProject: (id: string) => void;

    // Model actions
    setModel: (model: NormalizedModel) => void;
    setModels: (models: NormalizedModel[]) => void;
    updateModel: (id: string, updates: Partial<NormalizedModel>) => void;
    removeModel: (id: string) => void;

    // Job actions
    setJob: (job: NormalizedJob) => void;
    setJobs: (jobs: NormalizedJob[]) => void;
    updateJob: (id: string, updates: Partial<NormalizedJob>) => void;
    removeJob: (id: string) => void;

    // Bulk operations
    clearAll: () => void;
    clearDatasets: () => void;
    clearProjects: () => void;
    clearModels: () => void;
    clearJobs: () => void;
}

// ============================================
// Transformation Utilities
// ============================================

/**
 * Raw API dataset response (snake_case from backend)
 */
interface RawDatasetResponse {
    id: string;
    name: string;
    source_format: string;
    total_events: number;
    total_cases: number;
    total_activities: number;
    activities?: string[];
    created_at: string;
    updated_at?: string | null;
    source_file?: string | null;
    status?: string;
    error_message?: string | null;
    validation_job_id?: string | null;
    ingestion_job_id?: string | null;
    file_size_bytes?: number | null;
}

/**
 * Transform dataset response to normalized entity
 * Handles both snake_case API responses and already-transformed data
 */
export function transformDataset(data: unknown): NormalizedDataset {
    // Type guard to check if it's raw API response (snake_case)
    const raw = data as RawDatasetResponse & Record<string, unknown>;

    // Check for snake_case properties (raw API response)
    if ('source_format' in raw || 'created_at' in raw) {
        return {
            id: raw.id,
            name: raw.name,
            sourceFormat: raw.source_format ?? (raw as Record<string, unknown>).sourceFormat as string ?? '',
            totalEvents: raw.total_events ?? (raw as Record<string, unknown>).totalEvents as number ?? 0,
            totalCases: raw.total_cases ?? (raw as Record<string, unknown>).totalCases as number ?? 0,
            totalActivities: raw.total_activities ?? (raw as Record<string, unknown>).totalActivities as number ?? 0,
            activities: raw.activities ?? [],
            createdAt: raw.created_at ?? (raw as Record<string, unknown>).createdAt as string ?? '',
            updatedAt: raw.updated_at ?? (raw as Record<string, unknown>).updatedAt as string | null,
            sourceFile: raw.source_file ?? (raw as Record<string, unknown>).sourceFile as string | null ?? null,
            status: (raw.status ?? (raw as Record<string, unknown>).status) as DatasetStatus | undefined,
            errorMessage: raw.error_message ?? (raw as Record<string, unknown>).errorMessage as string | null,
            validationJobId: raw.validation_job_id ?? (raw as Record<string, unknown>).validationJobId as string | null,
            ingestionJobId: raw.ingestion_job_id ?? (raw as Record<string, unknown>).ingestionJobId as string | null,
            fileSizeBytes: raw.file_size_bytes ?? (raw as Record<string, unknown>).fileSizeBytes as number | null,
        };
    }

    // Already in camelCase format (from SDK types)
    const camel = data as NormalizedDataset;
    return {
        id: camel.id,
        name: camel.name,
        sourceFormat: camel.sourceFormat ?? '',
        totalEvents: camel.totalEvents ?? 0,
        totalCases: camel.totalCases ?? 0,
        totalActivities: camel.totalActivities ?? 0,
        activities: camel.activities ?? [],
        createdAt: camel.createdAt ?? '',
        updatedAt: camel.updatedAt,
        sourceFile: camel.sourceFile ?? null,
        status: camel.status,
        errorMessage: camel.errorMessage,
        validationJobId: camel.validationJobId,
        ingestionJobId: camel.ingestionJobId,
        fileSizeBytes: camel.fileSizeBytes,
    };
}

/**
 * Transform project response to normalized entity
 * Handles both snake_case API responses and already-transformed data
 */
export function transformProject(data: unknown): NormalizedProject {
    const raw = data as Record<string, unknown>;

    // Check for snake_case properties (raw API response)
    if ('total_files' in raw || 'created_at' in raw) {
        return {
            id: raw.id as string,
            name: raw.name as string,
            description: raw.description as string | null,
            tags: raw.tags as string[] | undefined,
            totalFiles: (raw.total_files ?? raw.totalFiles ?? 0) as number,
            totalAnalyses: (raw.total_analyses ?? raw.totalAnalyses ?? 0) as number,
            createdAt: (raw.created_at ?? raw.createdAt ?? '') as string,
            updatedAt: (raw.updated_at ?? raw.updatedAt ?? null) as string | null,
            datasetIds: (raw.datasets as Array<{ id: string }> | undefined)?.map((d) => d.id),
        };
    }

    // Already in camelCase format
    const camel = data as NormalizedProject;
    return {
        id: camel.id,
        name: camel.name,
        description: camel.description,
        tags: camel.tags,
        totalFiles: camel.totalFiles ?? 0,
        totalAnalyses: camel.totalAnalyses ?? 0,
        createdAt: camel.createdAt ?? '',
        updatedAt: camel.updatedAt,
        datasetIds: camel.datasetIds,
    };
}

/**
 * Transform model response to normalized entity
 * Handles both snake_case API responses and already-transformed data
 */
export function transformModel(data: unknown): NormalizedModel {
    const raw = data as Record<string, unknown>;

    // Check for snake_case properties (raw API response)
    if ('miner_type' in raw || 'model_format' in raw || 'created_at' in raw) {
        return {
            id: raw.id as string,
            name: raw.name as string,
            minerType: (raw.miner_type ?? raw.minerType ?? '') as string,
            modelFormat: (raw.model_format ?? raw.modelFormat ?? '') as string,
            datasetId: (raw.dataset_id ?? raw.datasetId ?? null) as string | null,
            fitness: (raw.fitness ?? null) as number | null,
            precision: (raw.precision ?? null) as number | null,
            createdAt: (raw.created_at ?? raw.createdAt ?? '') as string,
        };
    }

    // Already in camelCase format
    const camel = data as NormalizedModel;
    return {
        id: camel.id,
        name: camel.name,
        minerType: camel.minerType ?? '',
        modelFormat: camel.modelFormat ?? '',
        datasetId: camel.datasetId ?? null,
        fitness: camel.fitness,
        precision: camel.precision,
        createdAt: camel.createdAt ?? '',
    };
}

/**
 * Transform job response to normalized entity
 * Handles both snake_case API responses and already-transformed data
 */
export function transformJob(data: unknown): NormalizedJob {
    const raw = data as Record<string, unknown>;

    // Check for snake_case properties (raw API response)
    if ('job_type' in raw || 'created_at' in raw) {
        return {
            id: raw.id as string,
            jobType: (raw.job_type ?? raw.jobType ?? raw.type ?? '') as string,
            status: (raw.status ?? 'pending') as JobStatus,
            progress: (raw.progress ?? 0) as number,
            stage: (raw.stage ?? null) as string | null,
            result: (raw.result ?? null) as Record<string, unknown> | null,
            error: (raw.error ?? null) as string | null,
            createdAt: (raw.created_at ?? raw.createdAt ?? '') as string,
            startedAt: (raw.started_at ?? raw.startedAt) as string | undefined,
            completedAt: (raw.completed_at ?? raw.completedAt) as string | undefined,
            entityType: (raw.entity_type ?? raw.entityType) as string | undefined,
            entityId: (raw.entity_id ?? raw.entityId) as string | undefined,
        };
    }

    // Already in camelCase format
    const camel = data as NormalizedJob;
    return {
        id: camel.id,
        jobType: camel.jobType ?? '',
        status: camel.status ?? 'pending',
        progress: camel.progress ?? 0,
        stage: camel.stage,
        result: camel.result,
        error: camel.error,
        createdAt: camel.createdAt ?? '',
        startedAt: camel.startedAt,
        completedAt: camel.completedAt,
        entityType: camel.entityType,
        entityId: camel.entityId,
    };
}
