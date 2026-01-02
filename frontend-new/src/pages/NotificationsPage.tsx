import React, { useState, useMemo, useEffect } from 'react';
import { List, Tabs, Button, Typography, Badge, Space } from 'antd';
import {
  CheckCircleOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import { PageHeader, EmptyState, tokens, logAction } from '@lumina/design-system';
import { useNotifications, Notification } from '../context/NotificationContext';
import { createLogger } from '../utils/logger';

const log = createLogger('Notifications');
const { Text, Paragraph } = Typography;

const typeIcons: Record<Notification['type'], React.ReactNode> = {
  success: <CheckCircleOutlined style={{ color: tokens.colors.success[500] }} />,
  info: <InfoCircleOutlined style={{ color: tokens.colors.info[500] }} />,
  warning: <WarningOutlined style={{ color: tokens.colors.warning[500] }} />,
  error: <CloseCircleOutlined style={{ color: tokens.colors.error[500] }} />,
};

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function NotificationsPage() {
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications();
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    log.info('Notifications page viewed', { total: notifications.length, unread: unreadCount });
  }, [notifications.length, unreadCount]);

  const filteredNotifications = useMemo(() => {
    if (activeTab === 'unread') {
      return notifications.filter((n) => !n.isRead);
    }
    return notifications;
  }, [notifications, activeTab]);

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.isRead) {
      logAction('NotificationsPage', 'notification_clicked', { id: notification.id, type: notification.type });
      markAsRead(notification.id);
      log.info('Notification marked as read', { id: notification.id });
    }
  };

  const handleMarkAllAsRead = () => {
    logAction('NotificationsPage', 'mark_all_read_clicked', { count: unreadCount });
    markAllAsRead();
    log.info('All notifications marked as read');
  };

  const tabItems = [
    { key: 'all', label: 'All' },
    {
      key: 'unread',
      label: (
        <Space>
          Unread
          {unreadCount > 0 && (
            <Badge count={unreadCount} size="small" style={{ marginLeft: 4 }} />
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Notifications"
        actions={
          unreadCount > 0 ? (
            <Button onClick={handleMarkAllAsRead}>Mark all as read</Button>
          ) : undefined
        }
      />

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
        style={{ marginBottom: tokens.spacing[4] }}
      />

      {filteredNotifications.length === 0 ? (
        <EmptyState
          icon={<InfoCircleOutlined />}
          title={activeTab === 'unread' ? 'No unread notifications' : 'No notifications'}
          description={
            activeTab === 'unread'
              ? "You're all caught up!"
              : 'Notifications will appear here when you have updates.'
          }
        />
      ) : (
        <List
          dataSource={filteredNotifications}
          renderItem={(notification) => (
            <List.Item
              onClick={() => handleNotificationClick(notification)}
              style={{
                cursor: 'pointer',
                padding: tokens.spacing[4],
                backgroundColor: notification.isRead
                  ? 'transparent'
                  : tokens.colors.primary[50],
                borderRadius: tokens.radius.md,
                marginBottom: tokens.spacing[2],
                border: `1px solid ${tokens.colors.neutral[200]}`,
              }}
            >
              <List.Item.Meta
                avatar={
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    {!notification.isRead && (
                      <div
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          backgroundColor: tokens.colors.primary[500],
                          marginRight: tokens.spacing[2],
                        }}
                      />
                    )}
                    <span style={{ fontSize: 20 }}>{typeIcons[notification.type]}</span>
                  </div>
                }
                title={
                  <Text strong={!notification.isRead}>{notification.title}</Text>
                }
                description={
                  <div>
                    <Paragraph
                      type="secondary"
                      style={{ marginBottom: tokens.spacing[1] }}
                      ellipsis={{ rows: 2 }}
                    >
                      {notification.description}
                    </Paragraph>
                    <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                      {formatRelativeTime(notification.createdAt)}
                    </Text>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      )}
    </div>
  );
}

export default NotificationsPage;
