'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/lib/stores/useAppStore';
import { useLogStore } from '@/lib/stores/useLogStore';
import { ROUTES } from '@/lib/constants';
import { formatFileSize } from '@/lib/utils';
import { useUploadFile } from '@/lib/api/queries/useUploads';
import type { UploadResponse } from '@/lib/api';
import { createLogger } from '@/lib/debug-logger';

const logger = createLogger('backend-upload');

interface UseBackendUploadOptions {
    onUploadSuccess?: (response: UploadResponse) => void;
    onUploadError?: (error: string) => void;
}

/**
 * Hook for uploading files to the backend API.
 * 
 * Uses React Query mutations for proper state management and caching.
 * The backend detects columns and types, which are then used
 * for the column mapping step.
 */
export function useBackendUpload(options: UseBackendUploadOptions = {}) {
    const router = useRouter();
    const addLog = useLogStore((state) => state.addLog);
    const clearLogs = useLogStore((state) => state.clearLogs);

    const {
        setUploadedFile,
        setUploadId,
        setBackendColumns,
        setParsedData,
        setCurrentStep,
        setJobStatus,
        setJobProgress,
        sessionId,
    } = useAppStore();

    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    // React Query mutation for upload
    const uploadMutation = useUploadFile({
        onSuccess: (response) => {
            setUploadId(response.upload_id);
            setBackendColumns(response.columns);

            // Create proper preview rows from column sample values
            const maxSamples = Math.max(...response.columns.map(c => c.sample_values.length), 0);
            const previewRows: Record<string, string>[] = [];

            for (let i = 0; i < maxSamples; i++) {
                const row: Record<string, string> = {};
                response.columns.forEach(col => {
                    row[col.name] = col.sample_values[i] || '';
                });
                previewRows.push(row);
            }

            // Also set parsed data for compatibility with existing UI
            setParsedData({
                headers: response.columns.map(c => c.name),
                rows: previewRows,
                rowCount: response.row_count,
            });

            setCurrentStep(2);
            setJobStatus('idle');
            setJobProgress(100, 'Upload complete');

            logger.info('Upload successful', {
                sessionId,
                uploadId: response.upload_id,
                rowCount: response.row_count,
                columnCount: response.columns.length,
                columns: response.columns.map(c => c.name),
            });
            addLog('success', `✅ [Upload: ${response.upload_id.slice(0, 8)}] ${response.row_count} rows, ${response.columns.length} columns`);
            addLog('info', `📊 Detected columns: ${response.columns.map(c => c.name).join(', ')}`);

            options.onUploadSuccess?.(response);
        },
        onError: (error) => {
            const message = error.message || 'Upload failed';
            setJobStatus('error');
            addLog('error', `❌ Upload failed: ${message}`);
            options.onUploadError?.(message);
        },
    });

    // Handle file selection
    const handleFileSelected = useCallback((file: File) => {
        setSelectedFile(file);
        uploadMutation.reset();

        // Store file info
        setUploadedFile({
            name: file.name,
            size: file.size,
            type: file.type,
            rawData: null,
        });

        logger.info('File selected', {
            sessionId,
            fileName: file.name,
            fileSize: file.size,
            fileType: file.type,
        });
        addLog('info', `📁 [Session: ${sessionId.slice(0, 8)}] File selected: ${file.name} (${formatFileSize(file.size)})`);
    }, [setUploadedFile, addLog, sessionId, uploadMutation]);

    // Handle file upload to backend
    const handleUpload = useCallback(() => {
        console.log('[useBackendUpload] handleUpload called');
        if (!selectedFile) {
            console.error('[useBackendUpload] No file selected');
            addLog('error', '❌ No file selected');
            return;
        }

        setJobStatus('uploading');
        setJobProgress(0, 'Uploading file...');

        console.log('[useBackendUpload] Starting upload mutation for file:', selectedFile.name);
        logger.info('Starting upload', {
            sessionId,
            fileName: selectedFile.name,
            fileSize: selectedFile.size,
        });
        addLog('info', `📤 [Session: ${sessionId.slice(0, 8)}] Uploading: ${selectedFile.name}`);

        uploadMutation.mutate(selectedFile);
    }, [selectedFile, addLog, setJobStatus, setJobProgress, sessionId, uploadMutation]);

    // Handle file removal
    const handleRemove = useCallback(() => {
        setSelectedFile(null);
        uploadMutation.reset();
        setUploadedFile(null);
        setUploadId(null);
        setBackendColumns([]);
        setParsedData(null);
        clearLogs();
    }, [setUploadedFile, setUploadId, setBackendColumns, setParsedData, clearLogs, uploadMutation]);

    // Handle reset
    const handleReset = useCallback(() => {
        handleRemove();
    }, [handleRemove]);

    // Navigate to configure
    const handleContinue = useCallback(() => {
        router.push(ROUTES.CONFIGURE);
    }, [router]);

    return {
        // State from React Query
        selectedFile,
        isUploading: uploadMutation.isPending,
        uploadProgress: uploadMutation.isPending ? 50 : (uploadMutation.isSuccess ? 100 : 0),
        error: uploadMutation.error?.message ?? null,
        uploadResponse: uploadMutation.data ?? null,

        // Actions
        handleFileSelected,
        handleUpload,
        handleRemove,
        handleReset,
        handleContinue,

        // Computed
        hasFile: !!selectedFile,
        hasUploadResponse: !!uploadMutation.data,
        canUpload: !!selectedFile && !uploadMutation.isPending,
    };
}
