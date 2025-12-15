// XES Parser - parses XML event log files

export interface ParsedData {
    headers: string[];
    rows: Record<string, unknown>[];
    rowCount: number;
}

export interface XESParseResult {
    success: boolean;
    data?: ParsedData;
    error?: string;
}

export interface XESParseCallbacks {
    onProgress?: (current: number, total: number) => void;
    onLog?: (message: string, type?: 'info' | 'success' | 'error' | 'warning') => void;
}

// XES attribute name mappings to friendly names
const ATTRIBUTE_MAPPINGS: Record<string, string> = {
    'concept:name': 'activity', // In events
    'time:timestamp': 'timestamp',
    'org:resource': 'resource',
    'org:group': 'group',
    'org:role': 'role',
    'lifecycle:transition': 'lifecycle',
    'cost:total': 'cost',
};

// For trace-level concept:name, we use case_id
const TRACE_ATTRIBUTE_MAPPINGS: Record<string, string> = {
    'concept:name': 'case_id',
};

function normalizeAttributeName(name: string, isTraceLevel: boolean = false): string {
    if (isTraceLevel && TRACE_ATTRIBUTE_MAPPINGS[name]) {
        return TRACE_ATTRIBUTE_MAPPINGS[name];
    }
    return ATTRIBUTE_MAPPINGS[name] || name.replace(':', '_');
}

function extractAttributes(
    element: Element,
    isTraceLevel: boolean = false
): Record<string, unknown> {
    const attributes: Record<string, unknown> = {};

    // XES attributes are child elements with key & value attributes
    const children = element.children;

    for (let i = 0; i < children.length; i++) {
        const child = children[i];
        const tagName = child.tagName.toLowerCase();
        const key = child.getAttribute('key');
        let value: unknown = child.getAttribute('value');

        if (!key || value === null) continue;

        // Parse value based on type
        switch (tagName) {
            case 'string':
                // Keep as string
                break;
            case 'date':
                value = new Date(value as string).toISOString();
                break;
            case 'int':
                value = parseInt(value as string, 10);
                break;
            case 'float':
                value = parseFloat(value as string);
                break;
            case 'boolean':
                value = (value as string).toLowerCase() === 'true';
                break;
            default:
                // Keep as string for unknown types
                break;
        }

        const normalizedKey = normalizeAttributeName(key, isTraceLevel);
        attributes[normalizedKey] = value;
    }

    return attributes;
}

export async function parseXES(
    file: File,
    callbacks?: XESParseCallbacks
): Promise<XESParseResult> {
    const { onProgress, onLog } = callbacks || {};

    try {
        onLog?.('⏳ Parsing XES file...', 'info');

        // Read file as text
        const text = await file.text();

        // Parse XML
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/xml');

        // Check for parse errors
        const parseError = doc.querySelector('parsererror');
        if (parseError) {
            onLog?.('❌ Invalid XML structure', 'error');
            return {
                success: false,
                error: 'Invalid XML structure',
            };
        }

        // Find all trace elements
        const traces = doc.querySelectorAll('trace');

        if (traces.length === 0) {
            onLog?.('❌ No trace elements found in XES file', 'error');
            return {
                success: false,
                error: 'No trace elements found in XES file',
            };
        }

        onLog?.(`📂 Found ${traces.length} traces (cases)`, 'info');
        onLog?.('📝 Extracting events from traces...', 'info');

        const rows: Record<string, unknown>[] = [];
        const allAttributes = new Set<string>();

        // Process each trace
        for (let i = 0; i < traces.length; i++) {
            const trace = traces[i];

            // Extract trace-level attributes (including case ID)
            const traceAttrs = extractAttributes(trace, true);
            const caseId = traceAttrs.case_id || `Case_${i + 1}`;

            // Find all events in this trace
            const events = trace.querySelectorAll('event');

            for (let j = 0; j < events.length; j++) {
                const event = events[j];
                const eventAttrs = extractAttributes(event, false);

                // Combine trace and event attributes
                const row: Record<string, unknown> = {
                    case_id: caseId,
                    ...eventAttrs,
                };

                // Track all attribute names
                Object.keys(row).forEach((key) => allAttributes.add(key));
                rows.push(row);
            }

            // Log progress every 100 traces
            if ((i + 1) % 100 === 0 || i === traces.length - 1) {
                onProgress?.(i + 1, traces.length);
                onLog?.(`Processing trace ${i + 1}/${traces.length}...`, 'info');
            }
        }

        // Get headers (ordered with important ones first)
        const priorityHeaders = ['case_id', 'activity', 'timestamp', 'resource'];
        const otherHeaders = Array.from(allAttributes)
            .filter((h) => !priorityHeaders.includes(h))
            .sort();
        const headers = [
            ...priorityHeaders.filter((h) => allAttributes.has(h)),
            ...otherHeaders,
        ];

        onLog?.(`📊 Total events extracted: ${rows.length}`, 'info');
        onLog?.(`🔍 Detected attributes: ${headers.join(', ')}`, 'info');
        onLog?.('✅ XES parsed successfully', 'success');

        return {
            success: true,
            data: {
                headers,
                rows,
                rowCount: rows.length,
            },
        };
    } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        onLog?.(`❌ Parse error: ${message}`, 'error');
        return {
            success: false,
            error: message,
        };
    }
}
