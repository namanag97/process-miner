/**
 * Analytics Dashboard Hook
 * 
 * Higher-level hook for analytics dashboard data with caching.
 */

import {
    useGetBottlenecksApiV1AnalyticsDatasetsDatasetIdBottlenecksGet,
    useGetCycleTimeApiV1AnalyticsDatasetsDatasetIdCycleTimeGet,
    useGetThroughputApiV1AnalyticsDatasetsDatasetIdThroughputGet,
} from '@/src/api/generated';

export interface AnalyticsDashboardData {
    /** Bottleneck analysis */
    bottlenecks: {
        data: any;
        isLoading: boolean;
        error: Error | null;
    };
    /** Cycle time statistics */
    cycleTime: {
        data: any;
        isLoading: boolean;
        error: Error | null;
    };
    /** Throughput metrics */
    throughput: {
        data: any;
        isLoading: boolean;
        error: Error | null;
    };
    /** Whether all data is loading */
    isLoading: boolean;
    /** Refetch all data */
    refetchAll: () => void;
}

/**
 * Fetch all analytics dashboard data for a dataset.
 * 
 * @param datasetId - Dataset ID to fetch analytics for
 * @returns Analytics data with loading states
 */
export function useAnalyticsDashboard(datasetId: string | null): AnalyticsDashboardData {
    const enabled = !!datasetId;

    const bottlenecksQuery = useGetBottlenecksApiV1AnalyticsDatasetsDatasetIdBottlenecksGet(
        datasetId ?? '',
        { query: { enabled } }
    );

    const cycleTimeQuery = useGetCycleTimeApiV1AnalyticsDatasetsDatasetIdCycleTimeGet(
        datasetId ?? '',
        { query: { enabled } }
    );

    const throughputQuery = useGetThroughputApiV1AnalyticsDatasetsDatasetIdThroughputGet(
        datasetId ?? '',
        { query: { enabled } }
    );

    const isLoading =
        bottlenecksQuery.isLoading ||
        cycleTimeQuery.isLoading ||
        throughputQuery.isLoading;

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

export default useAnalyticsDashboard;
