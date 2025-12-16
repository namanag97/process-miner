/**
 * Process Mining Worker
 * Handles heavy mining operations in a background thread
 */

import { mineProcess } from './process-miner';
import type { ParsedData, ColumnConfig } from '../stores/useAppStore';

// Define message types
export type WorkerMessage =
    | { type: 'START'; payload: { parsedData: ParsedData; columnConfig: ColumnConfig } };

export type WorkerResponse =
    | { type: 'PROGRESS'; stage: string; progress: number }
    | { type: 'SUCCESS'; result: any } // ProcessModel
    | { type: 'ERROR'; error: string };

self.onmessage = async (e: MessageEvent<WorkerMessage>) => {
    const { type, payload } = e.data;

    if (type === 'START') {
        const { parsedData, columnConfig } = payload;

        try {
            const result = await mineProcess(
                parsedData,
                columnConfig,
                (stage, progress) => {
                    self.postMessage({ type: 'PROGRESS', stage, progress });
                }
            );

            if (result.success) {
                self.postMessage({ type: 'SUCCESS', result: result.model });
            } else {
                self.postMessage({ type: 'ERROR', error: result.error || 'Unknown mining error' });
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Worker error';
            self.postMessage({ type: 'ERROR', error: errorMessage });
        }
    }
};
