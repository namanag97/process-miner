/**
 * Process Mining Module
 * Core algorithms and utilities for process discovery and analysis
 */

// Types
export type {
    Event,
    Case,
    DirectlyFollowsEdge,
    ActivityStats,
    ProcessVariant,
    Deviation,
    ProcessStats,
    ProcessModel,
} from './types';

// Utilities
export {
    groupEventsByCase,
    sortEventsByTime,
    calculateDuration,
    formatDuration,
    getVariantKey,
    calculateMedian,
    calculateAverage,
} from './utils';

// DFG Builder
export {
    buildDirectlyFollowsGraph,
    buildActivityStats,
    type DFGResult,
} from './dfg-builder';

// Variant Analyzer
export {
    analyzeVariants,
    detectDeviations,
    analyzeVariantsWithDeviations,
    type VariantAnalysisResult,
} from './variant-analyzer';

// Process Miner (Main Orchestrator)
export {
    mineProcess,
    type MiningResult,
    type ProgressCallback,
} from './process-miner';

// React Hook
export {
    useMining,
    type MiningProgress,
    type UseMiningResult,
} from './useMining';
