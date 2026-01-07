/**
 * Analytics Hooks
 *
 * TanStack Query hooks for analytics operations.
 */

import { useQuery } from '@tanstack/react-query';
import { sdk, type BottleneckResponse, type CycleTimeResponse, type ThroughputResponse } from '../sdk';
import { queryKeys } from './queryKeys';

// ============================================
// Query Hooks
// ============================================

/**
 * Fetch bottleneck analysis for a dataset
 */
export function useBottlenecks(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.analytics.bottlenecks(datasetId ?? ''),
        queryFn: () => sdk.analytics.getBottlenecks(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000, // 5 minutes
    });
}

/**
 * Fetch cycle time statistics for a dataset
 */
export function useCycleTime(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.analytics.cycleTime(datasetId ?? ''),
        queryFn: () => sdk.analytics.getCycleTime(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Fetch throughput metrics for a dataset
 */
export function useThroughput(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.analytics.throughput(datasetId ?? ''),
        queryFn: () => sdk.analytics.getThroughput(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Fetch rework analysis for a dataset
 */
export function useRework(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.analytics.rework(datasetId ?? ''),
        queryFn: () => sdk.analytics.getRework(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Fetch overall performance metrics for a dataset
 */
export function usePerformance(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.analytics.performance(datasetId ?? ''),
        queryFn: () => sdk.analytics.getPerformance(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

// ============================================
// Dashboard Hook (combines multiple analytics)
// ============================================

export interface AnalyticsDashboardData {
    bottlenecks: {
        data: BottleneckResponse | null;
        isLoading: boolean;
        error: Error | null;
    };
    cycleTime: {
        data: CycleTimeResponse | null;
        isLoading: boolean;
        error: Error | null;
    };
    throughput: {
        data: ThroughputResponse | null;
        isLoading: boolean;
        error: Error | null;
    };
    isLoading: boolean;
    refetchAll: () => void;
}

/**
 * Combined hook for analytics dashboard data
 */
export function useAnalyticsDashboard(datasetId: string | null): AnalyticsDashboardData {
    const enabled = !!datasetId;

    const bottlenecksQuery = useBottlenecks(enabled ? datasetId : null);
    const cycleTimeQuery = useCycleTime(enabled ? datasetId : null);
    const throughputQuery = useThroughput(enabled ? datasetId : null);

    const isLoading =
        bottlenecksQuery.isLoading || cycleTimeQuery.isLoading || throughputQuery.isLoading;

    const refetchAll = () => {
        bottlenecksQuery.refetch();
        cycleTimeQuery.refetch();
        throughputQuery.refetch();
    };

    return {
        bottlenecks: {
            data: bottlenecksQuery.data ?? null,
            isLoading: bottlenecksQuery.isLoading,
            error: bottlenecksQuery.error as Error | null,
        },
        cycleTime: {
            data: cycleTimeQuery.data ?? null,
            isLoading: cycleTimeQuery.isLoading,
            error: cycleTimeQuery.error as Error | null,
        },
        throughput: {
            data: throughputQuery.data ?? null,
            isLoading: throughputQuery.isLoading,
            error: throughputQuery.error as Error | null,
        },
        isLoading,
        refetchAll,
    };
}

// ============================================
// KPI Hooks
// ============================================

/**
 * Fetch automation metrics for a dataset
 */
export function useAutomation(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.kpi.automation(datasetId ?? ''),
        queryFn: () => sdk.kpi.getAutomation(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Fetch deadline compliance for a dataset
 */
export function useDeadlines(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.kpi.deadlines(datasetId ?? ''),
        queryFn: () => sdk.kpi.getDeadlines(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Fetch unwanted activities for a dataset
 */
export function useUnwantedActivities(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.kpi.unwantedActivities(datasetId ?? ''),
        queryFn: () => sdk.kpi.getUnwantedActivities(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}
