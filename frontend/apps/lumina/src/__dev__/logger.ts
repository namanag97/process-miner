/**
 * Development Logger
 *
 * Logs to both browser console (during development) and can be extended
 * to write to file via a dev server endpoint.
 *
 * Log files location: frontend/dev-logs/YYYY-MM-DD.log
 */

type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'API' | 'RENDER' | 'STATE';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  context: string;
  message: string;
  data?: unknown;
}

const isDev = import.meta.env.DEV;

// In-memory log buffer (for potential file writing via API)
const logBuffer: LogEntry[] = [];
const MAX_BUFFER_SIZE = 1000;

function formatLogLine(entry: LogEntry): string {
  const dataStr = entry.data ? `\n${JSON.stringify(entry.data, null, 2)}` : '';
  return `[${entry.timestamp}] [${entry.level}] [${entry.context}] ${entry.message}${dataStr}`;
}

function writeLog(level: LogLevel, context: string, message: string, data?: unknown): void {
  if (!isDev) return;

  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    level,
    context,
    message,
    data,
  };

  // Add to buffer
  logBuffer.push(entry);
  if (logBuffer.length > MAX_BUFFER_SIZE) {
    logBuffer.shift();
  }

  // Console output with appropriate styling
  const formattedLine = formatLogLine(entry);

  switch (level) {
    case 'ERROR':
      console.error(`%c${formattedLine}`, 'color: #DE350B');
      break;
    case 'WARN':
      console.warn(`%c${formattedLine}`, 'color: #FAAD14');
      break;
    case 'API':
      console.log(`%c${formattedLine}`, 'color: #0052CC');
      break;
    case 'RENDER':
      console.log(`%c${formattedLine}`, 'color: #36B37E');
      break;
    case 'STATE':
      console.log(`%c${formattedLine}`, 'color: #9254DE');
      break;
    case 'DEBUG':
      console.debug(`%c${formattedLine}`, 'color: #8C8C8C');
      break;
    default:
      console.log(formattedLine);
  }

  // Attempt to write to file via dev server (if available)
  if (typeof window !== 'undefined' && (window as { __DEV_LOG_ENDPOINT__?: string }).__DEV_LOG_ENDPOINT__) {
    fetch((window as { __DEV_LOG_ENDPOINT__?: string }).__DEV_LOG_ENDPOINT__!, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(entry),
    }).catch(() => {
      // Silently fail if dev server endpoint not available
    });
  }
}

export const devLog = {
  /**
   * General debug logging
   */
  debug: (context: string, message: string, data?: unknown) => {
    writeLog('DEBUG', context, message, data);
  },

  /**
   * General info logging
   */
  info: (context: string, message: string, data?: unknown) => {
    writeLog('INFO', context, message, data);
  },

  /**
   * Warning logging
   */
  warn: (context: string, message: string, data?: unknown) => {
    writeLog('WARN', context, message, data);
  },

  /**
   * Error logging
   */
  error: (context: string, message: string, error?: unknown) => {
    writeLog('ERROR', context, message, error);
  },

  /**
   * API request/response logging
   */
  api: (method: string, url: string, status: number, duration: number) => {
    writeLog('API', 'request', `${method} ${url} → ${status} (${duration}ms)`);
  },

  /**
   * Component render logging
   */
  render: (component: string, props?: Record<string, unknown>) => {
    writeLog('RENDER', component, 'rendered', props);
  },

  /**
   * State change logging
   */
  state: (store: string, action: string, payload?: unknown) => {
    writeLog('STATE', store, action, payload);
  },

  /**
   * Get buffered logs (useful for exporting)
   */
  getBuffer: (): LogEntry[] => [...logBuffer],

  /**
   * Clear log buffer
   */
  clearBuffer: () => {
    logBuffer.length = 0;
  },

  /**
   * Export logs as text file
   */
  exportLogs: () => {
    const logText = logBuffer.map(formatLogLine).join('\n');
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lumina-dev-logs-${new Date().toISOString().split('T')[0]}.log`;
    a.click();
    URL.revokeObjectURL(url);
  },
};

export default devLog;
