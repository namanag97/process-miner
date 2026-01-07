/**
 * Entity Store
 *
 * Normalized entity cache for datasets, projects, models, and jobs.
 * Uses Zustand with immer for immutable updates.
 *
 * This store acts as a single source of truth for entities.
 * TanStack Query hooks populate this store, and components select from it.
 * When an entity is updated, all components see the update immediately.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

import type {
    EntityState,
    NormalizedDataset,
    NormalizedProject,
    NormalizedModel,
    NormalizedJob,
} from './entityStore.types';

// ============================================
// Entity Store
// ============================================

export const useEntityStore = create<EntityState>()(
    devtools(
        immer((set) => ({
            // Initial state - empty entity maps
            datasets: {},
            projects: {},
            models: {},
            jobs: {},

            // ============================================
            // Dataset Actions
            // ============================================

            setDataset: (dataset) =>
                set(
                    (state) => {
                        state.datasets[dataset.id] = dataset;
                    },
                    false,
                    'entity/setDataset'
                ),

            setDatasets: (datasets) =>
                set(
                    (state) => {
                        datasets.forEach((dataset) => {
                            state.datasets[dataset.id] = dataset;
                        });
                    },
                    false,
                    'entity/setDatasets'
                ),

            updateDataset: (id, updates) =>
                set(
                    (state) => {
                        if (state.datasets[id]) {
                            Object.assign(state.datasets[id], updates);
                        }
                    },
                    false,
                    'entity/updateDataset'
                ),

            removeDataset: (id) =>
                set(
                    (state) => {
                        delete state.datasets[id];
                    },
                    false,
                    'entity/removeDataset'
                ),

            // ============================================
            // Project Actions
            // ============================================

            setProject: (project) =>
                set(
                    (state) => {
                        state.projects[project.id] = project;
                    },
                    false,
                    'entity/setProject'
                ),

            setProjects: (projects) =>
                set(
                    (state) => {
                        projects.forEach((project) => {
                            state.projects[project.id] = project;
                        });
                    },
                    false,
                    'entity/setProjects'
                ),

            updateProject: (id, updates) =>
                set(
                    (state) => {
                        if (state.projects[id]) {
                            Object.assign(state.projects[id], updates);
                        }
                    },
                    false,
                    'entity/updateProject'
                ),

            removeProject: (id) =>
                set(
                    (state) => {
                        delete state.projects[id];
                    },
                    false,
                    'entity/removeProject'
                ),

            // ============================================
            // Model Actions
            // ============================================

            setModel: (model) =>
                set(
                    (state) => {
                        state.models[model.id] = model;
                    },
                    false,
                    'entity/setModel'
                ),

            setModels: (models) =>
                set(
                    (state) => {
                        models.forEach((model) => {
                            state.models[model.id] = model;
                        });
                    },
                    false,
                    'entity/setModels'
                ),

            updateModel: (id, updates) =>
                set(
                    (state) => {
                        if (state.models[id]) {
                            Object.assign(state.models[id], updates);
                        }
                    },
                    false,
                    'entity/updateModel'
                ),

            removeModel: (id) =>
                set(
                    (state) => {
                        delete state.models[id];
                    },
                    false,
                    'entity/removeModel'
                ),

            // ============================================
            // Job Actions
            // ============================================

            setJob: (job) =>
                set(
                    (state) => {
                        state.jobs[job.id] = job;
                    },
                    false,
                    'entity/setJob'
                ),

            setJobs: (jobs) =>
                set(
                    (state) => {
                        jobs.forEach((job) => {
                            state.jobs[job.id] = job;
                        });
                    },
                    false,
                    'entity/setJobs'
                ),

            updateJob: (id, updates) =>
                set(
                    (state) => {
                        if (state.jobs[id]) {
                            Object.assign(state.jobs[id], updates);
                        }
                    },
                    false,
                    'entity/updateJob'
                ),

            removeJob: (id) =>
                set(
                    (state) => {
                        delete state.jobs[id];
                    },
                    false,
                    'entity/removeJob'
                ),

            // ============================================
            // Bulk Operations
            // ============================================

            clearAll: () =>
                set(
                    (state) => {
                        state.datasets = {};
                        state.projects = {};
                        state.models = {};
                        state.jobs = {};
                    },
                    false,
                    'entity/clearAll'
                ),

            clearDatasets: () =>
                set(
                    (state) => {
                        state.datasets = {};
                    },
                    false,
                    'entity/clearDatasets'
                ),

            clearProjects: () =>
                set(
                    (state) => {
                        state.projects = {};
                    },
                    false,
                    'entity/clearProjects'
                ),

            clearModels: () =>
                set(
                    (state) => {
                        state.models = {};
                    },
                    false,
                    'entity/clearModels'
                ),

            clearJobs: () =>
                set(
                    (state) => {
                        state.jobs = {};
                    },
                    false,
                    'entity/clearJobs'
                ),
        })),
        { name: 'EntityStore' }
    )
);

// ============================================
// Selectors - Single Entity
// ============================================

/**
 * Select a single dataset by ID
 */
export const useDataset = (id: string | null | undefined): NormalizedDataset | undefined =>
    useEntityStore((state) => (id ? state.datasets[id] : undefined));

/**
 * Select a single project by ID
 */
export const useProject = (id: string | null | undefined): NormalizedProject | undefined =>
    useEntityStore((state) => (id ? state.projects[id] : undefined));

/**
 * Select a single model by ID
 */
export const useModel = (id: string | null | undefined): NormalizedModel | undefined =>
    useEntityStore((state) => (id ? state.models[id] : undefined));

/**
 * Select a single job by ID
 */
export const useJob = (id: string | null | undefined): NormalizedJob | undefined =>
    useEntityStore((state) => (id ? state.jobs[id] : undefined));

// ============================================
// Selectors - Multiple Entities
// ============================================

/**
 * Select multiple datasets by IDs
 */
export const useDatasetsById = (ids: string[]): NormalizedDataset[] =>
    useEntityStore((state) =>
        ids.map((id) => state.datasets[id]).filter((d): d is NormalizedDataset => d !== undefined)
    );

/**
 * Select multiple projects by IDs
 */
export const useProjectsById = (ids: string[]): NormalizedProject[] =>
    useEntityStore((state) =>
        ids.map((id) => state.projects[id]).filter((p): p is NormalizedProject => p !== undefined)
    );

/**
 * Select multiple models by IDs
 */
export const useModelsById = (ids: string[]): NormalizedModel[] =>
    useEntityStore((state) =>
        ids.map((id) => state.models[id]).filter((m): m is NormalizedModel => m !== undefined)
    );

/**
 * Select multiple jobs by IDs
 */
export const useJobsById = (ids: string[]): NormalizedJob[] =>
    useEntityStore((state) =>
        ids.map((id) => state.jobs[id]).filter((j): j is NormalizedJob => j !== undefined)
    );

// ============================================
// Selectors - All Entities
// ============================================

/**
 * Select all datasets as an array
 */
export const useAllDatasets = (): NormalizedDataset[] =>
    useEntityStore((state) => Object.values(state.datasets));

/**
 * Select all projects as an array
 */
export const useAllProjects = (): NormalizedProject[] =>
    useEntityStore((state) => Object.values(state.projects));

/**
 * Select all models as an array
 */
export const useAllModels = (): NormalizedModel[] =>
    useEntityStore((state) => Object.values(state.models));

/**
 * Select all jobs as an array
 */
export const useAllJobs = (): NormalizedJob[] =>
    useEntityStore((state) => Object.values(state.jobs));

// ============================================
// Selectors - Relationship Queries
// ============================================

/**
 * Select datasets for a project
 */
export const useProjectDatasets = (projectId: string | null | undefined): NormalizedDataset[] =>
    useEntityStore((state) => {
        if (!projectId) return [];
        const project = state.projects[projectId];
        if (!project?.datasetIds) return [];
        return project.datasetIds
            .map((id) => state.datasets[id])
            .filter((d): d is NormalizedDataset => d !== undefined);
    });

/**
 * Select models for a dataset
 */
export const useDatasetModels = (datasetId: string | null | undefined): NormalizedModel[] =>
    useEntityStore((state) => {
        if (!datasetId) return [];
        return Object.values(state.models).filter((m) => m.datasetId === datasetId);
    });

/**
 * Select jobs for an entity
 */
export const useEntityJobs = (
    entityType: string | null | undefined,
    entityId: string | null | undefined
): NormalizedJob[] =>
    useEntityStore((state) => {
        if (!entityType || !entityId) return [];
        return Object.values(state.jobs).filter(
            (j) => j.entityType === entityType && j.entityId === entityId
        );
    });

// ============================================
// Static Selectors (for use outside React)
// ============================================

export const selectDataset = (id: string) => useEntityStore.getState().datasets[id];
export const selectProject = (id: string) => useEntityStore.getState().projects[id];
export const selectModel = (id: string) => useEntityStore.getState().models[id];
export const selectJob = (id: string) => useEntityStore.getState().jobs[id];

export const selectAllDatasets = () => Object.values(useEntityStore.getState().datasets);
export const selectAllProjects = () => Object.values(useEntityStore.getState().projects);
export const selectAllModels = () => Object.values(useEntityStore.getState().models);
export const selectAllJobs = () => Object.values(useEntityStore.getState().jobs);
