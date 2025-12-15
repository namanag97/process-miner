import { create } from 'zustand';

export type LogLevel = 'info' | 'success' | 'warning' | 'error';

export interface LogEntry {
    id: string;
    timestamp: Date;
    level: LogLevel;
    message: string;
    details?: unknown;
}

interface LogState {
    logs: LogEntry[];
    addLog: (level: LogLevel, message: string, details?: unknown) => void;
    clearLogs: () => void;
}

const MAX_LOGS = 500;

export const useLogStore = create<LogState>((set) => ({
    logs: [],

    addLog: (level, message, details) => set((state) => {
        const newLog: LogEntry = {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            timestamp: new Date(),
            level,
            message,
            details,
        };

        const updatedLogs = [...state.logs, newLog];

        // Keep only the last MAX_LOGS entries
        if (updatedLogs.length > MAX_LOGS) {
            return { logs: updatedLogs.slice(updatedLogs.length - MAX_LOGS) };
        }

        return { logs: updatedLogs };
    }),

    clearLogs: () => set({ logs: [] }),
}));
