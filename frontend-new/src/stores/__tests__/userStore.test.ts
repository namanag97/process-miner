/**
 * User Store Tests
 */

import { act, renderHook } from '@testing-library/react';
import {
  useUserStore,
  selectUser,
  selectWorkspace,
  selectOrganization,
  selectPreferences,
} from '../userStore';

describe('userStore', () => {
  // Store has default MVP data, so we test against that

  describe('initial state', () => {
    it('should have default user', () => {
      const { result } = renderHook(() => useUserStore());

      expect(result.current.user).toBeTruthy();
      expect(result.current.user?.id).toBe('mvp-user-001');
      expect(result.current.user?.name).toBe('Process Analyst');
    });

    it('should have default organization', () => {
      const { result } = renderHook(() => useUserStore());

      expect(result.current.organization).toBeTruthy();
      expect(result.current.organization?.id).toBe('mvp-org-001');
    });

    it('should have default workspace', () => {
      const { result } = renderHook(() => useUserStore());

      expect(result.current.currentWorkspace).toBeTruthy();
      expect(result.current.currentWorkspace?.id).toBe('mvp-ws-001');
    });

    it('should be authenticated by default (MVP mode)', () => {
      const { result } = renderHook(() => useUserStore());
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('should have default preferences', () => {
      const { result } = renderHook(() => useUserStore());

      expect(result.current.preferences.theme).toBe('light');
      expect(result.current.preferences.notifications).toBe(true);
    });
  });

  describe('user actions', () => {
    it('updateUser should update user properties', () => {
      const { result } = renderHook(() => useUserStore());

      act(() => {
        result.current.updateUser({ name: 'New Name' });
      });

      expect(result.current.user?.name).toBe('New Name');
    });

    it('updateUser should preserve other properties', () => {
      const { result } = renderHook(() => useUserStore());
      const originalEmail = result.current.user?.email;

      act(() => {
        result.current.updateUser({ name: 'New Name' });
      });

      expect(result.current.user?.email).toBe(originalEmail);
    });

    it('setUser should replace entire user', () => {
      const { result } = renderHook(() => useUserStore());

      act(() => {
        result.current.setUser({
          id: 'new-user',
          name: 'New User',
          email: 'new@example.com',
          role: 'user',
        });
      });

      expect(result.current.user?.id).toBe('new-user');
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('setUser with null should set unauthenticated', () => {
      const { result } = renderHook(() => useUserStore());

      act(() => {
        result.current.setUser(null);
      });

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('workspace actions', () => {
    it('setCurrentWorkspace should update workspace', () => {
      const { result } = renderHook(() => useUserStore());

      act(() => {
        result.current.setCurrentWorkspace({
          id: 'new-ws',
          orgId: 'org-1',
          name: 'New Workspace',
          createdAt: new Date().toISOString(),
        });
      });

      expect(result.current.currentWorkspace?.id).toBe('new-ws');
    });

    it('addWorkspace should add to workspaces list', () => {
      const { result } = renderHook(() => useUserStore());
      const initialCount = result.current.workspaces.length;

      act(() => {
        result.current.addWorkspace({
          id: 'another-ws',
          orgId: 'org-1',
          name: 'Another Workspace',
          createdAt: new Date().toISOString(),
        });
      });

      expect(result.current.workspaces.length).toBe(initialCount + 1);
    });

    it('setWorkspaces should replace all workspaces', () => {
      const { result } = renderHook(() => useUserStore());

      act(() => {
        result.current.setWorkspaces([
          {
            id: 'ws-1',
            orgId: 'org-1',
            name: 'Workspace 1',
            createdAt: new Date().toISOString(),
          },
          {
            id: 'ws-2',
            orgId: 'org-1',
            name: 'Workspace 2',
            createdAt: new Date().toISOString(),
          },
        ]);
      });

      expect(result.current.workspaces.length).toBe(2);
      expect(result.current.workspaces[0].id).toBe('ws-1');
    });
  });

  describe('preferences actions', () => {
    it('updatePreferences should merge preferences', () => {
      const { result } = renderHook(() => useUserStore());

      act(() => {
        result.current.updatePreferences({ theme: 'dark' });
      });

      expect(result.current.preferences.theme).toBe('dark');
      expect(result.current.preferences.notifications).toBe(true);
    });

    it('resetPreferences should restore defaults', () => {
      const { result } = renderHook(() => useUserStore());

      act(() => {
        result.current.updatePreferences({ theme: 'dark', timezone: 'UTC' });
        result.current.resetPreferences();
      });

      expect(result.current.preferences.theme).toBe('light');
    });
  });

  describe('auth actions', () => {
    it('login should set user, token, and auth state', () => {
      const { result } = renderHook(() => useUserStore());

      act(() => {
        result.current.login(
          {
            id: 'user-123',
            name: 'Test User',
            email: 'test@example.com',
            role: 'admin',
          },
          'auth-token-xyz',
          {
            id: 'org-123',
            name: 'Test Org',
            slug: 'test-org',
            plan: 'pro',
          }
        );
      });

      expect(result.current.user?.id).toBe('user-123');
      expect(result.current.token).toBe('auth-token-xyz');
      expect(result.current.organization?.id).toBe('org-123');
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('logout should clear auth state', () => {
      const { result } = renderHook(() => useUserStore());

      act(() => {
        result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.currentWorkspace).toBeNull();
    });

    it('getToken should return current token', () => {
      const { result } = renderHook(() => useUserStore());

      act(() => {
        result.current.setToken('my-token');
      });

      expect(result.current.getToken()).toBe('my-token');
    });
  });

  describe('selectors', () => {
    it('selectUser returns user', () => {
      const state = useUserStore.getState();
      expect(selectUser(state)).toEqual(state.user);
    });

    it('selectWorkspace returns current workspace', () => {
      const state = useUserStore.getState();
      expect(selectWorkspace(state)).toEqual(state.currentWorkspace);
    });

    it('selectOrganization returns organization', () => {
      const state = useUserStore.getState();
      expect(selectOrganization(state)).toEqual(state.organization);
    });

    it('selectPreferences returns preferences', () => {
      const state = useUserStore.getState();
      expect(selectPreferences(state)).toEqual(state.preferences);
    });
  });
});
