/**
 * Instrumented Fetch - Wrapper around native fetch() that logs to DevConsole
 * 
 * Features:
 * - Captures request method, URL, and body
 * - Logs response status, duration, and body (truncated)
 * - Integrates with devLogger for DevConsole visibility
 * - Skips verbose logging for health/heartbeat endpoints
 */

import { logRequest, logResponse, logError } from './devLogger';

// ============================================
// Constants
// ============================================

const MAX_BODY_CHARS = 5000;
const SKIP_BODY_PATTERNS = ['/health', '/heartbeat', '/dev/logs'];

// ============================================
// Helpers
// ============================================

/**
 * Extract path from URL for logging
 */
function extractPath(url: string): string {
    try {
        const urlObj = new URL(url, window.location.origin);
        return urlObj.pathname + urlObj.search;
    } catch {
        return url;
    }
}

/**
 * Truncate JSON string to prevent massive log entries
 */
function truncateJson(data: unknown, maxChars = MAX_BODY_CHARS): unknown {
    if (data === undefined || data === null) return undefined;

    try {
        const str = typeof data === 'string' ? data : JSON.stringify(data);
        if (str.length <= maxChars) {
            return typeof data === 'string' ? data : JSON.parse(str);
        }
        return {
            _truncated: true,
            _originalLength: str.length,
            preview: str.slice(0, maxChars),
        };
    } catch {
        return String(data).slice(0, maxChars);
    }
}

/**
 * Parse request body for logging
 */
function parseRequestBody(body: BodyInit | null | undefined): unknown {
    if (!body) return undefined;

    if (typeof body === 'string') {
        try {
            return JSON.parse(body);
        } catch {
            return body;
        }
    }

    if (body instanceof FormData) {
        return '[FormData]';
    }

    if (body instanceof Blob) {
        return `[Blob: ${body.size} bytes]`;
    }

    if (body instanceof ArrayBuffer) {
        return `[ArrayBuffer: ${body.byteLength} bytes]`;
    }

    return '[Unknown body type]';
}

/**
 * Safely parse JSON response body
 */
async function safeParseResponseBody(response: Response): Promise<unknown> {
    const contentType = response.headers.get('content-type') || '';

    if (!contentType.includes('application/json')) {
        return `[${contentType || 'unknown content type'}]`;
    }

    try {
        const cloned = response.clone();
        return await cloned.json();
    } catch {
        return '[Failed to parse response body]';
    }
}

/**
 * Check if URL should skip body logging (high-frequency endpoints)
 */
function shouldSkipBodyLogging(url: string): boolean {
    return SKIP_BODY_PATTERNS.some(pattern => url.includes(pattern));
}

// ============================================
// Main Export
// ============================================

/**
 * Instrumented fetch wrapper that logs all requests/responses to DevConsole
 * 
 * @example
 * // Replace:
 * const res = await fetch('/api/v1/data', { method: 'POST', body: JSON.stringify(data) });
 * 
 * // With:
 * const res = await instrumentedFetch('/api/v1/data', { method: 'POST', body: JSON.stringify(data) });
 */
export async function instrumentedFetch(
    input: RequestInfo | URL,
    init?: RequestInit
): Promise<Response> {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
    const method = init?.method?.toUpperCase() || 'GET';
    const path = extractPath(url);
    const startTime = performance.now();
    const skipBody = shouldSkipBodyLogging(url);

    // Log request
    const requestBody = skipBody ? undefined : truncateJson(parseRequestBody(init?.body));
    logRequest(method, path, requestBody);

    try {
        const response = await fetch(input, init);
        const duration = performance.now() - startTime;

        // Log response with body
        let responseBody: unknown = undefined;
        if (!skipBody) {
            responseBody = truncateJson(await safeParseResponseBody(response));
        }

        logResponse(method, path, response.status, duration, responseBody);

        return response;
    } catch (error) {
        const duration = performance.now() - startTime;
        logError(`${method} ${path}`, error, { duration_ms: Math.round(duration) });
        throw error;
    }
}

/**
 * Create an instrumented fetch with a base URL prefix
 * 
 * @example
 * const apiFetch = createInstrumentedFetch('http://localhost:8001');
 * const res = await apiFetch('/api/v1/data');
 */
export function createInstrumentedFetch(baseUrl: string) {
    return (path: string, init?: RequestInit) => {
        const url = path.startsWith('http') ? path : `${baseUrl}${path}`;
        return instrumentedFetch(url, init);
    };
}

export default instrumentedFetch;
