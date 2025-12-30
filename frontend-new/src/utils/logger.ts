/**
 * Frontend Logger Utility
 * Provides structured logging with levels and namespaces
 * Also sends logs to the file-based dev logger for persistence
 */

import { devLog, logError as devLogError } from '@lumina/design-system';

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

// Current log level - can be set via localStorage for debugging
const getLogLevel = (): LogLevel => {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('lumina_log_level');
    if (stored && stored in LogLevel) {
      return LogLevel[stored as keyof typeof LogLevel];
    }
  }
  // Default to DEBUG in development (localhost), INFO otherwise
  const isDev = typeof window !== 'undefined' && window.location.hostname === 'localhost';
  return isDev ? LogLevel.DEBUG : LogLevel.INFO;
};

const formatTimestamp = (): string => {
  return new Date().toISOString().split('T')[1].slice(0, 12);
};

const LEVEL_COLORS: Record<LogLevel, string> = {
  [LogLevel.DEBUG]: '#9CA3AF', // gray
  [LogLevel.INFO]: '#3B82F6',  // blue
  [LogLevel.WARN]: '#F59E0B',  // yellow
  [LogLevel.ERROR]: '#EF4444', // red
};

const LEVEL_LABELS: Record<LogLevel, string> = {
  [LogLevel.DEBUG]: 'DEBUG',
  [LogLevel.INFO]: 'INFO',
  [LogLevel.WARN]: 'WARN',
  [LogLevel.ERROR]: 'ERROR',
};

interface LogMessage {
  level: LogLevel;
  namespace: string;
  message: string;
  data?: unknown;
  timestamp: string;
}

class Logger {
  private namespace: string;

  constructor(namespace: string) {
    this.namespace = namespace;
  }

  private log(level: LogLevel, message: string, data?: unknown): void {
    if (level < getLogLevel()) {
      return;
    }

    const logMessage: LogMessage = {
      level,
      namespace: this.namespace,
      message,
      data,
      timestamp: formatTimestamp(),
    };

    const prefix = `%c[${logMessage.timestamp}] [${LEVEL_LABELS[level]}] [${this.namespace}]`;
    const style = `color: ${LEVEL_COLORS[level]}; font-weight: bold;`;

    if (data !== undefined) {
      console[level === LogLevel.ERROR ? 'error' : level === LogLevel.WARN ? 'warn' : 'log'](
        prefix,
        style,
        message,
        data
      );
    } else {
      console[level === LogLevel.ERROR ? 'error' : level === LogLevel.WARN ? 'warn' : 'log'](
        prefix,
        style,
        message
      );
    }

    // Also send to file-based dev logger for persistence
    if (level === LogLevel.ERROR) {
      devLogError(this.namespace, message, data as Record<string, unknown>);
    } else {
      devLog('FE-ACTION', this.namespace, data ? { message, ...( typeof data === 'object' ? data : { data }) } : message);
    }
  }

  debug(message: string, data?: unknown): void {
    this.log(LogLevel.DEBUG, message, data);
  }

  info(message: string, data?: unknown): void {
    this.log(LogLevel.INFO, message, data);
  }

  warn(message: string, data?: unknown): void {
    this.log(LogLevel.WARN, message, data);
  }

  error(message: string, data?: unknown): void {
    this.log(LogLevel.ERROR, message, data);
  }
}

/**
 * Create a namespaced logger instance
 * @example
 * const log = createLogger('Auth');
 * log.info('User logged in', { userId: '123' });
 */
export function createLogger(namespace: string): Logger {
  return new Logger(namespace);
}

// Pre-configured loggers for common namespaces
export const loggers = {
  auth: createLogger('Auth'),
  settings: createLogger('Settings'),
  notifications: createLogger('Notifications'),
  activity: createLogger('Activity'),
  navigation: createLogger('Navigation'),
  help: createLogger('Help'),
};

export default createLogger;
