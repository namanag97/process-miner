/**
 * Dev Logger - File-based logging for development debugging
 * 
 * Sends log entries to backend which appends to dev-logs/app.log
 * Format: [TIMESTAMP] [TYPE] [SOURCE] → MESSAGE
 */

type LogType = 'FE-ACTION' | 'API-REQ' | 'API-RES' | 'ERROR';

interface LogEntry {
  type: LogType;
  source: string;
  message: unknown;
  timestamp: string;
}

// Backend URL - hardcoded for dev (frontend at 5173/4200, backend at 8001)
const DEV_LOG_ENDPOINT = 'http://localhost:8001/api/v1/dev/log';

// Queue for batching logs (reduces network overhead)
let logQueue: LogEntry[] = [];
let flushTimeout: ReturnType<typeof setTimeout> | null = null;
const FLUSH_INTERVAL_MS = 500;

/**
 * Truncate message to keep logs concise
 */
function truncate(str: string, maxLen: number = 50): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 3) + '...';
}

/**
 * Flush queued logs to backend
 */
async function flushLogs(): Promise<void> {
  if (logQueue.length === 0) return;

  const entries = [...logQueue];
  logQueue = [];

  try {
    for (const entry of entries) {
      await fetch(DEV_LOG_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry),
      });
    }
  } catch {
    // Silently fail - dev logging shouldn't break the app
  }
}

/**
 * Schedule a flush of the log queue
 */
function scheduleFlush(): void {
  if (flushTimeout) return;
  flushTimeout = setTimeout(() => {
    flushTimeout = null;
    flushLogs();
  }, FLUSH_INTERVAL_MS);
}

/**
 * Log a dev event to the file-based log
 */
export function devLog(type: LogType, source: string, message: unknown): void {
  const entry: LogEntry = {
    type,
    source,
    message: typeof message === 'string' ? truncate(message) : message,
    timestamp: new Date().toISOString(),
  };

  logQueue.push(entry);
  scheduleFlush();
}

/**
 * Log a frontend action (click, submit, navigation, state change)
 */
export function logAction(source: string, message: unknown = 'triggered'): void {
  devLog('FE-ACTION', source, message);
}

/**
 * Log an API request
 */
export function logRequest(method: string, path: string, payload?: unknown): void {
  const sanitized = payload ? truncate(JSON.stringify(payload)) : undefined;
  devLog('API-REQ', `${method} ${path}`, sanitized ?? 'no-body');
}

/**
 * Log an API response
 */
export function logResponse(method: string, path: string, status: number, duration: number, body?: unknown): void {
  devLog('API-RES', `${method} ${path}`, { status, ms: Math.round(duration), body: body ? truncate(JSON.stringify(body)) : undefined });
}

/**
 * Log an error with context
 */
export function logError(source: string, error: unknown, context?: Record<string, unknown>): void {
  const errObj = error instanceof Error 
    ? { message: error.message, stack: error.stack?.split('\n').slice(0, 3).join(' ') }
    : { message: String(error) };
  
  devLog('ERROR', source, { ...errObj, ...context });
}

/**
 * Force flush all pending logs (useful before page unload)
 */
export function flushDevLogs(): Promise<void> {
  if (flushTimeout) {
    clearTimeout(flushTimeout);
    flushTimeout = null;
  }
  return flushLogs();
}

// Flush on page unload
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    flushDevLogs();
  });
}

export default devLog;
