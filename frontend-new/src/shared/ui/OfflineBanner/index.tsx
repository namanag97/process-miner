/**
 * OfflineBanner Component
 *
 * Displays a banner when the user is offline.
 * Automatically shows/hides based on network status.
 */

import { ReactElement } from 'react';
import { Alert, Space, Typography } from 'antd';
import { CloudOutlined } from '@ant-design/icons';
import { useNetworkStatus, useOfflineDuration } from '../../hooks/useNetworkStatus';

const { Text } = Typography;

function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return seconds + 's';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return minutes + 'm ' + (seconds % 60) + 's';
  const hours = Math.floor(minutes / 60);
  return hours + 'h ' + (minutes % 60) + 'm';
}

export function OfflineBanner(): ReactElement | null {
  const isOnline = useNetworkStatus();
  const offlineDuration = useOfflineDuration();

  if (isOnline) {
    return null;
  }

  return (
    <Alert
      banner
      type="warning"
      icon={<CloudOutlined />}
      message={
        <Space>
          <Text strong>You are offline</Text>
          {offlineDuration > 0 && (
            <Text type="secondary">
              ({formatDuration(offlineDuration)})
            </Text>
          )}
        </Space>
      }
      description={
        <Text type="secondary">
          Some features may be unavailable. Changes will be saved when you reconnect.
        </Text>
      }
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
      }}
    />
  );
}

export default OfflineBanner;
