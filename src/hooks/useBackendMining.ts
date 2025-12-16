/**
 * Hook for backend-powered process mining
 * 
 * This hook replaces the client-side mining with backend API calls.
 * It manages the full workflow: upload → map → process → analyze
 */

import { useState, useCallback } from 'react';
import {
    uploadFile,
    createMapping,
    validateMapping,
    startProcessing,
    waitForJob,
    getFullAnalysis,
    type UploadResponse,
    type MappingCreate,
    type MappingResponse,
    type ValidationResult,
    type JobResponse,
    type FullAnalysisResponse,
    type DFGResponse,
    type VariantsResponse,
    type ProcessStats,
    type Deviation,
} from '@/lib/api';
import { useLogStore } from '@/lib/stores/useLogStore';

export type MiningStep =
    | 'idle'
    | 'uploading'
    | 'uploaded'
    | 'mapping'
    | 'validating'
    | 'processing'
    | 'complete'
    | 'error';

export interface BackendMiningState {
    step: MiningStep;
    progress: number;
    progressMessage: string;
    error: string | null;

    // Backend IDs
    uploadId: string | null;
    mappingId: string | null;
    jobId: string | null;
    datasetId: string | null;

    // Upload data
    uploadInfo: UploadResponse | null;

    // Validation
    validationResult: ValidationResult | null;

    // Results
    dfg: DFGResponse | null;
    variants: VariantsResponse | null;
    stats: ProcessStats | null;
    deviations: Deviation[] | null;
}

const initialState: BackendMiningState = {
    step: 'idle',
    progress: 0,
    progressMessage: '',
    error: null,
    uploadId: null,
    mappingId: null,
    jobId: null,
    datasetId: null,
    uploadInfo: null,
    validationResult: null,
    dfg: null,
    variants: null,
    stats: null,
    deviations: null,
};

export function useBackendMining() {
    const [state, setState] = useState<BackendMiningState>(initialState);
    const addLog = useLogStore((s) => s.addLog);

    const updateState = useCallback((updates: Partial<BackendMiningState>) => {
        setState((prev) => ({ ...prev, ...updates }));
    }, []);

    /**
     * Upload a file to the backend
     */
    const upload = useCallback(async (file: File): Promise<UploadResponse | null> => {
        updateState({ step: 'uploading', progress: 0, error: null });
        addLog('info', `📤 Uploading ${file.name}...`);

        try {
            const response = await uploadFile(file);

            updateState({
                step: 'uploaded',
                progress: 100,
                uploadId: response.upload_id,
                uploadInfo: response,
            });

            addLog('success', `✅ Uploaded: ${response.row_count} rows, ${response.columns.length} columns`);
            return response;

        } catch (error) {
            const message = error instanceof Error ? error.message : 'Upload failed';
            updateState({ step: 'error', error: message });
            addLog('error', `❌ Upload failed: ${message}`);
            return null;
        }
    }, [updateState, addLog]);

    /**
     * Create and validate a column mapping
     */
    const map = useCallback(async (
        uploadId: string,
        mapping: MappingCreate
    ): Promise<MappingResponse | null> => {
        updateState({ step: 'mapping', progress: 0, error: null });
        addLog('info', '🔧 Creating column mapping...');

        try {
            // Create mapping
            const mappingResponse = await createMapping(uploadId, mapping);
            updateState({ mappingId: mappingResponse.mapping_id });
            addLog('success', '✅ Mapping created');

            // Validate
            updateState({ step: 'validating', progress: 50 });
            addLog('info', '🔍 Validating mapping...');

            const validation = await validateMapping(mappingResponse.mapping_id);
            updateState({ validationResult: validation, progress: 100 });

            if (validation.is_valid) {
                addLog('success', `✅ Validation passed: ${validation.stats?.case_count} cases`);
            } else {
                const errorMsgs = validation.errors.map(e => e.message).join(', ');
                addLog('warning', `⚠️ Validation issues: ${errorMsgs}`);
            }

            return mappingResponse;

        } catch (error) {
            const message = error instanceof Error ? error.message : 'Mapping failed';
            updateState({ step: 'error', error: message });
            addLog('error', `❌ Mapping failed: ${message}`);
            return null;
        }
    }, [updateState, addLog]);

    /**
     * Start processing and wait for results
     */
    const process = useCallback(async (mappingId: string): Promise<FullAnalysisResponse | null> => {
        updateState({ step: 'processing', progress: 0, error: null });
        addLog('info', '⚙️ Starting process mining...');

        try {
            // Start processing
            const job = await startProcessing(mappingId);
            updateState({ jobId: job.job_id });

            // Wait for completion with progress updates
            const completedJob = await waitForJob(
                job.job_id,
                (progress, message) => {
                    updateState({
                        progress,
                        progressMessage: message || '',
                    });
                    if (message) {
                        addLog('info', `⏳ ${message} (${progress}%)`);
                    }
                }
            );

            if (completedJob.status === 'failed') {
                throw new Error(completedJob.error || 'Processing failed');
            }

            // Get full analysis
            const datasetId = completedJob.dataset_id!;
            const analysis = await getFullAnalysis(datasetId);

            updateState({
                step: 'complete',
                progress: 100,
                datasetId,
                dfg: analysis.dfg,
                variants: analysis.variants,
                stats: analysis.stats,
                deviations: analysis.deviations,
            });

            addLog('success', `✅ Mining complete: ${analysis.stats.total_cases} cases, ${analysis.stats.total_variants} variants`);
            return analysis;

        } catch (error) {
            const message = error instanceof Error ? error.message : 'Processing failed';
            updateState({ step: 'error', error: message });
            addLog('error', `❌ Processing failed: ${message}`);
            return null;
        }
    }, [updateState, addLog]);

    /**
     * Full pipeline: upload → map → process
     */
    const runPipeline = useCallback(async (
        file: File,
        mapping: MappingCreate
    ): Promise<FullAnalysisResponse | null> => {
        // Upload
        const uploadResponse = await upload(file);
        if (!uploadResponse) return null;

        // Map
        const mappingResponse = await map(uploadResponse.upload_id, mapping);
        if (!mappingResponse) return null;

        // Process
        return process(mappingResponse.mapping_id);
    }, [upload, map, process]);

    /**
     * Reset state
     */
    const reset = useCallback(() => {
        setState(initialState);
    }, []);

    return {
        state,
        upload,
        map,
        process,
        runPipeline,
        reset,
    };
}
