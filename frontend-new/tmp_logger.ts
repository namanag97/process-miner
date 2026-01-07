/**
 * Frontend Logger Utility
 * Provides structured logging with levels and namespaces
 */

export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3,
}

const getLogLevel = (): LogLevel => {
    if (typeof window !== 'undefined') {
        const stored = localStorage.getItem('lumina_log_level');
        if (stored && stored in LogLevel) {
            return LogLevel[stored as keyof typeof LogLevel];
        }
    }
    const isDev = typeof window !== 'undefined' && window.location.hostname === 'localhost';
    return isDev ? LogLevel.DEBUG : LogLevel.INFO;
};

const formatTimestamp = (): string => new Date().toISOString().split('T')[1].slice(0, 12);

const LEVEL_COLORS: Record<LogLevel, string> = {
    [LogLevel.DEBUG]: '#9CA3AF',
    [LogLevel.INFO]: '#3B82F6',
    [LogLevel.WARN]: '#F59E0B',
    [LogLevel.ERROR]: '#EF4444',
};

const LEVEL_LABELS: Record<LogLevel, string> = {
    [LogLevel.DEBUG]: 'DEBUG',
    [LogLevel.INFO]: 'INFO',
    [LogLevel.WARN]: 'WARN',
    [LogLevel.ERROR]: 'ERROR',
};

class Logger {
    private namespace: string;
    constructor(namespace: string) { this.namespace = namespace; }

    private log(level: LogLevel, message: string, data?: unknown): void {
        if (level < getLogLevel()) return;
        const prefix = `%c[${formatTimestamp()}] [${LEVEL_LABELS[level]}] [${this.namespace}]`;
        const style = `color: ${LEVEL_COLORS[level]}; font-weight: bold;`;
        const method = level === LogLevel.ERROR ? 'error' : level === LogLevel.WARN ? 'warn' : 'log';
        data !== undefined ? console[method](prefix, style, message, data) : console[method](prefix, style, message);
    }

    debug(message: string, data?: unknown): void { this.log(LogLevel.DEBUG, message, data); }
    info(message: string, data?: unknown): void { this.log(LogLevel.INFO, message, data); }
    warn(message: string, data?: unknown): void { this.log(LogLevel.WARN, message, data); }
    error(message: string, data?: unknown): void { this.log(LogLevel.ERROR, message, data); }
}

export function createLogger(namespace: string): Logger { return new Logger(namespace); }
export const loggers = {
    auth: createLogger('Auth'),
    settings: createLogger('Settings'),
    notifications: createLogger('Notifications'),
    activity: createLogger('Activity'),
    navigation: createLogger('Navigation'),
    help: createLogger('Help'),
};
export default createLogger;
