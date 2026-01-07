/**
 * FeatureErrorBoundary - Route-level error boundary using React Router
 *
 * This component is designed to be used as the `errorElement` in React Router routes.
 * It catches errors at the feature/route level, allowing the rest of the application
 * to continue working while showing a helpful error UI for the affected feature.
 *
 * Usage in routes:
 * ```tsx
 * const routes = [
 *   {
 *     path: '/explorer/:datasetId',
 *     element: <ExplorerPage />,
 *     errorElement: <FeatureErrorBoundary featureName="Process Explorer" />,
 *   },
 * ];
 * ```
 */
import { useRouteError, isRouteErrorResponse, useNavigate, useLocation } from 'react-router-dom';
import { Result, Button, Typography, Space, Alert } from 'antd';
import {
  ExclamationCircleOutlined,
  HomeOutlined,
  ReloadOutlined,
  ArrowLeftOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import { useEffect } from 'react';
import { devLog } from '../DevConsole';

const { Text, Paragraph } = Typography;

// ============================================
// Types
// ============================================

interface FeatureErrorBoundaryProps {
  /** Name of the feature for display and logging */
  featureName?: string;
  /** Custom recovery actions */
  showBackButton?: boolean;
  /** Custom fallback path instead of home */
  fallbackPath?: string;
}

// ============================================
// HTTP Status Helpers
// ============================================

function getHttpErrorTitle(status: number): string {
  switch (status) {
    case 400:
      return 'Bad Request';
    case 401:
      return 'Unauthorized';
    case 403:
      return 'Access Denied';
    case 404:
      return 'Page Not Found';
    case 500:
      return 'Server Error';
    case 502:
      return 'Bad Gateway';
    case 503:
      return 'Service Unavailable';
    default:
      return 'Error';
  }
}

function getHttpErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return 'The request could not be understood by the server.';
    case 401:
      return 'Please log in to access this feature.';
    case 403:
      return "You don't have permission to access this feature.";
    case 404:
      return "The page you're looking for doesn't exist or has been moved.";
    case 500:
      return 'An internal server error occurred. Please try again later.';
    case 502:
      return 'The server received an invalid response. Please try again.';
    case 503:
      return 'The service is temporarily unavailable. Please try again later.';
    default:
      return 'An unexpected error occurred.';
  }
}

function getHttpErrorStatus(status: number): 'warning' | 'error' | '403' | '404' | '500' {
  switch (status) {
    case 403:
      return '403';
    case 404:
      return '404';
    case 500:
    case 502:
    case 503:
      return '500';
    default:
      return 'error';
  }
}

// ============================================
// FeatureErrorBoundary Component
// ============================================

export function FeatureErrorBoundary({
  featureName = 'this feature',
  showBackButton = true,
  fallbackPath = '/workspace',
}: FeatureErrorBoundaryProps) {
  const error = useRouteError();
  const navigate = useNavigate();
  const location = useLocation();
  const isDevelopment = import.meta.env.DEV;

  // Log error to DevConsole
  useEffect(() => {
    const errorData = {
      featureName,
      location: location.pathname,
      timestamp: new Date().toISOString(),
    };

    if (isRouteErrorResponse(error)) {
      devLog.error(`FeatureErrorBoundary:${featureName}`, `Route error ${error.status}`, {
        ...errorData,
        status: error.status,
        statusText: error.statusText,
        data: error.data,
      });
    } else if (error instanceof Error) {
      devLog.error(`FeatureErrorBoundary:${featureName}`, error.message, {
        ...errorData,
        error: error.message,
        stack: error.stack,
      });
    } else {
      devLog.error(`FeatureErrorBoundary:${featureName}`, 'Unknown error', {
        ...errorData,
        error: String(error),
      });
    }
  }, [error, featureName, location.pathname]);

  // Action handlers
  const handleRetry = () => {
    devLog.action(`FeatureErrorBoundary:${featureName}`, 'User clicked Retry');
    window.location.reload();
  };

  const handleGoBack = () => {
    devLog.action(`FeatureErrorBoundary:${featureName}`, 'User clicked Go Back');
    navigate(-1);
  };

  const handleGoHome = () => {
    devLog.action(`FeatureErrorBoundary:${featureName}`, 'User clicked Go Home');
    navigate(fallbackPath);
  };

  // Handle React Router error responses (404, etc.)
  if (isRouteErrorResponse(error)) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
          padding: '24px',
        }}
      >
        <Result
          status={getHttpErrorStatus(error.status)}
          title={getHttpErrorTitle(error.status)}
          subTitle={getHttpErrorMessage(error.status)}
          extra={
            <Space>
              {showBackButton && (
                <Button icon={<ArrowLeftOutlined />} onClick={handleGoBack}>
                  Go Back
                </Button>
              )}
              <Button type="primary" icon={<HomeOutlined />} onClick={handleGoHome}>
                Go to Workspace
              </Button>
            </Space>
          }
        />
      </div>
    );
  }

  // Handle thrown errors
  const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
  const errorStack = error instanceof Error ? error.stack : undefined;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        padding: '24px',
      }}
    >
      <Result
        status="error"
        icon={<ExclamationCircleOutlined />}
        title={`Something went wrong with ${featureName}`}
        subTitle={
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Paragraph>
              We encountered an unexpected error. This has been logged and our team will investigate.
            </Paragraph>

            {isDevelopment && (
              <Alert
                type="error"
                icon={<WarningOutlined />}
                message="Development Error Details"
                description={
                  <div style={{ marginTop: '8px', textAlign: 'left' }}>
                    <Text strong type="danger">
                      {errorMessage}
                    </Text>
                    {errorStack && (
                      <pre
                        style={{
                          marginTop: '12px',
                          fontSize: '11px',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          maxHeight: '200px',
                          overflow: 'auto',
                          background: '#fff1f0',
                          padding: '8px',
                          borderRadius: '4px',
                        }}
                      >
                        {errorStack}
                      </pre>
                    )}
                  </div>
                }
              />
            )}
          </Space>
        }
        extra={
          <Space>
            {showBackButton && (
              <Button icon={<ArrowLeftOutlined />} onClick={handleGoBack}>
                Go Back
              </Button>
            )}
            <Button type="primary" icon={<ReloadOutlined />} onClick={handleRetry}>
              Retry
            </Button>
            <Button icon={<HomeOutlined />} onClick={handleGoHome}>
              Go to Workspace
            </Button>
          </Space>
        }
      />
    </div>
  );
}

export default FeatureErrorBoundary;
