import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'analyst' | 'admin' | 'viewer';
}

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const STORAGE_KEY = 'lumina_auth';

interface StoredAuth {
  user: User;
  token: string;
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const { user } = JSON.parse(stored) as StoredAuth;
        setUser(user);
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, _password: string) => {
    // Mock authentication - accepts any credentials
    // Use "admin" / any password for admin role
    setIsLoading(true);

    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 500));

    const username = email.includes('@') ? email.split('@')[0] : email;
    const role = username.toLowerCase() === 'admin' ? 'admin' : 'analyst';

    const mockUser: User = {
      id: crypto.randomUUID(),
      email: email.includes('@') ? email : `${email}@lumina.local`,
      name: username,
      role,
    };

    const authData: StoredAuth = {
      user: mockUser,
      token: `mock_token_${Date.now()}`,
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(authData));
    setUser(mockUser);
    setIsLoading(false);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
