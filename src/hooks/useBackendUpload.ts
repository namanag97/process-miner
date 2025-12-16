'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/lib/stores/useAppStore';
import { useLogStore } from '@/lib/stores/useLogStore';
import { ROUTES } from '@/lib/constants';
import { formatFileSize } from '@/lib/utils';
import {
    uploadFile as apiUploadFile,
    createMapping,
    startProcessing,
    waitForJob,
    getFullAnalysis,
    type UploadResponse,
    type MappingCreate,
} from '@/lib/api';

interface UseBackendUploadOptions {
    onUploadSuccess?: (response: UploadResponse) => void;
    onUploadError?: (error: string) => void;
}

/**
 * Hook for uploading files to the backend API.
 * 
 * This replaces client-side parsing with backend processing.
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
    } = useAppStore();

    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [uploadResponse, setUploadResponse] = useState<UploadResponse | null>(null);

    // Handle file selection
    const handleFileSelected = useCallback((file: File) => {
        setSelectedFile(file);
        setError(null);
        setUploadResponse(null);

        // Store file info
        setUploadedFile({
            name: file.name,
            size: file.size,
            type: file.type,
            rawData: null,
        });

        addLog('info', `📁 File selected: ${file.name} (${formatFileSize(file.size)})`);
    }, [setUploadedFile, addLog]);

    // Handle file upload to backend
    const handleUpload = useCallback(async () => {
        if (!selectedFile) {
            addLog('error', '❌ No file selected');
            return;
        }

        setIsUploading(true);
        setError(null);
        setJobStatus('uploading');
        setJobProgress(0, 'Uploading file...');
        addLog('info', `📤 Uploading: ${selectedFile.name}`);

        try {
            // Upload to backend
            const response = await apiUploadFile(selectedFile);

            setUploadResponse(response);
            setUploadId(response.upload_id);
            setBackendColumns(response.columns);

            // Also set parsed data for compatibility with existing UI
            setParsedData({
                headers: response.columns.map(c => c.name),
                rows: response.columns.map(c => {
                    const row: Record<string, string> = {};
                    row[c.name] = c.sample_values[0] || '';
                    return row;
                }),
                rowCount: response.row_count,
            });

            setCurrentStep(2);
            setJobStatus('idle');
            setJobProgress(100, 'Upload complete');

            addLog('success', `✅ Uploaded: ${response.row_count} rows, ${response.columns.length} columns`);
            addLog('info', `📊 Detected columns: ${response.columns.map(c => c.name).join(', ')}`);

            options.onUploadSuccess?.(response);

        } catch (err) {
            const message = err instanceof Error ? err.message : 'Upload failed';
            setError(message);
            setJobStatus('error');
            addLog('error', `❌ Upload failed: ${message}`);
            options.onUploadError?.(message);
        } finally {
            setIsUploading(false);
        }
    }, [
        selectedFile,
        addLog,
        setUploadId,
        setBackendColumns,
        setParsedData,
        setCurrentStep,
        setJobStatus,
        setJobProgress,
        options
    ]);

    // Handle file removal
    const handleRemove = useCallback(() => {
        setSelectedFile(null);
        setError(null);
        setUploadResponse(null);
        setUploadedFile(null);
        setUploadId(null);
        setBackendColumns([]);
        setParsedData(null);
        clearLogs();
    }, [setUploadedFile, setUploadId, setBackendColumns, setParsedData, clearLogs]);

    // Handle reset
    const handleReset = useCallback(() => {
        handleRemove();
    }, [handleRemove]);

    // Navigate to configure
    const handleContinue = useCallback(() => {
        router.push(ROUTES.CONFIGURE);
    }, [router]);

    return {
        // State
        selectedFile,
        isUploading,
        uploadProgress,
        error,
        uploadResponse,

        // Actions
        handleFileSelected,
        handleUpload,
        handleRemove,
        handleReset,
        handleContinue,

        // Computed
        hasFile: !!selectedFile,
        hasUploadResponse: !!uploadResponse,
        canUpload: !!selectedFile && !isUploading,
    };
}
