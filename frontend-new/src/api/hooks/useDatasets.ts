/**
 * Dataset Hooks
 *
 * TanStack Query hooks for dataset operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sdk, type ColumnMapping } from '../sdk';
import { queryKeys } from './queryKeys';

// ============================================
// Query Hooks
// ============================================

/**
 * Fetch list of datasets
 */
export function useDatasets(params?: { projectId?: string; page?: number; pageSize?: number }) {
    return useQuery({
        queryKey: queryKeys.datasets.list(params),
        queryFn: () => sdk.datasets.list(params),
    });
}

/**
 * Fetch single dataset by ID
 */
export function useDataset(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.datasets.detail(datasetId ?? ''),
        queryFn: () => sdk.datasets.get(datasetId!),
        enabled: !!datasetId,
    });
}

/**
 * Fetch dataset columns (detected schema)
 */
export function useDatasetColumns(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.datasets.columns(datasetId ?? ''),
        queryFn: () => sdk.datasets.getColumns(datasetId!),
        enabled: !!datasetId,
    });
}

/**
 * Fetch dataset column mapping
 */
export function useDatasetMapping(datasetId: string | null) {
    return useQuery({
        queryKey: queryKeys.datasets.mapping(datasetId ?? ''),
        queryFn: () => sdk.datasets.getMapping(datasetId!),
        enabled: !!datasetId,
    });
}

// ============================================
// Mutation Hooks
// ============================================

/**
 * Upload a new dataset
 */
export function useUploadDataset() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (params: {
            projectId: string;
            file: File;
            name?: string;
            asyncStore?: boolean;
            signal?: AbortSignal;
        }) => sdk.datasets.upload(params),
        onSuccess: (_data, variables) => {
            // Invalidate datasets list for the project
            queryClient.invalidateQueries({
                queryKey: queryKeys.datasets.list({ projectId: variables.projectId }),
            });
            // Also invalidate the general datasets list
            queryClient.invalidateQueries({
                queryKey: queryKeys.datasets.all,
            });
            // Invalidate projects to refresh dataset counts
            queryClient.invalidateQueries({
                queryKey: queryKeys.projects.all,
            });
        },
    });
}

/**
 * Delete a dataset
 */
export function useDeleteDataset() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (datasetId: string) => sdk.datasets.delete(datasetId),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: queryKeys.datasets.all,
            });
        },
    });
}

/**
 * Set column mapping for a dataset
 */
export function useSetColumnMapping() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ datasetId, mapping }: { datasetId: string; mapping: ColumnMapping }) =>
            sdk.datasets.setMapping(datasetId, mapping),
        onSuccess: (_data, variables) => {
            // Invalidate the mapping query
            queryClient.invalidateQueries({
                queryKey: queryKeys.datasets.mapping(variables.datasetId),
            });
            // Invalidate the dataset detail (status may change)
            queryClient.invalidateQueries({
                queryKey: queryKeys.datasets.detail(variables.datasetId),
            });
        },
    });
}

/**
 * Trigger dataset ingestion
 */
export function useIngestDataset() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (datasetId: string) => sdk.datasets.ingest(datasetId),
        onSuccess: (_data, datasetId) => {
            // Invalidate the dataset detail (status will change)
            queryClient.invalidateQueries({
                queryKey: queryKeys.datasets.detail(datasetId),
            });
        },
    });
}

/**
 * Fetch event logs list (alias for useDatasets for explorer)
 * @deprecated Use useDatasets instead
 */
export function useEventLogsList(params?: { pageSize?: number }) {
    return useQuery({
        queryKey: queryKeys.datasets.list({ pageSize: params?.pageSize }),
        queryFn: () => sdk.datasets.list({ pageSize: params?.pageSize }),
    });
}
