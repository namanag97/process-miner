/**
 * Analytics Hooks - React Query hooks for performance and analytics
 */

import { useQuery } from '@tanstack/react-query';
import { useSDK } from '../context/SDKContext';
import { queryKeys } from '../api/queryKeys';

/**
 * Get performance dashboard data (cycle time, throughput, bottlenecks)
 */
export function usePerformance(datasetId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.performance(datasetId),
    queryFn: () => sdk.analytics.getPerformance(datasetId),
    enabled: !!datasetId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get rework analysis data
 */
export function useRework(datasetId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.rework(datasetId),
    queryFn: () => sdk.analytics.getRework(datasetId),
    enabled: !!datasetId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get bottleneck analysis
 */
export function useBottlenecks(datasetId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.bottlenecks(datasetId),
    queryFn: () => sdk.analytics.getBottlenecks(datasetId),
    enabled: !!datasetId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get cycle time statistics
 */
export function useCycleTime(datasetId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.cycleTime(datasetId),
    queryFn: () => sdk.analytics.getCycleTime(datasetId),
    enabled: !!datasetId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get throughput statistics
 */
export function useThroughput(datasetId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.throughput(datasetId),
    queryFn: () => sdk.analytics.getThroughput(datasetId),
    enabled: !!datasetId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get pattern mining results
 */
export function usePatterns(datasetId: string, minSupport?: number) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.patterns(datasetId),
    queryFn: () => sdk.analytics.getPatterns(datasetId, minSupport),
    enabled: !!datasetId,
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Get full process summary (aggregated analytics for LLM context)
 */
export function useProcessSummary(datasetId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.summary(datasetId),
    queryFn: () => sdk.analytics.getProcessSummary(datasetId),
    enabled: !!datasetId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get deadline metrics (placeholder - may need backend endpoint)
 * TODO: Connect to real endpoint when available
 */
export function useDeadlines(datasetId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.deadlines(datasetId),
    queryFn: async () => {
      // For now, derive from throughput data
      const throughput = await sdk.analytics.getThroughput(datasetId);
      return {
        datasetId,
        onTimeRate: 0.85, // Placeholder
        lateRate: 0.15,
        avgDelayDays: 2.3,
        totalCases: throughput.total_cases,
        completedCases: throughput.completed_cases,
      };
    },
    enabled: !!datasetId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get automation metrics (placeholder - may need backend endpoint)
 * TODO: Connect to real endpoint when available
 */
export function useAutomation(datasetId: string) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.analytics.automation(datasetId),
    queryFn: async () => {
      // For now, derive from performance data
      const performance = await sdk.analytics.getPerformance(datasetId);
      return {
        datasetId,
        automationRate: 0.42, // Placeholder
        manualActivities: 12,
        automatedActivities: 8,
        potentialSavingsHours: 156,
        cycleTimeData: performance.cycleTime,
      };
    },
    enabled: !!datasetId,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Combined hook for KPI page data
 */
export function useKPIData(datasetId: string) {
  const performanceQuery = usePerformance(datasetId);
  const reworkQuery = useRework(datasetId);
  const bottlenecksQuery = useBottlenecks(datasetId);
  
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
