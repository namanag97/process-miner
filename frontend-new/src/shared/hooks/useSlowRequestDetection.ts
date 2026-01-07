/**
 * Slow Request Detection Hooks
 *
 * Provides hooks for detecting slow network requests and progressive loading states.
 */

import { useState, useEffect, useRef, useCallback } from 'react';

// ============================================
// Types
// ============================================

export interface UseSlowRequestDetectionOptions {
  /** Time in ms before considering request as slow (default: 3000) */
  slowThreshold?: number;
  /** Time in ms before showing very slow message (default: 10000) */
  verySlowThreshold?: number;
  /** Whether detection is enabled (default: true) */
  enabled?: boolean;
}

export interface UseSlowRequestDetectionReturn {
  /** Whether the request is currently considered slow */
  isSlow: boolean;
  /** Whether the request is currently considered very slow */
  isVerySlow: boolean;
  /** Duration of the current request in ms */
  duration: number;
  /** Start tracking a request */
  startTracking: () => void;
  /** Stop tracking a request */
  stopTracking: () => void;
  /** Reset tracking state */
  reset: () => void;
}

// ============================================
// useSlowRequestDetection Hook
// ============================================

/**
 * Hook to detect slow network requests and provide progressive feedback
 */
export function useSlowRequestDetection(
  options: UseSlowRequestDetectionOptions = {}
): UseSlowRequestDetectionReturn {
  const {
    slowThreshold = 3000,
    verySlowThreshold = 10000,
    enabled = true,
  } = options;

  const [isSlow, setIsSlow] = useState(false);
  const [isVerySlow, setIsVerySlow] = useState(false);
  const [duration, setDuration] = useState(0);
  const [isTracking, setIsTracking] = useState(false);

  const startTimeRef = useRef<number | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const startTracking = useCallback(() => {
    if (!enabled) return;

    startTimeRef.current = Date.now();
    setIsTracking(true);
    setIsSlow(false);
    setIsVerySlow(false);
    setDuration(0);
  }, [enabled]);

  const stopTracking = useCallback(() => {
    startTimeRef.current = null;
    setIsTracking(false);

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    stopTracking();
    setIsSlow(false);
    setIsVerySlow(false);
    setDuration(0);
  }, [stopTracking]);

  // Update duration and slow status while tracking
  useEffect(() => {
    if (!isTracking || !enabled) return;

    intervalRef.current = setInterval(() => {
      if (startTimeRef.current) {
        const elapsed = Date.now() - startTimeRef.current;
        setDuration(elapsed);
        setIsSlow(elapsed >= slowThreshold);
        setIsVerySlow(elapsed >= verySlowThreshold);
      }
    }, 100);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isTracking, enabled, slowThreshold, verySlowThreshold]);

  return {
    isSlow,
    isVerySlow,
    duration,
    startTracking,
    stopTracking,
    reset,
  };
}

// ============================================
// useProgressiveSlowDetection Hook
// ============================================

/**
 * Hook for progressive loading states with multiple thresholds
 */
export function useProgressiveSlowDetection(
  isLoading: boolean,
  options: UseSlowRequestDetectionOptions = {}
): UseSlowRequestDetectionReturn {
  const detection = useSlowRequestDetection(options);
  const wasLoadingRef = useRef(false);

  useEffect(() => {
    if (isLoading && !wasLoadingRef.current) {
      // Started loading
      detection.startTracking();
    } else if (!isLoading && wasLoadingRef.current) {
      // Finished loading
      detection.stopTracking();
    }

    wasLoadingRef.current = isLoading;
  }, [isLoading, detection]);

  // Reset when component unmounts
  useEffect(() => {
    return () => {
      detection.reset();
    };
  }, [detection]);

  return detection;
}

export default useSlowRequestDetection;
