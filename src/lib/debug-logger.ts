// Debug Logger - Centralized logging with persistence
// Access logs via: window.__DEBUG_LOGS__ or localStorage.getItem('debug_logs')

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface DebugLogEntry {
    id: string;
    timestamp: string;
    level: LogLevel;
    context: string;
    message: string;
    data?: unknown;
}

const MAX_LOGS = 1000;
const STORAGE_KEY = 'process_miner_debug_logs';

// In-memory log store
let logs: DebugLogEntry[] = [];

// Load from localStorage on init
function loadLogs(): void {
    if (typeof window === 'undefined') return;
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            logs = JSON.parse(stored);
        }
    } catch (e) {
        console.warn('Failed to load debug logs', e);
    }
}

// Save to localStorage
function saveLogs(): void {
    if (typeof window === 'undefined') return;
    try {
        // Keep only last MAX_LOGS
        if (logs.length > MAX_LOGS) {
            logs = logs.slice(-MAX_LOGS);
        }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(logs));

        // Also expose on window for easy access
        (window as unknown as { __DEBUG_LOGS__: DebugLogEntry[] }).__DEBUG_LOGS__ = logs;
    } catch (e) {
        console.warn('Failed to save debug logs', e);
    }
}

// Console colors
const colors: Record<LogLevel, string> = {
    debug: '#888',
    info: '#0099ff',
    warn: '#ff9900',
    error: '#ff0000',
};

function log(level: LogLevel, context: string, message: string, data?: unknown): void {
    const entry: DebugLogEntry = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        timestamp: new Date().toISOString(),
        level,
        context,
        message,
        data,
    };

    logs.push(entry);
    saveLogs();

    // Console output with styling
    const style = `color: ${colors[level]}; font-weight: bold;`;
    const prefix = `[${entry.timestamp.split('T')[1].split('.')[0]}] [${context}]`;

    if (data !== undefined) {
        console.groupCollapsed(`%c${prefix} ${message}`, style);
        console.log('Data:', data);
        console.groupEnd();
    } else {
        console.log(`%c${prefix} ${message}`, style);
    }
}

// Logger factory - creates a logger for a specific context
export function createLogger(context: string) {
    return {
        debug: (msg: string, data?: unknown) => log('debug', context, msg, data),
        info: (msg: string, data?: unknown) => log('info', context, msg, data),
        warn: (msg: string, data?: unknown) => log('warn', context, msg, data),
        error: (msg: string, data?: unknown) => log('error', context, msg, data),
    };
}

// Utility functions
export function getLogs(): DebugLogEntry[] {
    return [...logs];
}

export function clearLogs(): void {
    logs = [];
    saveLogs();
}

export function exportLogs(): string {
    return JSON.stringify(logs, null, 2);
}

export function downloadLogs(): void {
    if (typeof window === 'undefined') return;
    const blob = new Blob([exportLogs()], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `process-miner-logs-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Initialize
if (typeof window !== 'undefined') {
    loadLogs();

    // Expose utilities on window for debugging
    (window as unknown as {
        __DEBUG_LOGS__: DebugLogEntry[];
        __CLEAR_LOGS__: typeof clearLogs;
        __DOWNLOAD_LOGS__: typeof downloadLogs;
    }).__DEBUG_LOGS__ = logs;
    (window as unknown as { __CLEAR_LOGS__: typeof clearLogs }).__CLEAR_LOGS__ = clearLogs;
    (window as unknown as { __DOWNLOAD_LOGS__: typeof downloadLogs }).__DOWNLOAD_LOGS__ = downloadLogs;
}

// Pre-made loggers for common contexts
export const loggers = {
    upload: createLogger('Upload'),
    parse: createLogger('Parse'),
    store: createLogger('Store'),
    config: createLogger('Config'),
    app: createLogger('App'),
};
