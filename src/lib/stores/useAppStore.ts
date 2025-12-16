import { create } from 'zustand';
import type { ProcessModel } from '../mining/types';
import type { ColumnMetadata } from '@/lib/api';

export interface UploadedFile {
    name: string;
    size: number;
    type: string;
    rawData: unknown;
}

export interface ParsedData {
    headers: string[];
    rows: object[];
    rowCount: number;
}

export interface ColumnConfig {
    caseId: string;
    activity: string;
    timestamp: string;
    resource?: string;
    cost?: string;
}

// ProcessMiningResults is now the ProcessModel from the mining module
export type ProcessMiningResults = ProcessModel;

// Backend job status
export type JobStatus = 'idle' | 'uploading' | 'processing' | 'complete' | 'error';

interface AppState {
    // Existing client-side state
    uploadedFile: UploadedFile | null;
    parsedData: ParsedData | null;
    columnConfig: ColumnConfig | null;
    miningResults: ProcessMiningResults | null;
    currentStep: 1 | 2 | 3 | 4;

    // Backend state
    uploadId: string | null;
    mappingId: string | null;
    datasetId: string | null;
    jobStatus: JobStatus;
    jobProgress: number;
    jobMessage: string;
    backendColumns: ColumnMetadata[];
    useBackend: boolean;

    // Existing actions
    setUploadedFile: (file: UploadedFile | null) => void;
    setParsedData: (data: ParsedData | null) => void;
    setColumnConfig: (config: ColumnConfig | null) => void;
    setMiningResults: (results: ProcessMiningResults | null) => void;
    setCurrentStep: (step: 1 | 2 | 3 | 4) => void;

    // Backend actions
    setUploadId: (id: string | null) => void;
    setMappingId: (id: string | null) => void;
    setDatasetId: (id: string | null) => void;
    setJobStatus: (status: JobStatus) => void;
    setJobProgress: (progress: number, message?: string) => void;
    setBackendColumns: (columns: ColumnMetadata[]) => void;
    setUseBackend: (use: boolean) => void;

    reset: () => void;
}

const initialState = {
    uploadedFile: null,
    parsedData: null,
    columnConfig: null,
    miningResults: null,
    currentStep: 1 as const,
    // Backend initial state
    uploadId: null,
    mappingId: null,
    datasetId: null,
    jobStatus: 'idle' as JobStatus,
    jobProgress: 0,
    jobMessage: '',
    backendColumns: [] as ColumnMetadata[],
    useBackend: true, // Default to backend mode
};

export const useAppStore = create<AppState>((set) => ({
    ...initialState,

    // Existing setters
    setUploadedFile: (file) => set({ uploadedFile: file }),
    setParsedData: (data) => set({ parsedData: data }),
    setColumnConfig: (config) => set({ columnConfig: config }),
    setMiningResults: (results) => set({ miningResults: results }),
    setCurrentStep: (step) => set({ currentStep: step }),

    // Backend setters
    setUploadId: (uploadId) => set({ uploadId }),
    setMappingId: (mappingId) => set({ mappingId }),
    setDatasetId: (datasetId) => set({ datasetId }),
    setJobStatus: (jobStatus) => set({ jobStatus }),
    setJobProgress: (jobProgress, jobMessage = '') => set({ jobProgress, jobMessage }),
    setBackendColumns: (backendColumns) => set({ backendColumns }),
    setUseBackend: (useBackend) => set({ useBackend }),

    reset: () => set(initialState),
}));
