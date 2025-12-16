/**
 * Upload API Hooks
 * 
 * React Query hooks for file upload operations.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
    uploadFile,
    getUpload,
    deleteUpload,
} from '../client';
import type { UploadResponse } from '../types';

// =============================================================================
// Query Keys
// =============================================================================

export const uploadKeys = {
    all: ['uploads'] as const,
    detail: (uploadId: string) => [...uploadKeys.all, uploadId] as const,
};

// =============================================================================
// Hooks
// =============================================================================

/**
 * Mutation hook for uploading a file.
 * 
 * Usage:
 * ```tsx
 * const { mutate: upload, isPending, error } = useUploadFile({
 *   onSuccess: (data) => console.log('Uploaded:', data.upload_id),
 * });
 * upload(file);
 * ```
 */
export function useUploadFile(options?: {
    onSuccess?: (data: UploadResponse) => void;
    onError?: (error: Error) => void;
}) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (file: File) => uploadFile(file),
        onSuccess: (data) => {
            // Invalidate uploads list and set the new upload in cache
            queryClient.invalidateQueries({ queryKey: uploadKeys.all });
            queryClient.setQueryData(uploadKeys.detail(data.upload_id), data);
            options?.onSuccess?.(data);
        },
        onError: (error: Error) => {
            options?.onError?.(error);
        },
    });
}

/**
 * Query hook for fetching upload details.
 * 
 * Usage:
 * ```tsx
 * const { data: upload, isLoading } = useUpload(uploadId);
 * ```
 */
export function useUpload(uploadId: string | null) {
    return useQuery({
        queryKey: uploadId ? uploadKeys.detail(uploadId) : ['uploads', 'none'],
        queryFn: () => getUpload(uploadId!),
        enabled: !!uploadId,
    });
}

/**
 * Mutation hook for deleting an upload.
 * 
 * Usage:
 * ```tsx
 * const { mutate: remove } = useDeleteUpload();
 * remove(uploadId);
 * ```
 */
export function useDeleteUpload(options?: {
    onSuccess?: () => void;
    onError?: (error: Error) => void;
}) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (uploadId: string) => deleteUpload(uploadId),
        onSuccess: (_, uploadId) => {
            // Remove from cache and invalidate list
            queryClient.removeQueries({ queryKey: uploadKeys.detail(uploadId) });
            queryClient.invalidateQueries({ queryKey: uploadKeys.all });
            options?.onSuccess?.();
        },
        onError: (error: Error) => {
            options?.onError?.(error);
        },
    });
}
