/**
 * FeaturePage - Standard page wrapper with consistent patterns
 *
 * Provides unified handling of:
 * - Loading states (skeleton)
 * - Error states (with retry)
 * - Empty states (with action)
 * - Page header with breadcrumbs
 * - Audit logging (optional)
 *
 * @example
 * <FeaturePage
 *   title="Project Details"
 *   description="Manage your project"
 *   breadcrumb={[{ label: 'Workspace', href: '/workspace' }, { label: 'Project' }]}
 *   isLoading={isLoading}
 *   error={error}
 *   isEmpty={!data}
 *   emptyState={{
 *     title: 'No data found',
 *     description: 'Upload a file to get started',
 *     actionLabel: 'Upload',
 *     onAction: () => navigate('/upload'),
 *   }}
 *   actions={<Button>Edit</Button>}
 * >
 *   <ProjectContent data={data} />
 * </FeaturePage>
 */

import { Suspense, ReactNode, useEffect } from 'react';
import { Button, Result, Skeleton, Space, Typography } from 'antd';
import {
  ReloadOutlined,
  InboxOutlined,
  WarningOutlined,
  HomeOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';

import { useNavigate } from 'react-router-dom';
import { PageHeader, tokens, logAction } from '@lumina/design-system';

const { Text } = Typography;

// ============================================
// Types
// ============================================

interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: ReactNode;
}

interface SecondaryAction {
  label: string;
  onClick: () => void;
}

interface EmptyStateConfig {
  icon?: ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  /** Secondary action shown as a text link below the primary action */
  secondaryAction?: SecondaryAction;
  /** Quick tips shown as a bulleted list to help users get started */
  tips?: string[];
}

interface FeaturePageProps {
  // Header configuration
  title: string;
  description?: string;
  breadcrumb?: BreadcrumbItem[];
  actions?: ReactNode;

  // Content
  children: ReactNode;

  // State handling
  isLoading?: boolean;
  error?: Error | null;
  onRetry?: () => void;
  isEmpty?: boolean;
  emptyState?: EmptyStateConfig;

  // Audit/logging
  auditCategory?: string;

  // Layout
  noPadding?: boolean;
  maxWidth?: number | string;
}

// ============================================
// Loading State Component
// ============================================

function LoadingSkeleton() {
  return (
    <div style={{ padding: tokens.spacing[6] }}>
      {/* Header skeleton */}
      <Skeleton
        active
        title={{ width: '30%' }}
        paragraph={{ rows: 1, width: ['50%'] }}
      />

      {/* Content skeleton */}
      <div style={{ marginTop: tokens.spacing[6] }}>
        <Skeleton active paragraph={{ rows: 4 }} />
      </div>

      {/* Cards skeleton */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: tokens.spacing[4],
          marginTop: tokens.spacing[6],
        }}
      >
        {[1, 2, 3].map((i) => (
          <Skeleton.Node
            key={i}
            active
            style={{ width: '100%', height: 120 }}
          />
        ))}
      </div>
    </div>
  );
}

// ============================================
// Error State Component
// ============================================

interface ErrorStateProps {
  error: Error;
  onRetry?: () => void;
}

function ErrorState({ error, onRetry }: ErrorStateProps) {
  const navigate = useNavigate();

  return (
    <Result
      status="error"
      icon={<WarningOutlined style={{ color: tokens.colors.error[500] }} />}
      title="Something went wrong"
      subTitle={error.message || 'An unexpected error occurred'}
      extra={[
        onRetry && (
          <Button
            key="retry"
            type="primary"
            icon={<ReloadOutlined />}
            onClick={onRetry}
          >
            Try Again
          </Button>
        ),
        <Button
          key="home"
          icon={<HomeOutlined />}
          onClick={() => navigate('/workspace')}
        >
          Go to Workspace
        </Button>,
      ].filter(Boolean)}
    />
  );
}

// ============================================
// Empty State Component
// ============================================

interface EmptyStateProps {
  config: EmptyStateConfig;
}

function EmptyState({ config }: EmptyStateProps) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: tokens.spacing[8],
        textAlign: 'center',
        maxWidth: 480,
        margin: '0 auto',
      }}
    >
      {/* Icon */}
      <div
        style={{
          fontSize: 48,
          color: tokens.colors.primary[400],
          marginBottom: tokens.spacing[4],
        }}
      >
        {config.icon || <InboxOutlined style={{ color: tokens.colors.neutral[400] }} />}
      </div>

      {/* Title */}
      <h3
        style={{
          marginBottom: tokens.spacing[2],
          color: tokens.colors.neutral[800],
          fontSize: tokens.fontSize.xl,
          fontWeight: 600,
        }}
      >
        {config.title}
      </h3>

      {/* Description */}
      {config.description && (
        <p
          style={{
            color: tokens.colors.neutral[500],
            marginBottom: tokens.spacing[4],
            maxWidth: 360,
          }}
        >
          {config.description}
        </p>
      )}

      {/* Tips list */}
      {config.tips && config.tips.length > 0 && (
        <div
          style={{
            marginBottom: tokens.spacing[6],
            textAlign: 'left',
            background: tokens.colors.neutral[50],
            padding: tokens.spacing[4],
            borderRadius: tokens.radius.md,
            width: '100%',
            maxWidth: 320,
          }}
        >
          <Text
            strong
            style={{
              display: 'block',
              marginBottom: tokens.spacing[2],
              color: tokens.colors.neutral[700],
              fontSize: 12,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            What you can do
          </Text>
          {config.tips.map((tip, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: tokens.spacing[2],
                marginBottom: index < config.tips!.length - 1 ? tokens.spacing[2] : 0,
              }}
            >
              <CheckCircleOutlined
                style={{
                  color: tokens.colors.success[500],
                  fontSize: 14,
                  marginTop: 3,
                }}
              />
              <Text style={{ color: tokens.colors.neutral[600], fontSize: 13 }}>
                {tip}
              </Text>
            </div>
          ))}
        </div>
      )}

      {/* Action buttons */}
      <Space direction="vertical" size="small" align="center">
        {config.actionLabel && config.onAction && (
          <Button type="primary" size="large" onClick={config.onAction}>
            {config.actionLabel}
          </Button>
        )}
        {config.secondaryAction && (
          <Button
            type="link"
            onClick={config.secondaryAction.onClick}
            style={{ color: tokens.colors.neutral[500] }}
          >
            {config.secondaryAction.label}
          </Button>
        )}
      </Space>
    </div>
  );
}

// ============================================
// Main Component
// ============================================

export function FeaturePage({
  title,
  description,
  breadcrumb,
  actions,
  children,
  isLoading = false,
  error,
  onRetry,
  isEmpty = false,
  emptyState,
  auditCategory,
  noPadding = false,
  maxWidth,
}: FeaturePageProps) {
  const navigate = useNavigate();

  // Audit logging for page views
  useEffect(() => {
    if (auditCategory) {
      logAction('PageView', {
        category: auditCategory,
        page: title,
        path: window.location.pathname,
      });
    }
  }, [auditCategory, title]);

  // Convert breadcrumb to PageHeader format
  const breadcrumbItems = breadcrumb?.map((item) => ({
    label: item.label,
    href: item.href,
    onClick: item.href ? () => navigate(item.href!) : undefined,
  }));

  // Loading state - show skeleton
  if (isLoading) {
    return (
      <div style={{ maxWidth }}>
        <LoadingSkeleton />
      </div>
    );
  }

  // Error state - show error with retry option
  if (error) {
    return (
      <div style={{ maxWidth, padding: tokens.spacing[6] }}>
        <ErrorState error={error} onRetry={onRetry} />
      </div>
    );
  }

  // Empty state - show empty with action
  if (isEmpty && emptyState) {
    return (
      <div style={{ maxWidth }}>
        <PageHeader
          title={title}
          description={description}
          breadcrumb={breadcrumbItems}
          actions={actions}
        />
        <div style={{ padding: noPadding ? 0 : tokens.spacing[6] }}>
          <EmptyState config={emptyState} />
        </div>
      </div>
    );
  }

  // Normal render
  return (
    <div style={{ maxWidth }}>
      <PageHeader
        title={title}
        description={description}
        breadcrumb={breadcrumbItems}
        actions={actions}
      />
      <Suspense fallback={<LoadingSkeleton />}>
        <div style={{ padding: noPadding ? 0 : undefined }}>
          {children}
        </div>
      </Suspense>
    </div>
  );
}

// ============================================
// Section Components (for composing pages)
// ============================================

interface PageSectionProps {
  title?: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  noPadding?: boolean;
}

export function PageSection({
  title,
  description,
  actions,
  children,
  noPadding = false,
}: PageSectionProps) {
  return (
    <section
      style={{
        marginTop: tokens.spacing[6],
        padding: noPadding ? 0 : tokens.spacing[4],
        background: tokens.colors.surface.card,
        borderRadius: tokens.radius.lg,
      }}
    >
      {(title || actions) && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: tokens.spacing[4],
          }}
        >
          <div>
            {title && (
              <h3 style={{
                margin: 0,
                fontSize: tokens.fontSize.lg,
                fontWeight: 600
              }}>
                {title}
              </h3>
            )}
            {description && (
              <p style={{
                margin: `${tokens.spacing[1]}px 0 0`,
                color: tokens.colors.neutral[500],
                fontSize: tokens.fontSize.sm,
              }}>
                {description}
              </p>
            )}
          </div>
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}

export type { FeaturePageProps, BreadcrumbItem, EmptyStateConfig };
