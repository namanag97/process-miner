/**
 * QueryError - Display error states for failed queries
 *
 * Provides consistent error UI across the app with retry functionality.
 *
 * Usage:
 * ```tsx
 * const { data, error, refetch } = useQuery(...);
 *
 * if (error) {
 *   return <QueryError error={error} onRetry={refetch} />;
 * }
 * ```
 */
import React from 'react';
import { Alert, Button, Result, Card, Typography, Space } from 'antd';
import {
  WarningOutlined,
  WifiOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { APIError } from '../api/client';

const { Text } = Typography;

// ============================================
// Types
// ============================================

export type QueryErrorVariant = 'inline' | 'card' | 'fullPage' | 'alert';

export interface QueryErrorProps {
  /** The error object */
  error: Error | APIError | null;
  /** Retry callback */
  onRetry?: () => void;
  /** Display variant */
  variant?: QueryErrorVariant;
  /** Custom title (overrides auto-detected title) */
  title?: string;
  /** Custom description (overrides error message) */
  description?: string;
  /** Show retry button */
  showRetry?: boolean;
  /** Additional action */
  extra?: React.ReactNode;
}

// ============================================
// Error Classification
// ============================================

interface ErrorDetails {
  icon: React.ReactNode;
  title: string;
  description: string;
  status: 'error' | 'warning' | 'info';
}

function classifyError(error: Error | APIError | null): ErrorDetails {
  if (!error) {
    return {
      icon: <ExclamationCircleOutlined />,
      title: 'Unknown Error',
      description: 'An unexpected error occurred.',
      status: 'error',
    };
  }

  // Check if it's an APIError
  if (error instanceof APIError) {
    // Network/connection errors
    if (error.isNetworkError()) {
      if (error.title === 'Connection Failed') {
        return {
          icon: <WifiOutlined />,
          title: 'Connection Failed',
          description: 'Unable to connect to the server. Please check your connection.',
          status: 'error',
        };
      }
      if (error.title === 'Request Timeout') {
        return {
          icon: <ClockCircleOutlined />,
          title: 'Request Timeout',
          description: 'The request took too long. Please try again.',
          status: 'warning',
        };
      }
      if (error.title === 'Request Aborted') {
        return {
          icon: <ExclamationCircleOutlined />,
          title: 'Request Cancelled',
          description: 'The request was cancelled.',
          status: 'info',
        };
      }
    }

    // 404 Not Found
    if (error.isNotFound()) {
      return {
        icon: <ExclamationCircleOutlined />,
        title: 'Not Found',
        description: error.detail || 'The requested resource was not found.',
        status: 'warning',
      };
    }

    // 5xx Server errors
    if (error.isServerError()) {
      return {
        icon: <WarningOutlined />,
        title: 'Server Error',
        description: 'Something went wrong on the server. Please try again later.',
        status: 'error',
      };
    }

    // 4xx Client errors
    if (error.isClientError()) {
      return {
        icon: <ExclamationCircleOutlined />,
        title: error.title || 'Request Failed',
        description: error.detail || 'The request could not be completed.',
        status: 'warning',
      };
    }

    // Validation errors
    if (error.title === 'Validation Error') {
      return {
        icon: <WarningOutlined />,
        title: 'Invalid Data',
        description: error.detail || 'The server returned unexpected data.',
        status: 'warning',
      };
    }
  }

  // Generic error fallback
  return {
    icon: <WarningOutlined />,
    title: 'Error',
    description: error.message || 'An unexpected error occurred.',
    status: 'error',
  };
}

// ============================================
// QueryError Component
// ============================================

export function QueryError({
  error,
  onRetry,
  variant = 'card',
  title,
  description,
  showRetry = true,
  extra,
}: QueryErrorProps) {
  const errorDetails = classifyError(error);
  const displayTitle = title || errorDetails.title;
  const displayDescription = description || errorDetails.description;

  const retryButton = showRetry && onRetry && (
    <Button type="primary" icon={<ReloadOutlined />} onClick={onRetry}>
      Try Again
    </Button>
  );

  // Alert variant - minimal inline display
  if (variant === 'alert') {
    return (
      <Alert
        type={errorDetails.status}
        message={displayTitle}
        description={displayDescription}
        showIcon
        icon={errorDetails.icon}
        action={retryButton}
      />
    );
  }

  // Inline variant - compact display
  if (variant === 'inline') {
    return (
      <Space direction="vertical" align="center" style={{ width: '100%', padding: 24 }}>
        <Text type="secondary" style={{ fontSize: 32 }}>
          {errorDetails.icon}
        </Text>
        <Text strong>{displayTitle}</Text>
        <Text type="secondary">{displayDescription}</Text>
        {retryButton}
        {extra}
      </Space>
    );
  }

  // Full page variant - for page-level errors
  if (variant === 'fullPage') {
    return (
      <Result
        status={errorDetails.status === 'warning' ? 'warning' : 'error'}
        icon={errorDetails.icon}
        title={displayTitle}
        subTitle={displayDescription}
        extra={
          <Space>
            {retryButton}
            {extra}
          </Space>
        }
      />
    );
  }

  // Card variant (default) - wrapped in a card
  return (
    <Card>
      <Result
        status={errorDetails.status === 'warning' ? 'warning' : 'error'}
        icon={errorDetails.icon}
        title={displayTitle}
        subTitle={displayDescription}
        extra={
          <Space>
            {retryButton}
            {extra}
          </Space>
        }
      />
    </Card>
  );
}

// ============================================
// Helper function
// ============================================

/**
 * Get a user-friendly error message from any error type
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof APIError) {
    return error.detail;
  }
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unexpected error occurred';
}

/**
 * Check if an error is a network-related error
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof APIError) {
    return error.isNetworkError();
  }
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return true;
  }
  return false;
}

export default QueryError;
