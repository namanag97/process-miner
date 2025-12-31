/**
 * Projects Feature Hooks
 *
 * Data fetching hooks using the createFeatureHook factory.
 * Wraps design-system hooks with standardized patterns.
 */

import { queryKeys } from '@lumina/design-system';
import { createQueryHook, createMutationHook } from '../../../core/hooks/createFeatureHook';
import type {
  Project,
  ProjectDetail,
  ProjectListOptions,
  ProjectListResponse,
  CreateProjectInput,
  UpdateProjectInput,
} from '../types';

// ============================================
// Query Hooks
// ============================================

/**
 * Hook to fetch paginated list of projects
 */
export const useProjectList = createQueryHook<
  ProjectListResponse,
  ProjectListOptions | undefined
>({
  queryKey: (options) => queryKeys.projects.list(options),
  queryFn: async (sdk, options) => {
    const result = await sdk.projects.list(options);
    return result;
  },
  staleTime: 5 * 60 * 1000,
});

/**
 * Hook to fetch single project by ID
 */
export const useProjectDetail = createQueryHook<ProjectDetail, string>({
  queryKey: (id) => queryKeys.projects.detail(id),
  queryFn: async (sdk, id) => {
    const result = await sdk.projects.get(id);
    return result;
  },
  enabled: (id) => !!id,
  staleTime: 2 * 60 * 1000,
});

// ============================================
// Mutation Hooks
// ============================================

/**
 * Hook to create a new project
 */
export const useCreateProject = createMutationHook<Project, CreateProjectInput>({
  mutationFn: async (sdk, input) => {
    const result = await sdk.projects.create(input);
    return result;
  },
  invalidateKeys: [queryKeys.projects.all()],
  onSuccessMessage: 'Project created successfully',
  onErrorMessage: 'Failed to create project',
});

/**
 * Hook to update an existing project
 */
export const useUpdateProject = createMutationHook<
  Project,
  { id: string; data: UpdateProjectInput }
>({
  mutationFn: async (sdk, { id, data }) => {
    const result = await sdk.projects.update(id, data);
    return result;
  },
  invalidateKeys: [queryKeys.projects.all()],
  onSuccessMessage: 'Project updated',
  onErrorMessage: 'Failed to update project',
});

/**
 * Hook to delete a project
 */
export const useDeleteProject = createMutationHook<void, string>({
  mutationFn: async (sdk, id) => {
    await sdk.projects.delete(id);
  },
  invalidateKeys: [queryKeys.projects.all()],
  onSuccessMessage: 'Project deleted',
  onErrorMessage: 'Failed to delete project',
});

/**
 * Hook to remove a file from a project
 */
export const useRemoveFileFromProject = createMutationHook<
  void,
  { projectId: string; logId: string }
>({
  mutationFn: async (sdk, { projectId, logId }) => {
    await sdk.projects.removeFile(projectId, logId);
  },
  invalidateKeys: [queryKeys.projects.all()],
  onSuccessMessage: 'Data source removed',
  onErrorMessage: 'Failed to remove data source',
});
