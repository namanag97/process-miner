import { Result, Button, Typography, Space } from 'antd';
import { useNavigate } from 'react-router-dom';
import { ExclamationCircleOutlined, HomeOutlined, ReloadOutlined } from '@ant-design/icons';
import { useEffect } from 'react';
import { devLog } from './DevConsole';

const { Paragraph, Text } = Typography;

interface FeatureErrorFallbackProps {
  error?: Error;
  resetError?: () => void;
  featureName?: string;
}

/**
 * Reusable error fallback component for feature-level error boundaries
 * Provides user-friendly error UI with recovery options
 * Logs all errors to DevConsole for debugging
 */
export function FeatureErrorFallback({
  error,
  resetError,
  featureName = 'this feature'
}: FeatureErrorFallbackProps) {
  const navigate = useNavigate();
  const isDevelopment = import.meta.env.DEV;

  // Log error to DevConsole
  useEffect(() => {
    if (error) {
      devLog.error(
        `Feature:${featureName}`,
        `Feature error boundary caught: ${error.message}`,
        {
          error: error.message,
          stack: error.stack,
          featureName,
          location: window.location.pathname,
          timestamp: new Date().toISOString(),
        }
      );
    }
  }, [error, featureName]);

  const handleRetry = () => {
    devLog.action(
      `Feature:${featureName}`,
      'User clicked Retry on error fallback',
      { featureName, location: window.location.pathname }
    );
    if (resetError) {
      resetError();
    } else {
      window.location.reload();
    }
  };

  const handleGoHome = () => {
    devLog.action(
      `Feature:${featureName}`,
      'User clicked Go Home on error fallback',
      { featureName, fromLocation: window.location.pathname }
    );
    navigate('/');
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '400px',
      padding: '24px'
    }}>
      <Result
        status="error"
        icon={<ExclamationCircleOutlined />}
        title={`Something went wrong with ${featureName}`}
        subTitle={
          <Space direction="vertical" size="small">
            <Paragraph>
              We encountered an unexpected error. This has been logged and our team will investigate.
            </Paragraph>
            {isDevelopment && error && (
              <div style={{
                marginTop: '16px',
                padding: '12px',
                background: '#f5f5f5',
                borderRadius: '4px',
                textAlign: 'left'
              }}>
                <Text strong>Error Details (Development Only):</Text>
                <pre style={{
                  marginTop: '8px',
                  fontSize: '12px',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  {error.message}
                  {error.stack && `\n\n${error.stack}`}
                </pre>
              </div>
            )}
          </Space>
        }
        extra={[
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            onClick={handleRetry}
            key="retry"
          >
            Try Again
          </Button>,
          <Button
            icon={<HomeOutlined />}
            onClick={handleGoHome}
            key="home"
          >
            Go to Home
          </Button>,
        ]}
      />
    </div>
  );
}
