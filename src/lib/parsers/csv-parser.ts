import Papa from 'papaparse';

export interface ParsedData {
    headers: string[];
    rows: Record<string, unknown>[];
    rowCount: number;
}

export interface CSVParseResult {
    success: boolean;
    data?: ParsedData;
    error?: string;
}

export interface CSVParseCallbacks {
    onProgress?: (percent: number) => void;
    onLog?: (message: string, type?: 'info' | 'success' | 'error' | 'warning') => void;
}

export function parseCSV(
    file: File,
    callbacks?: CSVParseCallbacks
): Promise<CSVParseResult> {
    const { onProgress, onLog } = callbacks || {};

    return new Promise((resolve) => {
        onLog?.('⏳ Parsing CSV file...', 'info');

        Papa.parse<Record<string, unknown>>(file, {
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            complete: (results) => {
                try {
                    if (results.errors.length > 0) {
                        const errorMessages = results.errors
                            .slice(0, 3)
                            .map((e) => e.message)
                            .join('; ');
                        onLog?.(`⚠️ Parse warnings: ${errorMessages}`, 'warning');
                    }

                    const headers = results.meta.fields || [];
                    const rows = results.data as Record<string, unknown>[];
                    const rowCount = rows.length;

                    onLog?.(
                        `📊 Detected ${headers.length} columns: ${headers.join(', ')}`,
                        'info'
                    );
                    onLog?.(`📝 Found ${rowCount} rows of event data`, 'info');
                    onLog?.('✅ CSV parsed successfully', 'success');

                    resolve({
                        success: true,
                        data: {
                            headers,
                            rows,
                            rowCount,
                        },
                    });
                } catch (error) {
                    const message =
                        error instanceof Error ? error.message : 'Unknown error';
                    onLog?.(`❌ Parse error: ${message}`, 'error');
                    resolve({
                        success: false,
                        error: message,
                    });
                }
            },
            error: (error) => {
                onLog?.(`❌ Parse error: ${error.message}`, 'error');
                resolve({
                    success: false,
                    error: error.message,
                });
            },
            // Progress callback for large files
            ...(onProgress && {
                step: (results, parser) => {
                    // Papa doesn't provide built-in progress, but we can estimate
                    // based on file cursor position
                    const cursor = (parser as unknown as { streamer?: { _handle?: { _cursor?: number } } }).streamer?._handle?._cursor || 0;
                    const percent = Math.round((cursor / file.size) * 100);
                    if (percent > 0 && percent < 100 && percent % 10 === 0) {
                        onProgress(percent);
                        onLog?.(`Parsing: ${percent}%`, 'info');
                    }
                },
            }),
        });
    });
}

export function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
