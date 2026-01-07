/**
 * Workspaces Hooks
 *
 * TanStack Query hooks for workspace operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sdk } from '../sdk';
import { queryKeys } from './queryKeys';

// ============================================
// Query Hooks
// ============================================

/**
 * Fetch list of workspaces
 */
export function useWorkspaces(params?: { orgId?: string; page?: number; pageSize?: number }) {
    return useQuery({
        queryKey: queryKeys.workspaces.list(params),
        queryFn: () => sdk.workspaces.list(params),
    });
}

/**
 * Fetch single workspace by ID
 */
export function useWorkspace(workspaceId: string | null) {
    return useQuery({
        queryKey: queryKeys.workspaces.detail(workspaceId ?? ''),
        queryFn: () => sdk.workspaces.get(workspaceId!),
        enabled: !!workspaceId,
    });
}

/**
 * Fetch workspace members
 */
export function useWorkspaceMembers(workspaceId: string | null) {
    return useQuery({
        queryKey: queryKeys.workspaces.members(workspaceId ?? ''),
        queryFn: () => sdk.workspaces.members.list(workspaceId!),
        enabled: !!workspaceId,
    });
}

// ============================================
// Mutation Hooks
// ============================================

/**
 * Create a new workspace
 */
export function useCreateWorkspace() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({
            orgId,
            name,
            description,
        }: {
            orgId: string;
            name: string;
            description?: string;
        }) => sdk.workspaces.create(orgId, { name, description }),
        onSuccess: (_data, variables) => {
            // Invalidate workspaces list for the org
            queryClient.invalidateQueries({
                queryKey: queryKeys.workspaces.list({ orgId: variables.orgId }),
            });
            // Also invalidate the general workspaces list
            queryClient.invalidateQueries({
                queryKey: queryKeys.workspaces.all,
            });
        },
    });
}

/**
 * Update a workspace
 */
export function useUpdateWorkspace() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({
            workspaceId,
            name,
            description,
        }: {
            workspaceId: string;
            name?: string;
            description?: string;
        }) => sdk.workspaces.update(workspaceId, { name, description }),
        onSuccess: (_data, variables) => {
            // Invalidate the workspace detail
            queryClient.invalidateQueries({
                queryKey: queryKeys.workspaces.detail(variables.workspaceId),
            });
            // Invalidate all workspace lists
            queryClient.invalidateQueries({
                queryKey: queryKeys.workspaces.all,
            });
        },
    });
}

/**
 * Delete a workspace
 */
export function useDeleteWorkspace() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (workspaceId: string) => sdk.workspaces.delete(workspaceId),
        onSuccess: () => {
            // Invalidate all workspace lists
            queryClient.invalidateQueries({
                queryKey: queryKeys.workspaces.all,
            });
        },
    });
}

/**
 * Add a member to a workspace
 */
export function useAddWorkspaceMember() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({
            workspaceId,
            userId,
            role,
        }: {
            workspaceId: string;
            userId: string;
            role?: string;
        }) => sdk.workspaces.members.add(workspaceId, userId, role),
        onSuccess: (_data, variables) => {
            // Invalidate the workspace members list
            queryClient.invalidateQueries({
                queryKey: queryKeys.workspaces.members(variables.workspaceId),
            });
        },
    });
}

/**
 * Remove a member from a workspace
 */
export function useRemoveWorkspaceMember() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ workspaceId, userId }: { workspaceId: string; userId: string }) =>
            sdk.workspaces.members.remove(workspaceId, userId),
        onSuccess: (_data, variables) => {
            // Invalidate the workspace members list
            queryClient.invalidateQueries({
                queryKey: queryKeys.workspaces.members(variables.workspaceId),
            });
        },
    });
}
