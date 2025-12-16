/**
 * Process Mining Utilities
 * Helper functions for process mining operations
 */

import type { Event } from './types';

/**
 * Groups events by their case ID
 * @param events Array of events to group
 * @returns Map where key is caseId and value is array of events for that case
 */
export function groupEventsByCase(events: Event[]): Map<string, Event[]> {
    const grouped = new Map<string, Event[]>();

    for (const event of events) {
        const existing = grouped.get(event.caseId);
        if (existing) {
            existing.push(event);
        } else {
            grouped.set(event.caseId, [event]);
        }
    }

    return grouped;
}

/**
 * Sorts events by their timestamp in ascending order
 * @param events Array of events to sort
 * @returns New array of events sorted by timestamp
 */
export function sortEventsByTime(events: Event[]): Event[] {
    return [...events].sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
}

/**
 * Calculates the duration between two dates in milliseconds
 * @param start Start date
 * @param end End date
 * @returns Duration in milliseconds
 */
export function calculateDuration(start: Date, end: Date): number {
    return end.getTime() - start.getTime();
}

/**
 * Formats a duration in milliseconds to a human-readable string
 * @param ms Duration in milliseconds
 * @returns Human-readable duration string (e.g., "2h 30m", "5d 3h", "45s")
 */
export function formatDuration(ms: number): string {
    if (ms < 0) {
        return '-' + formatDuration(-ms);
    }

    if (ms < 1000) {
        return `${Math.round(ms)}ms`;
    }

    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
        const remainingHours = hours % 24;
        if (remainingHours > 0) {
            return `${days}d ${remainingHours}h`;
        }
        return `${days}d`;
    }

    if (hours > 0) {
        const remainingMinutes = minutes % 60;
        if (remainingMinutes > 0) {
            return `${hours}h ${remainingMinutes}m`;
        }
        return `${hours}h`;
    }

    if (minutes > 0) {
        const remainingSeconds = seconds % 60;
        if (remainingSeconds > 0) {
            return `${minutes}m ${remainingSeconds}s`;
        }
        return `${minutes}m`;
    }

    return `${seconds}s`;
}

/**
 * Generates a variant key from a sequence of events
 * Creates a string representation of the activity sequence
 * @param events Array of events (should be sorted by time)
 * @returns Variant key string with activities joined by → (e.g., "A→B→C")
 */
export function getVariantKey(events: Event[]): string {
    return events.map((e) => e.activity).join('→');
}

/**
 * Calculates the median of an array of numbers
 * @param values Array of numbers
 * @returns Median value, or 0 if array is empty
 */
export function calculateMedian(values: number[]): number {
    if (values.length === 0) {
        return 0;
    }

    const sorted = [...values].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);

    if (sorted.length % 2 === 0) {
        return (sorted[mid - 1] + sorted[mid]) / 2;
    }

    return sorted[mid];
}

/**
 * Calculates the average of an array of numbers
 * @param values Array of numbers
 * @returns Average value, or 0 if array is empty
 */
export function calculateAverage(values: number[]): number {
    if (values.length === 0) {
        return 0;
    }
    return values.reduce((sum, val) => sum + val, 0) / values.length;
}
