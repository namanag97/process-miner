/**
 * Dataset Ingestion Hook
 * 
 * Higher-level hook for dataset upload and ingestion with workflow tracking.
 */

import { useState, useCallback } from 'react';
import {
    useUploadDatasetApiV1DatasetsPost,
    useListDatasetsApiV1DatasetsGet,
    useGetDatasetApiV1DatasetsDatasetIdGet,
} from '../../../libs/api-hooks/src/generated/api';
import { useWorkflowPolling } from './useWorkflowPolling';

export interface DatasetIngestionState {
    /** Upload and start ingestion */
    uploadAndIngest: (file: File, workspaceId: string, name?: string) => Promise<string>;
    /** Current workflow progress (null if no active ingestion) */
    progress: ReturnType<typeof useWorkflowPolling>;
    /** Whether upload is in progress */
    isUploading: boolean;
    /** Whether ingestion is in progress (after upload) */
    isIngesting: boolean;
    /** Human-readable current step */
    currentStep: string | null;
    /** Dataset ID after upload */
    datasetId: string | null;
    /** Error if any */
    error: Error | null;
    /** Combined error check (upload error or workflow failure) */
    hasError: boolean;
    /** Reset state for new upload */
    reset: () => void;
}

/**
 * Hook for uploading and ingesting datasets with workflow tracking.
 * 
 * @example
 * ```tsx
 * const { uploadAndIngest, progress, isUploading } = useDatasetIngestion();
 * 
 * const handleUpload = async (file: File) => {
 *   const datasetId = await uploadAndIngest(file, workspaceId);
 *   // Track progress via progress.progressPercent, progress.isComplete
 * };
 * ```
 */
export function useDatasetIngestion(): DatasetIngestionState {
    const [workflowId, setWorkflowId] = useState<string | null>(null);
    const [datasetId, setDatasetId] = useState<string | null>(null);
    const [error, setError] = useState<Error | null>(null);

    // Upload mutation (also handles ingestion)
    const uploadMutation = useUploadDatasetApiV1DatasetsPost();

    // Track workflow progress
    const progress = useWorkflowPolling(workflowId);

    // Combined upload and ingest
    const uploadAndIngest = useCallback(async (
        file: File,
        projectId: string,
        name?: string
    ): Promise<string> => {
        try {
            setError(null);

            // Upload file (ingestion is triggered automatically by backend)
            const uploadResponse = await uploadMutation.mutateAsync({
                data: {
                    file,
                    name: name || file.name,
                    project_id: projectId,
                },
            });

            const datasetId = uploadResponse.id;
            if (!datasetId) {
                throw new Error('Upload succeeded but no dataset ID returned');
            }

            // Track workflow if available
            const wfId = (uploadResponse as any).workflow_id || datasetId;
            setWorkflowId(wfId);
            setDatasetId(datasetId);

            return datasetId;
        } catch (err) {
            setError(err as Error);
            throw err;
        }
    }, [uploadMutation]);

    // Reset state
    const reset = useCallback(() => {
        setWorkflowId(null);
        setDatasetId(null);
        setError(null);
    }, []);

    const isIngesting = progress?.isActive ?? false;
    const hasError = !!error || (progress?.isFailed ?? false);
    const currentStep = progress?.currentStep ?? null;

    return {
        uploadAndIngest,
        progress,
        isUploading: uploadMutation.isPending,
        isIngesting,
        currentStep,
        datasetId,
        error,
        hasError,
        reset,
    };
}

/**
 * List datasets for a workspace.
 */
export function useDatasets(projectId: string) {
    const { data, isLoading, refetch } = useListDatasetsApiV1DatasetsGet(
        { project_id: projectId },
        { query: { enabled: !!projectId } }
    );

    return {
        datasets: data?.items ?? [],
        total: data?.total ?? 0,
        isLoading,
        refetch,
    };
}

/**
 * Get single dataset details.
 */
export function useDataset(datasetId: string | null) {
    const { data, isLoading, refetch } = useGetDatasetApiV1DatasetsDatasetIdGet(
        datasetId ?? '',
        { query: { enabled: !!datasetId } }
    );

    return {
        dataset: data ?? null,
        isLoading,
        refetch,
    };
}

export default useDatasetIngestion;
