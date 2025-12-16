import { create } from 'zustand';
import type { ColumnMetadata } from '@/lib/api';

/**
 * Application State
 * 
 * Manages both UI state and workflow entity IDs.
 * Server data is fetched via React Query using these IDs.
 */

// Generate a unique session ID for debugging
function generateSessionId(): string {
    return `sess_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

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

// Backend job status
export type JobStatus = 'idle' | 'uploading' | 'processing' | 'complete' | 'error';

// UI step in the workflow
export type WorkflowStep = 1 | 2 | 3 | 4;

// ProcessMiningResults - used for navigation guards and display
export interface ProcessMiningResults {
    stats: {
        totalCases: number;
        totalEvents: number;
        avgCaseDuration?: number;
        medianCaseDuration?: number;
        startActivities?: string[];
        endActivities?: string[];
    };
    variants?: unknown[];
    deviations?: unknown[];
    dfg?: unknown;
}

interface AppState {
    // UI state
    currentStep: WorkflowStep;
    sessionId: string;

    // Cached data for current workflow
    uploadedFile: UploadedFile | null;
    parsedData: ParsedData | null;
    columnConfig: ColumnConfig | null;
    miningResults: ProcessMiningResults | null;
    backendColumns: ColumnMetadata[];

    // Current entity IDs (for React Query keys)
    uploadId: string | null;
    mappingId: string | null;
    datasetId: string | null;

    // Job status for processing
    jobStatus: JobStatus;
    jobProgress: number;
    jobMessage: string;

    // Actions
    setCurrentStep: (step: WorkflowStep) => void;
    setUploadedFile: (file: UploadedFile | null) => void;
    setParsedData: (data: ParsedData | null) => void;
    setColumnConfig: (config: ColumnConfig | null) => void;
    setMiningResults: (results: ProcessMiningResults | null) => void;
    setBackendColumns: (columns: ColumnMetadata[]) => void;
    setUploadId: (id: string | null) => void;
    setMappingId: (id: string | null) => void;
    setDatasetId: (id: string | null) => void;
    setJobStatus: (status: JobStatus) => void;
    setJobProgress: (progress: number, message?: string) => void;
    regenerateSessionId: () => void;
    reset: () => void;
}

const initialState = {
    currentStep: 1 as WorkflowStep,
    sessionId: generateSessionId(),
    uploadedFile: null,
    parsedData: null,
    columnConfig: null,
    miningResults: null,
    backendColumns: [] as ColumnMetadata[],
    uploadId: null,
    mappingId: null,
    datasetId: null,
    jobStatus: 'idle' as JobStatus,
    jobProgress: 0,
    jobMessage: '',
};

export const useAppStore = create<AppState>((set) => ({
    ...initialState,

    setCurrentStep: (currentStep) => set({ currentStep }),
    setUploadedFile: (uploadedFile) => set({ uploadedFile }),
    setParsedData: (parsedData) => set({ parsedData }),
    setColumnConfig: (columnConfig) => set({ columnConfig }),
    setMiningResults: (miningResults) => set({ miningResults }),
    setBackendColumns: (backendColumns) => set({ backendColumns }),
    setUploadId: (uploadId) => set({ uploadId }),
    setMappingId: (mappingId) => set({ mappingId }),
    setDatasetId: (datasetId) => set({ datasetId }),
    setJobStatus: (jobStatus) => set({ jobStatus }),
    setJobProgress: (jobProgress, jobMessage = '') => set({ jobProgress, jobMessage }),
    regenerateSessionId: () => set({ sessionId: generateSessionId() }),
    reset: () => set({ ...initialState, sessionId: generateSessionId() }),
}));
