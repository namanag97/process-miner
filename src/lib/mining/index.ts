/**
 * Process Mining Module
 * Types and utilities for process mining data structures.
 * 
 * NOTE: Core algorithms are now handled by the backend.
 * This module provides shared types used for frontend display.
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

// Utilities (still used for formatting)
export {
    formatDuration,
    calculateMedian,
    calculateAverage,
} from './utils';
