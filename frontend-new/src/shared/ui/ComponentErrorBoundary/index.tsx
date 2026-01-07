/**
 * ComponentErrorBoundary - Inline component-level error boundary
 *
 * Wraps risky components (third-party libraries, complex visualizations)
 * and displays an inline error message without crashing the entire feature.
 * The component can retry rendering without a full page reload.
 *
 * Usage:
 * ```tsx
 * <ComponentErrorBoundary componentName="Process Graph">
 *   <ProcessGraph data={graphData} />
 * </ComponentErrorBoundary>
 *
 * // With custom fallback
 * <ComponentErrorBoundary
 *   componentName="Chart"
 *   fallback={<ChartPlaceholder message="Unable to render chart" />}
 * >
 *   <Chart data={data} />
 * </ComponentErrorBoundary>
 * ```
 */
import { Component, ReactNode, ErrorInfo } from 'react';
import { Alert, Button, Space, Typography } from 'antd';
import { ReloadOutlined, BugOutlined, WarningOutlined } from '@ant-design/icons';
import { devLog } from '../DevConsole';

const { Text } = Typography;

// ============================================
// Types
// ============================================

export interface ComponentErrorBoundaryProps {
  /** Content to render when no error */
  children: ReactNode;
  /** Name of the component for display and logging */
  componentName: string;
  /** Custom fallback UI (optional) */
  fallback?: ReactNode;
  /** Callback when error is caught */
  onError?: (error: Error, componentName: string) => void;
  /** Show error details in development mode */
  showDetails?: boolean;
  /** Custom retry handler */
  onRetry?: () => void;
  /** Variant of the error display */
  variant?: 'alert' | 'card' | 'minimal';
  /** Size of the error display */
  size?: 'small' | 'default' | 'large';
}

interface ComponentErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  retryCount: number;
}

// ============================================
// Default Fallback Components
// ============================================

interface DefaultFallbackProps {
  error: Error;
  errorInfo: ErrorInfo | null;
  componentName: string;
  showDetails: boolean;
  onRetry: () => void;
  variant: 'alert' | 'card' | 'minimal';
  size: 'small' | 'default' | 'large';
  retryCount: number;
}

function DefaultFallback({
  error,
  errorInfo,
  componentName,
  showDetails,
  onRetry,
  variant,
  size,
  retryCount,
}: DefaultFallbackProps) {
  const isDev = import.meta.env.DEV;
  const shouldShowDetails = showDetails || isDev;

  // Minimal variant - just a simple inline message
  if (variant === 'minimal') {
    return (
      <div
        style={{
          padding: size === 'small' ? '8px' : '16px',
          textAlign: 'center',
          color: '#ff4d4f',
        }}
      >
        <Space direction="vertical" size="small">
          <Text type="danger">
            <WarningOutlined /> Failed to load {componentName}
          </Text>
          <Button size="small" icon={<ReloadOutlined />} onClick={onRetry}>
            Retry
          </Button>
        </Space>
      </div>
    );
  }

  // Card variant - more prominent error display
  if (variant === 'card') {
    return (
      <div
        style={{
          padding: size === 'small' ? '16px' : '24px',
          border: '1px solid #ffccc7',
          borderRadius: '8px',
          background: '#fff2f0',
          textAlign: 'center',
        }}
      >
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <BugOutlined style={{ fontSize: size === 'small' ? 24 : 32, color: '#ff4d4f' }} />
          <div>
            <Text strong style={{ display: 'block', marginBottom: 4 }}>
              {componentName} encountered an error
            </Text>
            <Text type="secondary" style={{ fontSize: size === 'small' ? 12 : 14 }}>
              Click retry to try loading again
            </Text>
          </div>

          {shouldShowDetails && (
            <div
              style={{
                textAlign: 'left',
                padding: '12px',
                background: 'white',
                borderRadius: '4px',
                maxHeight: '120px',
                overflow: 'auto',
                fontSize: '12px',
              }}
            >
              <Text type="danger">{error.message}</Text>
            </div>
          )}

          <Button type="primary" icon={<ReloadOutlined />} onClick={onRetry} size={size}>
            Retry {retryCount > 0 ? `(${retryCount})` : ''}
          </Button>
        </Space>
      </div>
    );
  }

  // Default alert variant
  return (
    <Alert
      type="error"
      showIcon
      icon={<BugOutlined />}
      message={`Error in ${componentName}`}
      description={
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <Text type="secondary">
            {shouldShowDetails ? error.message : 'An unexpected error occurred'}
          </Text>

          {shouldShowDetails && errorInfo?.componentStack && (
            <details style={{ fontSize: '11px' }}>
              <summary style={{ cursor: 'pointer', color: '#ff4d4f' }}>Stack trace</summary>
              <pre
                style={{
                  marginTop: '8px',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  maxHeight: '100px',
                  overflow: 'auto',
                  fontSize: '10px',
                  background: '#fff1f0',
                  padding: '8px',
                  borderRadius: '4px',
                }}
              >
                {errorInfo.componentStack}
              </pre>
            </details>
          )}
        </Space>
      }
      action={
        <Button size={size} icon={<ReloadOutlined />} onClick={onRetry}>
          Retry {retryCount > 0 ? `(${retryCount})` : ''}
        </Button>
      }
      style={{ marginBottom: 0 }}
    />
  );
}

// ============================================
// ComponentErrorBoundary Class
// ============================================

export class ComponentErrorBoundary extends Component<
  ComponentErrorBoundaryProps,
  ComponentErrorBoundaryState
> {
  constructor(props: ComponentErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ComponentErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    const { componentName, onError } = this.props;

    // Update state with error info
    this.setState({ errorInfo });

    // Log to DevConsole
    devLog.error(`ComponentErrorBoundary:${componentName}`, error.message, {
      componentName,
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      retryCount: this.state.retryCount,
      timestamp: new Date().toISOString(),
    });

    // Console error in development
    if (import.meta.env.DEV) {
      console.error(`[ComponentErrorBoundary] Error in ${componentName}:`, error);
      console.error('[ComponentErrorBoundary] Component stack:', errorInfo.componentStack);
    }

    // Call optional error callback
    onError?.(error, componentName);
  }

  handleRetry = (): void => {
    const { componentName, onRetry } = this.props;

    devLog.action(`ComponentErrorBoundary:${componentName}`, 'Retry clicked', {
      retryCount: this.state.retryCount + 1,
    });

    // Call custom retry handler if provided
    if (onRetry) {
      onRetry();
    }

    // Reset error state to retry rendering
    this.setState((prevState) => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1,
    }));
  };

  render(): ReactNode {
    const { hasError, error, errorInfo, retryCount } = this.state;
    const {
      children,
      fallback,
      componentName,
      showDetails = false,
      variant = 'alert',
      size = 'default',
    } = this.props;

    if (hasError && error) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback;
      }

      // Use default fallback UI
      return (
        <DefaultFallback
          error={error}
          errorInfo={errorInfo}
          componentName={componentName}
          showDetails={showDetails}
          onRetry={this.handleRetry}
          variant={variant}
          size={size}
          retryCount={retryCount}
        />
      );
    }

    return children;
  }
}

export default ComponentErrorBoundary;
