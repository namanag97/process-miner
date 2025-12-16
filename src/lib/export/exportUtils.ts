/**
 * Export Utilities
 * Utility functions for exporting data in various formats
 */

import { createLogger } from '../debug-logger';
import type { ProcessModel, ProcessVariant, Deviation } from '../mining/types';

const logger = createLogger('export');

/**
 * Format a timestamp for use in filenames
 */
export function formatTimestampForFilename(): string {
    const now = new Date();
    return now.toISOString().replace(/[:.]/g, '-').slice(0, 19);
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Trigger a browser download of a blob
 */
export function downloadBlob(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Convert an array of objects to CSV string
 */
export function objectsToCSV<T extends Record<string, unknown>>(
    data: T[],
    columns: { key: keyof T; header: string }[]
): string {
    const headers = columns.map((c) => c.header).join(',');
    const rows = data.map((item) =>
        columns
            .map((c) => {
                const value = item[c.key];
                if (value === null || value === undefined) return '';
                if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return String(value);
            })
            .join(',')
    );
    return [headers, ...rows].join('\n');
}

/**
 * Export Process Model as JSON
 */
export function exportProcessModel(model: ProcessModel): void {
    logger.info('📥 Exporting Process Model (JSON)...');

    const json = JSON.stringify(model, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const filename = `process-model-${formatTimestampForFilename()}.json`;

    downloadBlob(blob, filename);
    logger.info(`✅ Exported ${filename} (${formatFileSize(blob.size)})`);
}

/**
 * Export Variants as CSV
 */
export function exportVariants(variants: ProcessVariant[]): void {
    logger.info('📥 Exporting Variants (CSV)...');

    const data = variants.map((v, idx) => ({
        rank: idx + 1,
        sequence: v.sequence.join(' → '),
        caseCount: v.caseCount,
        percentage: v.percentage.toFixed(2),
        avgDuration: v.avgDuration,
        isHappyPath: v.isHappyPath ? 'Yes' : 'No',
    }));

    const csv = objectsToCSV(data, [
        { key: 'rank', header: 'Rank' },
        { key: 'sequence', header: 'Sequence' },
        { key: 'caseCount', header: 'Case Count' },
        { key: 'percentage', header: 'Percentage' },
        { key: 'avgDuration', header: 'Avg Duration (ms)' },
        { key: 'isHappyPath', header: 'Is Happy Path' },
    ]);

    const blob = new Blob([csv], { type: 'text/csv' });
    const filename = `variants-${formatTimestampForFilename()}.csv`;

    downloadBlob(blob, filename);
    logger.info(`✅ Exported ${filename} (${formatFileSize(blob.size)})`);
}

/**
 * Export Deviations as CSV
 */
export function exportDeviations(deviations: Deviation[]): void {
    logger.info('📥 Exporting Deviations (CSV)...');

    const data = deviations.map((d) => ({
        type: d.type,
        description: d.description,
        affectedCaseCount: d.affectedCases.length,
        frequency: d.frequency,
    }));

    const csv = objectsToCSV(data, [
        { key: 'type', header: 'Type' },
        { key: 'description', header: 'Description' },
        { key: 'affectedCaseCount', header: 'Affected Case Count' },
        { key: 'frequency', header: 'Frequency' },
    ]);

    const blob = new Blob([csv], { type: 'text/csv' });
    const filename = `deviations-${formatTimestampForFilename()}.csv`;

    downloadBlob(blob, filename);
    logger.info(`✅ Exported ${filename} (${formatFileSize(blob.size)})`);
}

/**
 * Case data for export
 */
export interface CaseExportData {
    caseId: string;
    startTime: Date;
    endTime: Date;
    duration: number;
    eventCount: number;
    variant: string;
    hasDeviation: boolean;
}

/**
 * Export All Cases as CSV
 */
export function exportCases(cases: CaseExportData[]): void {
    logger.info('📥 Exporting All Cases (CSV)...');

    const data = cases.map((c) => ({
        caseId: c.caseId,
        startTime: c.startTime.toISOString(),
        endTime: c.endTime.toISOString(),
        duration: c.duration,
        eventCount: c.eventCount,
        variant: c.variant,
        hasDeviation: c.hasDeviation ? 'Yes' : 'No',
    }));

    const csv = objectsToCSV(data, [
        { key: 'caseId', header: 'Case ID' },
        { key: 'startTime', header: 'Start Time' },
        { key: 'endTime', header: 'End Time' },
        { key: 'duration', header: 'Duration (ms)' },
        { key: 'eventCount', header: 'Event Count' },
        { key: 'variant', header: 'Variant' },
        { key: 'hasDeviation', header: 'Has Deviation' },
    ]);

    const blob = new Blob([csv], { type: 'text/csv' });
    const filename = `cases-${formatTimestampForFilename()}.csv`;

    downloadBlob(blob, filename);
    logger.info(`✅ Exported ${filename} (${formatFileSize(blob.size)})`);
}

/**
 * Export Statistics as JSON
 */
export function exportStatistics(model: ProcessModel): void {
    logger.info('📥 Exporting Statistics (JSON)...');

    const happyPathVariant = model.variants.find((v) => v.isHappyPath);
    const happyPathRate = happyPathVariant?.percentage || 0;

    const affectedCases = new Set<string>();
    model.deviations.forEach((d) => d.affectedCases.forEach((c) => affectedCases.add(c)));
    const deviationRate = model.stats.totalCases > 0
        ? (affectedCases.size / model.stats.totalCases) * 100
        : 0;

    const stats = {
        summary: {
            totalCases: model.stats.totalCases,
            totalEvents: model.stats.totalEvents,
            uniqueActivities: model.activities.length,
            processVariants: model.variants.length,
            avgCaseDuration: model.stats.avgCaseDuration,
            medianCaseDuration: model.stats.medianCaseDuration,
            happyPathRate,
            conformanceRate: 100 - deviationRate,
        },
        activities: model.activities,
        startActivities: model.stats.startActivities,
        endActivities: model.stats.endActivities,
        deviationSummary: {
            totalDeviations: model.deviations.length,
            reworkCount: model.deviations.filter((d) => d.type === 'rework').length,
            skipCount: model.deviations.filter((d) => d.type === 'skip').length,
            unusualPathCount: model.deviations.filter((d) => d.type === 'unusual_path').length,
        },
        exportedAt: new Date().toISOString(),
    };

    const json = JSON.stringify(stats, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const filename = `stats-${formatTimestampForFilename()}.json`;

    downloadBlob(blob, filename);
    logger.info(`✅ Exported ${filename} (${formatFileSize(blob.size)})`);
}

/**
 * Export a single case as JSON
 */
export function exportSingleCaseJSON(caseData: {
    caseId: string;
    startTime: Date;
    endTime: Date;
    duration: number;
    variant: string;
    events: Array<{
        activity: string;
        timestamp: Date;
        resource?: string;
    }>;
}): void {
    logger.info(`📥 Exporting Case ${caseData.caseId} (JSON)...`);

    const json = JSON.stringify(caseData, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const filename = `case-${caseData.caseId}-${formatTimestampForFilename()}.json`;

    downloadBlob(blob, filename);
    logger.info(`✅ Exported ${filename} (${formatFileSize(blob.size)})`);
}

/**
 * Export a single case as CSV
 */
export function exportSingleCaseCSV(caseData: {
    caseId: string;
    events: Array<{
        activity: string;
        timestamp: Date;
        resource?: string;
    }>;
}): void {
    logger.info(`📥 Exporting Case ${caseData.caseId} (CSV)...`);

    const data = caseData.events.map((e, idx) => ({
        eventNumber: idx + 1,
        activity: e.activity,
        timestamp: e.timestamp.toISOString(),
        resource: e.resource || '',
    }));

    const csv = objectsToCSV(data, [
        { key: 'eventNumber', header: 'Event #' },
        { key: 'activity', header: 'Activity' },
        { key: 'timestamp', header: 'Timestamp' },
        { key: 'resource', header: 'Resource' },
    ]);

    const blob = new Blob([csv], { type: 'text/csv' });
    const filename = `case-${caseData.caseId}-${formatTimestampForFilename()}.csv`;

    downloadBlob(blob, filename);
    logger.info(`✅ Exported ${filename} (${formatFileSize(blob.size)})`);
}
