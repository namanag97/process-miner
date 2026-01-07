/**
 * Authentication Hooks
 * 
 * Higher-level hooks for authentication with token management.
 */

import { useCallback, useEffect, useState } from 'react';
import {
    useLoginApiV1AuthLoginPost,
    useRefreshTokenApiV1AuthRefreshPost,
    useGetCurrentUserInfoApiV1AuthMeGet,
    useLogoutApiV1AuthLogoutPost,
    LoginRequest,
    CurrentUserResponse,
} from '@/src/api/generated';

const ACCESS_TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'auth_refresh_token';

export interface AuthState {
    /** Current user if authenticated */
    user: CurrentUserResponse | null;
    /** Whether user is authenticated */
    isAuthenticated: boolean;
    /** Whether auth state is loading */
    isLoading: boolean;
    /** Login function */
    login: (credentials: LoginRequest) => Promise<void>;
    /** Logout function */
    logout: () => Promise<void>;
    /** Refresh token function */
    refreshToken: () => Promise<void>;
    /** Error if any */
    error: Error | null;
}

/**
 * Main authentication hook with token management.
 * 
 * @example
 * ```tsx
 * const { user, isAuthenticated, login, logout } = useAuth();
 * 
 * if (!isAuthenticated) {
 *   return <LoginForm onSubmit={login} />;
 * }
 * ```
 */
export function useAuth(): AuthState {
    const [error, setError] = useState<Error | null>(null);

    // Get current user
    const {
        data: user,
        isLoading: isUserLoading,
        refetch: refetchUser,
    } = useGetCurrentUserInfoApiV1AuthMeGet({
        query: {
            enabled: !!localStorage.getItem(ACCESS_TOKEN_KEY),
            retry: false,
        },
    });

    // Login mutation
    const loginMutation = useLoginApiV1AuthLoginPost();

    // Logout mutation
    const logoutMutation = useLogoutApiV1AuthLogoutPost();

    // Refresh mutation
    const refreshMutation = useRefreshTokenApiV1AuthRefreshPost();

    // Login handler
    const login = useCallback(async (credentials: LoginRequest) => {
        try {
            setError(null);
            const response = await loginMutation.mutateAsync({ data: credentials });

            // Store tokens
            if (response.access_token) {
                localStorage.setItem(ACCESS_TOKEN_KEY, response.access_token);
            }
            if (response.refresh_token) {
                localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
            }

            // Refetch user
            await refetchUser();
        } catch (err) {
            setError(err as Error);
            throw err;
        }
    }, [loginMutation, refetchUser]);

    // Logout handler
    const logout = useCallback(async () => {
        try {
            await logoutMutation.mutateAsync();
        } finally {
            // Clear tokens regardless of API success
            localStorage.removeItem(ACCESS_TOKEN_KEY);
            localStorage.removeItem(REFRESH_TOKEN_KEY);
        }
    }, [logoutMutation]);

    // Refresh handler
    const refreshToken = useCallback(async () => {
        try {
            const refreshTokenValue = localStorage.getItem(REFRESH_TOKEN_KEY);
            if (!refreshTokenValue) {
                throw new Error('No refresh token available');
            }

            const response = await refreshMutation.mutateAsync({
                data: { refresh_token: refreshTokenValue },
            });

            if (response.access_token) {
                localStorage.setItem(ACCESS_TOKEN_KEY, response.access_token);
            }
            if (response.refresh_token) {
                localStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
            }
        } catch (err) {
            // Refresh failed, clear tokens
            localStorage.removeItem(ACCESS_TOKEN_KEY);
            localStorage.removeItem(REFRESH_TOKEN_KEY);
            throw err;
        }
    }, [refreshMutation]);

    // Listen for 401 events from axios interceptor
    useEffect(() => {
        const handleLogout = () => {
            localStorage.removeItem(ACCESS_TOKEN_KEY);
            localStorage.removeItem(REFRESH_TOKEN_KEY);
        };

        window.addEventListener('auth:logout', handleLogout);
        return () => window.removeEventListener('auth:logout', handleLogout);
    }, []);

    const isAuthenticated = !!user && !!localStorage.getItem(ACCESS_TOKEN_KEY);

    return {
        user: user ?? null,
        isAuthenticated,
        isLoading: isUserLoading || loginMutation.isPending,
        login,
        logout,
        refreshToken,
        error,
    };
}

/**
 * Get only the current user (for components that don't need full auth).
 */
export function useCurrentUser() {
    const { data: user, isLoading } = useGetCurrentUserInfoApiV1AuthMeGet({
        query: {
            enabled: !!localStorage.getItem(ACCESS_TOKEN_KEY),
        },
    });

    return { user: user ?? null, isLoading };
}

export default useAuth;
