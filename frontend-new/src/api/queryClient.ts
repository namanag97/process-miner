/**
 * TanStack Query Client Configuration Utilities
 *
 * Utilities for working with the QueryClient from SDKProvider:
 * - Query persistence to localStorage
 * - Cache management utilities
 * - Offline-first configuration helpers
 *
 * Note: The QueryClient itself is created in SDKProvider from @lumina/design-system.
 * These utilities extend its functionality.
 */
import { queryClient } from '@lumina/design-system';
import { env } from '../config/env';

// ============================================
// Configuration Constants
// ============================================

const CACHE_KEY = 'react-query-cache';
const CACHE_VERSION = env.APP_VERSION || '0.0.0';
const MAX_CACHE_AGE_MS = 24 * 60 * 60 * 1000; // 24 hours

// ============================================
// Cache Persistence Types
// ============================================

interface CachedQueryData {
    queryKey: unknown[];
    data: unknown;
    dataUpdatedAt: number;
}

interface PersistedCache {
    version: string;
    timestamp: number;
    queries: CachedQueryData[];
}

// ============================================
// Query Persistence
// ============================================

/**
 * Save current query cache to localStorage
 *
 * Only persists queries that have data and are not stale.
 */
function saveQueryCache(): void {
    try {
        const queries = queryClient.getQueryCache().getAll();
        const cachedData: CachedQueryData[] = [];

        for (const query of queries) {
            // Only persist queries with data that aren't too old
            if (
                query.state.data !== undefined &&
                query.state.status === 'success' &&
                Date.now() - query.state.dataUpdatedAt < MAX_CACHE_AGE_MS
            ) {
                cachedData.push({
                    queryKey: [...query.queryKey],
                    data: query.state.data,
                    dataUpdatedAt: query.state.dataUpdatedAt,
                });
            }
        }

        const persistedCache: PersistedCache = {
            version: CACHE_VERSION,
            timestamp: Date.now(),
            queries: cachedData,
        };

        localStorage.setItem(CACHE_KEY, JSON.stringify(persistedCache));
        console.log(`[QueryPersist] Saved ${cachedData.length} queries to cache`);
    } catch (error) {
        console.warn('[QueryPersist] Failed to save cache:', error);
    }
}

/**
 * Restore query cache from localStorage
 *
 * Validates version and age before restoring.
 */
function restoreQueryCache(): void {
    try {
        const cached = localStorage.getItem(CACHE_KEY);
        if (!cached) return;

        const persistedCache: PersistedCache = JSON.parse(cached);

        // Check version
        if (persistedCache.version !== CACHE_VERSION) {
            console.log('[QueryPersist] Cache version mismatch, clearing cache');
            localStorage.removeItem(CACHE_KEY);
            return;
        }

        // Check age
        if (Date.now() - persistedCache.timestamp > MAX_CACHE_AGE_MS) {
            console.log('[QueryPersist] Cache expired, clearing cache');
            localStorage.removeItem(CACHE_KEY);
            return;
        }

        // Restore queries
        let restoredCount = 0;
        for (const cachedQuery of persistedCache.queries) {
            // Check individual query age
            if (Date.now() - cachedQuery.dataUpdatedAt > MAX_CACHE_AGE_MS) {
                continue;
            }

            queryClient.setQueryData(cachedQuery.queryKey, cachedQuery.data);
            restoredCount++;
        }

        console.log(`[QueryPersist] Restored ${restoredCount} queries from cache`);
    } catch (error) {
        console.warn('[QueryPersist] Failed to restore cache:', error);
        localStorage.removeItem(CACHE_KEY);
    }
}

/**
 * Initialize query persistence
 *
 * - Restores cache on startup
 * - Sets up periodic saves
 * - Saves on window unload
 */
export function initializeQueryPersistence(): void {
    // Only persist in browser environment
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        return;
    }

    // Restore cache on startup
    restoreQueryCache();

    // Save cache periodically (every 30 seconds)
    const saveInterval = setInterval(saveQueryCache, 30000);

    // Save cache before unload
    const handleBeforeUnload = () => {
        saveQueryCache();
    };
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Save when tab becomes hidden
    const handleVisibilityChange = () => {
        if (document.hidden) {
            saveQueryCache();
        }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Cleanup function (not typically called, but available)
    const cleanup = () => {
        clearInterval(saveInterval);
        window.removeEventListener('beforeunload', handleBeforeUnload);
        document.removeEventListener('visibilitychange', handleVisibilityChange);
    };

    // Store cleanup for potential use
    (window as unknown as { __queryPersistCleanup?: () => void }).__queryPersistCleanup = cleanup;

    console.log('[QueryPersist] Persistence initialized');
}

// ============================================
// Utility Functions
// ============================================

/**
 * Clear all cached queries and persisted storage
 */
export function clearQueryCache(): void {
    queryClient.clear();
    localStorage.removeItem(CACHE_KEY);
    console.log('[QueryClient] Cache cleared');
}

/**
 * Get cache statistics
 */
export function getQueryCacheStats(): {
    queryCount: number;
    staleQueries: number;
    fetchingQueries: number;
    persistedSize: number;
} {
    const queries = queryClient.getQueryCache().getAll();
    const persistedData = localStorage.getItem(CACHE_KEY);

    return {
        queryCount: queries.length,
        staleQueries: queries.filter(q => q.isStale()).length,
        fetchingQueries: queries.filter(q => q.state.fetchStatus === 'fetching').length,
        persistedSize: persistedData ? persistedData.length : 0,
    };
}

/**
 * Force save the current cache to localStorage
 */
export function forceSaveCache(): void {
    saveQueryCache();
}

/**
 * Manually restore cache from localStorage
 */
export function forceRestoreCache(): void {
    restoreQueryCache();
}

// Re-export queryClient for convenience
export { queryClient };

export default queryClient;
