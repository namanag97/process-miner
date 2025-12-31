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

import React, { Suspense, ReactNode, useEffect } from 'react';
import { Button, Result, Skeleton } from 'antd';
import {
  ReloadOutlined,
  InboxOutlined,
  WarningOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, tokens, logAction } from '@lumina/design-system';

// ============================================
// Types
// ============================================

interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: ReactNode;
}

interface EmptyStateConfig {
  icon?: ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
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
      icon={<WarningOutlined style={{ color: tokens.colors.error }} />}
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
          onClick={() => navigate('/home')}
        >
          Go Home
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
    <Result
      icon={config.icon || <InboxOutlined style={{ color: tokens.colors.text.tertiary }} />}
      title={config.title}
      subTitle={config.description}
      extra={
        config.actionLabel && config.onAction && (
          <Button type="primary" onClick={config.onAction}>
            {config.actionLabel}
          </Button>
        )
      }
    />
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
    title: item.href ? (
      <a onClick={() => navigate(item.href!)} style={{ cursor: 'pointer' }}>
        {item.icon} {item.label}
      </a>
    ) : (
      <span>{item.icon} {item.label}</span>
    ),
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
          breadcrumb={breadcrumbItems ? { items: breadcrumbItems } : undefined}
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
        breadcrumb={breadcrumbItems ? { items: breadcrumbItems } : undefined}
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
                color: tokens.colors.text.secondary,
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
