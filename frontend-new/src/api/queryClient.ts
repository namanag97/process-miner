/**
 * TanStack Query Client Configuration
 *
 * Enhanced QueryClient with:
 * - Offline-first mode (use stale data when offline)
 * - Query persistence to localStorage
 * - Configurable retry behavior
 * - Network-aware refetching
 */
import { QueryClient, QueryCache, MutationCache } from '@tanstack/react-query';
import { persistQueryClient } from '@tanstack/query-persist-client-core';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

import { env } from '../config/env';

// ============================================
// Configuration Constants
// ============================================

const CACHE_KEY = 'react-query-cache';
const CACHE_VERSION = env.APP_VERSION || '0.0.0';
const MAX_CACHE_AGE_MS = 24 * 60 * 60 * 1000; // 24 hours

// ============================================
// Logging Utilities
// ============================================

function logQueryEvent(type: 'success' | 'error', queryKey: unknown, data?: unknown) {
    if (process.env.NODE_ENV === 'development') {
        const key = Array.isArray(queryKey) ? queryKey.join('/') : String(queryKey);
        if (type === 'success') {
            console.debug(`[Query] ${key} - success`, data ? typeof data : '');
        } else {
            console.warn(`[Query] ${key} - error`, data);
        }
    }
}

function logMutationEvent(type: 'start' | 'success' | 'error', mutationKey: unknown, data?: unknown) {
    if (process.env.NODE_ENV === 'development') {
        const key = mutationKey
            ? Array.isArray(mutationKey) ? mutationKey.join('/') : String(mutationKey)
            : 'anonymous';
        console.debug(`[Mutation] ${key} - ${type}`, data || '');
    }
}

// ============================================
// Query Cache with Logging
// ============================================

const queryCache = new QueryCache({
    onSuccess: (data, query) => {
        logQueryEvent('success', query.queryKey, data);
    },
    onError: (error, query) => {
        logQueryEvent('error', query.queryKey, error instanceof Error ? error.message : error);
    },
});

// ============================================
// Mutation Cache with Logging
// ============================================

const mutationCache = new MutationCache({
    onMutate: (variables, mutation) => {
        logMutationEvent('start', mutation.options.mutationKey, variables);
    },
    onSuccess: (data, _variables, _context, mutation) => {
        logMutationEvent('success', mutation.options.mutationKey, data);
    },
    onError: (error, _variables, _context, mutation) => {
        logMutationEvent('error', mutation.options.mutationKey, error);
    },
});

// ============================================
// QueryClient Instance
// ============================================

/**
 * Enhanced QueryClient with offline-first configuration
 */
export const queryClient = new QueryClient({
    queryCache,
    mutationCache,
    defaultOptions: {
        queries: {
            // Cache data for 5 minutes before considering stale
            staleTime: 5 * 60 * 1000,
            // Keep cached data for 30 minutes
            gcTime: 30 * 60 * 1000,
            // Retry configuration with exponential backoff
            retry: (failureCount, error) => {
                // Don't retry on 4xx errors (client errors)
                if (error instanceof Error && 'response' in error) {
                    const status = (error as { response?: { status?: number } }).response?.status;
                    if (status && status >= 400 && status < 500) {
                        return false;
                    }
                }
                return failureCount < 3;
            },
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
            // Don't refetch on window focus when offline
            refetchOnWindowFocus: () => navigator.onLine,
            // Use stale data when offline (offline-first)
            networkMode: 'offlineFirst',
            // Don't refetch on mount if data is still fresh
            refetchOnMount: true,
            // Don't refetch on reconnect if we have cached data
            refetchOnReconnect: 'always',
        },
        mutations: {
            // Retry mutations once (more dangerous to retry)
            retry: 1,
            retryDelay: 1000,
            // Pause mutations when offline
            networkMode: 'offlineFirst',
        },
    },
});

// ============================================
// Query Persistence
// ============================================

/**
 * Initialize query persistence to localStorage
 *
 * This persists the query cache across page refreshes,
 * allowing users to see cached data immediately on reload.
 */
export function initializeQueryPersistence(): void {
    // Only persist in browser environment
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        return;
    }

    try {
        const persister = createSyncStoragePersister({
            storage: window.localStorage,
            key: CACHE_KEY,
            // Serialize/deserialize with version check
            serialize: (data) => {
                return JSON.stringify({
                    version: CACHE_VERSION,
                    data,
                });
            },
            deserialize: (cachedString) => {
                try {
                    const parsed = JSON.parse(cachedString);
                    // Invalidate cache if version changed
                    if (parsed.version !== CACHE_VERSION) {
                        console.log('[QueryPersist] Cache version mismatch, clearing cache');
                        return undefined;
                    }
                    return parsed.data;
                } catch {
                    return undefined;
                }
            },
        });

        persistQueryClient({
            queryClient,
            persister,
            maxAge: MAX_CACHE_AGE_MS,
            buster: CACHE_VERSION,
        });

        console.log('[QueryPersist] Persistence initialized');
    } catch (error) {
        console.warn('[QueryPersist] Failed to initialize persistence:', error);
    }
}

// ============================================
// Utility Functions
// ============================================

/**
 * Clear all cached queries
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
} {
    const queries = queryClient.getQueryCache().getAll();
    return {
        queryCount: queries.length,
        staleQueries: queries.filter(q => q.isStale()).length,
        fetchingQueries: queries.filter(q => q.state.fetchStatus === 'fetching').length,
    };
}

/**
 * Prefetch common queries on app startup
 */
export async function prefetchCommonQueries(): Promise<void> {
    // Prefetch queries that are commonly needed
    // This can be customized based on your app's needs
    try {
        // Example: Prefetch user data, common configs, etc.
        // await queryClient.prefetchQuery({ queryKey: ['user'], queryFn: fetchUser });
        console.log('[QueryClient] Prefetch complete');
    } catch (error) {
        console.warn('[QueryClient] Prefetch failed:', error);
    }
}

export default queryClient;
