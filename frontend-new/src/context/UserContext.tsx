import React, { createContext, useContext, useMemo, useState, useCallback } from 'react';

/**
 * UserContext - MVP user context stub (no authentication required)
 *
 * Provides a default user context without authentication gates.
 * When auth is needed in the future, swap this for a full AuthContext implementation.
 *
 * Key differences from AuthContext:
 * - Always authenticated (isAuthenticated: true)
 * - No login/logout flows
 * - No loading state
 * - User preferences stored locally
 */

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
  // Compatibility with old AuthContext (no-ops or stubs)
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  getToken: () => string;
}

const STORAGE_KEY = 'lumina_user_prefs';
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

  const [user, setUser] = useState<User>(() => ({
    ...DEFAULT_USER,
    preferences: { ...DEFAULT_USER.preferences, ...loadPreferences() },
  }));

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
    login,
    logout,
    getToken,
  }), [user, updateUser, updatePreferences, login, logout, getToken]);

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
 * Alias for useUser - for backward compatibility with AuthContext
 * @deprecated Use useUser instead
 */
export const useAuth = useUser;

export type { UserContextType, UserPreferences };
