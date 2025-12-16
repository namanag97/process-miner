'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/lib/stores/useAppStore';
import { useLogStore } from '@/lib/stores/useLogStore';
import { parseCSV, parseXES } from '@/lib/parsers';
import { ROUTES, FILE_EXTENSIONS } from '@/lib/constants';
import { formatFileSize } from '@/lib/utils';

interface UseFileUploadOptions {
    onParseSuccess?: () => void;
    onParseError?: (error: string) => void;
}

export function useFileUpload(options: UseFileUploadOptions = {}) {
    const router = useRouter();
    const addLog = useLogStore((state) => state.addLog);
    const clearLogs = useLogStore((state) => state.clearLogs);
    const {
        parsedData,
        setParsedData,
        setCurrentStep,
        setUploadedFile,
        uploadedFile
    } = useAppStore();

    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isParsing, setIsParsing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Handle file selection
    const handleFileSelected = useCallback((file: File) => {
        setSelectedFile(file);
        setError(null);

        // Store file info in app store
        setUploadedFile({
            name: file.name,
            size: file.size,
            type: file.type,
            rawData: null,
        });

        addLog('info', `📁 File selected: ${file.name} (${formatFileSize(file.size)})`);
    }, [setUploadedFile, addLog]);

    // Handle file parsing
    const handleParse = useCallback(async () => {
        if (!selectedFile) {
            addLog('error', '❌ No file selected');
            return;
        }

        setIsParsing(true);
        setError(null);
        addLog('info', `🔄 Starting to parse: ${selectedFile.name}`);

        const isXES = selectedFile.name.toLowerCase().endsWith(FILE_EXTENSIONS.XES);
        const logCallback = (message: string, type?: 'info' | 'success' | 'error' | 'warning') => {
            addLog(type || 'info', message);
        };

        try {
            const result = isXES
                ? await parseXES(selectedFile, { onLog: logCallback })
                : await parseCSV(selectedFile, { onLog: logCallback });

            if (result.success && result.data) {
                setParsedData({
                    headers: result.data.headers,
                    rows: result.data.rows as object[],
                    rowCount: result.data.rowCount,
                });
                setCurrentStep(2);
                addLog('success', `✅ Parsed ${result.data.rowCount} rows successfully`);
                options.onParseSuccess?.();
            } else {
                const errorMsg = result.error || 'Failed to parse file';
                setError(errorMsg);
                addLog('error', `❌ Parse failed: ${errorMsg}`);
                options.onParseError?.(errorMsg);
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Unknown error';
            setError(message);
            addLog('error', `❌ Parse error: ${message}`);
            options.onParseError?.(message);
        } finally {
            setIsParsing(false);
        }
    }, [selectedFile, addLog, setParsedData, setCurrentStep, options]);

    // Handle file removal
    const handleRemove = useCallback(() => {
        setSelectedFile(null);
        setError(null);
        setParsedData(null);
        setUploadedFile(null);
        clearLogs();
    }, [setParsedData, setUploadedFile, clearLogs]);

    // Handle reset (after parsing)
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
        uploadedFile,
        parsedData,
        isParsing,
        error,

        // Actions
        handleFileSelected,
        handleParse,
        handleRemove,
        handleReset,
        handleContinue,

        // Computed
        hasFile: !!selectedFile,
        hasParsedData: !!parsedData,
        canParse: !!selectedFile && !isParsing,
    };
}
