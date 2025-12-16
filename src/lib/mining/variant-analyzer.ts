/**
 * Variant Analysis Module
 * Analyzes process variants and detects deviations from the happy path
 */

import { createLogger } from '../debug-logger';
import type { Case, ProcessVariant, Deviation } from './types';
import { calculateAverage } from './utils';

const logger = createLogger('variant-analyzer');

/**
 * Accumulated data for a single variant during analysis
 */
interface VariantAccumulator {
    sequence: string[];
    cases: Case[];
    durations: number[];
}

/**
 * Result of variant analysis
 */
export interface VariantAnalysisResult {
    variants: ProcessVariant[];
    deviations: Deviation[];
}

/**
 * Analyzes process variants from a set of cases
 * 
 * Groups cases by their activity sequence, calculates statistics,
 * and identifies the happy path (most common variant).
 * 
 * @param cases Array of cases to analyze
 * @returns Array of process variants sorted by frequency
 */
export function analyzeVariants(cases: Case[]): ProcessVariant[] {
    logger.info('📊 Analyzing process variants...');

    if (cases.length === 0) {
        logger.warn('No cases provided for variant analysis');
        return [];
    }

    const variantMap = new Map<string, VariantAccumulator>();

    // Group cases by variant
    for (const caseData of cases) {
        const variantKey = caseData.variant;

        let acc = variantMap.get(variantKey);
        if (!acc) {
            acc = {
                sequence: caseData.events.map((e) => e.activity),
                cases: [],
                durations: [],
            };
            variantMap.set(variantKey, acc);
        }

        acc.cases.push(caseData);
        acc.durations.push(caseData.duration);
    }

    logger.info(`Found ${variantMap.size} unique variants`);

    const totalCases = cases.length;

    // Convert to ProcessVariant objects
    const variants: ProcessVariant[] = Array.from(variantMap.entries()).map(
        ([key, acc], index) => ({
            id: `variant-${index + 1}`,
            sequence: acc.sequence,
            caseCount: acc.cases.length,
            percentage: (acc.cases.length / totalCases) * 100,
            avgDuration: calculateAverage(acc.durations),
            isHappyPath: false, // Will be set after sorting
            caseIds: acc.cases.map((c) => c.caseId),
        })
    );

    // Sort by frequency (most common first)
    variants.sort((a, b) => b.caseCount - a.caseCount);

    // Re-assign IDs based on sorted order and mark happy path
    variants.forEach((variant, index) => {
        variant.id = `variant-${index + 1}`;
        if (index === 0) {
            variant.isHappyPath = true;
        }
    });

    if (variants.length > 0) {
        const happyPath = variants[0];
        logger.info(
            `Happy path: ${happyPath.sequence.join('→')} (${happyPath.percentage.toFixed(1)}% of cases)`
        );
    }

    return variants;
}

/**
 * Detects deviations from the happy path
 * 
 * Identifies three types of deviations:
 * - Rework: Activity appears multiple times in a case
 * - Skip: Activity from happy path is missing
 * - Unusual path: Variant has <1% frequency
 * 
 * @param cases Array of cases to analyze
 * @param happyPath The happy path sequence (most common variant)
 * @returns Array of detected deviations
 */
export function detectDeviations(cases: Case[], happyPath: string[]): Deviation[] {
    logger.info('🔍 Detecting deviations...');

    const deviations: Deviation[] = [];
    const happyPathSet = new Set(happyPath);

    // Track rework patterns: activity -> cases where it's repeated
    const reworkPatterns = new Map<string, Set<string>>();

    // Track skip patterns: activity -> cases where it's skipped
    const skipPatterns = new Map<string, Set<string>>();

    // Track unusual paths: cases in variants with <1% frequency
    const unusualPathCases = new Set<string>();

    // First, identify variants with <1% frequency
    const variantCounts = new Map<string, number>();
    for (const caseData of cases) {
        variantCounts.set(caseData.variant, (variantCounts.get(caseData.variant) || 0) + 1);
    }

    const totalCases = cases.length;
    const unusualVariants = new Set<string>();
    Array.from(variantCounts.entries()).forEach(([variant, count]) => {
        if ((count / totalCases) * 100 < 1) {
            unusualVariants.add(variant);
        }
    });

    // Analyze each case
    for (const caseData of cases) {
        const caseActivities = caseData.events.map((e) => e.activity);

        // Check for rework (repeated activities)
        const activityCounts = new Map<string, number>();
        for (const activity of caseActivities) {
            activityCounts.set(activity, (activityCounts.get(activity) || 0) + 1);
        }

        Array.from(activityCounts.entries()).forEach(([activity, count]) => {
            if (count > 1) {
                if (!reworkPatterns.has(activity)) {
                    reworkPatterns.set(activity, new Set());
                }
                reworkPatterns.get(activity)!.add(caseData.caseId);
            }
        });

        // Check for skips (missing happy path activities)
        const caseActivitySet = new Set(caseActivities);
        for (const activity of happyPath) {
            if (!caseActivitySet.has(activity)) {
                if (!skipPatterns.has(activity)) {
                    skipPatterns.set(activity, new Set());
                }
                skipPatterns.get(activity)!.add(caseData.caseId);
            }
        }

        // Check for unusual paths
        if (unusualVariants.has(caseData.variant)) {
            unusualPathCases.add(caseData.caseId);
        }
    }

    // Create rework deviations
    Array.from(reworkPatterns.entries()).forEach(([activity, caseIds]) => {
        // Count average repetitions
        let totalRepeats = 0;
        Array.from(caseIds).forEach((caseId) => {
            const caseData = cases.find((c) => c.caseId === caseId);
            if (caseData) {
                const count = caseData.events.filter((e) => e.activity === activity).length;
                totalRepeats += count;
            }
        });
        const avgRepeats = Math.round(totalRepeats / caseIds.size);

        deviations.push({
            type: 'rework',
            description: `Activity '${activity}' repeated ${avgRepeats} times in ${caseIds.size} cases`,
            affectedCases: Array.from(caseIds),
            frequency: caseIds.size,
        });
    });

    // Create skip deviations
    Array.from(skipPatterns.entries()).forEach(([activity, caseIds]) => {
        deviations.push({
            type: 'skip',
            description: `Activity '${activity}' skipped in ${caseIds.size} cases`,
            affectedCases: Array.from(caseIds),
            frequency: caseIds.size,
        });
    });

    // Create unusual path deviation
    if (unusualPathCases.size > 0) {
        deviations.push({
            type: 'unusual_path',
            description: `${unusualPathCases.size} cases follow unusual paths (variants with <1% frequency)`,
            affectedCases: Array.from(unusualPathCases),
            frequency: unusualPathCases.size,
        });
    }

    // Sort deviations by frequency
    deviations.sort((a, b) => b.frequency - a.frequency);

    // Log summary
    const reworkCount = deviations.filter((d) => d.type === 'rework').length;
    const skipCount = deviations.filter((d) => d.type === 'skip').length;
    const unusualCount = deviations.filter((d) => d.type === 'unusual_path').length;

    logger.info(`Found ${reworkCount} rework patterns`);
    logger.info(`Found ${skipCount} skip patterns`);
    logger.info(`Found ${unusualCount} unusual path cases`);
    logger.info('✅ Variant analysis complete');

    return deviations;
}

/**
 * Complete variant analysis including deviation detection
 * @param cases Array of cases to analyze
 * @returns Variants and deviations
 */
export function analyzeVariantsWithDeviations(cases: Case[]): VariantAnalysisResult {
    const variants = analyzeVariants(cases);

    // Get happy path sequence
    const happyPath = variants.length > 0 ? variants[0].sequence : [];

    const deviations = detectDeviations(cases, happyPath);

    return { variants, deviations };
}
