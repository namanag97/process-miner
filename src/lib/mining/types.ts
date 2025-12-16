/**
 * Process Mining Types
 * Core type definitions for process mining operations
 */

/**
 * Represents a single event in a process log
 */
export interface Event {
    /** Unique identifier for the case/trace this event belongs to */
    caseId: string;
    /** The activity name performed in this event */
    activity: string;
    /** When this event occurred */
    timestamp: Date;
    /** Optional: Who or what performed this activity */
    resource?: string;
    /** Optional: Cost associated with this event */
    cost?: number;
    /** The original row data from the source file */
    originalRow: Record<string, unknown>;
}

/**
 * Represents a complete case/trace in the process
 */
export interface Case {
    /** Unique identifier for this case */
    caseId: string;
    /** All events in this case, ordered by timestamp */
    events: Event[];
    /** When the first event occurred */
    startTime: Date;
    /** When the last event occurred */
    endTime: Date;
    /** Total duration of the case in milliseconds */
    duration: number;
    /** Activity sequence as a string (e.g., "A→B→C") */
    variant: string;
}

/**
 * Represents an edge in the Directly-Follows Graph (DFG)
 */
export interface DirectlyFollowsEdge {
    /** Source activity name */
    source: string;
    /** Target activity name */
    target: string;
    /** How many times this transition occurred */
    frequency: number;
    /** Average duration between source and target activities (ms) */
    avgDuration: number;
    /** Case IDs that contain this edge */
    cases: string[];
}

/**
 * Statistics for a single activity
 */
export interface ActivityStats {
    /** Activity name */
    name: string;
    /** How many times this activity occurred */
    frequency: number;
    /** Average duration of this activity (ms) */
    avgDuration: number;
    /** Whether this activity appears as a start activity */
    isStart: boolean;
    /** Whether this activity appears as an end activity */
    isEnd: boolean;
}

/**
 * Represents a unique process variant (trace pattern)
 */
export interface ProcessVariant {
    /** Unique identifier for this variant */
    id: string;
    /** The sequence of activities in this variant */
    sequence: string[];
    /** Number of cases following this variant */
    caseCount: number;
    /** Percentage of total cases following this variant */
    percentage: number;
    /** Average duration for cases of this variant (ms) */
    avgDuration: number;
    /** Whether this is the most common ("happy") path */
    isHappyPath: boolean;
    /** Case IDs that follow this variant */
    caseIds: string[];
}

/**
 * Represents a deviation from the expected process
 */
export interface Deviation {
    /** Type of deviation */
    type: 'rework' | 'skip' | 'unusual_path';
    /** Human-readable description of the deviation */
    description: string;
    /** Case IDs affected by this deviation */
    affectedCases: string[];
    /** How often this deviation occurs */
    frequency: number;
}

/**
 * Overall process statistics
 */
export interface ProcessStats {
    /** Total number of cases in the log */
    totalCases: number;
    /** Total number of events in the log */
    totalEvents: number;
    /** Average case duration (ms) */
    avgCaseDuration: number;
    /** Median case duration (ms) */
    medianCaseDuration: number;
    /** Activities that start cases */
    startActivities: string[];
    /** Activities that end cases */
    endActivities: string[];
}

/**
 * Complete process model containing all mining results
 */
export interface ProcessModel {
    /** Statistics for each activity */
    activities: ActivityStats[];
    /** Edges in the Directly-Follows Graph */
    edges: DirectlyFollowsEdge[];
    /** All discovered process variants */
    variants: ProcessVariant[];
    /** Detected deviations from the expected process */
    deviations: Deviation[];
    /** Overall process statistics */
    stats: ProcessStats;
}
