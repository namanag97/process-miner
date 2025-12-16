/**
 * Process Miner - Main Mining Orchestrator
 * Coordinates all process mining operations to generate a complete ProcessModel
 */

import { createLogger } from '../debug-logger';
import type { ParsedData, ColumnConfig } from '../stores/useAppStore';
import type { Event, Case, ProcessModel, ProcessStats } from './types';
import {
    groupEventsByCase,
    sortEventsByTime,
    calculateDuration,
    getVariantKey,
    calculateMedian,
    calculateAverage,
} from './utils';
import { buildDirectlyFollowsGraph } from './dfg-builder';
import { analyzeVariantsWithDeviations } from './variant-analyzer';

const logger = createLogger('process-miner');

/**
 * Parse options for timestamp handling
 */
interface ParseOptions {
    dateFormats?: string[];
}

/**
 * Result of the mining process
 */
export interface MiningResult {
    success: boolean;
    model: ProcessModel | null;
    error?: string;
    warnings: string[];
}

/**
 * Progress callback for UI updates
 */
export type ProgressCallback = (stage: string, progress: number) => void;

/**
 * Attempts to parse a timestamp string into a Date object
 * Tries multiple common formats
 */
function parseTimestamp(value: unknown): Date | null {
    if (value instanceof Date) {
        return value;
    }

    if (typeof value === 'number') {
        // Assume Unix timestamp (seconds or milliseconds)
        const ts = value > 1e12 ? value : value * 1000;
        return new Date(ts);
    }

    if (typeof value === 'string') {
        // Try ISO format first
        const isoDate = new Date(value);
        if (!isNaN(isoDate.getTime())) {
            return isoDate;
        }

        // Try common formats
        const formats = [
            // ISO variants
            /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})/,
            /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/,
            // US format
            /^(\d{1,2})\/(\d{1,2})\/(\d{4}) (\d{1,2}):(\d{2}):(\d{2})/,
            // European format
            /^(\d{1,2})\.(\d{1,2})\.(\d{4}) (\d{1,2}):(\d{2}):(\d{2})/,
        ];

        for (const format of formats) {
            const match = value.match(format);
            if (match) {
                const parsed = new Date(value);
                if (!isNaN(parsed.getTime())) {
                    return parsed;
                }
            }
        }
    }

    return null;
}

/**
 * Transforms raw parsed data into Event objects
 */
function transformToEvents(
    parsedData: ParsedData,
    columnConfig: ColumnConfig,
    onProgress?: ProgressCallback
): { events: Event[]; warnings: string[] } {
    const { rows } = parsedData;
    const { caseId: caseIdCol, activity: activityCol, timestamp: timestampCol, resource: resourceCol, cost: costCol } = columnConfig;

    logger.info(`🔄 Transforming ${rows.length} rows to events...`);
    onProgress?.('Transforming data', 0);

    const events: Event[] = [];
    const warnings: string[] = [];
    let parseErrors = 0;

    for (let i = 0; i < rows.length; i++) {
        const row = rows[i] as Record<string, unknown>;

        // Progress update every 1000 rows
        if (i % 1000 === 0) {
            onProgress?.('Transforming data', (i / rows.length) * 100);
        }

        // Extract required fields
        const caseIdValue = row[caseIdCol];
        const activityValue = row[activityCol];
        const timestampValue = row[timestampCol];

        // Validate required fields
        if (caseIdValue === undefined || caseIdValue === null || caseIdValue === '') {
            parseErrors++;
            continue;
        }

        if (activityValue === undefined || activityValue === null || activityValue === '') {
            parseErrors++;
            continue;
        }

        // Parse timestamp
        const timestamp = parseTimestamp(timestampValue);
        if (!timestamp) {
            parseErrors++;
            if (parseErrors <= 5) {
                logger.warn(`Failed to parse timestamp: ${timestampValue} (row ${i + 1})`);
            }
            continue;
        }

        // Create event
        const event: Event = {
            caseId: String(caseIdValue),
            activity: String(activityValue),
            timestamp,
            originalRow: row,
        };

        // Add optional fields
        if (resourceCol && row[resourceCol] !== undefined) {
            event.resource = String(row[resourceCol]);
        }

        if (costCol && row[costCol] !== undefined) {
            const costValue = Number(row[costCol]);
            if (!isNaN(costValue)) {
                event.cost = costValue;
            }
        }

        events.push(event);
    }

    if (parseErrors > 0) {
        const warning = `${parseErrors} rows could not be parsed (missing data or invalid timestamps)`;
        warnings.push(warning);
        logger.warn(warning);
    }

    logger.info(`Successfully transformed ${events.length} events from ${rows.length} rows`);
    onProgress?.('Transforming data', 100);

    return { events, warnings };
}

/**
 * Groups events into Case objects
 */
function buildCases(events: Event[], onProgress?: ProgressCallback): Case[] {
    logger.info('📦 Grouping events into cases...');
    onProgress?.('Building cases', 0);

    const groupedEvents = groupEventsByCase(events);
    const cases: Case[] = [];
    const totalCases = groupedEvents.size;
    let processed = 0;

    Array.from(groupedEvents.entries()).forEach(([caseId, caseEvents]) => {
        // Sort events by timestamp
        const sortedEvents = sortEventsByTime(caseEvents);

        if (sortedEvents.length === 0) {
            return;
        }

        const startTime = sortedEvents[0].timestamp;
        const endTime = sortedEvents[sortedEvents.length - 1].timestamp;
        const duration = calculateDuration(startTime, endTime);
        const variant = getVariantKey(sortedEvents);

        cases.push({
            caseId,
            events: sortedEvents,
            startTime,
            endTime,
            duration,
            variant,
        });

        processed++;
        if (processed % 100 === 0) {
            onProgress?.('Building cases', (processed / totalCases) * 100);
        }
    });

    logger.info(`📦 Grouped into ${cases.length} cases`);
    onProgress?.('Building cases', 100);

    return cases;
}

/**
 * Calculates overall process statistics
 */
function calculateStats(
    cases: Case[],
    events: Event[],
    startActivities: string[],
    endActivities: string[]
): ProcessStats {
    const durations = cases.map((c) => c.duration);

    return {
        totalCases: cases.length,
        totalEvents: events.length,
        avgCaseDuration: calculateAverage(durations),
        medianCaseDuration: calculateMedian(durations),
        startActivities,
        endActivities,
    };
}

/**
 * Helper to yield to the event loop so React can render
 */
function yieldToEventLoop(): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, 0));
}

/**
 * Main mining function - orchestrates all mining operations
 * 
 * @param parsedData The parsed CSV/XES data
 * @param columnConfig Column mapping configuration
 * @param onProgress Optional progress callback for UI updates
 * @returns Complete ProcessModel or error
 */
export async function mineProcess(
    parsedData: ParsedData,
    columnConfig: ColumnConfig,
    onProgress?: ProgressCallback
): Promise<MiningResult> {
    logger.info('⛏️ Starting process mining...');
    const startTime = Date.now();
    const warnings: string[] = [];

    try {
        // Step 1: Transform raw data to Event objects
        onProgress?.('Starting', 0);
        await yieldToEventLoop();

        const { events, warnings: transformWarnings } = transformToEvents(
            parsedData,
            columnConfig,
            onProgress
        );
        warnings.push(...transformWarnings);

        if (events.length === 0) {
            return {
                success: false,
                model: null,
                error: 'No valid events could be extracted from the data',
                warnings,
            };
        }

        // Step 2: Group events into Cases
        await yieldToEventLoop();
        const cases = buildCases(events, onProgress);

        if (cases.length === 0) {
            return {
                success: false,
                model: null,
                error: 'No cases could be created from the events',
                warnings,
            };
        }

        // Step 3: Build DFG
        onProgress?.('Building DFG', 0);
        await yieldToEventLoop();
        const { edges, activities } = buildDirectlyFollowsGraph(cases);
        onProgress?.('Building DFG', 100);

        // Step 4 & 5: Analyze variants and detect deviations
        onProgress?.('Analyzing variants', 0);
        await yieldToEventLoop();
        const { variants, deviations } = analyzeVariantsWithDeviations(cases);
        onProgress?.('Analyzing variants', 100);

        // Step 6: Calculate overall statistics
        onProgress?.('Calculating statistics', 0);
        await yieldToEventLoop();
        const startActivities = activities.filter((a) => a.isStart).map((a) => a.name);
        const endActivities = activities.filter((a) => a.isEnd).map((a) => a.name);
        const stats = calculateStats(cases, events, startActivities, endActivities);
        onProgress?.('Calculating statistics', 100);

        // Step 7: Build complete ProcessModel
        const model: ProcessModel = {
            activities,
            edges,
            variants,
            deviations,
            stats,
        };

        const duration = Date.now() - startTime;
        logger.info(
            `✅ Process mining complete! Generated process model with ${activities.length} activities and ${edges.length} edges (${duration}ms)`
        );

        onProgress?.('Complete', 100);

        return {
            success: true,
            model,
            warnings,
        };
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error during mining';
        logger.error(`Mining failed: ${errorMessage}`);

        return {
            success: false,
            model: null,
            error: errorMessage,
            warnings,
        };
    }
}
