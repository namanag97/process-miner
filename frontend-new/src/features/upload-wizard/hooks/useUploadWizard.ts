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
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import { instrumentedFetch } from '@lumina/design-system';
import { env } from '../../../config/env';
import type {
    WizardStep,
    WizardState,
    DataPreview,
    SheetsResponse,
    ColumnMapping
} from '../types';

const API_BASE = env.API_BASE_URL;

// API helpers (using instrumentedFetch for DevConsole logging)
async function fetchPreview(datasetId: string, rows: number = 10): Promise<DataPreview> {
    const res = await instrumentedFetch(`${API_BASE}/api/v1/datasets/${datasetId}/preview?rows=${rows}`);
    if (!res.ok) throw new Error('Failed to fetch preview');
    return res.json();
}

async function fetchSheets(datasetId: string): Promise<SheetsResponse> {
    const res = await instrumentedFetch(`${API_BASE}/api/v1/datasets/${datasetId}/sheets`);
    if (!res.ok) throw new Error('Failed to fetch sheets');
    return res.json();
}

async function startIngestion(datasetId: string, mapping: ColumnMapping): Promise<{ id: string }> {
    const res = await instrumentedFetch(`${API_BASE}/api/v1/datasets/${datasetId}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mapping),
    });
    if (!res.ok) throw new Error('Failed to start analysis');
    return res.json();
}

async function checkJobStatus(jobId: string): Promise<{ status: string; progress?: number; error?: string }> {
    const res = await instrumentedFetch(`${API_BASE}/api/v1/jobs/${jobId}`);
    if (!res.ok) throw new Error('Failed to check job status');
    return res.json();
}

const STEP_ORDER: WizardStep[] = ['upload', 'sheets', 'configure', 'mapping', 'finalize'];

export function useUploadWizard(projectId: string, initialDatasetId?: string) {
    const queryClient = useQueryClient();

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
        startAnalysis,

        // Helpers
        stepIndex: STEP_ORDER.indexOf(state.currentStep),
        totalSteps: STEP_ORDER.length,
        canGoBack: STEP_ORDER.indexOf(state.currentStep) > 0,
        canGoNext: state.currentStep !== 'finalize',
    };
}
