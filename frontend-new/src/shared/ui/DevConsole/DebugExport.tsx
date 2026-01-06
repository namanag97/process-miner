/**
 * DebugExport - One-click issue report export for MVP debugging
 * 
 * Provides:
 * - Session summary (errors, slow requests, duration)
 * - User flow timeline (action → API → result)
 * - System state (route, params, user context)
 * - Compressed log format ready for GitHub issues
 * 
 * This component adds an "Export Issue Report" button to DevConsole
 * that generates a structured JSON ready for debugging.
 */

import { useState, useCallback, useMemo } from 'react';
import { Button, Modal, Typography, Space, Tag, message, Tooltip, Checkbox, Divider, Alert } from 'antd';
import {
    CopyOutlined,
    DownloadOutlined,
    BugOutlined,
    CheckOutlined,
    ExclamationCircleOutlined,
    ClockCircleOutlined,
    ThunderboltOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

// Types (should match DevConsole types)
type LogLevel = 'info' | 'api-req' | 'api-res' | 'error' | 'action' | 'state' | 'query' | 'mutation' | 'metric' | 'perf' | 'circuit' | 'db-query' | 'cache' | 'auth';

interface LogEntry {
    id: string;
    timestamp: Date;
    level: LogLevel;
    source: string;
    message: string;
    data?: unknown;
    duration?: number;
    status?: number;
    importance: number;
    correlationId?: string;
    requestId?: string;
    isPending?: boolean;
}

interface IssueReport {
    issue_report: {
        generated_at: string;
        session_duration_ms: number;
        summary: string;
        user_context: {
            route: string;
            search?: string;
            user_id?: string;
        };
    };
    errors: Array<{
        time: string;
        type: string;
        source: string;
        message: string;
        correlation_id?: string;
        data?: unknown;
    }>;
    user_flow: Array<{
        time: string;
        action: string;
        result: 'success' | 'error' | 'pending';
        api_calls?: number;
    }>;
    slow_requests: Array<{
        url: string;
        duration: number;
        status: number;
    }>;
    pending_requests: Array<{
        url: string;
        pending_since: string;
    }>;
    system_state: {
        browser: string;
        viewport: string;
        timestamp: string;
    };
    logs: unknown[];
}

interface DebugExportProps {
    logs: LogEntry[];
    sessionStart: Date;
}

/**
 * Generate a structured issue report from logs
 */
function generateIssueReport(logs: LogEntry[], sessionStart: Date): IssueReport {
    const now = new Date();
    const sessionDuration = now.getTime() - sessionStart.getTime();

    // Extract errors
    const errors = logs
        .filter(l => l.level === 'error' || (l.status && l.status >= 400))
        .slice(0, 20)
        .map(l => ({
            time: l.timestamp.toLocaleTimeString('en-US', { hour12: false }),
            type: l.status && l.status >= 400 ? 'API Error' : 'Application Error',
            source: l.source,
            message: l.message,
            correlation_id: l.correlationId || l.requestId,
            data: l.data,
        }));

    // Build user flow timeline from actions
    const actions = logs.filter(l => l.level === 'action' || l.level === 'mutation');
    const userFlow = actions.slice(0, 50).map(action => {
        const correlatedLogs = logs.filter(l => l.correlationId === action.correlationId && l.id !== action.id);
        const hasError = correlatedLogs.some(l => l.level === 'error' || (l.status && l.status >= 400));
        const hasPending = correlatedLogs.some(l => l.isPending);
        const apiCalls = correlatedLogs.filter(l => l.level === 'api-req' || l.level === 'api-res').length;

        return {
            time: action.timestamp.toLocaleTimeString('en-US', { hour12: false }),
            action: `${action.source}: ${action.message}`,
            result: hasError ? 'error' as const : hasPending ? 'pending' as const : 'success' as const,
            api_calls: apiCalls > 0 ? apiCalls : undefined,
        };
    });

    // Extract slow requests
    const slowRequests = logs
        .filter(l => l.level === 'api-res' && l.duration && l.duration > 1000)
        .slice(0, 10)
        .map(l => ({
            url: l.source,
            duration: l.duration!,
            status: l.status || 0,
        }));

    // Extract pending requests
    const pendingRequests = logs
        .filter(l => l.isPending && l.level === 'api-req')
        .map(l => ({
            url: l.source,
            pending_since: l.timestamp.toLocaleTimeString('en-US', { hour12: false }),
        }));

    // Build summary
    const errorCount = errors.length;
    const slowCount = slowRequests.length;
    const pendingCount = pendingRequests.length;
    const durationMins = Math.round(sessionDuration / 60000);

    const summaryParts: string[] = [];
    if (errorCount > 0) summaryParts.push(`${errorCount} error${errorCount > 1 ? 's' : ''}`);
    if (slowCount > 0) summaryParts.push(`${slowCount} slow request${slowCount > 1 ? 's' : ''}`);
    if (pendingCount > 0) summaryParts.push(`${pendingCount} pending`);
    summaryParts.push(`session ${durationMins}min`);

    // Compress logs - only important ones
    const importantLogs = logs
        .filter(l => l.importance >= 3) // Medium and above
        .slice(0, 100)
        .map(l => ({
            t: l.timestamp.toISOString(),
            l: l.level,
            s: l.source,
            m: l.message,
            st: l.status,
            d: l.duration,
            i: l.importance,
        }));

    return {
        issue_report: {
            generated_at: now.toISOString(),
            session_duration_ms: sessionDuration,
            summary: summaryParts.join(', '),
            user_context: {
                route: window.location.pathname,
                search: window.location.search || undefined,
                user_id: typeof localStorage !== 'undefined' ? localStorage.getItem('userId') || undefined : undefined,
            },
        },
        errors,
        user_flow: userFlow,
        slow_requests: slowRequests,
        pending_requests: pendingRequests,
        system_state: {
            browser: navigator.userAgent.split(' ').slice(-2).join(' '),
            viewport: `${window.innerWidth}x${window.innerHeight}`,
            timestamp: now.toISOString(),
        },
        logs: importantLogs,
    };
}

/**
 * Generate markdown summary for quick paste into GitHub issue
 */
function generateMarkdownSummary(report: IssueReport): string {
    const lines: string[] = [];

    lines.push('## Debug Report');
    lines.push(`**Generated:** ${new Date(report.issue_report.generated_at).toLocaleString()}`);
    lines.push(`**Summary:** ${report.issue_report.summary}`);
    lines.push(`**Route:** \`${report.issue_report.user_context.route}\``);
    lines.push('');

    if (report.errors.length > 0) {
        lines.push('### Errors');
        report.errors.slice(0, 5).forEach(e => {
            lines.push(`- **${e.time}** \`${e.source}\`: ${e.message}`);
            if (e.correlation_id) lines.push(`  - Correlation ID: \`${e.correlation_id}\``);
        });
        lines.push('');
    }

    if (report.slow_requests.length > 0) {
        lines.push('### Slow Requests');
        report.slow_requests.forEach(r => {
            lines.push(`- \`${r.url}\`: ${r.duration}ms (status: ${r.status})`);
        });
        lines.push('');
    }

    if (report.user_flow.length > 0) {
        lines.push('### User Flow');
        report.user_flow.slice(0, 10).forEach(f => {
            const emoji = f.result === 'error' ? '❌' : f.result === 'pending' ? '⏳' : '✅';
            lines.push(`- ${emoji} ${f.time}: ${f.action}`);
        });
        lines.push('');
    }

    lines.push('<details>');
    lines.push('<summary>Full Log Data (JSON)</summary>');
    lines.push('');
    lines.push('```json');
    lines.push(JSON.stringify(report, null, 2));
    lines.push('```');
    lines.push('</details>');

    return lines.join('\n');
}

export function DebugExport({ logs, sessionStart }: DebugExportProps) {
    const [showModal, setShowModal] = useState(false);
    const [includeFullLogs, setIncludeFullLogs] = useState(true);
    const [copied, setCopied] = useState<'json' | 'md' | null>(null);

    const report = useMemo(() => generateIssueReport(logs, sessionStart), [logs, sessionStart]);
    const markdown = useMemo(() => generateMarkdownSummary(report), [report]);

    const errorCount = report.errors.length;
    const slowCount = report.slow_requests.length;

    const handleCopyJSON = useCallback(async () => {
        const data = includeFullLogs ? report : { ...report, logs: [] };
        await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
        setCopied('json');
        message.success('JSON copied to clipboard!');
        setTimeout(() => setCopied(null), 2000);
    }, [report, includeFullLogs]);

    const handleCopyMarkdown = useCallback(async () => {
        await navigator.clipboard.writeText(markdown);
        setCopied('md');
        message.success('Markdown copied to clipboard!');
        setTimeout(() => setCopied(null), 2000);
    }, [markdown]);

    const handleDownload = useCallback(() => {
        const data = includeFullLogs ? report : { ...report, logs: [] };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `debug-report-${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
        a.click();
        URL.revokeObjectURL(url);
        setShowModal(false);
        message.success('Report downloaded!');
    }, [report, includeFullLogs]);

    return (
        <>
            <Tooltip title="Export Issue Report for debugging">
                <Button
                    type="primary"
                    danger={errorCount > 0}
                    icon={<BugOutlined />}
                    onClick={() => setShowModal(true)}
                    style={{ marginLeft: 8 }}
                >
                    Export Issue
                    {(errorCount > 0 || slowCount > 0) && (
                        <Tag color="red" style={{ marginLeft: 4, padding: '0 4px' }}>
                            {errorCount + slowCount}
                        </Tag>
                    )}
                </Button>
            </Tooltip>

            <Modal
                title={
                    <Space>
                        <BugOutlined style={{ color: '#ff4d4f' }} />
                        <span>Export Debug Report</span>
                    </Space>
                }
                open={showModal}
                onCancel={() => setShowModal(false)}
                footer={null}
                width={600}
            >
                {/* Summary */}
                <Alert
                    message={report.issue_report.summary}
                    type={errorCount > 0 ? 'error' : slowCount > 0 ? 'warning' : 'info'}
                    showIcon
                    style={{ marginBottom: 16 }}
                />

                {/* Stats */}
                <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
                    <div style={{ flex: 1, padding: 12, background: '#fafafa', borderRadius: 8 }}>
                        <ExclamationCircleOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
                        <Text strong>{errorCount}</Text>
                        <Text type="secondary"> Errors</Text>
                    </div>
                    <div style={{ flex: 1, padding: 12, background: '#fafafa', borderRadius: 8 }}>
                        <ClockCircleOutlined style={{ color: '#fa8c16', marginRight: 8 }} />
                        <Text strong>{slowCount}</Text>
                        <Text type="secondary"> Slow Requests</Text>
                    </div>
                    <div style={{ flex: 1, padding: 12, background: '#fafafa', borderRadius: 8 }}>
                        <ThunderboltOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                        <Text strong>{report.user_flow.length}</Text>
                        <Text type="secondary"> Actions</Text>
                    </div>
                </div>

                {/* Options */}
                <Checkbox
                    checked={includeFullLogs}
                    onChange={e => setIncludeFullLogs(e.target.checked)}
                    style={{ marginBottom: 16 }}
                >
                    Include full log data (larger file, more details)
                </Checkbox>

                <Divider />

                {/* Export Actions */}
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                    <Button
                        block
                        size="large"
                        icon={copied === 'md' ? <CheckOutlined /> : <CopyOutlined />}
                        onClick={handleCopyMarkdown}
                        type={copied === 'md' ? 'primary' : 'default'}
                    >
                        📋 Copy for GitHub Issue (Markdown)
                    </Button>

                    <Button
                        block
                        size="large"
                        icon={copied === 'json' ? <CheckOutlined /> : <CopyOutlined />}
                        onClick={handleCopyJSON}
                    >
                        📄 Copy JSON to Clipboard
                    </Button>

                    <Button
                        block
                        size="large"
                        icon={<DownloadOutlined />}
                        onClick={handleDownload}
                    >
                        💾 Download JSON File
                    </Button>
                </Space>

                {/* Preview */}
                <Divider />
                <details>
                    <summary style={{ cursor: 'pointer', marginBottom: 8 }}>
                        <Text type="secondary">Preview Markdown Output</Text>
                    </summary>
                    <pre style={{
                        background: '#f5f5f5',
                        padding: 12,
                        borderRadius: 8,
                        fontSize: 11,
                        maxHeight: 200,
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap',
                    }}>
                        {markdown}
                    </pre>
                </details>
            </Modal>
        </>
    );
}

export default DebugExport;
