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
            {header && <Header style={{ background: tokens.colors.surface, padding: `0 ${tokens.spacing.lg}px` }}>{header}</Header>}
            <Layout>
                {sider && <Sider width={240} style={{ background: tokens.colors.surface }}>{sider}</Sider>}
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
// ProcessMiningSdk placeholder (permissive)
// ==============================================
export interface ProcessMiningSdk {
    baseUrl: string;
    processes?: unknown;
    analytics?: unknown;
    predictions?: unknown;
    discovery?: unknown;
    conformance?: unknown;
    [key: string]: unknown;
}
