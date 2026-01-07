/**
 * Query Keys
 *
 * Centralized query key definitions for TanStack Query.
 * Using a factory pattern for type-safe, consistent keys.
 */

export const queryKeys = {
    // Health
    health: {
        all: ['health'] as const,
        check: () => [...queryKeys.health.all, 'check'] as const,
        detailed: () => [...queryKeys.health.all, 'detailed'] as const,
    },

    // Auth
    auth: {
        all: ['auth'] as const,
        me: () => [...queryKeys.auth.all, 'me'] as const,
    },

    // Organizations
    organizations: {
        all: ['organizations'] as const,
        list: (params?: { page?: number; pageSize?: number }) =>
            [...queryKeys.organizations.all, 'list', params] as const,
        detail: (orgId: string) => [...queryKeys.organizations.all, 'detail', orgId] as const,
    },

    // Workspaces
    workspaces: {
        all: ['workspaces'] as const,
        list: (params?: { orgId?: string; page?: number; pageSize?: number }) =>
            [...queryKeys.workspaces.all, 'list', params] as const,
        detail: (workspaceId: string) => [...queryKeys.workspaces.all, 'detail', workspaceId] as const,
        members: (workspaceId: string) => [...queryKeys.workspaces.all, 'members', workspaceId] as const,
    },

    // Projects
    projects: {
        all: ['projects'] as const,
        list: (workspaceId: string, params?: { page?: number; pageSize?: number }) =>
            [...queryKeys.projects.all, 'list', workspaceId, params] as const,
        detail: (projectId: string) => [...queryKeys.projects.all, 'detail', projectId] as const,
    },

    // Datasets
    datasets: {
        all: ['datasets'] as const,
        list: (params?: { projectId?: string; page?: number; pageSize?: number }) =>
            [...queryKeys.datasets.all, 'list', params] as const,
        detail: (datasetId: string) => [...queryKeys.datasets.all, 'detail', datasetId] as const,
        columns: (datasetId: string) => [...queryKeys.datasets.all, 'columns', datasetId] as const,
        mapping: (datasetId: string) => [...queryKeys.datasets.all, 'mapping', datasetId] as const,
    },

    // Discovery
    discovery: {
        all: ['discovery'] as const,
        models: (datasetId: string) => [...queryKeys.discovery.all, 'models', datasetId] as const,
        model: (modelId: string) => [...queryKeys.discovery.all, 'model', modelId] as const,
        dfg: (datasetId: string, options?: Record<string, unknown>) =>
            [...queryKeys.discovery.all, 'dfg', datasetId, options] as const,
        variants: (datasetId: string, options?: Record<string, unknown>) =>
            [...queryKeys.discovery.all, 'variants', datasetId, options] as const,
        activities: (datasetId: string) => [...queryKeys.discovery.all, 'activities', datasetId] as const,
        explorer: (datasetId: string, options?: Record<string, unknown>) =>
            [...queryKeys.discovery.all, 'explorer', datasetId, options] as const,
    },

    // Analytics
    analytics: {
        all: ['analytics'] as const,
        bottlenecks: (datasetId: string) => [...queryKeys.analytics.all, 'bottlenecks', datasetId] as const,
        cycleTime: (datasetId: string) => [...queryKeys.analytics.all, 'cycleTime', datasetId] as const,
        throughput: (datasetId: string) => [...queryKeys.analytics.all, 'throughput', datasetId] as const,
        rework: (datasetId: string) => [...queryKeys.analytics.all, 'rework', datasetId] as const,
        performance: (datasetId: string) => [...queryKeys.analytics.all, 'performance', datasetId] as const,
    },

    // Conformance
    conformance: {
        all: ['conformance'] as const,
        check: (datasetId: string, modelId?: string) =>
            [...queryKeys.conformance.all, 'check', datasetId, modelId] as const,
        alignments: (datasetId: string, modelId?: string) =>
            [...queryKeys.conformance.all, 'alignments', datasetId, modelId] as const,
    },

    // Predictions
    predictions: {
        all: ['predictions'] as const,
        predictors: (datasetId: string) => [...queryKeys.predictions.all, 'predictors', datasetId] as const,
        predictor: (predictorId: string) => [...queryKeys.predictions.all, 'predictor', predictorId] as const,
    },

    // Analyses
    analyses: {
        all: ['analyses'] as const,
        list: (datasetId: string, params?: { page?: number; pageSize?: number }) =>
            [...queryKeys.analyses.all, 'list', datasetId, params] as const,
        detail: (analysisId: string) => [...queryKeys.analyses.all, 'detail', analysisId] as const,
        metadata: () => [...queryKeys.analyses.all, 'metadata'] as const,
    },

    // Jobs
    jobs: {
        all: ['jobs'] as const,
        list: (params?: { status?: string; type?: string }) => [...queryKeys.jobs.all, 'list', params] as const,
        detail: (jobId: string) => [...queryKeys.jobs.all, 'detail', jobId] as const,
    },

    // KPI
    kpi: {
        all: ['kpi'] as const,
        automation: (datasetId: string) => [...queryKeys.kpi.all, 'automation', datasetId] as const,
        deadlines: (datasetId: string) => [...queryKeys.kpi.all, 'deadlines', datasetId] as const,
        unwantedActivities: (datasetId: string) =>
            [...queryKeys.kpi.all, 'unwantedActivities', datasetId] as const,
    },

    // Audit
    audit: {
        all: ['audit'] as const,
        logs: (params?: { startDate?: string; endDate?: string }) =>
            [...queryKeys.audit.all, 'logs', params] as const,
    },

    // Explorer (unified)
    explorer: {
        all: ['explorer'] as const,
        data: (datasetId: string, options?: Record<string, unknown>) =>
            [...queryKeys.explorer.all, 'data', datasetId, options] as const,
        processes: () => [...queryKeys.explorer.all, 'processes'] as const,
        process: (id: string) => [...queryKeys.explorer.all, 'process', id] as const,
    },

    // Processes (legacy compatibility)
    processes: {
        all: ['processes'] as const,
        list: (options?: Record<string, unknown>) => [...queryKeys.processes.all, 'list', options] as const,
        detail: (id: string) => [...queryKeys.processes.all, 'detail', id] as const,
    },
};

export default queryKeys;
