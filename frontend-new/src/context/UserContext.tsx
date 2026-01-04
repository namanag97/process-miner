import React, { createContext, useContext, useMemo, useState, useCallback } from 'react';

/**
 * UserContext - MVP user context with workspace support
 *
 * Provides a default user context without authentication gates.
 * Includes workspace context for enterprise multi-tenancy.
 *
 * Key features:
 * - Always authenticated (isAuthenticated: true)
 * - Workspace selection and context
 * - User preferences stored locally
 */

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
  preferences?: UserPreferences;
}

interface UserPreferences {
  theme?: 'light' | 'dark';
  timezone?: string;
  notifications?: boolean;
}

interface UserContextType {
  user: User;
  isAuthenticated: true; // Always true for MVP
  isLoading: false; // Never loading for MVP
  updateUser: (updates: Partial<Pick<User, 'name' | 'avatar'>>) => void;
  updatePreferences: (prefs: Partial<UserPreferences>) => void;
  // Workspace context
  organization: Organization | null;
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  setCurrentWorkspace: (workspace: Workspace | null) => void;
  // Compatibility with old AuthContext (no-ops or stubs)
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  getToken: () => string;
}

const STORAGE_KEY = 'lumina_user_prefs';
const WORKSPACE_KEY = 'lumina_current_workspace';
const DEFAULT_TOKEN = 'mvp_development_token';

const DEFAULT_USER: User = {
  id: 'mvp-user-001',
  name: 'Process Analyst',
  email: 'analyst@company.local',
  role: 'admin',
  preferences: {
    theme: 'light',
    notifications: true,
  },
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

const UserContext = createContext<UserContextType | null>(null);

export function UserProvider({ children }: { children: React.ReactNode }) {
  // Load saved preferences
  const loadPreferences = (): UserPreferences => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  };

  // Load saved workspace
  const loadCurrentWorkspace = (): Workspace | null => {
    try {
      const stored = localStorage.getItem(WORKSPACE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  };

  const [user, setUser] = useState<User>(() => ({
    ...DEFAULT_USER,
    preferences: { ...DEFAULT_USER.preferences, ...loadPreferences() },
  }));

  const [organization] = useState<Organization | null>(DEFAULT_ORG);
  const [workspaces] = useState<Workspace[]>([DEFAULT_WORKSPACE]);
  const [currentWorkspace, setCurrentWorkspaceState] = useState<Workspace | null>(() => {
    const saved = loadCurrentWorkspace();
    return saved || DEFAULT_WORKSPACE;
  });

  // Persist workspace selection
  const setCurrentWorkspace = useCallback((workspace: Workspace | null) => {
    setCurrentWorkspaceState(workspace);
    if (workspace) {
      localStorage.setItem(WORKSPACE_KEY, JSON.stringify(workspace));
    } else {
      localStorage.removeItem(WORKSPACE_KEY);
    }
  }, []);

  const updateUser = useCallback((updates: Partial<Pick<User, 'name' | 'avatar'>>) => {
    setUser(prev => ({ ...prev, ...updates }));
  }, []);

  const updatePreferences = useCallback((prefs: Partial<UserPreferences>) => {
    setUser(prev => {
      const newPrefs = { ...prev.preferences, ...prefs };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newPrefs));
      return { ...prev, preferences: newPrefs };
    });
  }, []);

  // Compatibility stubs for old AuthContext interface
  const login = useCallback(async (_email: string, _password: string) => {
    // No-op in MVP mode - already authenticated
    console.debug('[UserContext] login() called but auth is disabled in MVP mode');
  }, []);

  const logout = useCallback(() => {
    // No-op in MVP mode - can't log out
    console.debug('[UserContext] logout() called but auth is disabled in MVP mode');
  }, []);

  const getToken = useCallback(() => DEFAULT_TOKEN, []);

  const value = useMemo<UserContextType>(() => ({
    user,
    isAuthenticated: true,
    isLoading: false,
    updateUser,
    updatePreferences,
    organization,
    workspaces,
    currentWorkspace,
    setCurrentWorkspace,
    login,
    logout,
    getToken,
  }), [user, updateUser, updatePreferences, organization, workspaces, currentWorkspace, setCurrentWorkspace, login, logout, getToken]);

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}

/**
 * Hook to access user context
 * @throws Error if used outside UserProvider
 */
export function useUser(): UserContextType {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within UserProvider');
  }
  return context;
}

/**
 * Hook to access current workspace (convenience wrapper)
 */
export function useWorkspace(): {
  workspace: Workspace | null;
  workspaces: Workspace[];
  setWorkspace: (ws: Workspace | null) => void;
} {
  const { currentWorkspace, workspaces, setCurrentWorkspace } = useUser();
  return {
    workspace: currentWorkspace,
    workspaces,
    setWorkspace: setCurrentWorkspace,
  };
}

/**
 * Alias for useUser - for backward compatibility with AuthContext
 * @deprecated Use useUser instead
 */
export const useAuth = useUser;

export type { UserContextType, UserPreferences };
