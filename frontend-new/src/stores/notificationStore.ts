/**
 * Notification Store
 *
 * Manages application notifications.
 * Replaces NotificationContext with Zustand for better performance.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface AppNotification {
  id: string;
  title: string;
  description: string;
  type: NotificationType;
  isRead: boolean;
  createdAt: Date;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface NotificationState {
  // State
  notifications: AppNotification[];

  // Computed (via selectors)
  // unreadCount - derived from notifications

  // Actions
  addNotification: (
    notification: Omit<AppNotification, 'id' | 'isRead' | 'createdAt'>
  ) => void;
  removeNotification: (id: string) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAll: () => void;

  // Utility
  getUnreadCount: () => number;
}

// Mock initial notifications for MVP
const mockNotifications: AppNotification[] = [
  {
    id: '1',
    title: 'File processing complete',
    description:
      'Orders.csv has been processed successfully with 1,250 cases extracted.',
    type: 'success',
    isRead: false,
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
  },
  {
    id: '2',
    title: 'New feature available',
    description:
      'Check out the new variant explorer for better process insights.',
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

export const useNotificationStore = create<NotificationState>()(
  devtools(
    (set, get) => ({
      // Initial state with mock notifications
      notifications: mockNotifications,

      // Actions
      addNotification: (notification) => {
        const newNotification: AppNotification = {
          ...notification,
          id: `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          isRead: false,
          createdAt: new Date(),
        };
        set(
          (state) => ({
            notifications: [newNotification, ...state.notifications],
          }),
          false,
          'notifications/add'
        );
      },

      removeNotification: (id) =>
        set(
          (state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          }),
          false,
          'notifications/remove'
        ),

      markAsRead: (id) =>
        set(
          (state) => ({
            notifications: state.notifications.map((n) =>
              n.id === id ? { ...n, isRead: true } : n
            ),
          }),
          false,
          'notifications/markAsRead'
        ),

      markAllAsRead: () =>
        set(
          (state) => ({
            notifications: state.notifications.map((n) => ({
              ...n,
              isRead: true,
            })),
          }),
          false,
          'notifications/markAllAsRead'
        ),

      clearAll: () => set({ notifications: [] }, false, 'notifications/clearAll'),

      // Utility
      getUnreadCount: () => get().notifications.filter((n) => !n.isRead).length,
    }),
    { name: 'NotificationStore' }
  )
);

// Selectors
export const selectNotifications = (state: NotificationState) =>
  state.notifications;
export const selectUnreadCount = (state: NotificationState) =>
  state.notifications.filter((n) => !n.isRead).length;
export const selectUnreadNotifications = (state: NotificationState) =>
  state.notifications.filter((n) => !n.isRead);
export const selectReadNotifications = (state: NotificationState) =>
  state.notifications.filter((n) => n.isRead);
