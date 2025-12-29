/**
 * Filter Hooks - React Query hooks for event log filtering
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSDK } from '../../../../apps/lumina/src/context/SDKContext';
import type { FilterRequest, FilterPreviewRequest } from 'process-mining-sdk';

// Query key factory for filtering
export const filterKeys = {
  all: ['filtering'] as const,
  options: (logId: string) => [...filterKeys.all, 'options', logId] as const,
  filtered: (logId: string) => [...filterKeys.all, 'filtered', logId] as const,
  templates: () => [...filterKeys.all, 'templates'] as const,
};

/**
 * Get available filter options for a log (activities, resources, time ranges, etc.)
 */
export function useFilterOptions(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: filterKeys.options(logId),
    queryFn: () => sdk.filtering.getFilterOptions(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Get filter templates (pre-built common filters)
 */
export function useFilterTemplates() {
  const sdk = useSDK();

  return useQuery({
    queryKey: filterKeys.templates(),
    queryFn: () => sdk.filtering.getTemplates(),
    staleTime: Infinity, // Templates are static
  });
}

/**
 * List filtered versions of a log
 */
export function useFilteredLogs(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: filterKeys.filtered(logId),
    queryFn: () => sdk.filtering.listFilteredLogs(logId),
    enabled: !!logId,
  });
}

/**
 * Preview filter impact without saving
 */
export function usePreviewFilter() {
  const sdk = useSDK();

  return useMutation({
    mutationFn: ({ logId, request }: { logId: string; request: FilterPreviewRequest }) =>
      sdk.filtering.previewFilter(logId, request),
  });
}

/**
 * Apply filter to create a new filtered log
 */
export function useApplyFilter() {
  const sdk = useSDK();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ logId, request }: { logId: string; request: FilterRequest }) =>
      sdk.filtering.applyFilter(logId, request),
    onSuccess: (_, { logId }) => {
      queryClient.invalidateQueries({ queryKey: filterKeys.filtered(logId) });
    },
  });
}

/**
 * Delete a filtered log
 */
export function useDeleteFilteredLog() {
  const sdk = useSDK();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ logId, filteredId }: { logId: string; filteredId: string }) =>
      sdk.filtering.deleteFiltered(logId, filteredId),
    onSuccess: (_, { logId }) => {
      queryClient.invalidateQueries({ queryKey: filterKeys.filtered(logId) });
    },
  });
}
