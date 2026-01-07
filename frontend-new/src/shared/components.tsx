/**
 * Shared UI Components
 * 
 * Local replacements for @lumina/design-system UI components.
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Card, Typography, Space, Empty, Layout, Breadcrumb, Statistic, Button } from 'antd';
import { tokens } from './design-system';

const { Title, Text } = Typography;
const { Header, Content, Sider } = Layout;

// ==============================================
// PageHeader Component
// ==============================================
interface PageHeaderProps {
    title: string;
    subtitle?: string;
    description?: string;
    breadcrumbs?: { label: string; href?: string }[];
    breadcrumb?: { label: string; href?: string }[];  // Alternative prop name
    extra?: ReactNode;
    actions?: ReactNode;
    children?: ReactNode;
    [key: string]: unknown;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
    title,
    subtitle,
    description,
    breadcrumbs,
    breadcrumb,
    extra,
    actions,
    children,
}) => {
    const crumbs = breadcrumbs || breadcrumb;
    const rightContent = extra || actions;
    const subText = subtitle || description;

    return (
        <div style={{ marginBottom: tokens.spacing.lg }}>
            {crumbs && crumbs.length > 0 && (
                <Breadcrumb
                    style={{ marginBottom: tokens.spacing.sm }}
                    items={crumbs.map((b) => ({ title: b.href ? <a href={b.href}>{b.label}</a> : b.label }))}
                />
            )}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <Title level={2} style={{ marginBottom: 0 }}>{title}</Title>
                    {subText && <Text type="secondary">{subText}</Text>}
                </div>
                {rightContent && <Space>{rightContent}</Space>}
            </div>
            {children}
        </div>
    );
};

// ==============================================
// MetricCard Component
// ==============================================
interface MetricCardProps {
    title: string;
    value: string | number;
    suffix?: string;
    prefix?: ReactNode;
    trend?: 'up' | 'down' | 'neutral';
    trendValue?: string;
    loading?: boolean;
    style?: React.CSSProperties;
    [key: string]: unknown;
}

export const MetricCard: React.FC<MetricCardProps> = ({
    title,
    value,
    suffix,
    prefix,
    loading = false,
    style,
}) => {
    return (
        <Card size="small" loading={loading} style={style}>
            <Statistic
                title={title}
                value={value}
                suffix={suffix}
                prefix={prefix}
            />
        </Card>
    );
};

// ==============================================
// ProcessQuestion Component
// ==============================================
interface ProcessQuestionProps {
    icon: ReactNode;
    title: string;
    description: string;
    onClick?: () => void;
    [key: string]: unknown;
}

export const ProcessQuestion: React.FC<ProcessQuestionProps> = ({
    icon,
    title,
    description,
    onClick,
}) => {
    return (
        <Card
            hoverable
            onClick={onClick}
            style={{ height: '100%', cursor: onClick ? 'pointer' : 'default' }}
        >
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                <div style={{ fontSize: 32, color: tokens.colors.primary }}>{icon}</div>
                <div>
                    <Title level={4} style={{ marginBottom: tokens.spacing.xs }}>{title}</Title>
                    <Text type="secondary">{description}</Text>
                </div>
            </Space>
        </Card>
    );
};

// ==============================================
// EmptyState Component
// ==============================================
interface EmptyStateProps {
    title?: string;
    description?: string;
    icon?: ReactNode;
    action?: ReactNode;
    actionLabel?: string;
    onAction?: () => void;
    [key: string]: unknown;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
    title = 'No data',
    description,
    icon,
    action,
    actionLabel,
    onAction,
}) => {
    const actionContent = action || (actionLabel && onAction ? (
        <Button type="primary" onClick={onAction}>{actionLabel}</Button>
    ) : null);

    return (
        <Empty
            image={icon || Empty.PRESENTED_IMAGE_SIMPLE}
            description={
                <Space direction="vertical" size="small">
                    <Text strong>{title}</Text>
                    {description && <Text type="secondary">{description}</Text>}
                </Space>
            }
        >
            {actionContent}
        </Empty>
    );
};

// ==============================================
// AppShell Component
// ==============================================
interface AppShellProps {
    children: ReactNode;
    sider?: ReactNode;
    header?: ReactNode;
    activeId?: string;
    onNavigate?: (id: string) => void;
    userName?: string;
    userEmail?: string;
    notificationCount?: number;
    [key: string]: unknown;
}

export const AppShell: React.FC<AppShellProps> = ({ children, sider, header }) => {
    return (
        <Layout style={{ minHeight: '100vh' }}>
            {header && <Header style={{ background: tokens.colors.surface.default, padding: `0 ${tokens.spacing.lg}px` }}>{header}</Header>}
            <Layout>
                {sider && <Sider width={240} style={{ background: tokens.colors.surface.default }}>{sider}</Sider>}
                <Content style={{ padding: tokens.spacing.lg, background: tokens.colors.background }}>
                    {children}
                </Content>
            </Layout>
        </Layout>
    );
};

// ==============================================
// ErrorBoundary Component
// ==============================================
interface ErrorBoundaryProps {
    children: ReactNode;
    fallback?: ReactNode;
    onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('[ErrorBoundary] Caught error:', error, errorInfo);
        this.props.onError?.(error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return this.props.fallback || (
                <Card>
                    <Empty
                        description={
                            <Space direction="vertical">
                                <Text type="danger">Something went wrong</Text>
                                <Text type="secondary">{this.state.error?.message}</Text>
                            </Space>
                        }
                    />
                </Card>
            );
        }

        return this.props.children;
    }
}

// ==============================================
// ProcessMiningSdk - Fully permissive interface
// ==============================================
 
export interface ProcessMiningSdk {
    baseUrl: string;
    checkHealth: () => Promise<boolean>;
    processes: {
        list: (options?: { pageSize?: number }) => Promise<any>;
        get: (id: string) => Promise<any>;
        analyze: (id: string) => Promise<any>;
        getProcessSummary?: (id: string) => Promise<any>;
        [key: string]: any;
    };
    analytics: {
        performance: (datasetId: string) => Promise<any>;
        conformance: (datasetId: string) => Promise<any>;
        getProcessSummary: (datasetId: string) => Promise<any>;
        [key: string]: any;
    };
    predictions: {
        list: (datasetId: string) => Promise<any>;
        listPredictors: (datasetId: string) => Promise<any>;
        create: (datasetId: string, config: any) => Promise<any>;
        [key: string]: any;
    };
    discovery: {
        dfg: (datasetId: string, options?: any) => Promise<any>;
        variants: (datasetId: string, options?: any) => Promise<any>;
        [key: string]: any;
    };
    conformance: {
        check: (datasetId: string, modelId: string) => Promise<any>;
        [key: string]: any;
    };
    [key: string]: any;
}

