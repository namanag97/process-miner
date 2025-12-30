/**
 * Analytics Hooks - React Query hooks for performance analytics
 */
import { useQuery } from '@tanstack/react-query';
import { useSDK } from '@lumina/design-system';

interface Bottleneck {
  activity: string;
  waitingTime: number;
  frequency: number;
}

interface ReworkItem {
  activity: string;
  reworkCount: number;
  cases: string[];
}

// Query key factory for analytics
export const analyticsKeys = {
  all: ['analytics'] as const,
  dashboard: (logId: string) => [...analyticsKeys.all, 'dashboard', logId] as const,
  bottlenecks: (logId: string) => [...analyticsKeys.all, 'bottlenecks', logId] as const,
  cycleTime: (logId: string) => [...analyticsKeys.all, 'cycleTime', logId] as const,
  throughput: (logId: string) => [...analyticsKeys.all, 'throughput', logId] as const,
  rework: (logId: string) => [...analyticsKeys.all, 'rework', logId] as const,
  serviceTimes: (logId: string) => [...analyticsKeys.all, 'serviceTimes', logId] as const,
  patterns: (logId: string) => [...analyticsKeys.all, 'patterns', logId] as const,
};

/**
 * Get comprehensive performance dashboard data
 */
export function usePerformanceDashboard(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: analyticsKeys.dashboard(logId),
    queryFn: () => sdk.analytics.getPerformanceDashboard(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Get bottleneck analysis
 */
export function useBottlenecks(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: analyticsKeys.bottlenecks(logId),
    queryFn: () => sdk.analytics.getBottlenecks(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
    select: (data) => ({
      ...data,
      // Sort by waiting time descending
      bottlenecks: [...(data.bottlenecks || [])]
        .sort((a: Bottleneck, b: Bottleneck) => b.waitingTime - a.waitingTime),
    }),
  });
}

/**
 * Get cycle time statistics
 */
export function useCycleTime(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: analyticsKeys.cycleTime(logId),
    queryFn: () => sdk.analytics.getCycleTime(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get throughput metrics
 */
export function useThroughput(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: analyticsKeys.throughput(logId),
    queryFn: () => sdk.analytics.getThroughput(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get rework analysis
 */
export function useRework(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: analyticsKeys.rework(logId),
    queryFn: () => sdk.analytics.getRework(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
    select: (data) => ({
      ...data,
      // Sort by rework count descending
      rework: [...(data.rework || [])]
        .sort((a: ReworkItem, b: ReworkItem) => b.reworkCount - a.reworkCount),
      // Calculate summary metrics
      totalRework: (data.rework || []).reduce(
        (sum: number, r: ReworkItem) => sum + r.reworkCount,
        0
      ),
      activitiesWithRework: (data.rework || []).length,
    }),
  });
}

/**
 * Get service time statistics per activity
 */
export function useServiceTimes(logId: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: analyticsKeys.serviceTimes(logId),
    queryFn: () => sdk.analytics.getServiceTimes(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get frequent activity patterns
 */
export function usePatterns(logId: string, minSupport = 0.1) {
  const sdk = useSDK();

  return useQuery({
    queryKey: [...analyticsKeys.patterns(logId), minSupport],
    queryFn: () => sdk.analytics.getPatterns(logId, minSupport),
    enabled: !!logId,
    staleTime: 10 * 60 * 1000, // 10 minutes - patterns are expensive
  });
}
