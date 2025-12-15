import { create } from 'zustand';

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

export interface ProcessMiningResults {
    // Define this type later based on actual mining results structure
    [key: string]: unknown;
}

interface AppState {
    uploadedFile: UploadedFile | null;
    parsedData: ParsedData | null;
    columnConfig: ColumnConfig | null;
    miningResults: ProcessMiningResults | null;
    currentStep: 1 | 2 | 3 | 4;

    setUploadedFile: (file: UploadedFile | null) => void;
    setParsedData: (data: ParsedData | null) => void;
    setColumnConfig: (config: ColumnConfig | null) => void;
    setMiningResults: (results: ProcessMiningResults | null) => void;
    setCurrentStep: (step: 1 | 2 | 3 | 4) => void;

    reset: () => void;
}

const initialState = {
    uploadedFile: null,
    parsedData: null,
    columnConfig: null,
    miningResults: null,
    currentStep: 1 as const,
};

export const useAppStore = create<AppState>((set) => ({
    ...initialState,

    setUploadedFile: (file) => set({ uploadedFile: file }),
    setParsedData: (data) => set({ parsedData: data }),
    setColumnConfig: (config) => set({ columnConfig: config }),
    setMiningResults: (results) => set({ miningResults: results }),
    setCurrentStep: (step) => set({ currentStep: step }),

    reset: () => set(initialState),
}));
