/**
 * useUploadDataset - Hook for uploading files with deferred ingestion
 *
 * Uses async_store=true to create UNSTRUCTURED dataset without parsing.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import { queryKeys } from '@lumina/design-system';
import { env } from '../../../config/env';

interface UploadDatasetParams {
    projectId: string;
    file: File;
    name?: string;
}

interface UploadDatasetResponse {
    id: string;
    name: string;
    status: string;
    sourceFormat: string;
    createdAt: string;
}

const MAX_FILE_SIZE_MB = 100;

async function uploadDataset({
    projectId,
    file,
    name,
}: UploadDatasetParams): Promise<UploadDatasetResponse> {
    // Validate file size
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        throw new Error(`File size exceeds ${MAX_FILE_SIZE_MB}MB limit`);
    }

    // Validate file extension
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'csv' && ext !== 'xes') {
        throw new Error('Only CSV and XES files are supported');
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('async_store', 'true');
    formData.append('project_id', projectId);
    if (name) {
        formData.append('name', name);
    }

    // Use API base URL from environment config
    const apiUrl = `${env.API_BASE_URL}/api/v1/datasets/upload`;
    console.log('[Upload] Uploading to:', apiUrl, 'projectId:', projectId);

    const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
        console.error('[Upload] Error:', error);
        throw new Error(error.detail || 'Failed to upload file');
    }

    const result = await response.json();
    console.log('[Upload] Success:', result);
    return result;
}

export function useUploadDataset() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: uploadDataset,
        onSuccess: (data) => {
            message.success(`Dataset "${data.name}" uploaded successfully`);
            // Invalidate project queries to refresh the dataset list
            queryClient.invalidateQueries({ queryKey: queryKeys.projects.all() });
        },
        onError: (error: Error) => {
            message.error(error.message || 'Failed to upload dataset');
        },
    });
}
