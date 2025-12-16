/**
 * useMining Hook
 * React hook for running process mining with progress updates
 */

import { useState, useCallback } from 'react';
import type { ParsedData, ColumnConfig } from '../stores/useAppStore';
import type { ProcessModel } from './types';
import { mineProcess, type MiningResult } from './process-miner';

/**
 * Mining progress state
 */
export interface MiningProgress {
    stage: string;
    progress: number;
}

/**
 * Return type for useMining hook
 */
export interface UseMiningResult {
    /** Execute the mining process */
    mine: () => Promise<MiningResult>;
    /** Whether mining is currently in progress */
    isProcessing: boolean;
    /** Current progress information */
    progress: MiningProgress;
    /** Mining results (if completed) */
    results: ProcessModel | null;
    /** Error message (if failed) */
    error: string | null;
    /** Warning messages from mining */
    warnings: string[];
    /** Reset the mining state */
    reset: () => void;
}

/**
 * Hook for running process mining with progress updates
 * 
 * @param parsedData The parsed CSV/XES data
 * @param columnConfig Column mapping configuration
 * @returns Mining functions and state
 */
export function useMining(
    parsedData: ParsedData | null,
    columnConfig: ColumnConfig | null
): UseMiningResult {
    const [isProcessing, setIsProcessing] = useState(false);
    const [progress, setProgress] = useState<MiningProgress>({ stage: 'Idle', progress: 0 });
    const [results, setResults] = useState<ProcessModel | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [warnings, setWarnings] = useState<string[]>([]);

    const reset = useCallback(() => {
        setIsProcessing(false);
        setProgress({ stage: 'Idle', progress: 0 });
        setResults(null);
        setError(null);
        setWarnings([]);
    }, []);

    const mine = useCallback(async (): Promise<MiningResult> => {
        // Validate inputs
        if (!parsedData) {
            const result: MiningResult = {
                success: false,
                model: null,
                error: 'No parsed data available',
                warnings: [],
            };
            setError(result.error!);
            return result;
        }

        if (!columnConfig) {
            const result: MiningResult = {
                success: false,
                model: null,
                error: 'No column configuration available',
                warnings: [],
            };
            setError(result.error!);
            return result;
        }

        // Reset state
        setIsProcessing(true);
        setError(null);
        setResults(null);
        setWarnings([]);
        setProgress({ stage: 'Starting', progress: 0 });

        return new Promise<MiningResult>((resolve) => {
            // Instantiate worker
            const worker = new Worker(new URL('./worker.ts', import.meta.url), {
                type: 'module'
            });

            worker.onmessage = (e) => {
                const { type } = e.data;

                if (type === 'PROGRESS') {
                    setProgress({ stage: e.data.stage, progress: e.data.progress });
                } else if (type === 'SUCCESS') {
                    setResults(e.data.result);
                    setProgress({ stage: 'Complete', progress: 100 });
                    setIsProcessing(false);
                    worker.terminate();
                    resolve({
                        success: true,
                        model: e.data.result,
                        warnings: [], // Warnings not passed from worker in this simple version yet, can add later
                    });
                } else if (type === 'ERROR') {
                    setError(e.data.error);
                    setProgress({ stage: 'Failed', progress: 0 });
                    setIsProcessing(false);
                    worker.terminate();
                    resolve({
                        success: false,
                        model: null,
                        error: e.data.error,
                        warnings: [],
                    });
                }
            };

            worker.onerror = (err) => {
                const errorMessage = err.message || 'Unknown worker error';
                setError(errorMessage);
                setProgress({ stage: 'Failed', progress: 0 });
                setIsProcessing(false);
                worker.terminate();
                resolve({
                    success: false,
                    model: null,
                    error: errorMessage,
                    warnings: [],
                });
            };

            // Start mining
            worker.postMessage({
                type: 'START',
                payload: { parsedData, columnConfig }
            });
        });
    }, [parsedData, columnConfig]);

    return {
        mine,
        isProcessing,
        progress,
        results,
        error,
        warnings,
        reset,
    };
}
