/**
 * GlobalErrorBoundary - Root-level error boundary with reporting
 *
 * This wraps the entire application and provides:
 * - Graceful error handling for unrecoverable errors
 * - Error reporting infrastructure
 * - User-friendly error UI with recovery options
 * - Session/context preservation where possible
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button, Result, Typography, Card, Space } from 'antd';
import { ReloadOutlined, HomeOutlined, BugOutlined } from '@ant-design/icons';

const { Text, Paragraph } = Typography;

// ============================================
// Error Reporting Interface
// ============================================

export interface ErrorReport {
  error: Error;
  errorInfo: ErrorInfo;
  timestamp: string;
  userAgent: string;
  url: string;
  sessionId?: string;
  userId?: string;
  componentStack?: string;
}

export interface GlobalErrorBoundaryProps {
  children: ReactNode;
  /** Callback for error reporting (e.g., to Sentry, LogRocket, etc.) */
  onError?: (report: ErrorReport) => void;
  /** Custom fallback component */
  fallback?: (props: { error: Error; reset: () => void }) => ReactNode;
  /** Environment for error display */
  environment?: 'development' | 'production';
}

interface GlobalErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
}

// ============================================
// Error ID Generator
// ============================================

function generateErrorId(): string {
  return `err_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

// ============================================
// Default Error UI
// ============================================

interface ErrorUIProps {
  error: Error;
  errorId: string;
  isDev: boolean;
  componentStack?: string;
  onReset: () => void;
  onGoHome: () => void;
}

function ErrorUI({ error, errorId, isDev, componentStack, onReset, onGoHome }: ErrorUIProps) {
  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%)',
        padding: 24,
      }}
    >
      <Card
        style={{
          maxWidth: 600,
          width: '100%',
          boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
          borderRadius: 12,
        }}
      >
        <Result
          status="error"
          icon={<BugOutlined style={{ color: '#ff4d4f', fontSize: 64 }} />}
          title="Application Error"
          subTitle="We're sorry, but something unexpected happened. Our team has been notified."
          extra={
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Space>
                <Button type="primary" icon={<ReloadOutlined />} onClick={onReset} size="large">
                  Try Again
                </Button>
                <Button icon={<HomeOutlined />} onClick={onGoHome} size="large">
                  Go to Home
                </Button>
              </Space>

              <Text type="secondary" style={{ fontSize: 12 }}>
                Error ID: <Text code copyable={{ text: errorId }}>{errorId}</Text>
              </Text>
            </Space>
          }
        >
          {isDev && (
            <div
              style={{
                textAlign: 'left',
                padding: 16,
                background: '#fff1f0',
                borderRadius: 8,
                marginTop: 16,
                border: '1px solid #ffa39e',
              }}
            >
              <Text type="danger" strong style={{ display: 'block', marginBottom: 8 }}>
                Development Error Details:
              </Text>
              <Text type="danger">
                {error.name}: {error.message}
              </Text>
              {componentStack && (
                <Paragraph
                  style={{ marginTop: 12, marginBottom: 0, maxHeight: 200, overflow: 'auto' }}
                  code
                  copyable
                >
                  {componentStack}
                </Paragraph>
              )}
            </div>
          )}
        </Result>
      </Card>
    </div>
  );
}

// ============================================
// Global Error Boundary Component
// ============================================

export class GlobalErrorBoundary extends Component<GlobalErrorBoundaryProps, GlobalErrorBoundaryState> {
  constructor(props: GlobalErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<GlobalErrorBoundaryState> {
    return {
      hasError: true,
      error,
      errorId: generateErrorId(),
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Update state with error info
    this.setState({ errorInfo });

    // Create error report
    const report: ErrorReport = {
      error,
      errorInfo,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      componentStack: errorInfo.componentStack ?? undefined,
    };

    // Try to get session info from sessionStorage
    try {
      const guestSession = sessionStorage.getItem('lumina_guest_session');
      if (guestSession) {
        const parsed = JSON.parse(guestSession);
        report.sessionId = parsed.sessionId;
      }

      const authUser = localStorage.getItem('lumina_auth_user');
      if (authUser) {
        const parsed = JSON.parse(authUser);
        report.userId = parsed.id;
      }
    } catch {
      // Ignore storage errors
    }

    // Log to console in development
    if (this.isDevelopment) {
      console.error('[GlobalErrorBoundary] Caught error:', error);
      console.error('[GlobalErrorBoundary] Error Info:', errorInfo);
      console.error('[GlobalErrorBoundary] Full Report:', report);
    }

    // Call error handler for external reporting
    this.props.onError?.(report);

    // Store error for potential recovery
    try {
      sessionStorage.setItem(
        'lumina_last_error',
        JSON.stringify({
          errorId: this.state.errorId,
          message: error.message,
          timestamp: report.timestamp,
          url: report.url,
        })
      );
    } catch {
      // Ignore storage errors
    }
  }

  get isDevelopment(): boolean {
    return (
      this.props.environment === 'development' ||
      (this.props.environment === undefined && process.env.NODE_ENV === 'development')
    );
  }

  handleReset = (): void => {
    // Clear error state
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
    });

    // Clear stored error
    try {
      sessionStorage.removeItem('lumina_last_error');
    } catch {
      // Ignore
    }
  };

  handleGoHome = (): void => {
    // Navigate to workspace and reset
    this.handleReset();
    window.location.href = '/workspace';
  };

  handleRefresh = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    const { hasError, error, errorInfo, errorId } = this.state;
    const { children, fallback } = this.props;

    if (hasError && error) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback({ error, reset: this.handleReset });
      }

      // Use default error UI
      return (
        <ErrorUI
          error={error}
          errorId={errorId || 'unknown'}
          isDev={this.isDevelopment}
          componentStack={errorInfo?.componentStack ?? undefined}
          onReset={this.handleReset}
          onGoHome={this.handleGoHome}
        />
      );
    }

    return children;
  }
}

export default GlobalErrorBoundary;
