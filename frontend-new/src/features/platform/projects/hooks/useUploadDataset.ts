/**
 * useUploadDataset - Hook for uploading files with deferred ingestion
 *
 * Uses async_store=true to create UNSTRUCTURED dataset without parsing.
 * 
 * BUG-043 FIX: Added auth header injection
 * BUG-045 FIX: Added AbortController support
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import { queryKeys } from '@/src/shared/design-system';
import { env } from '../../../../config/env';

interface UploadDatasetParams {
    projectId: string;
    file: File;
    name?: string;
    signal?: AbortSignal;
}

interface UploadDatasetResponse {
    id: string;
    name: string;
    status: string;
    sourceFormat: string;
    createdAt: string;
}

const MAX_FILE_SIZE_MB = 100;

// BUG-043 FIX: Get auth token for uploads
function getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
}

async function uploadDataset({
    projectId,
    file,
    name,
    signal,
}: UploadDatasetParams): Promise<UploadDatasetResponse> {
    // Validate file size
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        throw new Error(`File size exceeds ${MAX_FILE_SIZE_MB}MB limit`);
    }

    // Validate file extension - support CSV and XES formats
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'csv' && ext !== 'xes') {
        throw new Error('Supported formats: CSV, XES');
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('async_store', 'true');
    console.log('[Upload] Setting async_store=true for deferred ingestion');
    formData.append('project_id', projectId);
    if (name) {
        formData.append('name', name);
    }

    // Use API base URL from environment config
    const apiUrl = `${env.API_BASE_URL}/api/v1/datasets/`;
    console.log('[Upload] Uploading to:', apiUrl, 'projectId:', projectId);

    // BUG-043 FIX: Add auth headers (no Content-Type for FormData)
    const headers: Record<string, string> = {};
    const token = getAuthToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // BUG-045 FIX: Add abort signal
    const response = await fetch(apiUrl, {
        method: 'POST',
        headers,
        body: formData,
        signal,
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
            // BUG-045 FIX: Don't show error for aborted requests
            if (error.name === 'AbortError') {
                console.log('[Upload] Request was cancelled');
                return;
            }
            message.error(error.message || 'Failed to upload dataset');
        },
    });
}

