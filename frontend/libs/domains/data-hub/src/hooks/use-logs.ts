/**
 * Event Logs Hooks - React Query hooks for event log operations
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSDK } from '../../../../apps/lumina/src/context/SDKContext';
import type { ListLogsOptions } from 'process-mining-sdk';

// Query key factory for logs
export const logsKeys = {
  all: ['logs'] as const,
  list: (params?: ListLogsOptions) => [...logsKeys.all, 'list', params] as const,
  detail: (id: string) => [...logsKeys.all, id] as const,
  statistics: (id: string) => [...logsKeys.all, id, 'statistics'] as const,
  quality: (id: string) => [...logsKeys.all, id, 'quality'] as const,
  variants: (id: string) => [...logsKeys.all, id, 'variants'] as const,
  activities: (id: string) => [...logsKeys.all, id, 'activities'] as const,
};

/**
 * Fetch paginated list of event logs
 */
export function useLogs(options?: ListLogsOptions) {
  const sdk = useSDK();

  return useQuery({
    queryKey: logsKeys.list(options),
    queryFn: () => sdk.logs.list(options),
  });
}

/**
 * Fetch single event log details
 */
export function useLog(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: logsKeys.detail(logId),
    queryFn: () => sdk.logs.get(logId),
    enabled: !!logId,
  });
}

/**
 * Fetch log statistics (detailed analysis)
 */
export function useLogStatistics(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: logsKeys.statistics(logId),
    queryFn: () => sdk.logs.analyze(logId),
    enabled: !!logId,
  });
}

/**
 * Fetch log quality report
 */
export function useLogQuality(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: logsKeys.quality(logId),
    queryFn: () => sdk.logs.assessQuality(logId),
    enabled: !!logId,
  });
}

/**
 * Fetch process variants
 */
export function useLogVariants(logId: string, limit = 50) {
  const sdk = useSDK();

  return useQuery({
    queryKey: logsKeys.variants(logId),
    queryFn: () => sdk.logs.listVariants(logId, limit),
    enabled: !!logId,
  });
}

/**
 * Fetch unique activities
 */
export function useLogActivities(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: logsKeys.activities(logId),
    queryFn: () => sdk.logs.listActivities(logId),
    enabled: !!logId,
  });
}

/**
 * Delete an event log
 */
export function useDeleteLog() {
  const sdk = useSDK();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (logId: string) => sdk.logs.remove(logId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: logsKeys.all });
    },
  });
}

/**
 * Update log metadata
 */
export function useUpdateLogMetadata() {
  const sdk = useSDK();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ logId, updates }: { logId: string; updates: { name?: string; description?: string } }) =>
      sdk.logs.updateMetadata(logId, updates),
    onSuccess: (_, { logId }) => {
      queryClient.invalidateQueries({ queryKey: logsKeys.detail(logId) });
      queryClient.invalidateQueries({ queryKey: logsKeys.list() });
    },
  });
}
