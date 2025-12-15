import { create } from 'zustand';

export interface LogEntry {
    id: string;
    timestamp: Date;
    message: string;
    type: 'info' | 'success' | 'error' | 'warning';
}

export interface ParsedData {
    headers: string[];
    rows: Record<string, unknown>[];
    rowCount: number;
}

interface AppState {
    // File state
    file: File | null;
    setFile: (file: File | null) => void;

    // Parsed data state
    parsedData: ParsedData | null;
    setParsedData: (data: ParsedData | null) => void;

    // Current step in the workflow (1-5)
    currentStep: number;
    setCurrentStep: (step: number) => void;

    // Logging
    logs: LogEntry[];
    addLog: (message: string, type?: LogEntry['type']) => void;
    clearLogs: () => void;

    // Reset all state
    reset: () => void;
}

const generateId = () => Math.random().toString(36).substring(2, 9);

export const useAppStore = create<AppState>((set) => ({
    // File
    file: null,
    setFile: (file) => set({ file }),

    // Parsed data
    parsedData: null,
    setParsedData: (parsedData) => set({ parsedData }),

    // Current step
    currentStep: 1,
    setCurrentStep: (currentStep) => set({ currentStep }),

    // Logging
    logs: [],
    addLog: (message, type = 'info') =>
        set((state) => ({
            logs: [
                ...state.logs,
                {
                    id: generateId(),
                    timestamp: new Date(),
                    message,
                    type,
                },
            ],
        })),
    clearLogs: () => set({ logs: [] }),

    // Reset
    reset: () =>
        set({
            file: null,
            parsedData: null,
            currentStep: 1,
            logs: [],
        }),
}));
