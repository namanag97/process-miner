/**
 * Offline Mutation Queue
 *
 * Stores mutations that occur while offline and replays them when back online.
 * Uses localStorage for persistence across page refreshes.
 */

const QUEUE_KEY = 'offline_mutation_queue';
const MAX_QUEUE_SIZE = 100;
const MAX_AGE_MS = 24 * 60 * 60 * 1000; // 24 hours

// ============================================
// Types
// ============================================

export interface QueuedMutation {
    id: string;
    mutationKey: unknown[];
    variables: unknown;
    timestamp: number;
    endpoint: string;
    method: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
    retryCount: number;
    maxRetries: number;
}

export interface OfflineQueueStats {
    size: number;
    oldestTimestamp: number | null;
    newestTimestamp: number | null;
}

// ============================================
// Queue Operations
// ============================================

/**
 * Offline mutation queue manager
 */
export const offlineQueue = {
    /**
     * Add a mutation to the queue
     */
    add(mutation: Omit<QueuedMutation, 'id' | 'timestamp' | 'retryCount'>): string {
        const queue = this.getAll();

        // Enforce max queue size
        while (queue.length >= MAX_QUEUE_SIZE) {
            queue.shift(); // Remove oldest
        }

        const newItem: QueuedMutation = {
            ...mutation,
            id: crypto.randomUUID(),
            timestamp: Date.now(),
            retryCount: 0,
        };

        queue.push(newItem);
        this._save(queue);

        console.log(`[OfflineQueue] Added mutation: ${newItem.method} ${newItem.endpoint}`);
        return newItem.id;
    },

    /**
     * Get all queued mutations
     */
    getAll(): QueuedMutation[] {
        try {
            const stored = localStorage.getItem(QUEUE_KEY);
            if (!stored) return [];

            const queue: QueuedMutation[] = JSON.parse(stored);

            // Filter out expired items
            const now = Date.now();
            const validItems = queue.filter(item => (now - item.timestamp) < MAX_AGE_MS);

            // Save back if we removed any expired items
            if (validItems.length !== queue.length) {
                this._save(validItems);
            }

            return validItems;
        } catch (error) {
            console.error('[OfflineQueue] Failed to parse queue:', error);
            return [];
        }
    },

    /**
     * Get a specific mutation by ID
     */
    get(id: string): QueuedMutation | undefined {
        return this.getAll().find(m => m.id === id);
    },

    /**
     * Remove a mutation from the queue
     */
    remove(id: string): void {
        const queue = this.getAll().filter(m => m.id !== id);
        this._save(queue);
        console.log(`[OfflineQueue] Removed mutation: ${id}`);
    },

    /**
     * Update a mutation's retry count
     */
    incrementRetry(id: string): QueuedMutation | null {
        const queue = this.getAll();
        const index = queue.findIndex(m => m.id === id);

        if (index === -1) return null;

        queue[index].retryCount++;
        this._save(queue);

        return queue[index];
    },

    /**
     * Clear all queued mutations
     */
    clear(): void {
        localStorage.removeItem(QUEUE_KEY);
        console.log('[OfflineQueue] Cleared all mutations');
    },

    /**
     * Get queue statistics
     */
    getStats(): OfflineQueueStats {
        const queue = this.getAll();
        const timestamps = queue.map(m => m.timestamp);

        return {
            size: queue.length,
            oldestTimestamp: timestamps.length > 0 ? Math.min(...timestamps) : null,
            newestTimestamp: timestamps.length > 0 ? Math.max(...timestamps) : null,
        };
    },

    /**
     * Check if the queue has any items
     */
    isEmpty(): boolean {
        return this.getAll().length === 0;
    },

    /**
     * Private: Save queue to localStorage
     */
    _save(queue: QueuedMutation[]): void {
        try {
            localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
        } catch (error) {
            console.error('[OfflineQueue] Failed to save queue:', error);
            // If storage is full, remove oldest items and retry
            if (error instanceof DOMException && error.name === 'QuotaExceededError') {
                const reducedQueue = queue.slice(Math.floor(queue.length / 2));
                localStorage.setItem(QUEUE_KEY, JSON.stringify(reducedQueue));
            }
        }
    },
};

// ============================================
// React Integration Hook
// ============================================

import { useEffect, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { notification } from 'antd';
import { useNetworkStatus } from '../shared/hooks/useNetworkStatus';
import apiClient from './client';

/**
 * Hook to automatically process the offline queue when back online
 *
 * @example
 * ```tsx
 * function App() {
 *   useOfflineQueueProcessor();
 *   return <AppContent />;
 * }
 * ```
 */
export function useOfflineQueueProcessor(): {
    isProcessing: boolean;
    queueSize: number;
    processQueue: () => Promise<void>;
} {
    const isOnline = useNetworkStatus();
    const queryClient = useQueryClient();
    const [isProcessing, setIsProcessing] = useState(false);
    const [queueSize, setQueueSize] = useState(() => offlineQueue.getAll().length);

    // Update queue size when it changes
    useEffect(() => {
        const checkSize = () => setQueueSize(offlineQueue.getAll().length);
        const interval = setInterval(checkSize, 1000);
        return () => clearInterval(interval);
    }, []);

    const processQueue = useCallback(async () => {
        const queue = offlineQueue.getAll();
        if (queue.length === 0) return;

        setIsProcessing(true);

        const notificationKey = 'offline-queue-processing';
        notification.info({
            key: notificationKey,
            message: 'Processing offline actions',
            description: `Syncing ${queue.length} queued action${queue.length > 1 ? 's' : ''}...`,
            duration: 0,
        });

        let successCount = 0;
        let failCount = 0;

        for (const item of queue) {
            try {
                // Re-execute the mutation
                await apiClient.request({
                    method: item.method,
                    url: item.endpoint,
                    data: item.variables,
                });

                offlineQueue.remove(item.id);
                successCount++;

                // Invalidate related queries
                if (item.mutationKey.length > 0) {
                    await queryClient.invalidateQueries({
                        queryKey: [item.mutationKey[0]],
                    });
                }
            } catch (error) {
                const updated = offlineQueue.incrementRetry(item.id);

                if (updated && updated.retryCount >= updated.maxRetries) {
                    offlineQueue.remove(item.id);
                    failCount++;
                    console.error(`[OfflineQueue] Failed to process mutation after ${updated.maxRetries} retries:`, error);
                } else {
                    failCount++;
                    console.warn(`[OfflineQueue] Retry ${updated?.retryCount}/${updated?.maxRetries} for:`, item.endpoint);
                }
            }
        }

        notification.destroy(notificationKey);
        setIsProcessing(false);
        setQueueSize(offlineQueue.getAll().length);

        // Show result notification
        if (successCount > 0 && failCount === 0) {
            notification.success({
                message: 'Offline actions synced',
                description: `Successfully processed ${successCount} action${successCount > 1 ? 's' : ''}.`,
            });
        } else if (failCount > 0) {
            notification.warning({
                message: 'Some actions failed',
                description: `${successCount} succeeded, ${failCount} failed. Failed actions will be retried.`,
            });
        }
    }, [queryClient]);

    // Process queue when coming back online
    useEffect(() => {
        if (isOnline && !isProcessing) {
            const queue = offlineQueue.getAll();
            if (queue.length > 0) {
                // Small delay to ensure network is stable
                const timeout = setTimeout(processQueue, 1000);
                return () => clearTimeout(timeout);
            }
        }
        return undefined;
    }, [isOnline, isProcessing, processQueue]);

    return { isProcessing, queueSize, processQueue };
}

/**
 * Helper to queue a mutation when offline
 *
 * @example
 * ```typescript
 * const mutation = useMutation({
 *   mutationFn: async (data) => {
 *     if (!navigator.onLine) {
 *       queueMutation({
 *         mutationKey: ['datasets'],
 *         variables: data,
 *         endpoint: '/api/v1/datasets',
 *         method: 'POST',
 *       });
 *       throw new Error('Queued for offline');
 *     }
 *     return api.createDataset(data);
 *   }
 * });
 * ```
 */
export function queueMutation(
    mutation: Omit<QueuedMutation, 'id' | 'timestamp' | 'retryCount' | 'maxRetries'> & { maxRetries?: number }
): string {
    return offlineQueue.add({
        ...mutation,
        maxRetries: mutation.maxRetries ?? 3,
    });
}

export default offlineQueue;
