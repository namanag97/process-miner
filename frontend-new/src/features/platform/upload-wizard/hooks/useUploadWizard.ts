/**
 * useUploadWizard - State management hook for 5-step upload wizard
 * 
 * Manages:
 * - Step navigation with validation
 * - File upload state
 * - Preview data fetching
 * - Column mapping state
 * - Processing job status
 * 
 * Supports: Navigation away and back without data loss
 */

import { useState, useCallback, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { message } from 'antd';
import { sdk } from '@/api/sdk';
import { devLog } from '../../../../shared/ui/DevConsole';
import type {
    WizardStep,
    WizardState,
    DataPreview,
    SheetsResponse,
    ColumnMapping
} from '../types';

interface PresignedUploadResponse {
    upload_url: string;
    storage_key: string;
    dataset_id: string;
    expires_in: number;
}

// API helpers using SDK
async function fetchPreview(datasetId: string, rows = 10): Promise<DataPreview> {
    console.log('[API:fetchPreview] Request started', { datasetId, rows });
    devLog.info('API:fetchPreview', 'Fetching dataset preview', { datasetId, rows });
    try {
        const data = await sdk.datasets.getPreview(datasetId, rows);
        console.log('[API:fetchPreview] Success', { columns: data.columns?.length, rows: data.rows?.length });
        devLog.action('API:fetchPreview', 'Preview fetched', { columns: data.columns?.length });
        return data;
    } catch (error) {
        console.error('[API:fetchPreview] Request failed', error);
        devLog.error('API:fetchPreview', 'Failed to fetch preview', { error });
        throw error;
    }
}

async function fetchSheets(datasetId: string): Promise<SheetsResponse> {
    console.log('[API:fetchSheets] Request started', { datasetId });
    devLog.info('API:fetchSheets', 'Fetching dataset sheets', { datasetId });
    try {
        const data = await sdk.datasets.getSheets(datasetId);
        console.log('[API:fetchSheets] Success', { sheets: data.sheets?.length });
        devLog.action('API:fetchSheets', 'Sheets fetched', { sheetCount: data.sheets?.length });
        return data;
    } catch (error) {
        console.error('[API:fetchSheets] Request failed', error);
        devLog.error('API:fetchSheets', 'Failed to fetch sheets', { error });
        throw error;
    }
}

async function submitMapping(datasetId: string, mapping: ColumnMapping): Promise<void> {
    console.log('[API:submitMapping] Request started', { datasetId, mapping });
    devLog.info('API:submitMapping', 'Submitting column mapping', { datasetId });
    try {
        // Convert wizard mapping format to SDK format
        const sdkMapping = {
            caseId: mapping.case_id_column,
            activity: mapping.activity_column,
            timestamp: mapping.timestamp_column,
            resource: mapping.resource_column,
        };
        await sdk.datasets.setMapping(datasetId, sdkMapping);
        console.log('[API:submitMapping] Success');
        devLog.action('API:submitMapping', 'Mapping submitted successfully');
    } catch (err: unknown) {
        const error = err instanceof Error ? err : new Error(String(err));
        console.error('[API:submitMapping] Exception thrown', { message: error.message, datasetId });
        devLog.error('API:submitMapping', `Exception: ${error.message}`, { datasetId });
        throw error;
    }
}

interface IngestionResponse {
    id: string;
    status: string;
    progress?: number;
    error?: string;
    result?: Record<string, unknown>;
}

async function startIngestion(datasetId: string, mapping: ColumnMapping): Promise<IngestionResponse> {
    console.log('[API:startIngestion] Request started', { datasetId });
    devLog.info('API:startIngestion', 'Starting dataset ingestion', { datasetId });
    try {
        // First submit the mapping to transition status to MAPPED
        await submitMapping(datasetId, mapping);

        // Then start ingestion
        const data = await sdk.datasets.ingest(datasetId);
        console.log('[API:startIngestion] Success', data);
        devLog.action('API:startIngestion', 'Ingestion started successfully', data);
        return data as IngestionResponse;
    } catch (err: unknown) {
        const error = err instanceof Error ? err : new Error(String(err));
        console.error('[API:startIngestion] Exception thrown', { message: error.message, datasetId });
        devLog.error('API:startIngestion', `Exception: ${error.message}`, { datasetId });
        throw error;
    }
}

async function checkJobStatus(jobId: string): Promise<{ id: string; status: string; progress?: number; error?: string }> {
    const data = await sdk.jobs.get(jobId);
    return { ...data, id: data.id ?? jobId };
}

async function getPresignedUrl(filename: string, fileSize: number, projectId: string, contentType = 'text/csv'): Promise<PresignedUploadResponse> {
    console.log('[API] getPresignedUrl request', { filename, fileSize, projectId, contentType });
    devLog.info('API', 'Requesting presigned upload URL', { filename, fileSize, projectId });
    try {
        const data = await sdk.datasets.getPresignedUrl({
            filename,
            fileSizeBytes: fileSize,
            projectId,
            contentType,
        });
        console.log('[API] getPresignedUrl success', { datasetId: data.dataset_id });
        devLog.action('API', 'Presigned URL received', { datasetId: data.dataset_id });
        return data;
    } catch (err: unknown) {
        const error = err instanceof Error ? err : new Error(String(err));
        console.error('[API] getPresignedUrl failed', { error: error.message });
        devLog.error('API', `Presigned URL request failed: ${error.message}`, { error: error.message });
        throw error;
    }
}

async function triggerValidation(datasetId: string): Promise<{ task_id: string }> {
    console.log('[API] triggerValidation request', { datasetId });
    devLog.info('API', 'Triggering dataset validation', { datasetId });
    try {
        const data = await sdk.datasets.triggerValidation(datasetId);
        console.log('[API] triggerValidation success', data);
        devLog.action('API', 'Dataset validation triggered', data);
        return data;
    } catch (err: unknown) {
        const error = err instanceof Error ? err : new Error(String(err));
        console.error('[API] triggerValidation failed', { error: error.message });
        devLog.error('API', 'Validation trigger failed', { error: error.message });
        throw error;
    }
}

const STEP_ORDER: WizardStep[] = ['upload', 'sheets', 'configure', 'mapping', 'finalize'];

export function useUploadWizard(_projectId: string, initialDatasetId?: string) {
    const [state, setState] = useState<WizardState>({
        currentStep: initialDatasetId ? 'sheets' : 'upload',
        datasetId: initialDatasetId || null,
        filename: null,
        fileSize: null,
        selectedSheet: null,
        preview: null,
        mapping: null,
        jobId: null,
        error: null,
        isLoading: false,
    });

    // Track sync completion to skip polling (when Temporal unavailable)
    const [syncJobResult, setSyncJobResult] = useState<IngestionResponse | null>(null);

    // Fetch sheets when we have a dataset
    const { data: sheetsData, isLoading: isSheetsLoading } = useQuery({
        queryKey: ['wizard', 'sheets', state.datasetId],
        queryFn: () => fetchSheets(state.datasetId!),
        enabled: !!state.datasetId && state.currentStep === 'sheets',
    });

    // Fetch preview when on configure step
    const { data: previewData, isLoading: isPreviewLoading } = useQuery({
        queryKey: ['wizard', 'preview', state.datasetId],
        queryFn: () => fetchPreview(state.datasetId!),
        enabled: !!state.datasetId && state.currentStep === 'configure',
    });

    // Update state when preview loads
    useEffect(() => {
        if (previewData) {
            setState(prev => ({ ...prev, preview: previewData }));
        }
    }, [previewData]);

    // Poll job status when finalizing with adaptive intervals
    // Skip polling if we have immediate sync result (Temporal unavailable fallback)
    const { data: polledJobStatus } = useQuery({
        queryKey: ['wizard', 'job', state.jobId],
        queryFn: () => checkJobStatus(state.jobId!),
        enabled: !!state.jobId && state.currentStep === 'finalize' && !syncJobResult,
        refetchInterval: (query) => {
            const status = query.state.data?.status;
            // Stop polling on terminal states
            if (status === 'completed' || status === 'failed' || status === 'cancelled') {
                return false;
            }
            // Adaptive polling based on data age
            // TanStack Query tracks dataUpdatedAt, use it to estimate how long polling has been going
            const dataUpdatedAt = query.state.dataUpdatedAt;

            // Use dataUpdatedAt to infer elapsed time (rough estimate)
            // If data was recently updated, we're probably still in early phase
            const timeSinceUpdate = dataUpdatedAt ? Date.now() - dataUpdatedAt : 0;

            // Progressive slowdown based on accumulated time
            // We track this implicitly through query state
            if (timeSinceUpdate < 10000 || !dataUpdatedAt) return 2000;   // Early phase: every 2s
            if (timeSinceUpdate < 60000) return 4000;                      // Mid phase: every 4s
            return 8000;                                                    // Late phase: every 8s
        },
    });

    // Use sync result if available, otherwise use polled status
    const jobStatus = syncJobResult || polledJobStatus;

    // Navigation functions
    const goToStep = useCallback((step: WizardStep) => {
        setState(prev => ({ ...prev, currentStep: step, error: null }));
    }, []);

    const nextStep = useCallback(() => {
        const currentIndex = STEP_ORDER.indexOf(state.currentStep);
        if (currentIndex < STEP_ORDER.length - 1) {
            goToStep(STEP_ORDER[currentIndex + 1]);
        }
    }, [state.currentStep, goToStep]);

    const prevStep = useCallback(() => {
        const currentIndex = STEP_ORDER.indexOf(state.currentStep);
        if (currentIndex > 0) {
            goToStep(STEP_ORDER[currentIndex - 1]);
        }
    }, [state.currentStep, goToStep]);

    // Upload complete handler
    const setUploadResult = useCallback((datasetId: string, filename: string, fileSize: number) => {
        setState(prev => ({
            ...prev,
            datasetId,
            filename,
            fileSize,
            currentStep: 'sheets',
        }));
    }, []);

    // Sheet selection
    const selectSheet = useCallback((sheetName: string) => {
        setState(prev => ({ ...prev, selectedSheet: sheetName }));
    }, []);

    // Set column mapping
    const setMapping = useCallback((mapping: ColumnMapping) => {
        setState(prev => ({ ...prev, mapping }));
    }, []);

    // Start analysis mutation
    const startAnalysisMutation = useMutation({
        mutationFn: async () => {
            if (!state.datasetId || !state.mapping) {
                throw new Error('Dataset and mapping required');
            }
            return startIngestion(state.datasetId, state.mapping);
        },
        onSuccess: (data) => {
            // Check if sync fallback completed immediately
            if (data.status === 'completed') {
                devLog.info('UploadWizard', 'Sync ingestion completed immediately', data);
                setSyncJobResult(data);
                message.success('Processing complete!');
            } else {
                message.info('Processing started...');
            }
            setState(prev => ({
                ...prev,
                jobId: data.id,
                currentStep: 'finalize',
            }));
        },
        onError: (error: Error) => {
            message.error(error.message);
            setState(prev => ({ ...prev, error: error.message }));
        },
    });

    const startAnalysis = useCallback(() => {
        startAnalysisMutation.mutate();
    }, [startAnalysisMutation]);

    // Skip sheets step for CSV (auto-select)
    useEffect(() => {
        if (sheetsData && state.currentStep === 'sheets') {
            // CSV has single sheet, auto-skip
            if (sheetsData.sheets.length === 1) {
                setState(prev => ({
                    ...prev,
                    selectedSheet: sheetsData.sheets[0].name,
                    currentStep: 'configure',
                }));
            }
        }
    }, [sheetsData, state.currentStep]);

    return {
        ...state,
        sheetsData,
        jobStatus,
        isLoading: isSheetsLoading || isPreviewLoading || startAnalysisMutation.isPending,

        // Actions
        goToStep,
        nextStep,
        prevStep,
        setUploadResult,
        selectSheet,
        setMapping,

        // Direct Upload Method (for local development without MinIO)
        uploadFileDirect: useCallback(async (file: File) => {
            console.log('[UploadWizard:uploadFileDirect] Upload started', {
                fileName: file.name,
                fileSize: file.size,
                fileType: file.type,
                projectId: _projectId
            });
            devLog.action('UploadWizard:uploadFileDirect', 'Starting direct upload flow', {
                fileName: file.name,
                fileSize: file.size,
                projectId: _projectId
            });

            try {
                setState(prev => ({ ...prev, isLoading: true, error: null }));
                devLog.state('UploadWizard:uploadFileDirect', 'Upload state: loading', { isLoading: true });

                console.log('[UploadWizard:uploadFileDirect] Uploading file directly to backend...');
                devLog.info('UploadWizard:uploadFileDirect', 'Uploading via SDK');

                const data = await sdk.datasets.upload({
                    projectId: _projectId,
                    file,
                    asyncStore: true, // Store without parsing
                });

                console.log('[UploadWizard:uploadFileDirect] Upload successful', data);
                devLog.action('UploadWizard:uploadFileDirect', 'Direct upload completed', { datasetId: data.id });

                // Update state
                setState(prev => ({
                    ...prev,
                    datasetId: data.id,
                    filename: file.name,
                    fileSize: file.size,
                    currentStep: 'sheets',
                    isLoading: false,
                }));

                return data.id;
            } catch (err: unknown) {
                const error = err instanceof Error ? err : new Error(String(err));
                console.error('[UploadWizard:uploadFileDirect] Exception thrown', { message: error.message, fileName: file.name });
                devLog.error('UploadWizard:uploadFileDirect', `Upload failed: ${error.message}`, { fileName: file.name });
                const msg = error.message || 'Upload failed';
                setState(prev => ({ ...prev, error: msg, isLoading: false }));
                throw error;
            }
        }, [_projectId]),

        // Presigned Upload Method (requires MinIO/S3)
        uploadFilePresigned: useCallback(async (file: File) => {
            const fileInfo = {
                fileName: file.name,
                fileSize: file.size,
                fileType: file.type,
                projectId: _projectId
            };
            console.log('[UploadWizard:uploadFilePresigned] Upload started', fileInfo);
            devLog.action('UploadWizard:uploadFilePresigned', 'Starting presigned upload flow', fileInfo);

            try {
                setState(prev => ({ ...prev, isLoading: true, error: null }));
                console.log('[UploadWizard:uploadFilePresigned] State updated: isLoading=true');
                devLog.state('UploadWizard:uploadFilePresigned', 'Upload state: loading', { isLoading: true });

                // 1. Get Presigned URL
                console.log('[UploadWizard:uploadFilePresigned] Step 1: Requesting presigned URL...');
                devLog.info('UploadWizard:uploadFilePresigned', 'Step 1/3: Getting presigned URL');
                const presignedData = await getPresignedUrl(
                    file.name,
                    file.size,
                    _projectId,
                    file.type || 'text/csv' // Fallback for some browsers
                );
                const urlData = {
                    datasetId: presignedData.dataset_id,
                    expiresIn: presignedData.expires_in,
                    hasUploadUrl: !!presignedData.upload_url
                };
                console.log('[UploadWizard:uploadFilePresigned] Presigned URL received', urlData);
                devLog.action('UploadWizard:uploadFilePresigned', 'Presigned URL obtained', urlData);

                // 2. Upload directly to storage (PUT)
                // Note: We don't use instrumentedFetch here to avoid adding auth headers to S3/MinIO request
                // which would cause signature mismatch
                console.log('[UploadWizard:uploadFilePresigned] Step 2: Uploading file to storage...');
                console.log('[UploadWizard:uploadFilePresigned] Upload URL:', presignedData.upload_url);
                console.log('[UploadWizard:uploadFilePresigned] File details:', {
                    name: file.name,
                    size: file.size,
                    type: file.type
                });
                devLog.info('UploadWizard:uploadFilePresigned', 'Step 2/3: Uploading to storage', {
                    datasetId: presignedData.dataset_id,
                    uploadUrl: presignedData.upload_url.substring(0, 100) + '...', // Truncate for security
                    fileSize: file.size,
                    fileType: file.type
                });

                let uploadRes;
                try {
                    uploadRes = await fetch(presignedData.upload_url, {
                        method: 'PUT',
                        body: file,
                        headers: {
                            'Content-Type': file.type || 'text/csv',
                        },
                    });
                } catch (fetchError: unknown) {
                    const error = fetchError instanceof Error ? fetchError : new Error(String(fetchError));
                    const fetchErrorData = {
                        message: error.message,
                        name: error.name,
                        stack: error.stack,
                        uploadUrl: presignedData.upload_url,
                        urlHost: new URL(presignedData.upload_url).host,
                        urlProtocol: new URL(presignedData.upload_url).protocol,
                    };
                    console.error('[UploadWizard:uploadFilePresigned] Fetch to storage failed', fetchErrorData);
                    devLog.error('UploadWizard:uploadFilePresigned', `Network error during storage upload: ${error.message}`, fetchErrorData);
                    throw new Error(`Storage upload failed: ${error.message}`);
                }

                const storageResData = {
                    status: uploadRes.status,
                    statusText: uploadRes.statusText,
                    ok: uploadRes.ok,
                    headers: Object.fromEntries((uploadRes.headers as any).entries())
                };
                console.log('[UploadWizard:uploadFilePresigned] Storage upload response', storageResData);
                devLog.info('UploadWizard', 'Storage upload response received', storageResData);

                if (!uploadRes.ok) {
                    const errorText = await uploadRes.text().catch(() => 'No error details');
                    const errorData = {
                        status: uploadRes.status,
                        statusText: uploadRes.statusText,
                        errorText,
                        headers: Object.fromEntries((uploadRes.headers as any).entries())
                    };
                    console.error('[UploadWizard:uploadFilePresigned] Storage upload failed', errorData);
                    devLog.error('UploadWizard', `Storage upload failed (${uploadRes.status})`, errorData);
                    throw new Error(`Failed to upload file to storage: ${uploadRes.status} ${uploadRes.statusText}`);
                }

                console.log('[UploadWizard:uploadFilePresigned] File uploaded to storage successfully');
                devLog.action('UploadWizard', 'File uploaded to storage', { datasetId: presignedData.dataset_id });

                // 3. Trigger Validation
                console.log('[UploadWizard:uploadFilePresigned] Step 3: Triggering validation...', {
                    datasetId: presignedData.dataset_id
                });
                devLog.info('UploadWizard', 'Step 3/3: Triggering validation', { datasetId: presignedData.dataset_id });
                const validationResult = await triggerValidation(presignedData.dataset_id);
                console.log('[UploadWizard:uploadFilePresigned] Validation triggered', validationResult);

                // Update state
                console.log('[UploadWizard:uploadFilePresigned] Updating state with upload results');
                setState(prev => ({
                    ...prev,
                    datasetId: presignedData.dataset_id,
                    filename: file.name,
                    fileSize: file.size,
                    currentStep: 'sheets',
                    isLoading: false,
                }));

                const completeData = {
                    datasetId: presignedData.dataset_id,
                    nextStep: 'sheets'
                };
                console.log('[UploadWizard:uploadFilePresigned] Upload complete', completeData);
                devLog.action('UploadWizard', 'Upload flow completed successfully', completeData);

                return presignedData.dataset_id;
            } catch (err: unknown) {
                const error = err instanceof Error ? err : new Error(String(err));
                const errorData = {
                    error: error.message,
                    message: error.message,
                    stack: error.stack,
                    fileName: file.name
                };
                console.error('[UploadWizard:uploadFilePresigned] Upload failed', errorData);
                devLog.error('UploadWizard', `Upload failed: ${error.message}`, errorData);
                const msg = error.message || 'Upload failed';
                setState(prev => ({ ...prev, error: msg, isLoading: false }));
                throw error;
            }
        }, [_projectId]),
        startAnalysis,

        // Helpers
        stepIndex: STEP_ORDER.indexOf(state.currentStep),
        totalSteps: STEP_ORDER.length,
        canGoBack: STEP_ORDER.indexOf(state.currentStep) > 0,
        canGoNext: state.currentStep !== 'finalize',
    };
}
