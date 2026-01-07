/**
 * Dataset Hooks
 *
 * TanStack Query hooks for dataset operations.
 * Uses normalized entity store for consistent data across the app.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { sdk, type ColumnMapping } from '../sdk';
import { queryKeys } from './queryKeys';
import {
    useEntityStore,
    useDatasetsById,
    useDataset as useDatasetFromStore,
    transformDataset,
} from '@/stores';

// ============================================
// Query Hooks
// ============================================

/**
 * List query result with pagination metadata
 */
export interface DatasetListResult {
    ids: string[];
    total: number;
    page: number;
    pageSize: number;
    pages: number;
}

/**
 * Fetch list of datasets
 * Normalizes response into entity store, returns IDs
 */
export function useDatasets(params?: { projectId?: string; page?: number; pageSize?: number }) {
    const setDatasets = useEntityStore((s) => s.setDatasets);

    const query = useQuery({
        queryKey: queryKeys.datasets.list(params),
        queryFn: async (): Promise<DatasetListResult> => {
            const response = await sdk.datasets.list(params) as {
                items: Array<{ id: string }>;
                total: number;
                page: number;
                page_size: number;
                pages: number;
            };
            // Normalize: store entities in entity store
            const normalized = response.items.map((item: unknown) => transformDataset(item));
            setDatasets(normalized);
            // Return IDs and pagination metadata
            return {
                ids: response.items.map((d: { id: string }) => d.id),
                total: response.total,
                page: response.page,
                pageSize: response.page_size,
                pages: response.pages,
            };
        },
    });

    // Select entities from store using IDs
    const datasets = useDatasetsById(query.data?.ids ?? []);

    return {
        ...query,
        data: datasets,
        // Expose pagination metadata
        pagination: query.data
            ? {
                  total: query.data.total,
                  page: query.data.page,
                  pageSize: query.data.pageSize,
                  pages: query.data.pages,
              }
            : undefined,
    };
}

/**
 * Fetch single dataset by ID
 * Normalizes response into entity store
 */
export function useDataset(datasetId: string | null) {
    const setDataset = useEntityStore((s) => s.setDataset);

    useQuery({
        queryKey: queryKeys.datasets.detail(datasetId ?? ''),
        queryFn: async () => {
            const response = await sdk.datasets.get(datasetId!);
            // Normalize: store entity
            const normalized = transformDataset(response);
            setDataset(normalized);
            return response.id;
        },
        enabled: !!datasetId,
    });

    // Select from entity store
    return useDatasetFromStore(datasetId);
}

/**
 * Fetch dataset columns (detected schema)
 * Note: Column data is not normalized as it's dataset-specific metadata
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
 * Note: Mapping data is not normalized as it's dataset-specific metadata
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
 * Updates entity store on success
 */
export function useUploadDataset() {
    const queryClient = useQueryClient();
    const setDataset = useEntityStore((s) => s.setDataset);

    return useMutation({
        mutationFn: (params: {
            projectId: string;
            file: File;
            name?: string;
            asyncStore?: boolean;
            signal?: AbortSignal;
        }) => sdk.datasets.upload(params),
        onSuccess: (data, variables) => {
            // Add new dataset to entity store
            if (data && typeof data === 'object' && 'id' in data) {
                setDataset(transformDataset(data));
            }
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
 * Removes from entity store on success
 */
export function useDeleteDataset() {
    const queryClient = useQueryClient();
    const removeDataset = useEntityStore((s) => s.removeDataset);

    return useMutation({
        mutationFn: (datasetId: string) => sdk.datasets.delete(datasetId),
        // Optimistic update: remove from store immediately
        onMutate: async (datasetId) => {
            const previous = useEntityStore.getState().datasets[datasetId];
            removeDataset(datasetId);
            return { previous, datasetId };
        },
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: queryKeys.datasets.all,
            });
        },
        onError: (_error, _datasetId, context) => {
            // Rollback on error
            if (context?.previous) {
                useEntityStore.getState().setDataset(context.previous);
            }
        },
    });
}

/**
 * Set column mapping for a dataset
 * Updates entity store status on success
 */
export function useSetColumnMapping() {
    const queryClient = useQueryClient();
    const updateDataset = useEntityStore((s) => s.updateDataset);

    return useMutation({
        mutationFn: ({ datasetId, mapping }: { datasetId: string; mapping: ColumnMapping }) =>
            sdk.datasets.setMapping(datasetId, mapping),
        onSuccess: (_data, variables) => {
            // Update dataset status in entity store
            updateDataset(variables.datasetId, { status: 'mapped' });
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
 * Updates entity store status
 */
export function useIngestDataset() {
    const queryClient = useQueryClient();
    const updateDataset = useEntityStore((s) => s.updateDataset);

    return useMutation({
        mutationFn: (datasetId: string) => sdk.datasets.ingest(datasetId),
        // Optimistic update: set status to ingesting
        onMutate: async (datasetId) => {
            const previous = useEntityStore.getState().datasets[datasetId];
            updateDataset(datasetId, { status: 'ingesting' });
            return { previous, datasetId };
        },
        onSuccess: (data, datasetId) => {
            // Update with job ID if returned
            if (data && typeof data === 'object' && 'job_id' in data) {
                updateDataset(datasetId, {
                    ingestionJobId: (data as { job_id: string }).job_id,
                });
            }
            // Invalidate the dataset detail (status will change)
            queryClient.invalidateQueries({
                queryKey: queryKeys.datasets.detail(datasetId),
            });
        },
        onError: (_error, datasetId, context) => {
            // Rollback on error
            if (context?.previous) {
                updateDataset(datasetId, {
                    status: context.previous.status,
                    ingestionJobId: context.previous.ingestionJobId,
                });
            }
        },
    });
}

/**
 * Fetch event logs list (alias for useDatasets for explorer)
 * @deprecated Use useDatasets instead
 */
export function useEventLogsList(params?: { pageSize?: number }) {
    return useDatasets({ pageSize: params?.pageSize });
}

// ============================================
// Re-export types for convenience
// ============================================

export type { NormalizedDataset as Dataset } from '@/stores/entityStore.types';
