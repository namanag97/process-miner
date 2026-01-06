/**
 * usePageLogging - Automatic page lifecycle logging hook for MVP debugging
 * 
 * Provides:
 * - Automatic page mount/unmount logging
 * - Route param capture
 * - Error boundary integration
 * - User action correlation
 * - Render timing metrics
 * 
 * Usage:
 *   function MyPage() {
 *     usePageLogging('MyPage', { datasetId, projectId });
 *     return <div>...</div>;
 *   }
 */

import { useEffect, useRef, useCallback } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { devLog, startCorrelation } from '../ui/DevConsole';

interface PageLoggingOptions {
    /** Custom metadata to include in logs */
    metadata?: Record<string, unknown>;
    /** Whether to log render timing (default: true in dev) */
    logRenderTiming?: boolean;
    /** Whether to log route changes (default: true) */
    logRouteChanges?: boolean;
}

interface PageLogger {
    /** Log a user action with correlation tracking */
    logAction: (action: string, data?: Record<string, unknown>) => void;
    /** Log an error with context */
    logError: (error: Error, context?: Record<string, unknown>) => void;
    /** Log a state change */
    logState: (stateName: string, value: unknown) => void;
    /** Log API call start (for manual tracking) */
    logApiStart: (method: string, url: string) => void;
    /** Log API call complete */
    logApiComplete: (method: string, url: string, status: number, duration: number) => void;
    /** Get current correlation ID for this page session */
    getCorrelationId: () => string;
}

/**
 * Hook for automatic page lifecycle logging
 * 
 * @param pageName - Name of the page (e.g., 'DiscoveryPage', 'ExplorerPage')
 * @param options - Optional configuration
 * @returns PageLogger with action/error logging methods
 */
export function usePageLogging(
    pageName: string,
    options: PageLoggingOptions = {}
): PageLogger {
    const location = useLocation();
    const params = useParams();
    const mountTimeRef = useRef<number>(performance.now());
    const correlationIdRef = useRef<string>('');
    const renderCountRef = useRef<number>(0);

    const {
        metadata = {},
        logRenderTiming = process.env.NODE_ENV === 'development',
        logRouteChanges = true,
    } = options;

    // Generate correlation ID on mount
    useEffect(() => {
        correlationIdRef.current = startCorrelation(pageName);
        mountTimeRef.current = performance.now();
        renderCountRef.current = 0;

        // Log page mount
        devLog.action(pageName, 'PAGE_MOUNTED', {
            path: location.pathname,
            params: Object.keys(params).length > 0 ? params : undefined,
            search: location.search || undefined,
            correlationId: correlationIdRef.current,
            ...metadata,
        });

        // Log unmount
        return () => {
            const sessionDuration = Math.round(performance.now() - mountTimeRef.current);
            devLog.info(pageName, 'PAGE_UNMOUNTED', {
                sessionDuration,
                renderCount: renderCountRef.current,
                correlationId: correlationIdRef.current,
            });
        };
    }, [pageName]); // Only on mount/unmount

    // Log route changes within the same page
    useEffect(() => {
        if (logRouteChanges && correlationIdRef.current) {
            devLog.info(pageName, 'ROUTE_CHANGED', {
                path: location.pathname,
                params: Object.keys(params).length > 0 ? params : undefined,
                search: location.search || undefined,
            });
        }
    }, [location.pathname, location.search, pageName, logRouteChanges]);

    // Track render count
    useEffect(() => {
        renderCountRef.current += 1;

        if (logRenderTiming && renderCountRef.current > 1) {
            const timeSinceMount = Math.round(performance.now() - mountTimeRef.current);
            // Only log if renders are happening frequently (possible issue)
            if (renderCountRef.current > 5 && timeSinceMount < 5000) {
                devLog.info(pageName, 'FREQUENT_RERENDERS', {
                    renderCount: renderCountRef.current,
                    timeSinceMount,
                    rendersPerSecond: Math.round((renderCountRef.current / timeSinceMount) * 1000),
                });
            }
        }
    });

    // Logging methods
    const logAction = useCallback((action: string, data?: Record<string, unknown>) => {
        devLog.action(pageName, action, {
            ...data,
            correlationId: correlationIdRef.current,
        });
    }, [pageName]);

    const logError = useCallback((error: Error, context?: Record<string, unknown>) => {
        devLog.error(pageName, error.message, {
            errorType: error.name,
            stack: error.stack?.split('\n').slice(0, 5).join('\n'),
            ...context,
            path: location.pathname,
            correlationId: correlationIdRef.current,
        });
    }, [pageName, location.pathname]);

    const logState = useCallback((stateName: string, value: unknown) => {
        devLog.state(pageName, `${stateName} changed`, {
            [stateName]: value,
            correlationId: correlationIdRef.current,
        });
    }, [pageName]);

    const logApiStart = useCallback((method: string, url: string) => {
        devLog.apiRequest(method, url);
    }, []);

    const logApiComplete = useCallback((method: string, url: string, status: number, duration: number) => {
        devLog.apiResponse(method, url, status, duration);
    }, []);

    const getCorrelationId = useCallback(() => {
        return correlationIdRef.current;
    }, []);

    return {
        logAction,
        logError,
        logState,
        logApiStart,
        logApiComplete,
        getCorrelationId,
    };
}

/**
 * Higher-order component version for class components or wrapping
 */
export function withPageLogging<P extends object>(
    WrappedComponent: React.ComponentType<P & { pageLogger: PageLogger }>,
    pageName: string
) {
    return function WithPageLogging(props: P) {
        const pageLogger = usePageLogging(pageName);
        return <WrappedComponent { ...props } pageLogger = { pageLogger } />;
    };
}

export default usePageLogging;
