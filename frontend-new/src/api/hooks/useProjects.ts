/**
 * Projects Hooks
 *
 * TanStack Query hooks for project operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sdk } from '../sdk';
import { queryKeys } from './queryKeys';

// ============================================
// Query Hooks
// ============================================

/**
 * Fetch list of projects for a workspace
 */
export function useProjects(workspaceId: string | null, params?: { page?: number; pageSize?: number }) {
    return useQuery({
        queryKey: queryKeys.projects.list(workspaceId ?? '', params),
        queryFn: () => sdk.projects.list(workspaceId!, params),
        enabled: !!workspaceId,
    });
}

/**
 * Fetch single project by ID
 */
export function useProject(projectId: string | null) {
    return useQuery({
        queryKey: queryKeys.projects.detail(projectId ?? ''),
        queryFn: () => sdk.projects.get(projectId!),
        enabled: !!projectId,
    });
}

// ============================================
// Mutation Hooks
// ============================================

/**
 * Create a new project
 */
export function useCreateProject() {
    const queryClient = useQueryClient();

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
        onSuccess: (_data, variables) => {
            // Invalidate projects list for the workspace
            queryClient.invalidateQueries({
                queryKey: queryKeys.projects.list(variables.workspaceId),
            });
        },
    });
}

/**
 * Update a project
 */
export function useUpdateProject() {
    const queryClient = useQueryClient();

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
        onSuccess: (_data, variables) => {
            // Invalidate the project detail
            queryClient.invalidateQueries({
                queryKey: queryKeys.projects.detail(variables.projectId),
            });
            // Invalidate all project lists (don't know which workspace)
            queryClient.invalidateQueries({
                queryKey: queryKeys.projects.all,
            });
        },
    });
}

/**
 * Delete a project
 */
export function useDeleteProject() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (projectId: string) => sdk.projects.delete(projectId),
        onSuccess: () => {
            // Invalidate all project lists
            queryClient.invalidateQueries({
                queryKey: queryKeys.projects.all,
            });
        },
    });
}
