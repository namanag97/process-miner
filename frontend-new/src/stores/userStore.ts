/**
 * User Store
 *
 * Manages user profile, workspace selection, and preferences.
 * Replaces the UserContext with Zustand for better performance.
 * Persists user preferences to localStorage.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface Workspace {
  id: string;
  orgId: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'user' | 'viewer';
}

export interface UserPreferences {
  theme?: 'light' | 'dark';
  timezone?: string;
  notifications?: boolean;
  language?: string;
}

export interface UserState {
  // State
  user: User | null;
  organization: Organization | null;
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  preferences: UserPreferences;
  isAuthenticated: boolean;
  token: string | null;

  // Actions - User
  setUser: (user: User | null) => void;
  updateUser: (updates: Partial<Pick<User, 'name' | 'avatar'>>) => void;

  // Actions - Organization
  setOrganization: (org: Organization | null) => void;

  // Actions - Workspace
  setWorkspaces: (workspaces: Workspace[]) => void;
  setCurrentWorkspace: (workspace: Workspace | null) => void;
  addWorkspace: (workspace: Workspace) => void;

  // Actions - Preferences
  updatePreferences: (prefs: Partial<UserPreferences>) => void;
  resetPreferences: () => void;

  // Actions - Auth
  login: (user: User, token: string, org?: Organization) => void;
  logout: () => void;
  setToken: (token: string | null) => void;
  getToken: () => string | null;

  // Reset
  resetUser: () => void;
}

const DEFAULT_USER: User = {
  id: 'mvp-user-001',
  name: 'Process Analyst',
  email: 'analyst@company.local',
  role: 'admin',
};

const DEFAULT_ORG: Organization = {
  id: 'mvp-org-001',
  name: 'Demo Organization',
  slug: 'demo-org',
  plan: 'free',
};

const DEFAULT_WORKSPACE: Workspace = {
  id: 'mvp-ws-001',
  orgId: 'mvp-org-001',
  name: 'Default Workspace',
  description: 'Your default process mining workspace',
  createdAt: new Date().toISOString(),
};

const DEFAULT_TOKEN = 'mvp_development_token';

const defaultPreferences: UserPreferences = {
  theme: 'light',
  notifications: true,
};

const initialState = {
  user: DEFAULT_USER,
  organization: DEFAULT_ORG,
  workspaces: [DEFAULT_WORKSPACE],
  currentWorkspace: DEFAULT_WORKSPACE,
  preferences: defaultPreferences,
  isAuthenticated: true, // MVP mode - always authenticated
  token: DEFAULT_TOKEN,
};

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // User actions
        setUser: (user) =>
          set({ user, isAuthenticated: !!user }, false, 'user/setUser'),

        updateUser: (updates) =>
          set(
            (state) => ({
              user: state.user ? { ...state.user, ...updates } : null,
            }),
            false,
            'user/updateUser'
          ),

        // Organization actions
        setOrganization: (org) =>
          set({ organization: org }, false, 'user/setOrganization'),

        // Workspace actions
        setWorkspaces: (workspaces) =>
          set({ workspaces }, false, 'user/setWorkspaces'),

        setCurrentWorkspace: (workspace) =>
          set({ currentWorkspace: workspace }, false, 'user/setCurrentWorkspace'),

        addWorkspace: (workspace) =>
          set(
            (state) => ({ workspaces: [...state.workspaces, workspace] }),
            false,
            'user/addWorkspace'
          ),

        // Preferences actions
        updatePreferences: (prefs) =>
          set(
            (state) => ({
              preferences: { ...state.preferences, ...prefs },
            }),
            false,
            'user/updatePreferences'
          ),

        resetPreferences: () =>
          set({ preferences: defaultPreferences }, false, 'user/resetPreferences'),

        // Auth actions
        login: (user, token, org) =>
          set(
            {
              user,
              token,
              isAuthenticated: true,
              organization: org || null,
            },
            false,
            'user/login'
          ),

        logout: () =>
          set(
            {
              user: null,
              token: null,
              isAuthenticated: false,
              currentWorkspace: null,
            },
            false,
            'user/logout'
          ),

        setToken: (token) => set({ token }, false, 'user/setToken'),

        getToken: () => get().token,

        // Reset
        resetUser: () => set(initialState, false, 'user/reset'),
      }),
      {
        name: 'lumina-user-store',
        partialize: (state) => ({
          preferences: state.preferences,
          currentWorkspace: state.currentWorkspace,
          token: state.token,
        }),
      }
    ),
    { name: 'UserStore' }
  )
);

// Selectors
export const selectUser = (state: UserState) => state.user;
export const selectWorkspace = (state: UserState) => state.currentWorkspace;
export const selectWorkspaces = (state: UserState) => state.workspaces;
export const selectOrganization = (state: UserState) => state.organization;
export const selectPreferences = (state: UserState) => state.preferences;
export const selectIsAuthenticated = (state: UserState) => state.isAuthenticated;
export const selectTheme = (state: UserState) => state.preferences.theme ?? 'light';
