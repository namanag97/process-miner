/**
 * ErrorBoundary - React error boundary component
 *
 * Catches JavaScript errors anywhere in child component tree and displays
 * a fallback UI instead of crashing the whole app.
 *
 * Usage:
 * ```tsx
 * <ErrorBoundary fallback={<ErrorFallback />}>
 *   <YourComponent />
 * </ErrorBoundary>
 * ```
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button, Result, Typography } from 'antd';
import { ReloadOutlined, BugOutlined } from '@ant-design/icons';

const { Text, Paragraph } = Typography;

// ============================================
// Types
// ============================================

export interface ErrorBoundaryProps {
  /** Content to render when no error */
  children: ReactNode;
  /** Custom fallback UI (optional) */
  fallback?: ReactNode;
  /** Callback when error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Show error details in development */
  showDetails?: boolean;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

// ============================================
// Default Fallback Component
// ============================================

interface DefaultFallbackProps {
  error: Error | null;
  errorInfo: ErrorInfo | null;
  onReset: () => void;
  showDetails: boolean;
}

function DefaultFallback({ error, errorInfo, onReset, showDetails }: DefaultFallbackProps) {
  const isDev = process.env.NODE_ENV === 'development';

  return (
    <Result
      status="error"
      icon={<BugOutlined style={{ color: '#ff4d4f' }} />}
      title="Something went wrong"
      subTitle="An unexpected error occurred. Please try again or refresh the page."
      extra={[
        <Button key="retry" type="primary" icon={<ReloadOutlined />} onClick={onReset}>
          Try Again
        </Button>,
        <Button key="refresh" onClick={() => window.location.reload()}>
          Refresh Page
        </Button>,
      ]}
    >
      {(showDetails || isDev) && error && (
        <div
          style={{
            textAlign: 'left',
            padding: 16,
            background: '#fafafa',
            borderRadius: 8,
            marginTop: 16,
            maxHeight: 300,
            overflow: 'auto',
          }}
        >
          <Text type="danger" strong>
            {error.name}: {error.message}
          </Text>
          {errorInfo?.componentStack && (
            <Paragraph
              style={{ marginTop: 8 }}
              code
              copyable
              ellipsis={{ rows: 8, expandable: true }}
            >
              {errorInfo.componentStack}
            </Paragraph>
          )}
        </div>
      )}
    </Result>
  );
}

// ============================================
// Error Boundary Component
// ============================================

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so next render shows fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error
    console.error('[ErrorBoundary] Caught error:', error);
    console.error('[ErrorBoundary] Component stack:', errorInfo.componentStack);

    // Update state with error info
    this.setState({ errorInfo });

    // Call optional error handler
    this.props.onError?.(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback, showDetails = false } = this.props;

    if (hasError) {
      // Render custom fallback if provided
      if (fallback) {
        return fallback;
      }

      // Render default fallback
      return (
        <DefaultFallback
          error={error}
          errorInfo={errorInfo}
          onReset={this.handleReset}
          showDetails={showDetails}
        />
      );
    }

    return children;
  }
}

// ============================================
// Hook for programmatic error handling
// ============================================

/**
 * Hook to throw an error that will be caught by the nearest ErrorBoundary
 * Useful for catching errors in event handlers and async code
 */
export function useErrorBoundary(): (error: Error) => void {
  const [, setError] = React.useState<Error | null>(null);

  return React.useCallback((error: Error) => {
    setError(() => {
      throw error;
    });
  }, []);
}

export default ErrorBoundary;
