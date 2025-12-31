/**
 * Processes Hooks - React Query hooks for event log operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSDK } from '../context/SDKContext';
import { queryKeys } from '../api/queryKeys';
import { toast } from '../utils';
import type { ProcessMetadata } from '../api/modules/processes';
import type { ListProcessesOptions } from '../api/queryKeys';

/**
 * Get paginated list of all processes/event logs
 */
export function useProcesses(options?: ListProcessesOptions) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.processes.list(options),
    queryFn: () => sdk.processes.list(options),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Get single process/event log by ID
 */
export function useProcess(id: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.processes.detail(id),
    queryFn: () => sdk.processes.get(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Get processes for a specific project
 * Uses the project detail endpoint which includes event logs
 */
export function useProjectProcesses(projectId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.projects.processes(projectId),
    queryFn: async () => {
      const project = await sdk.projects.get(projectId);
      return project.eventLogs;
    },
    enabled: !!projectId,
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Upload a new process file
 */
export function useUploadProcess() {
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ 
      file, 
      metadata, 
      onProgress 
    }: { 
      file: File; 
      metadata?: ProcessMetadata;
      onProgress?: (percent: number) => void;
    }) => sdk.processes.ingestWithProgress(file, metadata, onProgress),
    onSuccess: () => {
      // Invalidate processes list
      queryClient.invalidateQueries({ queryKey: queryKeys.processes.all() });
      toast.success('File uploaded successfully');
    },
    onError: (error: Error) => {
      toast.error(`Upload failed: ${error.message}`);
    },
  });
}

/**
 * Delete a process/event log
 */
export function useDeleteProcess() {
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => sdk.processes.delete(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache and invalidate lists
      queryClient.removeQueries({ queryKey: queryKeys.processes.detail(deletedId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.processes.all() });
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all() });
      toast.success('Process deleted');
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete process: ${error.message}`);
    },
  });
}

/**
 * Detect columns in a file before upload
 */
export function useDetectColumns() {
  const sdk = useSDK();
  
  return useMutation({
    mutationFn: (file: File) => sdk.processes.detectColumns(file),
  });
}

/**
 * Get process statistics
 */
export function useProcessStatistics(logId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.processes.statistics(logId),
    queryFn: () => sdk.processes.analyze(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}
