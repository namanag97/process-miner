/**
 * Directly-Follows Graph (DFG) Builder
 * Constructs DFG from process cases for process discovery
 */

import { createLogger } from '../debug-logger';
import type { Case, DirectlyFollowsEdge, ActivityStats } from './types';
import { calculateAverage } from './utils';

const logger = createLogger('dfg-builder');

/**
 * Edge data accumulated during DFG construction
 */
interface EdgeAccumulator {
    source: string;
    target: string;
    durations: number[];
    cases: Set<string>;
}

/**
 * Activity data accumulated during stats construction
 */
interface ActivityAccumulator {
    name: string;
    occurrences: number;
    durations: number[];
    isStart: boolean;
    isEnd: boolean;
}

/**
 * Result of DFG construction
 */
export interface DFGResult {
    edges: DirectlyFollowsEdge[];
    activities: ActivityStats[];
}

/**
 * Builds a Directly-Follows Graph from a set of cases
 * 
 * For each case, iterates through events in order and records
 * consecutive event pairs (A→B) as edges. Tracks frequency,
 * average duration, and which cases contain each edge.
 * 
 * @param cases Array of cases to process
 * @returns DFG edges and activity statistics
 */
export function buildDirectlyFollowsGraph(cases: Case[]): DFGResult {
    logger.info('🔨 Building Directly-Follows Graph...');

    const edgeMap = new Map<string, EdgeAccumulator>();
    const activityMap = new Map<string, ActivityAccumulator>();
    const totalCases = cases.length;

    // Process each case
    for (let i = 0; i < cases.length; i++) {
        const caseData = cases[i];

        // Log progress every 100 cases
        if ((i + 1) % 100 === 0 || i === cases.length - 1) {
            logger.info(`Processing case ${i + 1}/${totalCases}...`);
        }

        const events = caseData.events;

        if (events.length === 0) {
            continue;
        }

        // Process each event in the case
        for (let j = 0; j < events.length; j++) {
            const event = events[j];
            const activityName = event.activity;

            // Track activity occurrence
            let activityAcc = activityMap.get(activityName);
            if (!activityAcc) {
                activityAcc = {
                    name: activityName,
                    occurrences: 0,
                    durations: [],
                    isStart: false,
                    isEnd: false,
                };
                activityMap.set(activityName, activityAcc);
            }
            activityAcc.occurrences++;

            // Mark start/end activities
            if (j === 0) {
                activityAcc.isStart = true;
            }
            if (j === events.length - 1) {
                activityAcc.isEnd = true;
            }

            // Calculate duration for this activity (time until next event)
            if (j < events.length - 1) {
                const nextEvent = events[j + 1];
                const duration = nextEvent.timestamp.getTime() - event.timestamp.getTime();
                activityAcc.durations.push(duration);

                // Create edge to next activity
                const edgeKey = `${activityName}→${nextEvent.activity}`;
                let edgeAcc = edgeMap.get(edgeKey);
                if (!edgeAcc) {
                    edgeAcc = {
                        source: activityName,
                        target: nextEvent.activity,
                        durations: [],
                        cases: new Set(),
                    };
                    edgeMap.set(edgeKey, edgeAcc);
                }
                edgeAcc.durations.push(duration);
                edgeAcc.cases.add(caseData.caseId);
            }
        }
    }

    // Convert edge accumulators to final edges
    const edges: DirectlyFollowsEdge[] = Array.from(edgeMap.values()).map((acc) => ({
        source: acc.source,
        target: acc.target,
        frequency: acc.durations.length,
        avgDuration: calculateAverage(acc.durations),
        cases: Array.from(acc.cases),
    }));

    // Convert activity accumulators to final stats
    const activities: ActivityStats[] = Array.from(activityMap.values()).map((acc) => ({
        name: acc.name,
        frequency: acc.occurrences,
        avgDuration: calculateAverage(acc.durations),
        isStart: acc.isStart,
        isEnd: acc.isEnd,
    }));

    // Log summary
    const startActivities = activities.filter((a) => a.isStart).map((a) => a.name);
    const endActivities = activities.filter((a) => a.isEnd).map((a) => a.name);

    logger.info(`Found ${edges.length} unique edges in DFG`);
    logger.info(`Found ${activities.length} unique activities`);
    logger.info(`Start activities: ${startActivities.join(', ')}`);
    logger.info(`End activities: ${endActivities.join(', ')}`);
    logger.info('✅ DFG construction complete');

    return { edges, activities };
}

/**
 * Builds activity statistics from a set of cases
 * 
 * Counts frequency of each activity, identifies start/end activities,
 * and calculates average time spent at each activity.
 * 
 * @param cases Array of cases to process
 * @returns Array of activity statistics
 */
export function buildActivityStats(cases: Case[]): ActivityStats[] {
    logger.info('📊 Building activity statistics...');

    const activityMap = new Map<string, ActivityAccumulator>();

    for (const caseData of cases) {
        const events = caseData.events;

        if (events.length === 0) {
            continue;
        }

        for (let j = 0; j < events.length; j++) {
            const event = events[j];
            const activityName = event.activity;

            let activityAcc = activityMap.get(activityName);
            if (!activityAcc) {
                activityAcc = {
                    name: activityName,
                    occurrences: 0,
                    durations: [],
                    isStart: false,
                    isEnd: false,
                };
                activityMap.set(activityName, activityAcc);
            }

            activityAcc.occurrences++;

            // Mark start activity (first event in case)
            if (j === 0) {
                activityAcc.isStart = true;
            }

            // Mark end activity (last event in case)
            if (j === events.length - 1) {
                activityAcc.isEnd = true;
            }

            // Calculate duration (time until next event in same case)
            if (j < events.length - 1) {
                const nextEvent = events[j + 1];
                const duration = nextEvent.timestamp.getTime() - event.timestamp.getTime();
                activityAcc.durations.push(duration);
            }
        }
    }

    const activities: ActivityStats[] = Array.from(activityMap.values()).map((acc) => ({
        name: acc.name,
        frequency: acc.occurrences,
        avgDuration: calculateAverage(acc.durations),
        isStart: acc.isStart,
        isEnd: acc.isEnd,
    }));

    const startActivities = activities.filter((a) => a.isStart).map((a) => a.name);
    const endActivities = activities.filter((a) => a.isEnd).map((a) => a.name);

    logger.info(`Found ${activities.length} unique activities`);
    logger.info(`Start activities: ${startActivities.join(', ')}`);
    logger.info(`End activities: ${endActivities.join(', ')}`);
    logger.info('✅ Activity statistics complete');

    return activities;
}
