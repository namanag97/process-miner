/**
 * Slow Request Detection Hook
 *
 * Detects when a request is taking longer than expected and provides
 * state to show appropriate loading messages to users.
 */
import { useState, useEffect, useRef } from 'react';

export interface UseSlowRequestDetectionOptions {
    /** Time in ms after which a request is considered slow. Default: 3000ms */
    threshold?: number;
    /** Whether to reset the slow state when loading completes. Default: true */
    resetOnComplete?: boolean;
}

export interface UseSlowRequestDetectionReturn {
    /** Whether the current request is taking longer than threshold */
    isSlow: boolean;
    /** How long the request has been loading in ms */
    loadingDuration: number;
    /** Reset the slow detection state */
    reset: () => void;
}

/**
 * Hook to detect slow-loading requests and show appropriate feedback
 *
 * @param isLoading - Whether a request is currently in progress
 * @param options - Configuration options
 *
 * @example
 * ```tsx
 * function DataLoader() {
 *   const { data, isLoading } = useDatasets();
 *   const { isSlow, loadingDuration } = useSlowRequestDetection(isLoading);
 *
 *   if (isLoading) {
 *     return (
 *       <div>
 *         <Spin />
 *         {isSlow && (
 *           <Text type="secondary">
 *             Still loading... ({Math.floor(loadingDuration / 1000)}s)
 *           </Text>
 *         )}
 *       </div>
 *     );
 *   }
 *
 *   return <DataList data={data} />;
 * }
 * ```
 */
export function useSlowRequestDetection(
    isLoading: boolean,
    options: UseSlowRequestDetectionOptions = {}
): UseSlowRequestDetectionReturn {
    const { threshold = 3000, resetOnComplete = true } = options;

    const [isSlow, setIsSlow] = useState(false);
    const [loadingDuration, setLoadingDuration] = useState(0);
    const loadingStartRef = useRef<number | null>(null);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        if (isLoading) {
            // Start tracking
            loadingStartRef.current = Date.now();
            setLoadingDuration(0);
            setIsSlow(false);

            // Set timeout for slow detection
            const slowTimeout = setTimeout(() => {
                setIsSlow(true);
            }, threshold);

            // Update duration periodically
            intervalRef.current = setInterval(() => {
                if (loadingStartRef.current) {
                    setLoadingDuration(Date.now() - loadingStartRef.current);
                }
            }, 100);

            return () => {
                clearTimeout(slowTimeout);
                if (intervalRef.current) {
                    clearInterval(intervalRef.current);
                }
            };
        } else {
            // Loading completed
            loadingStartRef.current = null;
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
            if (resetOnComplete) {
                setIsSlow(false);
                setLoadingDuration(0);
            }
            return undefined;
        }
    }, [isLoading, threshold, resetOnComplete]);

    const reset = () => {
        setIsSlow(false);
        setLoadingDuration(0);
        loadingStartRef.current = null;
    };

    return { isSlow, loadingDuration, reset };
}

/**
 * Hook variant with multiple threshold levels
 *
 * @example
 * ```tsx
 * function DataLoader() {
 *   const { data, isLoading } = useDatasets();
 *   const { level, message } = useProgressiveSlowDetection(isLoading);
 *
 *   if (isLoading) {
 *     return (
 *       <div>
 *         <Spin />
 *         {level !== 'normal' && <Text type="secondary">{message}</Text>}
 *       </div>
 *     );
 *   }
 *
 *   return <DataList data={data} />;
 * }
 * ```
 */
export function useProgressiveSlowDetection(
    isLoading: boolean,
    options: {
        slowThreshold?: number;
        verySlowThreshold?: number;
        criticalThreshold?: number;
    } = {}
): {
    level: 'normal' | 'slow' | 'very-slow' | 'critical';
    message: string;
    loadingDuration: number;
} {
    const {
        slowThreshold = 3000,
        verySlowThreshold = 10000,
        criticalThreshold = 30000,
    } = options;

    const { loadingDuration } = useSlowRequestDetection(isLoading, {
        threshold: slowThreshold,
        resetOnComplete: true,
    });

    let level: 'normal' | 'slow' | 'very-slow' | 'critical' = 'normal';
    let message = '';

    if (loadingDuration >= criticalThreshold) {
        level = 'critical';
        message = 'This is taking much longer than expected. You may want to refresh the page.';
    } else if (loadingDuration >= verySlowThreshold) {
        level = 'very-slow';
        message = 'Still working on it. This is taking longer than usual.';
    } else if (loadingDuration >= slowThreshold) {
        level = 'slow';
        message = 'Still loading... This is taking a bit longer than expected.';
    }

    return { level, message, loadingDuration };
}

export default useSlowRequestDetection;
