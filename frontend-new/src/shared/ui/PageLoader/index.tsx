/**
 * PageLoader - Loading fallback for lazy-loaded routes
 *
 * Displays a centered loading spinner while route components are being loaded.
 * Used as the Suspense fallback for React.lazy routes.
 */
import { Spin, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface PageLoaderProps {
  /** Optional loading message */
  message?: string;
  /** Size of the spinner */
  size?: 'small' | 'default' | 'large';
  /** Full page mode (centers in viewport) */
  fullPage?: boolean;
}

export function PageLoader({
  message = 'Loading...',
  size = 'large',
  fullPage = true,
}: PageLoaderProps) {
  const antIcon = <LoadingOutlined style={{ fontSize: size === 'large' ? 48 : 24 }} spin />;

  const content = (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 16,
      }}
    >
      <Spin indicator={antIcon} size={size} />
      {message && (
        <Text type="secondary" style={{ fontSize: 14 }}>
          {message}
        </Text>
      )}
    </div>
  );

  if (fullPage) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#f5f5f5',
        }}
      >
        {content}
      </div>
    );
  }

  return (
    <div
      style={{
        padding: 48,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {content}
    </div>
  );
}

export default PageLoader;
