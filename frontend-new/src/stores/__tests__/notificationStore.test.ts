/**
 * Notification Store Tests
 */

import { act, renderHook } from '@testing-library/react';
import {
  useNotificationStore,
  selectNotifications,
  selectUnreadCount,
} from '../notificationStore';

describe('notificationStore', () => {
  // Note: We don't reset the store because it has mock data
  // and we test against that initial state

  describe('initial state', () => {
    it('should have mock notifications', () => {
      const { result } = renderHook(() => useNotificationStore());
      expect(result.current.notifications.length).toBeGreaterThan(0);
    });

    it('should have some unread notifications', () => {
      const { result } = renderHook(() => useNotificationStore());
      const unreadCount = result.current.getUnreadCount();
      expect(unreadCount).toBeGreaterThan(0);
    });
  });

  describe('addNotification', () => {
    it('should add a notification to the beginning', () => {
      const { result } = renderHook(() => useNotificationStore());
      const initialCount = result.current.notifications.length;

      act(() => {
        result.current.addNotification({
          title: 'Test Notification',
          description: 'This is a test',
          type: 'info',
        });
      });

      expect(result.current.notifications.length).toBe(initialCount + 1);
      expect(result.current.notifications[0].title).toBe('Test Notification');
      expect(result.current.notifications[0].isRead).toBe(false);
    });

    it('should generate unique id for new notification', () => {
      const { result } = renderHook(() => useNotificationStore());

      act(() => {
        result.current.addNotification({
          title: 'Test 1',
          description: 'Test',
          type: 'success',
        });
        result.current.addNotification({
          title: 'Test 2',
          description: 'Test',
          type: 'success',
        });
      });

      const ids = result.current.notifications.map((n) => n.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('should set createdAt to current time', () => {
      const { result } = renderHook(() => useNotificationStore());
      const before = new Date();

      act(() => {
        result.current.addNotification({
          title: 'Test',
          description: 'Test',
          type: 'info',
        });
      });

      const after = new Date();
      const createdAt = result.current.notifications[0].createdAt;

      expect(createdAt.getTime()).toBeGreaterThanOrEqual(before.getTime());
      expect(createdAt.getTime()).toBeLessThanOrEqual(after.getTime());
    });
  });

  describe('removeNotification', () => {
    it('should remove notification by id', () => {
      const { result } = renderHook(() => useNotificationStore());

      // Add a notification we can control
      act(() => {
        result.current.addNotification({
          title: 'To Remove',
          description: 'Test',
          type: 'info',
        });
      });

      const notificationId = result.current.notifications[0].id;
      const initialCount = result.current.notifications.length;

      act(() => {
        result.current.removeNotification(notificationId);
      });

      expect(result.current.notifications.length).toBe(initialCount - 1);
      expect(result.current.notifications.find((n) => n.id === notificationId)).toBeUndefined();
    });
  });

  describe('markAsRead', () => {
    it('should mark a notification as read', () => {
      const { result } = renderHook(() => useNotificationStore());

      // Add unread notification
      act(() => {
        result.current.addNotification({
          title: 'Unread Test',
          description: 'Test',
          type: 'warning',
        });
      });

      const notificationId = result.current.notifications[0].id;
      expect(result.current.notifications[0].isRead).toBe(false);

      act(() => {
        result.current.markAsRead(notificationId);
      });

      const notification = result.current.notifications.find((n) => n.id === notificationId);
      expect(notification?.isRead).toBe(true);
    });
  });

  describe('markAllAsRead', () => {
    it('should mark all notifications as read', () => {
      const { result } = renderHook(() => useNotificationStore());

      // Add some unread notifications
      act(() => {
        result.current.addNotification({
          title: 'Unread 1',
          description: 'Test',
          type: 'info',
        });
        result.current.addNotification({
          title: 'Unread 2',
          description: 'Test',
          type: 'success',
        });
      });

      expect(result.current.getUnreadCount()).toBeGreaterThan(0);

      act(() => {
        result.current.markAllAsRead();
      });

      expect(result.current.getUnreadCount()).toBe(0);
      result.current.notifications.forEach((n) => {
        expect(n.isRead).toBe(true);
      });
    });
  });

  describe('clearAll', () => {
    it('should clear all notifications', () => {
      const { result } = renderHook(() => useNotificationStore());
      expect(result.current.notifications.length).toBeGreaterThan(0);

      act(() => {
        result.current.clearAll();
      });

      expect(result.current.notifications.length).toBe(0);
    });
  });

  describe('getUnreadCount', () => {
    it('should return correct unread count', () => {
      const { result } = renderHook(() => useNotificationStore());

      // Clear and add controlled notifications
      act(() => {
        result.current.clearAll();
        result.current.addNotification({
          title: 'Unread 1',
          description: 'Test',
          type: 'info',
        });
        result.current.addNotification({
          title: 'Unread 2',
          description: 'Test',
          type: 'info',
        });
      });

      expect(result.current.getUnreadCount()).toBe(2);

      act(() => {
        result.current.markAsRead(result.current.notifications[0].id);
      });

      expect(result.current.getUnreadCount()).toBe(1);
    });
  });

  describe('selectors', () => {
    it('selectNotifications returns all notifications', () => {
      const state = useNotificationStore.getState();
      const notifications = selectNotifications(state);
      expect(Array.isArray(notifications)).toBe(true);
    });

    it('selectUnreadCount returns unread count', () => {
      // Clear and set controlled state
      act(() => {
        useNotificationStore.getState().clearAll();
        useNotificationStore.getState().addNotification({
          title: 'Test',
          description: 'Test',
          type: 'info',
        });
      });

      const count = selectUnreadCount(useNotificationStore.getState());
      expect(count).toBe(1);
    });
  });
});
