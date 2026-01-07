/**
 * Network Status Hooks
 *
 * Provides hooks for detecting online/offline status and network conditions.
 */

import { useState, useEffect } from 'react';

// ============================================
// Types
// ============================================

export interface NetworkInfo {
  isOnline: boolean;
  effectiveType?: 'slow-2g' | '2g' | '3g' | '4g';
  downlink?: number;
  rtt?: number;
  saveData?: boolean;
}

// ============================================
// useNetworkStatus Hook
// ============================================

/**
 * Simple hook to track online/offline status
 */
export function useNetworkStatus(): boolean {
  const [isOnline, setIsOnline] = useState(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}

// ============================================
// useNetworkInfo Hook
// ============================================

/**
 * Extended hook with detailed network information
 * Uses Network Information API when available
 */
export function useNetworkInfo(): NetworkInfo {
  const [networkInfo, setNetworkInfo] = useState<NetworkInfo>(() => ({
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
  }));

  useEffect(() => {
    const updateNetworkInfo = () => {
      const info: NetworkInfo = {
        isOnline: navigator.onLine,
      };

      // Check for Network Information API
      const connection = (navigator as Navigator & {
        connection?: {
          effectiveType?: 'slow-2g' | '2g' | '3g' | '4g';
          downlink?: number;
          rtt?: number;
          saveData?: boolean;
        };
      }).connection;

      if (connection) {
        info.effectiveType = connection.effectiveType;
        info.downlink = connection.downlink;
        info.rtt = connection.rtt;
        info.saveData = connection.saveData;
      }

      setNetworkInfo(info);
    };

    // Initial update
    updateNetworkInfo();

    // Listen for online/offline events
    window.addEventListener('online', updateNetworkInfo);
    window.addEventListener('offline', updateNetworkInfo);

    // Listen for connection changes if supported
    const connection = (navigator as Navigator & {
      connection?: EventTarget;
    }).connection;

    if (connection) {
      connection.addEventListener('change', updateNetworkInfo);
    }

    return () => {
      window.removeEventListener('online', updateNetworkInfo);
      window.removeEventListener('offline', updateNetworkInfo);
      if (connection) {
        connection.removeEventListener('change', updateNetworkInfo);
      }
    };
  }, []);

  return networkInfo;
}

// ============================================
// useOfflineDuration Hook
// ============================================

/**
 * Hook to track how long the user has been offline
 */
export function useOfflineDuration(): number {
  const isOnline = useNetworkStatus();
  const [offlineStartTime, setOfflineStartTime] = useState<number | null>(null);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (!isOnline) {
      // Just went offline
      setOfflineStartTime(Date.now());
    } else {
      // Back online
      setOfflineStartTime(null);
      setDuration(0);
    }
  }, [isOnline]);

  // Update duration while offline
  useEffect(() => {
    if (offlineStartTime === null) return;

    const interval = setInterval(() => {
      setDuration(Date.now() - offlineStartTime);
    }, 1000);

    return () => clearInterval(interval);
  }, [offlineStartTime]);

  return duration;
}

export default useNetworkStatus;
