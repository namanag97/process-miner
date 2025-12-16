// Auto-detection utility for column mapping

export interface AutoDetectionResult {
    caseId: string | null;
    activity: string | null;
    timestamp: string | null;
    resource: string | null;
    cost: string | null;
}

const CASE_ID_PATTERNS = ['case', 'trace', 'instance', 'case_id', 'caseid', 'case-id'];
const ACTIVITY_PATTERNS = ['activity', 'event', 'action', 'task', 'concept:name', 'activity_name', 'eventname'];
const TIMESTAMP_PATTERNS = ['time', 'date', 'timestamp', 'time:timestamp', 'start', 'end', 'datetime'];
const RESOURCE_PATTERNS = ['resource', 'user', 'employee', 'org', 'org:resource', 'performer', 'agent'];
const COST_PATTERNS = ['cost', 'price', 'amount', 'value', 'cost:total'];

function matchesPattern(columnName: string, patterns: string[]): boolean {
    const lowerName = columnName.toLowerCase();
    return patterns.some(pattern => {
        // Exact match
        if (lowerName === pattern) return true;
        // Contains match (but be careful with just "id")
        if (pattern !== 'id' && lowerName.includes(pattern)) return true;
        return false;
    });
}

function findBestMatch(columns: string[], patterns: string[], exclude: Set<string>): string | null {
    // First try exact matches
    for (const col of columns) {
        if (exclude.has(col)) continue;
        const lowerCol = col.toLowerCase();
        if (patterns.includes(lowerCol)) {
            return col;
        }
    }

    // Then try contains matches
    for (const col of columns) {
        if (exclude.has(col)) continue;
        if (matchesPattern(col, patterns)) {
            return col;
        }
    }

    return null;
}

export function autoDetectColumns(columns: string[]): AutoDetectionResult {
    const result: AutoDetectionResult = {
        caseId: null,
        activity: null,
        timestamp: null,
        resource: null,
        cost: null,
    };

    const usedColumns = new Set<string>();

    // Detect in priority order
    result.caseId = findBestMatch(columns, CASE_ID_PATTERNS, usedColumns);
    if (result.caseId) usedColumns.add(result.caseId);

    result.activity = findBestMatch(columns, ACTIVITY_PATTERNS, usedColumns);
    if (result.activity) usedColumns.add(result.activity);

    result.timestamp = findBestMatch(columns, TIMESTAMP_PATTERNS, usedColumns);
    if (result.timestamp) usedColumns.add(result.timestamp);

    result.resource = findBestMatch(columns, RESOURCE_PATTERNS, usedColumns);
    if (result.resource) usedColumns.add(result.resource);

    result.cost = findBestMatch(columns, COST_PATTERNS, usedColumns);

    return result;
}

export function getColumnSamples(
    rows: Record<string, unknown>[],
    columnName: string,
    count: number = 3
): string[] {
    const samples: string[] = [];
    const seen = new Set<string>();

    for (const row of rows) {
        if (samples.length >= count) break;
        const value = row[columnName];
        if (value !== undefined && value !== null && value !== '') {
            const strValue = String(value);
            if (!seen.has(strValue)) {
                seen.add(strValue);
                samples.push(strValue.length > 30 ? strValue.slice(0, 30) + '...' : strValue);
            }
        }
    }

    return samples;
}
