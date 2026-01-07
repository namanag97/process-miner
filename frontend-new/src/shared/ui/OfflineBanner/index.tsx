/**
 * Offline Banner Component
 *
 * Displays a persistent banner when the user is offline,
 * with information about queued actions and connection status.
 */
import React from 'react';
import { Alert, Badge, Button, Space, Typography } from 'antd';
import { WifiOutlined, CloudSyncOutlined, ReloadOutlined } from '@ant-design/icons';

import { useNetworkStatus, useOfflineDuration } from '../../hooks/useNetworkStatus';
import { useOfflineQueueProcessor } from '../../../api/offlineQueue';

const { Text } = Typography;

// ============================================
// Offline Banner Component
// ============================================

interface OfflineBannerProps {
    /** Custom message to display when offline */
    message?: string;
    /** Whether to show the queued actions count */
    showQueueCount?: boolean;
    /** Custom styles */
    style?: React.CSSProperties;
}

/**
 * Banner that appears when the user goes offline
 *
 * @example
 * ```tsx
 * function App() {
 *   return (
 *     <>
 *       <OfflineBanner />
 *       <AppContent />
 *     </>
 *   );
 * }
 * ```
 */
export function OfflineBanner({
    message = "You're offline. Some features may be unavailable.",
    showQueueCount = true,
    style,
}: OfflineBannerProps): React.ReactElement | null {
    const isOnline = useNetworkStatus();
    const { isOffline, offlineDuration } = useOfflineDuration();
    const { queueSize, isProcessing, processQueue } = useOfflineQueueProcessor();

    // Don't render anything when online (unless processing queue)
    if (isOnline && !isProcessing && queueSize === 0) {
        return null;
    }

    // Format offline duration
    const formatDuration = (ms: number): string => {
        const seconds = Math.floor(ms / 1000);
        if (seconds < 60) return `${seconds}s`;
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m ${seconds % 60}s`;
        const hours = Math.floor(minutes / 60);
        return `${hours}h ${minutes % 60}m`;
    };

    // Syncing state (just came back online)
    if (isOnline && (isProcessing || queueSize > 0)) {
        return (
            <Alert
                type="info"
                banner
                icon={<CloudSyncOutlined spin={isProcessing} />}
                message={
                    <Space>
                        <Text>
                            {isProcessing
                                ? `Syncing ${queueSize} queued action${queueSize !== 1 ? 's' : ''}...`
                                : `${queueSize} action${queueSize !== 1 ? 's' : ''} queued while offline`}
                        </Text>
                        {!isProcessing && queueSize > 0 && (
                            <Button
                                type="link"
                                size="small"
                                icon={<ReloadOutlined />}
                                onClick={processQueue}
                            >
                                Sync Now
                            </Button>
                        )}
                    </Space>
                }
                style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    zIndex: 1001,
                    borderRadius: 0,
                    ...style,
                }}
            />
        );
    }

    // Offline state
    return (
        <Alert
            type="warning"
            banner
            icon={<WifiOutlined />}
            message={
                <Space size="middle">
                    <Text>{message}</Text>
                    {isOffline && offlineDuration > 0 && (
                        <Text type="secondary">
                            Offline for {formatDuration(offlineDuration)}
                        </Text>
                    )}
                    {showQueueCount && queueSize > 0 && (
                        <Badge
                            count={queueSize}
                            style={{ backgroundColor: '#faad14' }}
                            title={`${queueSize} action${queueSize !== 1 ? 's' : ''} queued`}
                        />
                    )}
                </Space>
            }
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                zIndex: 1001,
                borderRadius: 0,
                ...style,
            }}
        />
    );
}

// ============================================
// Minimal Offline Indicator
// ============================================

interface OfflineIndicatorProps {
    /** Size of the indicator */
    size?: 'small' | 'default';
}

/**
 * Small indicator showing online/offline status
 *
 * Useful for status bars or headers
 *
 * @example
 * ```tsx
 * function Header() {
 *   return (
 *     <header>
 *       <Logo />
 *       <OfflineIndicator />
 *     </header>
 *   );
 * }
 * ```
 */
export function OfflineIndicator({ size = 'default' }: OfflineIndicatorProps): React.ReactElement {
    const isOnline = useNetworkStatus();
    const { queueSize } = useOfflineQueueProcessor();

    const dotSize = size === 'small' ? 8 : 10;

    return (
        <Space size={4}>
            <span
                style={{
                    display: 'inline-block',
                    width: dotSize,
                    height: dotSize,
                    borderRadius: '50%',
                    backgroundColor: isOnline ? '#52c41a' : '#faad14',
                    boxShadow: isOnline ? '0 0 4px #52c41a' : '0 0 4px #faad14',
                }}
                title={isOnline ? 'Online' : 'Offline'}
            />
            {!isOnline && queueSize > 0 && (
                <Text type="secondary" style={{ fontSize: size === 'small' ? 10 : 12 }}>
                    {queueSize} queued
                </Text>
            )}
        </Space>
    );
}

export default OfflineBanner;
