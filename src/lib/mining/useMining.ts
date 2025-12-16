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

        try {
            // Run mining in a microtask to allow UI to update
            const result = await new Promise<MiningResult>((resolve) => {
                // Use setTimeout to allow the UI to render the "Starting" state
                setTimeout(() => {
                    const miningResult = mineProcess(parsedData, columnConfig, (stage, prog) => {
                        setProgress({ stage, progress: prog });
                    });
                    resolve(miningResult);
                }, 0);
            });

            if (result.success && result.model) {
                setResults(result.model);
                setProgress({ stage: 'Complete', progress: 100 });
            } else {
                setError(result.error || 'Mining failed');
                setProgress({ stage: 'Failed', progress: 0 });
            }

            setWarnings(result.warnings);
            setIsProcessing(false);

            return result;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
            setProgress({ stage: 'Failed', progress: 0 });
            setIsProcessing(false);

            return {
                success: false,
                model: null,
                error: errorMessage,
                warnings: [],
            };
        }
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
