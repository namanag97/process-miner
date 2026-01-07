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
import { instrumentedFetch } from '@lumina/design-system';
import { env } from '../../../../config/env';
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

const API_BASE = env.API_BASE_URL;

// API helpers (using instrumentedFetch for DevConsole logging)
async function fetchPreview(datasetId: string, rows: number = 10): Promise<DataPreview> {
    console.log('[API:fetchPreview] Request started', { datasetId, rows });
    devLog.info('API:fetchPreview', 'Fetching dataset preview', { datasetId, rows });
    const res = await instrumentedFetch(`${API_BASE}/api/v1/datasets/${datasetId}/preview?rows=${rows}`);
    if (!res.ok) {
        console.error('[API:fetchPreview] Request failed', { status: res.status });
        devLog.error('API:fetchPreview', 'Failed to fetch preview', { status: res.status });
        throw new Error('Failed to fetch preview');
    }
    const data = await res.json();
    console.log('[API:fetchPreview] Success', { columns: data.columns?.length, rows: data.rows?.length });
    devLog.action('API:fetchPreview', 'Preview fetched', { columns: data.columns?.length });
    return data;
}

async function fetchSheets(datasetId: string): Promise<SheetsResponse> {
    console.log('[API:fetchSheets] Request started', { datasetId });
    devLog.info('API:fetchSheets', 'Fetching dataset sheets', { datasetId });
    const res = await instrumentedFetch(`${API_BASE}/api/v1/datasets/${datasetId}/sheets`);
    if (!res.ok) {
        console.error('[API:fetchSheets] Request failed', { status: res.status });
        devLog.error('API:fetchSheets', 'Failed to fetch sheets', { status: res.status });
        throw new Error('Failed to fetch sheets');
    }
    const data = await res.json();
    console.log('[API:fetchSheets] Success', { sheets: data.sheets?.length });
    devLog.action('API:fetchSheets', 'Sheets fetched', { sheetCount: data.sheets?.length });
    return data;
}

async function startIngestion(datasetId: string, mapping: ColumnMapping): Promise<{ id: string }> {
    console.log('[API:startIngestion] Request started', {
        datasetId,
        mapping,
        url: `${API_BASE}/api/v1/datasets/${datasetId}/ingest`
    });
    devLog.info('API:startIngestion', 'Starting dataset ingestion', { datasetId, mapping });

    try {
        const res = await instrumentedFetch(`${API_BASE}/api/v1/datasets/${datasetId}/ingest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mapping),
        });

        console.log('[API:startIngestion] Response received', {
            status: res.status,
            statusText: res.statusText,
            ok: res.ok
        });

        if (!res.ok) {
            const errorData = await res.json().catch(() => ({ detail: 'Failed to start analysis' }));
            console.error('[API:startIngestion] Request failed', errorData);
            devLog.error('API:startIngestion', `Ingestion failed: ${errorData.detail}`, errorData);
            throw new Error(errorData.detail || 'Failed to start analysis');
        }

        const data = await res.json();
        console.log('[API:startIngestion] Success', data);
        devLog.action('API:startIngestion', 'Ingestion started successfully', data);
        return data;
    } catch (err: any) {
        const errorInfo = {
            message: err.message,
            name: err.name,
            stack: err.stack,
            datasetId
        };
        console.error('[API:startIngestion] Exception thrown', errorInfo);
        devLog.error('API:startIngestion', `Exception: ${err.message}`, errorInfo);
        throw err;
    }
}

async function checkJobStatus(jobId: string): Promise<{ id: string; status: string; progress?: number; error?: string }> {
    const res = await instrumentedFetch(`${API_BASE}/api/v1/jobs/${jobId}`);
    if (!res.ok) throw new Error('Failed to check job status');
    const data = await res.json();
    return { id: jobId, ...data };
}

async function getPresignedUrl(filename: string, fileSize: number, projectId: string, contentType: string = 'text/csv'): Promise<PresignedUploadResponse> {
    const reqData = {
        filename,
        fileSize,
        projectId,
        contentType,
        url: `${API_BASE}/api/v1/datasets/presign`
    };
    console.log('[API] getPresignedUrl request', reqData);
    devLog.info('API', 'Requesting presigned upload URL', reqData);

    const res = await instrumentedFetch(`${API_BASE}/api/v1/datasets/presign`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            filename,
            file_size_bytes: fileSize,
            project_id: projectId,
            content_type: contentType
        }),
    });

    const resData = {
        status: res.status,
        statusText: res.statusText,
        ok: res.ok
    };
    console.log('[API] getPresignedUrl response', resData);

    if (!res.ok) {
        const err = await res.json();
        const errorData = { status: res.status, error: err };
        console.error('[API] getPresignedUrl failed', errorData);
        devLog.error('API', `Presigned URL request failed: ${err.detail || 'Unknown error'}`, errorData);
        throw new Error(err.detail || 'Failed to get upload URL');
    }

    const data = await res.json();
    const successData = {
        hasUploadUrl: !!data.upload_url,
        datasetId: data.dataset_id,
        expiresIn: data.expires_in
    };
    console.log('[API] getPresignedUrl success', successData);
    devLog.action('API', 'Presigned URL received', successData);

    return data;
}

async function triggerValidation(datasetId: string): Promise<{ task_id: string }> {
    const reqData = {
        datasetId,
        url: `${API_BASE}/api/v1/datasets/${datasetId}/uploaded`
    };
    console.log('[API] triggerValidation request', reqData);
    devLog.info('API', 'Triggering dataset validation', reqData);

    const res = await instrumentedFetch(`${API_BASE}/api/v1/datasets/${datasetId}/uploaded`, {
        method: 'POST',
    });

    const resData = {
        status: res.status,
        statusText: res.statusText,
        ok: res.ok
    };
    console.log('[API] triggerValidation response', resData);

    if (!res.ok) {
        const errorText = await res.text().catch(() => 'No error details');
        const errorData = {
            status: res.status,
            statusText: res.statusText,
            errorText
        };
        console.error('[API] triggerValidation failed', errorData);
        devLog.error('API', 'Validation trigger failed', errorData);
        throw new Error('Failed to trigger validation');
    }

    const data = await res.json();
    console.log('[API] triggerValidation success', data);
    devLog.action('API', 'Dataset validation triggered', data);
    return data;
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

    // Poll job status when finalizing
    const { data: jobStatus } = useQuery({
        queryKey: ['wizard', 'job', state.jobId],
        queryFn: () => checkJobStatus(state.jobId!),
        enabled: !!state.jobId && state.currentStep === 'finalize',
        refetchInterval: (query) => {
            const status = query.state.data?.status;
            if (status === 'completed' || status === 'failed' || status === 'cancelled') {
                return false;
            }
            return 2000; // Poll every 2s
        },
    });

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
            setState(prev => ({
                ...prev,
                jobId: data.id,
                currentStep: 'finalize',
            }));
            message.info('Processing started...');
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

                // Create FormData for multipart upload
                const formData = new FormData();
                formData.append('file', file);
                formData.append('project_id', _projectId);
                formData.append('async_store', 'true'); // Store without parsing

                console.log('[UploadWizard:uploadFileDirect] Uploading file directly to backend...');
                devLog.info('UploadWizard:uploadFileDirect', 'Uploading to /api/v1/datasets/');

                const res = await instrumentedFetch(`${API_BASE}/api/v1/datasets/`, {
                    method: 'POST',
                    body: formData,
                    // Don't set Content-Type - browser will set it with boundary
                });

                if (!res.ok) {
                    const errorData = await res.json().catch(() => ({ detail: 'Upload failed' }));
                    console.error('[UploadWizard:uploadFileDirect] Upload failed', errorData);
                    devLog.error('UploadWizard:uploadFileDirect', `Upload failed: ${errorData.detail}`, errorData);
                    throw new Error(errorData.detail || 'Upload failed');
                }

                const data = await res.json();
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
            } catch (err: any) {
                const errorData = {
                    error: err,
                    message: err.message,
                    stack: err.stack,
                    fileName: file.name
                };
                console.error('[UploadWizard:uploadFileDirect] Exception thrown', errorData);
                devLog.error('UploadWizard:uploadFileDirect', `Upload failed: ${err.message}`, errorData);
                const msg = err.message || 'Upload failed';
                setState(prev => ({ ...prev, error: msg, isLoading: false }));
                throw err;
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
                } catch (fetchError: any) {
                    const fetchErrorData = {
                        message: fetchError.message,
                        name: fetchError.name,
                        stack: fetchError.stack,
                        uploadUrl: presignedData.upload_url,
                        urlHost: new URL(presignedData.upload_url).host,
                        urlProtocol: new URL(presignedData.upload_url).protocol,
                    };
                    console.error('[UploadWizard:uploadFilePresigned] Fetch to storage failed', fetchErrorData);
                    devLog.error('UploadWizard:uploadFilePresigned', `Network error during storage upload: ${fetchError.message}`, fetchErrorData);
                    throw new Error(`Storage upload failed: ${fetchError.message}`);
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
            } catch (err: any) {
                const errorData = {
                    error: err,
                    message: err.message,
                    stack: err.stack,
                    fileName: file.name
                };
                console.error('[UploadWizard:uploadFilePresigned] Upload failed', errorData);
                devLog.error('UploadWizard', `Upload failed: ${err.message}`, errorData);
                const msg = err.message || 'Upload failed';
                setState(prev => ({ ...prev, error: msg, isLoading: false }));
                throw err;
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
