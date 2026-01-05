import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';
import { createLogger } from '../lib/logger';

const log = createLogger('Notifications');

export interface Notification {
  id: string;
  title: string;
  description: string;
  type: 'info' | 'success' | 'warning' | 'error';
  isRead: boolean;
  createdAt: Date;
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  addNotification: (notification: Omit<Notification, 'id' | 'isRead' | 'createdAt'>) => void;
}

const NotificationContext = createContext<NotificationContextType | null>(null);

// Mock initial notifications
const mockNotifications: Notification[] = [
  {
    id: '1',
    title: 'File processing complete',
    description: 'Orders.csv has been processed successfully with 1,250 cases extracted.',
    type: 'success',
    isRead: false,
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
  },
  {
    id: '2',
    title: 'New feature available',
    description: 'Check out the new variant explorer for better process insights.',
    type: 'info',
    isRead: false,
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
  },
  {
    id: '3',
    title: 'Weekly summary ready',
    description: 'Your activity summary for last week is now available.',
    type: 'info',
    isRead: false,
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
  },
  {
    id: '4',
    title: 'Upload limit reminder',
    description: 'You have used 80% of your monthly upload quota.',
    type: 'warning',
    isRead: true,
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000), // 5 days ago
  },
  {
    id: '5',
    title: 'Welcome to Lumina!',
    description: 'Get started by uploading your first event log.',
    type: 'info',
    isRead: true,
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
  },
];

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);

  const unreadCount = useMemo(
    () => notifications.filter((n) => !n.isRead).length,
    [notifications]
  );

  const markAsRead = useCallback((id: string) => {
    log.info('Marking notification as read', { id });
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, isRead: true } : n))
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    log.info('Marking all notifications as read');
    setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })));
  }, []);

  const addNotification = useCallback(
    (notification: Omit<Notification, 'id' | 'isRead' | 'createdAt'>) => {
      const newNotification: Notification = {
        ...notification,
        id: Date.now().toString(),
        isRead: false,
        createdAt: new Date(),
      };
      log.info('Adding new notification', { notification: newNotification });
      setNotifications((prev) => [newNotification, ...prev]);
    },
    []
  );

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        markAsRead,
        markAllAsRead,
        addNotification,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
}
