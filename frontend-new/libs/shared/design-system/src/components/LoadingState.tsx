/**
 * LoadingState - Consistent loading UI component
 *
 * Provides standardized loading states across the app.
 *
 * Usage:
 * ```tsx
 * if (isLoading) {
 *   return <LoadingState type="skeleton" rows={4} />;
 * }
 * ```
 */
import React from 'react';
import { Skeleton, Spin, Card, Space, Typography } from 'antd';
import { LoadingOutlined, SyncOutlined } from '@ant-design/icons';

const { Text } = Typography;

// ============================================
// Types
// ============================================

export type LoadingStateType = 'skeleton' | 'spinner' | 'inline' | 'card' | 'fullPage';

export interface LoadingStateProps {
  /** Type of loading indicator */
  type?: LoadingStateType;
  /** Number of skeleton rows (for skeleton type) */
  rows?: number;
  /** Custom loading text */
  text?: string;
  /** Show avatar in skeleton */
  showAvatar?: boolean;
  /** Custom height for card skeleton */
  height?: number | string;
  /** Size for spinner */
  size?: 'small' | 'default' | 'large';
  /** Custom spin indicator */
  indicator?: React.ReactNode;
}

// ============================================
// LoadingState Component
// ============================================

export function LoadingState({
  type = 'skeleton',
  rows = 4,
  text,
  showAvatar = false,
  height,
  size = 'default',
  indicator,
}: LoadingStateProps) {
  const defaultIndicator = <LoadingOutlined style={{ fontSize: 24 }} spin />;
  const spinIndicator = indicator ? (indicator as React.ReactElement) : defaultIndicator;

  // Inline spinner - minimal inline loading
  if (type === 'inline') {
    return (
      <Space>
        <Spin size={size} indicator={spinIndicator} />
        {text && <Text type="secondary">{text}</Text>}
      </Space>
    );
  }

  // Spinner - centered spinner
  if (type === 'spinner') {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 40,
          gap: 16,
        }}
      >
        <Spin size={size} indicator={spinIndicator} />
        {text && <Text type="secondary">{text}</Text>}
      </div>
    );
  }

  // Full page - centered spinner for full page loading
  if (type === 'fullPage') {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          gap: 24,
        }}
      >
        <SyncOutlined spin style={{ fontSize: 48, color: '#1890ff' }} />
        <Text type="secondary" style={{ fontSize: 16 }}>
          {text || 'Loading...'}
        </Text>
      </div>
    );
  }

  // Card - skeleton wrapped in card
  if (type === 'card') {
    return (
      <Card style={{ height }}>
        <Skeleton
          active
          avatar={showAvatar}
          paragraph={{ rows }}
          title={{ width: '40%' }}
        />
      </Card>
    );
  }

  // Skeleton (default) - just the skeleton
  return (
    <Skeleton
      active
      avatar={showAvatar}
      paragraph={{ rows }}
      title={{ width: '40%' }}
    />
  );
}

// ============================================
// Preset Loading States
// ============================================

/**
 * Loading state for metric cards (4 cards in a row)
 */
export function MetricsLoadingState() {
  return (
    <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
      {[1, 2, 3, 4].map((i) => (
        <Card key={i} style={{ flex: '1 1 200px', minWidth: 200 }}>
          <Skeleton active paragraph={{ rows: 1 }} title={{ width: '60%' }} />
        </Card>
      ))}
    </div>
  );
}

/**
 * Loading state for tables
 */
export function TableLoadingState({ rows = 5 }: { rows?: number }) {
  return (
    <Card>
      <Skeleton active paragraph={{ rows }} title={false} />
    </Card>
  );
}

/**
 * Loading state for page content
 */
export function PageLoadingState({ title = true }: { title?: boolean }) {
  return (
    <div style={{ padding: 24 }}>
      {title && (
        <Skeleton
          active
          paragraph={false}
          title={{ width: '30%' }}
          style={{ marginBottom: 24 }}
        />
      )}
      <Card>
        <Skeleton active paragraph={{ rows: 8 }} />
      </Card>
    </div>
  );
}

/**
 * Loading state for detail pages
 */
export function DetailLoadingState() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <Skeleton active paragraph={{ rows: 2 }} title={{ width: '40%' }} />
      <Card>
        <Skeleton active paragraph={{ rows: 6 }} />
      </Card>
      <Card>
        <Skeleton active paragraph={{ rows: 4 }} />
      </Card>
    </div>
  );
}

export default LoadingState;
