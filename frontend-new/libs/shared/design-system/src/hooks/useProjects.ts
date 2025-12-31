/**
 * Projects Hooks - React Query hooks for project operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSDK } from '../context/SDKContext';
import { queryKeys } from '../api/queryKeys';
import { toast } from '../utils';
import type { CreateProjectData, UpdateProjectData } from '../api/modules/projects';

/**
 * Get paginated list of projects
 */
export function useProjects(options?: { page?: number; pageSize?: number; search?: string }) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.projects.list(options),
    queryFn: () => sdk.projects.list(options),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Get single project by ID with its event logs
 */
export function useProject(id: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.projects.detail(id),
    queryFn: () => sdk.projects.get(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Create a new project
 */
export function useCreateProject() {
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateProjectData) => sdk.projects.create(data),
    onSuccess: (newProject) => {
      // Invalidate projects list to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all() });
      toast.success(`Project "${newProject.name}" created`);
    },
    onError: (error: Error) => {
      toast.error(`Failed to create project: ${error.message}`);
    },
  });
}

/**
 * Update an existing project
 */
export function useUpdateProject() {
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateProjectData }) => 
      sdk.projects.update(id, data),
    onSuccess: (updatedProject) => {
      // Invalidate specific project and projects list
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(updatedProject.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all() });
      toast.success(`Project "${updatedProject.name}" updated`);
    },
    onError: (error: Error) => {
      toast.error(`Failed to update project: ${error.message}`);
    },
  });
}

/**
 * Delete a project
 */
export function useDeleteProject() {
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => sdk.projects.delete(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache and invalidate list
      queryClient.removeQueries({ queryKey: queryKeys.projects.detail(deletedId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all() });
      toast.success('Project deleted');
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete project: ${error.message}`);
    },
  });
}

/**
 * Add an event log to a project
 */
export function useAddFileToProject() {
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ projectId, logId }: { projectId: string; logId: string }) =>
      sdk.projects.addFile(projectId, logId),
    onSuccess: (updatedProject) => {
      // Invalidate project detail to show new file
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(updatedProject.id) });
      toast.success('File added to project');
    },
    onError: (error: Error) => {
      toast.error(`Failed to add file: ${error.message}`);
    },
  });
}

/**
 * Remove an event log from a project
 */
export function useRemoveFileFromProject() {
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ projectId, logId }: { projectId: string; logId: string }) =>
      sdk.projects.removeFile(projectId, logId),
    onSuccess: (_, { projectId }) => {
      // Invalidate project detail
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(projectId) });
      toast.success('File removed from project');
    },
    onError: (error: Error) => {
      toast.error(`Failed to remove file: ${error.message}`);
    },
  });
}
