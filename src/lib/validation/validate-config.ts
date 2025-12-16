// Data validation for column configuration

export interface ValidationCheck {
    id: string;
    label: string;
    status: 'success' | 'warning' | 'error';
    message: string;
}

export interface ValidationStatistics {
    totalEvents: number;
    totalCases: number;
    uniqueActivities: number;
    dateRange: { start: string; end: string } | null;
    avgEventsPerCase: number;
    minEventsPerCase: number;
    maxEventsPerCase: number;
}

export interface ValidationResult {
    isValid: boolean;
    hasWarnings: boolean;
    checks: ValidationCheck[];
    statistics: ValidationStatistics;
    activities: string[];
    warnings: string[];
}

export interface ColumnMapping {
    caseId: string;
    activity: string;
    timestamp: string;
    resource?: string;
    cost?: string;
}

interface LogCallback {
    (level: 'info' | 'success' | 'warning' | 'error', message: string): void;
}

function tryParseDate(value: unknown): Date | null {
    if (value === null || value === undefined) return null;

    if (value instanceof Date) return value;

    const strValue = String(value);

    // Try standard parsing
    const date = new Date(strValue);
    if (!isNaN(date.getTime())) return date;

    // Try common formats
    // ISO format: 2023-01-15T10:30:00
    // Date only: 2023-01-15
    // US format: 01/15/2023

    return null;
}

export function validateColumnConfiguration(
    rows: Record<string, unknown>[],
    mapping: ColumnMapping,
    onLog?: LogCallback
): ValidationResult {
    const checks: ValidationCheck[] = [];
    const warnings: string[] = [];

    onLog?.('info', '🔍 Validating column configuration...');

    // Case ID validation
    const caseValues = rows.map(row => row[mapping.caseId]);
    const uniqueCases = new Set(caseValues.filter(v => v !== null && v !== undefined));
    const caseCount = uniqueCases.size;

    onLog?.('info', `📊 Found ${caseCount} unique cases`);

    if (caseCount === 0) {
        checks.push({
            id: 'case-count',
            label: 'Case ID Detection',
            status: 'error',
            message: 'No valid case IDs found',
        });
    } else if (caseCount === 1) {
        checks.push({
            id: 'case-count',
            label: 'Case ID Detection',
            status: 'warning',
            message: 'Only 1 case found - is this the right column?',
        });
        warnings.push('Only 1 unique case found');
    } else if (caseCount === rows.length) {
        checks.push({
            id: 'case-count',
            label: 'Case ID Detection',
            status: 'warning',
            message: `Each row is a unique case (${caseCount}) - might not be groupable`,
        });
        warnings.push('Case count equals row count - events may not be grouped correctly');
    } else {
        checks.push({
            id: 'case-count',
            label: 'Case ID Detection',
            status: 'success',
            message: `${caseCount} unique cases detected`,
        });
    }

    // Activity validation
    const activityValues = rows.map(row => row[mapping.activity]);
    const uniqueActivities = new Set(activityValues.filter(v => v !== null && v !== undefined));
    const activityCount = uniqueActivities.size;
    const activities = Array.from(uniqueActivities).map(String);

    onLog?.('info', `📋 Found ${activityCount} unique activities`);

    if (activityCount === 0) {
        checks.push({
            id: 'activity-count',
            label: 'Activity Detection',
            status: 'error',
            message: 'No valid activities found',
        });
    } else if (activityCount === 1) {
        checks.push({
            id: 'activity-count',
            label: 'Activity Detection',
            status: 'warning',
            message: 'Only 1 activity found - no process to discover',
        });
        warnings.push('Only 1 unique activity found - no process flow to discover');
    } else if (activityCount > 500) {
        checks.push({
            id: 'activity-count',
            label: 'Activity Detection',
            status: 'warning',
            message: `${activityCount} activities - might be too granular`,
        });
        warnings.push('More than 500 unique activities - data might be too granular');
    } else {
        checks.push({
            id: 'activity-count',
            label: 'Activity Detection',
            status: 'success',
            message: `${activityCount} unique activities detected`,
        });
    }

    // Timestamp validation
    const timestampValues = rows.map(row => row[mapping.timestamp]);
    const parsedDates: Date[] = [];
    let parseSuccessCount = 0;

    for (const value of timestampValues) {
        const parsed = tryParseDate(value);
        if (parsed) {
            parseSuccessCount++;
            parsedDates.push(parsed);
        }
    }

    const parseRate = rows.length > 0 ? (parseSuccessCount / rows.length) * 100 : 0;

    let dateRange: { start: string; end: string } | null = null;

    if (parsedDates.length > 0) {
        const sortedDates = parsedDates.sort((a, b) => a.getTime() - b.getTime());
        const earliest = sortedDates[0];
        const latest = sortedDates[sortedDates.length - 1];
        dateRange = {
            start: earliest.toISOString().split('T')[0],
            end: latest.toISOString().split('T')[0],
        };

        onLog?.('info', `📅 Date range: ${dateRange.start} to ${dateRange.end}`);

        if (earliest.getTime() === latest.getTime()) {
            checks.push({
                id: 'timestamp-range',
                label: 'Timestamp Range',
                status: 'warning',
                message: 'All timestamps are identical',
            });
            warnings.push('All timestamps have the same value');
        }
    }

    if (parseRate < 50) {
        checks.push({
            id: 'timestamp-parse',
            label: 'Timestamp Parsing',
            status: 'error',
            message: `Only ${parseRate.toFixed(0)}% of timestamps could be parsed`,
        });
    } else if (parseRate < 90) {
        checks.push({
            id: 'timestamp-parse',
            label: 'Timestamp Parsing',
            status: 'warning',
            message: `${parseRate.toFixed(0)}% of timestamps parsed successfully`,
        });
        warnings.push(`${(100 - parseRate).toFixed(0)}% of timestamps could not be parsed`);
    } else {
        checks.push({
            id: 'timestamp-parse',
            label: 'Timestamp Parsing',
            status: 'success',
            message: `${parseRate.toFixed(0)}% of timestamps parsed successfully`,
        });
    }

    // Calculate statistics
    const caseCounts = new Map<unknown, number>();
    for (const caseId of caseValues) {
        caseCounts.set(caseId, (caseCounts.get(caseId) || 0) + 1);
    }

    const countValues = Array.from(caseCounts.values());
    const avgEventsPerCase = countValues.length > 0
        ? countValues.reduce((a, b) => a + b, 0) / countValues.length
        : 0;
    const minEventsPerCase = countValues.length > 0 ? Math.min(...countValues) : 0;
    const maxEventsPerCase = countValues.length > 0 ? Math.max(...countValues) : 0;

    const statistics: ValidationStatistics = {
        totalEvents: rows.length,
        totalCases: caseCount,
        uniqueActivities: activityCount,
        dateRange,
        avgEventsPerCase: Math.round(avgEventsPerCase * 10) / 10,
        minEventsPerCase,
        maxEventsPerCase,
    };

    const hasErrors = checks.some(c => c.status === 'error');
    const hasWarnings = checks.some(c => c.status === 'warning');

    if (hasErrors) {
        onLog?.('error', '❌ Validation failed with errors');
    } else if (hasWarnings) {
        onLog?.('warning', '⚠️ Validation complete with warnings');
    } else {
        onLog?.('success', '✅ Validation complete');
    }

    return {
        isValid: !hasErrors,
        hasWarnings,
        checks,
        statistics,
        activities,
        warnings,
    };
}
