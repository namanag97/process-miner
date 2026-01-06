/**
 * PageErrorBoundary - Enhanced error boundary with detailed context for MVP debugging
 * 
 * Features:
 * - Captures component stack trace
 * - Captures current route and params
 * - Captures recent user actions from DevConsole
 * - Provides "Copy Error Report" button for quick issue filing
 * - Shows user-friendly error message with recovery options
 * 
 * Use this to wrap individual pages for granular error capture.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button, Result, Typography, Space, Collapse, Tag, message, Alert } from 'antd';
import { CopyOutlined, ReloadOutlined, HomeOutlined, BugOutlined, CheckOutlined } from '@ant-design/icons';
import { devLog } from '.';

const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface Props {
    children: ReactNode;
    /** Page name for error context */
    pageName?: string;
    /** Fallback component to render on error */
    fallback?: ReactNode;
    /** Callback when error is captured */
    onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
    errorTime: Date | null;
    copied: boolean;
}

/**
 * Get current route information for error context
 */
function getCurrentRouteInfo(): { pathname: string; search: string; hash: string } {
    if (typeof window === 'undefined') {
        return { pathname: '', search: '', hash: '' };
    }
    return {
        pathname: window.location.pathname,
        search: window.location.search,
        hash: window.location.hash,
    };
}

/**
 * Enhanced error boundary that captures detailed context for debugging
 */
export class PageErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
            errorTime: null,
            copied: false,
        };
    }

    static getDerivedStateFromError(error: Error): Partial<State> {
        return {
            hasError: true,
            error,
            errorTime: new Date(),
        };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        this.setState({ errorInfo });

        // Log to DevConsole
        const { pageName = 'UnknownPage' } = this.props;
        devLog.error(pageName, `Component Error: ${error.message}`, {
            errorType: error.name,
            componentStack: errorInfo.componentStack,
            route: getCurrentRouteInfo(),
        });

        // Call custom error handler if provided
        if (this.props.onError) {
            this.props.onError(error, errorInfo);
        }

        // Also log to console with full details
        console.error(`[PageErrorBoundary] ${pageName} crashed:`, error);
        console.error('Component Stack:', errorInfo.componentStack);
    }

    handleRetry = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
            errorTime: null,
        });
    };

    handleGoHome = () => {
        window.location.href = '/workspace';
    };

    handleCopyReport = async () => {
        const { error, errorInfo, errorTime } = this.state;
        const { pageName = 'UnknownPage' } = this.props;
        const route = getCurrentRouteInfo();

        const report = {
            error_report: {
                generated_at: new Date().toISOString(),
                error_time: errorTime?.toISOString(),
                page: pageName,
                type: 'Component Crash',
            },
            error: {
                name: error?.name,
                message: error?.message,
                stack: error?.stack?.split('\n').slice(0, 10).join('\n'),
            },
            context: {
                route: route.pathname,
                search: route.search,
                user_agent: navigator.userAgent,
                viewport: `${window.innerWidth}x${window.innerHeight}`,
            },
            component_stack: errorInfo?.componentStack?.trim(),
        };

        // Generate markdown for GitHub
        const markdown = `## 🐛 Frontend Component Crash

**Page:** \`${pageName}\`
**Route:** \`${route.pathname}${route.search}\`
**Time:** ${errorTime?.toLocaleString()}

### Error
\`\`\`
${error?.name}: ${error?.message}
\`\`\`

### Stack Trace
\`\`\`
${error?.stack?.split('\n').slice(0, 8).join('\n') || 'No stack available'}
\`\`\`

### Component Stack
\`\`\`
${errorInfo?.componentStack?.trim() || 'No component stack available'}
\`\`\`

<details>
<summary>Full Error Report (JSON)</summary>

\`\`\`json
${JSON.stringify(report, null, 2)}
\`\`\`

</details>`;

        try {
            await navigator.clipboard.writeText(markdown);
            this.setState({ copied: true });
            message.success('Error report copied! Paste it into a GitHub issue.');
            setTimeout(() => this.setState({ copied: false }), 3000);
        } catch (e) {
            // Fallback: copy JSON
            await navigator.clipboard.writeText(JSON.stringify(report, null, 2));
            message.info('JSON report copied to clipboard');
        }
    };

    render() {
        const { hasError, error, errorInfo, errorTime, copied } = this.state;
        const { children, pageName = 'Page', fallback } = this.props;

        if (hasError) {
            // If custom fallback provided, use it
            if (fallback) {
                return fallback;
            }

            return (
                <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
                    <Result
                        status="error"
                        title={`${pageName} encountered an error`}
                        subTitle="We've captured the error details. You can copy the report below and share it with the team for debugging."
                        extra={
                            <Space wrap>
                                <Button
                                    type="primary"
                                    icon={copied ? <CheckOutlined /> : <CopyOutlined />}
                                    onClick={this.handleCopyReport}
                                >
                                    {copied ? 'Copied!' : 'Copy Error Report'}
                                </Button>
                                <Button icon={<ReloadOutlined />} onClick={this.handleRetry}>
                                    Try Again
                                </Button>
                                <Button icon={<HomeOutlined />} onClick={this.handleGoHome}>
                                    Go to Workspace
                                </Button>
                            </Space>
                        }
                    />

                    <Alert
                        message="Quick Debug Info"
                        description={
                            <Space direction="vertical" size="small" style={{ width: '100%' }}>
                                <div>
                                    <Text strong>Error: </Text>
                                    <Text code>{error?.name}: {error?.message}</Text>
                                </div>
                                <div>
                                    <Text strong>Route: </Text>
                                    <Text code>{getCurrentRouteInfo().pathname}</Text>
                                </div>
                                <div>
                                    <Text strong>Time: </Text>
                                    <Text>{errorTime?.toLocaleTimeString()}</Text>
                                </div>
                            </Space>
                        }
                        type="error"
                        showIcon
                        icon={<BugOutlined />}
                        style={{ marginTop: 16 }}
                    />

                    <Collapse style={{ marginTop: 16 }} ghost>
                        <Panel
                            header={
                                <Space>
                                    <Tag color="red">Technical Details</Tag>
                                    <Text type="secondary">For developers</Text>
                                </Space>
                            }
                            key="1"
                        >
                            <div style={{ fontFamily: 'monospace', fontSize: 12 }}>
                                <Paragraph strong>Stack Trace:</Paragraph>
                                <pre style={{
                                    background: '#f5f5f5',
                                    padding: 12,
                                    borderRadius: 4,
                                    overflow: 'auto',
                                    maxHeight: 200,
                                    whiteSpace: 'pre-wrap',
                                    wordBreak: 'break-word',
                                }}>
                                    {error?.stack || 'No stack trace available'}
                                </pre>

                                {errorInfo?.componentStack && (
                                    <>
                                        <Paragraph strong style={{ marginTop: 16 }}>Component Stack:</Paragraph>
                                        <pre style={{
                                            background: '#fff7e6',
                                            padding: 12,
                                            borderRadius: 4,
                                            overflow: 'auto',
                                            maxHeight: 200,
                                            whiteSpace: 'pre-wrap',
                                            wordBreak: 'break-word',
                                        }}>
                                            {errorInfo.componentStack.trim()}
                                        </pre>
                                    </>
                                )}
                            </div>
                        </Panel>
                    </Collapse>
                </div>
            );
        }

        return children;
    }
}

/**
 * HOC to wrap any component with PageErrorBoundary
 */
export function withPageErrorBoundary<P extends object>(
    WrappedComponent: React.ComponentType<P>,
    pageName: string
) {
    return function WithErrorBoundary(props: P) {
        return (
            <PageErrorBoundary pageName={pageName}>
                <WrappedComponent {...props} />
            </PageErrorBoundary>
        );
    };
}

export default PageErrorBoundary;
