import Papa from 'papaparse';
import { loggers } from '@/lib/debug-logger';

const log = loggers.parse;

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

    log.info('parseCSV called', { fileName: file.name, size: file.size, type: file.type });

    return new Promise((resolve) => {
        onLog?.('⏳ Parsing CSV file...', 'info');
        log.debug('Starting Papa.parse');

        Papa.parse<Record<string, unknown>>(file, {
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            worker: false, // Disable worker for large files - can cause issues
            complete: (results) => {
                log.info('Papa.parse complete callback', {
                    rowCount: results.data?.length,
                    fieldCount: results.meta?.fields?.length,
                    errors: results.errors?.length,
                    aborted: results.meta?.aborted,
                    truncated: results.meta?.truncated,
                });

                try {
                    if (results.errors && results.errors.length > 0) {
                        const errorMessages = results.errors
                            .slice(0, 5)
                            .map((e) => `Row ${e.row}: ${e.message}`)
                            .join('; ');
                        log.warn('Parse had errors', results.errors.slice(0, 5));
                        onLog?.(`⚠️ Parse warnings: ${errorMessages}`, 'warning');
                    }

                    const headers = results.meta.fields || [];
                    const rows = results.data as Record<string, unknown>[];
                    const rowCount = rows.length;

                    log.info('Parse results', { headers, rowCount, sampleRow: rows[0] });

                    if (rowCount === 0) {
                        log.error('No rows parsed - possible encoding or format issue');
                        onLog?.(`⚠️ No rows found - check file format/encoding`, 'warning');
                    }

                    onLog?.(
                        `📊 Detected ${headers.length} columns: ${headers.slice(0, 10).join(', ')}${headers.length > 10 ? '...' : ''}`,
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
                    const message = error instanceof Error ? error.message : 'Unknown error';
                    log.error('Parse processing error', error);
                    onLog?.(`❌ Parse error: ${message}`, 'error');
                    resolve({
                        success: false,
                        error: message,
                    });
                }
            },
            error: (error) => {
                log.error('Papa.parse error callback', error);
                onLog?.(`❌ Parse error: ${error.message}`, 'error');
                resolve({
                    success: false,
                    error: error.message,
                });
            },
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
