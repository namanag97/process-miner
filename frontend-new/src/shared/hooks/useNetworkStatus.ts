/**
 * Network Status Hook
 *
 * Provides reactive online/offline status detection using browser APIs.
 * Uses useSyncExternalStore for optimal React 18+ compatibility.
 */
import { useSyncExternalStore, useCallback, useEffect, useState } from 'react';

// ============================================
// External Store for Network Status
// ============================================

function subscribe(callback: () => void): () => void {
    window.addEventListener('online', callback);
    window.addEventListener('offline', callback);
    return () => {
        window.removeEventListener('online', callback);
        window.removeEventListener('offline', callback);
    };
}

function getSnapshot(): boolean {
    return navigator.onLine;
}

function getServerSnapshot(): boolean {
    // Server-side rendering always assumes online
    return true;
}

/**
 * Hook to detect online/offline status
 *
 * @example
 * ```tsx
 * function App() {
 *   const isOnline = useNetworkStatus();
 *
 *   return (
 *     <>
 *       {!isOnline && <Banner type="warning">You're offline</Banner>}
 *       <Content />
 *     </>
 *   );
 * }
 * ```
 */
export function useNetworkStatus(): boolean {
    return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

// ============================================
// Extended Network Info
// ============================================

interface NetworkInfo {
    isOnline: boolean;
    /** Estimated effective connection type (4g, 3g, 2g, slow-2g) */
    effectiveType?: '4g' | '3g' | '2g' | 'slow-2g';
    /** Estimated downlink speed in Mbps */
    downlink?: number;
    /** Estimated round-trip time in ms */
    rtt?: number;
    /** Whether the user has requested reduced data usage */
    saveData?: boolean;
}

interface NavigatorConnection {
    effectiveType?: '4g' | '3g' | '2g' | 'slow-2g';
    downlink?: number;
    rtt?: number;
    saveData?: boolean;
    addEventListener?: (event: string, callback: () => void) => void;
    removeEventListener?: (event: string, callback: () => void) => void;
}

interface NavigatorWithConnection extends Navigator {
    connection?: NavigatorConnection;
}

/**
 * Extended hook with connection quality information
 *
 * Uses the Network Information API where available.
 *
 * @example
 * ```tsx
 * function NetworkIndicator() {
 *   const { isOnline, effectiveType, rtt } = useNetworkInfo();
 *
 *   if (!isOnline) return <Tag color="red">Offline</Tag>;
 *   if (effectiveType === 'slow-2g') return <Tag color="orange">Slow</Tag>;
 *   return <Tag color="green">Online</Tag>;
 * }
 * ```
 */
export function useNetworkInfo(): NetworkInfo {
    const isOnline = useNetworkStatus();
    const [connectionInfo, setConnectionInfo] = useState<Omit<NetworkInfo, 'isOnline'>>({});

    const updateConnectionInfo = useCallback(() => {
        const nav = navigator as NavigatorWithConnection;
        const connection = nav.connection;

        if (connection) {
            setConnectionInfo({
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData,
            });
        }
    }, []);

    useEffect(() => {
        updateConnectionInfo();

        const nav = navigator as NavigatorWithConnection;
        const connection = nav.connection;

        if (connection?.addEventListener) {
            connection.addEventListener('change', updateConnectionInfo);
            return () => {
                connection.removeEventListener?.('change', updateConnectionInfo);
            };
        }
        return undefined;
    }, [updateConnectionInfo]);

    return {
        isOnline,
        ...connectionInfo,
    };
}

// ============================================
// Offline Duration Tracking
// ============================================

/**
 * Hook to track how long the user has been offline
 *
 * @example
 * ```tsx
 * function OfflineBanner() {
 *   const { isOffline, offlineDuration } = useOfflineDuration();
 *
 *   if (!isOffline) return null;
 *
 *   return (
 *     <Alert>
 *       You've been offline for {Math.floor(offlineDuration / 1000)}s
 *     </Alert>
 *   );
 * }
 * ```
 */
export function useOfflineDuration(): { isOffline: boolean; offlineDuration: number } {
    const isOnline = useNetworkStatus();
    const [offlineStart, setOfflineStart] = useState<number | null>(null);
    const [offlineDuration, setOfflineDuration] = useState(0);

    useEffect(() => {
        if (!isOnline && offlineStart === null) {
            setOfflineStart(Date.now());
        } else if (isOnline) {
            setOfflineStart(null);
            setOfflineDuration(0);
        }
    }, [isOnline, offlineStart]);

    useEffect(() => {
        if (offlineStart === null) return;

        const interval = setInterval(() => {
            setOfflineDuration(Date.now() - offlineStart);
        }, 1000);

        return () => clearInterval(interval);
    }, [offlineStart]);

    return {
        isOffline: !isOnline,
        offlineDuration,
    };
}

export default useNetworkStatus;
