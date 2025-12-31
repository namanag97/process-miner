import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role?: 'admin' | 'user' | 'viewer';
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loginAsGuest: () => void;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

const STORAGE_KEY = 'lumina_auth_user';
const TOKEN_KEY = 'auth_token';

// Check if real authentication is enabled via environment variable
const USE_REAL_AUTH = import.meta.env.VITE_USE_REAL_AUTH === 'true';
const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8001/auth';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const initAuth = async () => {
      const stored = localStorage.getItem(STORAGE_KEY);
      const token = localStorage.getItem(TOKEN_KEY);

      if (stored) {
        try {
          const parsedUser = JSON.parse(stored);
          
          // If real auth is enabled and we have a token, validate it
          if (USE_REAL_AUTH && token) {
            try {
              const response = await fetch(`${AUTH_API_URL}/me`, {
                headers: {
                  'Authorization': `Bearer ${token}`,
                },
              });
              
              if (response.ok) {
                const userData = await response.json();
                setUser({
                  id: userData.id,
                  name: userData.name || userData.email?.split('@')[0],
                  email: userData.email,
                  avatar: userData.avatar,
                  role: userData.role,
                });
              } else {
                // Token is invalid, clear storage
                localStorage.removeItem(STORAGE_KEY);
                localStorage.removeItem(TOKEN_KEY);
              }
            } catch (error) {
              console.warn('Failed to validate auth token:', error);
              // Keep local user for offline support in dev mode
              if (!USE_REAL_AUTH) {
                setUser(parsedUser);
              }
            }
          } else {
            // Mock mode - use stored user directly
            setUser(parsedUser);
          }
        } catch (error) {
          console.warn('Failed to parse stored auth data:', error);
          localStorage.removeItem(STORAGE_KEY);
          localStorage.removeItem(TOKEN_KEY);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    if (USE_REAL_AUTH) {
      // Real authentication
      const response = await fetch(`${AUTH_API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Login failed' }));
        throw new Error(error.message || 'Invalid credentials');
      }

      const data = await response.json();
      const loggedInUser: User = {
        id: data.user.id,
        name: data.user.name || email.split('@')[0],
        email: data.user.email,
        avatar: data.user.avatar,
        role: data.user.role,
      };

      setUser(loggedInUser);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(loggedInUser));
      localStorage.setItem(TOKEN_KEY, data.access_token);
    } else {
      // Mock login - accepts any credentials
      const mockUser: User = {
        id: '1',
        name: email.split('@')[0],
        email,
        role: 'admin',
      };
      setUser(mockUser);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(mockUser));
      localStorage.setItem(TOKEN_KEY, 'mock_token_' + Date.now());
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(TOKEN_KEY);
    
    // If real auth is enabled, call logout endpoint
    if (USE_REAL_AUTH) {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        fetch(`${AUTH_API_URL}/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }).catch(() => {
          // Ignore logout errors
        });
      }
    }
  }, []);

  const loginAsGuest = useCallback(() => {
    const guestUser: User = {
      id: 'guest',
      name: 'Guest User',
      email: 'guest@example.com',
      role: 'viewer',
    };
    setUser(guestUser);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(guestUser));
    localStorage.setItem(TOKEN_KEY, 'guest_token');
  }, []);

  const getToken = useCallback(() => {
    return localStorage.getItem(TOKEN_KEY);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        loginAsGuest,
        getToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
