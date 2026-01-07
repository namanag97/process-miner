/**
 * Projects Hooks
 *
 * TanStack Query hooks for project operations.
 * Uses normalized entity store for consistent data across the app.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sdk } from '../sdk';
import { queryKeys } from './queryKeys';
import {
    useEntityStore,
    useProjectsById,
    useProject as useProjectFromStore,
    transformProject,
    transformDataset,
} from '@/stores';

// ============================================
// Query Hooks
// ============================================

/**
 * List query result with pagination metadata
 */
export interface ProjectListResult {
    ids: string[];
    total: number;
    page: number;
    pageSize: number;
    pages: number;
}

/**
 * Fetch list of projects for a workspace
 * Normalizes response into entity store, returns IDs
 */
export function useProjects(workspaceId: string | null, params?: { page?: number; pageSize?: number }) {
    const setProjects = useEntityStore((s) => s.setProjects);

    const query = useQuery({
        queryKey: queryKeys.projects.list(workspaceId ?? '', params),
        queryFn: async (): Promise<ProjectListResult> => {
            const response = await sdk.projects.list(workspaceId!, params) as {
                items: Array<{ id: string }>;
                total: number;
                page: number;
                page_size: number;
                pages: number;
            };
            // Normalize: store entities in entity store
            const normalized = response.items.map((item: unknown) => transformProject(item));
            setProjects(normalized);
            // Return IDs and pagination metadata
            return {
                ids: response.items.map((p: { id: string }) => p.id),
                total: response.total,
                page: response.page,
                pageSize: response.page_size,
                pages: response.pages,
            };
        },
        enabled: !!workspaceId,
    });

    // Select entities from store using IDs
    const projects = useProjectsById(query.data?.ids ?? []);

    return {
        ...query,
        data: projects,
        // Expose pagination metadata
        pagination: query.data
            ? {
                  total: query.data.total,
                  page: query.data.page,
                  pageSize: query.data.pageSize,
                  pages: query.data.pages,
              }
            : undefined,
    };
}

/**
 * Fetch single project by ID
 * Normalizes response into entity store, including nested datasets
 */
export function useProject(projectId: string | null) {
    const setProject = useEntityStore((s) => s.setProject);
    const setDatasets = useEntityStore((s) => s.setDatasets);
    const updateProject = useEntityStore((s) => s.updateProject);

    useQuery({
        queryKey: queryKeys.projects.detail(projectId ?? ''),
        queryFn: async () => {
            const response = await sdk.projects.get(projectId!);

            // Normalize nested datasets if present
            if (response.datasets && Array.isArray(response.datasets)) {
                const normalizedDatasets = response.datasets.map((d: unknown) => ({
                    ...transformDataset(d),
                    projectId: response.id, // Add FK reference
                }));
                setDatasets(normalizedDatasets);
            }

            // Normalize: store project entity
            const normalized = transformProject(response);
            setProject(normalized);

            // Store dataset IDs on project
            if (response.datasets) {
                updateProject(response.id, {
                    datasetIds: response.datasets.map((d: { id: string }) => d.id),
                });
            }

            return response.id;
        },
        enabled: !!projectId,
    });

    // Select from entity store
    return useProjectFromStore(projectId);
}

// ============================================
// Mutation Hooks
// ============================================

/**
 * Create a new project
 * Updates entity store on success
 */
export function useCreateProject() {
    const queryClient = useQueryClient();
    const setProject = useEntityStore((s) => s.setProject);

    return useMutation({
        mutationFn: ({
            workspaceId,
            name,
            description,
        }: {
            workspaceId: string;
            name: string;
            description?: string;
        }) => sdk.projects.create(workspaceId, { name, description }),
        onSuccess: (data, variables) => {
            // Add new project to entity store
            if (data && typeof data === 'object' && 'id' in data) {
                const normalized = transformProject(data as Parameters<typeof transformProject>[0]);
                setProject({ ...normalized, workspaceId: variables.workspaceId });
            }
            // Invalidate projects list for the workspace
            queryClient.invalidateQueries({
                queryKey: queryKeys.projects.list(variables.workspaceId),
            });
        },
    });
}

/**
 * Update a project
 * Updates entity store with optimistic update
 */
export function useUpdateProject() {
    const queryClient = useQueryClient();
    const updateProject = useEntityStore((s) => s.updateProject);

    return useMutation({
        mutationFn: ({
            projectId,
            name,
            description,
        }: {
            projectId: string;
            name?: string;
            description?: string;
        }) => sdk.projects.update(projectId, { name, description }),
        // Optimistic update
        onMutate: async ({ projectId, name, description }) => {
            const previous = useEntityStore.getState().projects[projectId];
            updateProject(projectId, {
                ...(name !== undefined && { name }),
                ...(description !== undefined && { description }),
            });
            return { previous, projectId };
        },
        onSuccess: (data, variables) => {
            // Update with server response
            if (data && typeof data === 'object' && 'id' in data) {
                const normalized = transformProject(data as Parameters<typeof transformProject>[0]);
                updateProject(variables.projectId, normalized);
            }
            // Invalidate the project detail
            queryClient.invalidateQueries({
                queryKey: queryKeys.projects.detail(variables.projectId),
            });
            // Invalidate all project lists (don't know which workspace)
            queryClient.invalidateQueries({
                queryKey: queryKeys.projects.all,
            });
        },
        onError: (_error, _variables, context) => {
            // Rollback on error
            if (context?.previous) {
                updateProject(context.projectId, context.previous);
            }
        },
    });
}

/**
 * Delete a project
 * Removes from entity store with optimistic update
 */
export function useDeleteProject() {
    const queryClient = useQueryClient();
    const removeProject = useEntityStore((s) => s.removeProject);

    return useMutation({
        mutationFn: (projectId: string) => sdk.projects.delete(projectId),
        // Optimistic update: remove from store immediately
        onMutate: async (projectId) => {
            const previous = useEntityStore.getState().projects[projectId];
            removeProject(projectId);
            return { previous, projectId };
        },
        onSuccess: () => {
            // Invalidate all project lists
            queryClient.invalidateQueries({
                queryKey: queryKeys.projects.all,
            });
        },
        onError: (_error, _projectId, context) => {
            // Rollback on error
            if (context?.previous) {
                useEntityStore.getState().setProject(context.previous);
            }
        },
    });
}

// ============================================
// Re-export types for convenience
// ============================================

export type { NormalizedProject as Project } from '@/stores/entityStore.types';
