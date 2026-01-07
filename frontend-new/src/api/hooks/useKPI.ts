/**
 * KPI Hooks
 *
 * TanStack Query hooks for KPI/quality metrics operations.
 */

import { useQuery } from '@tanstack/react-query';
import { sdk } from '../sdk';
import { queryKeys } from './queryKeys';

// ============================================
// Query Hooks
// ============================================

/**
 * Fetch automation metrics for a dataset
 */
export function useAutomation(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.kpi.automation(datasetId ?? ''),
        queryFn: () => sdk.kpi.getAutomation(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000, // 5 minutes
    });
}

/**
 * Fetch deadline/SLA compliance metrics for a dataset
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
 * Fetch unwanted activities/rework metrics for a dataset
 */
export function useUnwantedActivities(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.kpi.unwantedActivities(datasetId ?? ''),
        queryFn: () => sdk.kpi.getUnwantedActivities(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}

/**
 * Fetch rework metrics for a dataset (uses analytics API)
 */
export function useRework(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.analytics.rework(datasetId ?? ''),
        queryFn: () => sdk.analytics.getRework(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000,
    });
}
