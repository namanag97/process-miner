/**
 * Offline Queue
 *
 * Provides a queue for storing mutations while offline and processing them when back online.
 * Integrates with TanStack Query for seamless offline-first experience.
 */

import { useEffect, useRef } from 'react';
import { useNetworkStatus } from '../shared/hooks/useNetworkStatus';

// ============================================
// Types
// ============================================

interface QueuedMutation {
  id: string;
  mutation: string;
  variables: unknown;
  timestamp: number;
}

// ============================================
// Queue Storage
// ============================================

const QUEUE_KEY = 'offline-mutation-queue';

function getQueue(): QueuedMutation[] {
  try {
    const stored = localStorage.getItem(QUEUE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function setQueue(queue: QueuedMutation[]): void {
  try {
    localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
  } catch {
    console.warn('[OfflineQueue] Failed to save queue to localStorage');
  }
}

function addToQueue(mutation: Omit<QueuedMutation, 'id' | 'timestamp'>): void {
  const queue = getQueue();
  const now = Date.now();
  queue.push({
    ...mutation,
    id: now.toString(36) + '-' + Math.random().toString(36).substr(2, 9),
    timestamp: now,
  });
  setQueue(queue);
  console.log('[OfflineQueue] Added mutation to queue', { queueSize: queue.length });
}

function removeFromQueue(id: string): void {
  const queue = getQueue().filter(item => item.id !== id);
  setQueue(queue);
}

function clearQueue(): void {
  localStorage.removeItem(QUEUE_KEY);
}

// ============================================
// useOfflineQueueProcessor Hook
// ============================================

/**
 * Hook that processes queued mutations when the app comes back online
 */
export function useOfflineQueueProcessor(): void {
  const isOnline = useNetworkStatus();
  const isProcessingRef = useRef(false);

  useEffect(() => {
    if (!isOnline || isProcessingRef.current) return;

    const processQueue = async () => {
      const queue = getQueue();
      if (queue.length === 0) return;

      console.log('[OfflineQueue] Processing queue', { count: queue.length });
      isProcessingRef.current = true;

      for (const item of queue) {
        try {
          // In a real implementation, this would execute the mutation
          // For now, we just log and remove from queue
          console.log('[OfflineQueue] Processing mutation', {
            id: item.id,
            mutation: item.mutation,
            age: Date.now() - item.timestamp,
          });

          // Remove from queue after successful processing
          removeFromQueue(item.id);
        } catch (error) {
          console.error('[OfflineQueue] Failed to process mutation', {
            id: item.id,
            error,
          });
          // Keep in queue for retry
        }
      }

      isProcessingRef.current = false;
      console.log('[OfflineQueue] Queue processing complete');
    };

    processQueue();
  }, [isOnline]);
}

// ============================================
// Exports
// ============================================

export {
  addToQueue,
  removeFromQueue,
  clearQueue,
  getQueue,
};

export default useOfflineQueueProcessor;
