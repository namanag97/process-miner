/**
 * Analytics Hooks - React Query hooks for performance and analytics
 */

import { useQuery } from '@tanstack/react-query';
import { useSDK } from '../context/SDKContext';
import { queryKeys } from '../api/queryKeys';

/**
 * Get performance dashboard data (cycle time, throughput, bottlenecks)
 */
export function usePerformance(logId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.performance(logId),
    queryFn: () => sdk.analytics.getPerformance(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get rework analysis data
 */
export function useRework(logId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.rework(logId),
    queryFn: () => sdk.analytics.getRework(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get bottleneck analysis
 */
export function useBottlenecks(logId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.bottlenecks(logId),
    queryFn: () => sdk.analytics.getBottlenecks(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get cycle time statistics
 */
export function useCycleTime(logId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.cycleTime(logId),
    queryFn: () => sdk.analytics.getCycleTime(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get throughput statistics
 */
export function useThroughput(logId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.throughput(logId),
    queryFn: () => sdk.analytics.getThroughput(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get pattern mining results
 */
export function usePatterns(logId: string, minSupport?: number) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.patterns(logId),
    queryFn: () => sdk.analytics.getPatterns(logId, minSupport),
    enabled: !!logId,
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Get full process summary (aggregated analytics for LLM context)
 */
export function useProcessSummary(logId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.summary(logId),
    queryFn: () => sdk.analytics.getProcessSummary(logId),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get deadline metrics (placeholder - may need backend endpoint)
 * TODO: Connect to real endpoint when available
 */
export function useDeadlines(logId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.deadlines(logId),
    queryFn: async () => {
      // For now, derive from throughput data
      const throughput = await sdk.analytics.getThroughput(logId);
      return {
        logId,
        onTimeRate: 0.85, // Placeholder
        lateRate: 0.15,
        avgDelayDays: 2.3,
        totalCases: throughput.total_cases,
        completedCases: throughput.completed_cases,
      };
    },
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get automation metrics (placeholder - may need backend endpoint)
 * TODO: Connect to real endpoint when available
 */
export function useAutomation(logId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.automation(logId),
    queryFn: async () => {
      // For now, derive from performance data
      const performance = await sdk.analytics.getPerformance(logId);
      return {
        logId,
        automationRate: 0.42, // Placeholder
        manualActivities: 12,
        automatedActivities: 8,
        potentialSavingsHours: 156,
        cycleTimeData: performance.cycleTime,
      };
    },
    enabled: !!logId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Combined hook for KPI page data
 */
export function useKPIData(logId: string) {
  const performanceQuery = usePerformance(logId);
  const reworkQuery = useRework(logId);
  const bottlenecksQuery = useBottlenecks(logId);
  
  return {
    performance: performanceQuery.data,
    rework: reworkQuery.data,
    bottlenecks: bottlenecksQuery.data,
    isLoading: performanceQuery.isLoading || reworkQuery.isLoading || bottlenecksQuery.isLoading,
    isError: performanceQuery.isError || reworkQuery.isError || bottlenecksQuery.isError,
    error: performanceQuery.error || reworkQuery.error || bottlenecksQuery.error,
    refetch: () => {
      performanceQuery.refetch();
      reworkQuery.refetch();
      bottlenecksQuery.refetch();
    },
  };
}
