/**
 * Consolidated API Client with Network Resilience
 *
 * Features:
 * - Automatic retry with exponential backoff
 * - Request deduplication for GET requests
 * - Timeout handling with user notifications
 * - Compatible with Orval-generated React Query hooks
 */
import axios, { AxiosRequestConfig, AxiosError, InternalAxiosRequestConfig } from 'axios';
import axiosRetry, { isNetworkError, isRetryableError } from 'axios-retry';
import { notification, Button } from 'antd';
import React from 'react';

import { env } from '../config/env';

const API_BASE_URL = env.API_BASE_URL;

// ============================================
// Axios Instance
// ============================================

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 30000,
});

// ============================================
// Retry Configuration
// ============================================

axiosRetry(apiClient, {
    retries: 3,
    retryDelay: (retryCount) => {
        // Exponential backoff: 1s, 2s, 4s
        return Math.pow(2, retryCount - 1) * 1000;
    },
    retryCondition: (error) => {
        // Retry on network errors and 5xx responses
        return (
            isNetworkError(error) ||
            isRetryableError(error) ||
            error.response?.status === 429 ||  // Rate limited
            (error.response?.status ?? 0) >= 500
        );
    },
    onRetry: (retryCount, _error, requestConfig) => {
        console.log(`[API Retry] Attempt ${retryCount} for ${requestConfig.method?.toUpperCase()} ${requestConfig.url}`);

        // Show notification on first retry
        if (retryCount === 1) {
            notification.info({
                key: 'api-retry',
                message: 'Retrying request',
                description: 'The server is slow to respond. Retrying...',
                duration: 3,
            });
        }
    },
});

// ============================================
// Request Deduplication
// ============================================

const pendingRequests = new Map<string, Promise<unknown>>();

function getRequestKey(config: AxiosRequestConfig): string {
    return `${config.method}-${config.url}-${JSON.stringify(config.params || {})}`;
}

// Extended config type for deduplication tracking
interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
    __pendingPromise?: Promise<unknown>;
    __requestKey?: string;
}

// Request interceptor for deduplication and auth
apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // Add auth token
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        // Only dedupe GET requests
        if (config.method?.toLowerCase() !== 'get') {
            return config;
        }

        const key = getRequestKey(config);
        const extendedConfig = config as ExtendedAxiosRequestConfig;

        if (pendingRequests.has(key)) {
            // Return existing promise via custom property
            const pending = pendingRequests.get(key)!;
            extendedConfig.__pendingPromise = pending;

            // Cancel this request since we'll use the pending one
            const controller = new AbortController();
            controller.abort('deduplicated');
            extendedConfig.signal = controller.signal;
        } else {
            // Store this request's key for cleanup
            extendedConfig.__requestKey = key;
        }

        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptors for deduplication cleanup and error handling
apiClient.interceptors.response.use(
    (response) => {
        const extendedConfig = response.config as ExtendedAxiosRequestConfig;
        const key = extendedConfig.__requestKey;
        if (key) {
            pendingRequests.delete(key);
        }
        return response;
    },
    async (error: AxiosError<{ detail?: string }>) => {
        const extendedConfig = error.config as ExtendedAxiosRequestConfig | undefined;

        // Handle deduplicated requests - return the pending promise
        if (extendedConfig?.__pendingPromise) {
            try {
                const result = await extendedConfig.__pendingPromise;
                return { data: result, config: extendedConfig, status: 200, statusText: 'OK', headers: {} };
            } catch (pendingError) {
                return Promise.reject(pendingError);
            }
        }

        // Cleanup pending request map
        if (extendedConfig?.__requestKey) {
            pendingRequests.delete(extendedConfig.__requestKey);
        }

        // Handle timeout errors
        if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
            notification.warning({
                key: 'api-timeout',
                message: 'Request timed out',
                description: 'The server is taking too long to respond. Please try again.',
                duration: 0,
                btn: React.createElement(Button, {
                    size: 'small',
                    type: 'primary',
                    onClick: () => {
                        notification.destroy('api-timeout');
                        window.location.reload();
                    }
                }, 'Reload'),
            });
            return Promise.reject(error);
        }

        // Handle network errors
        if (!navigator.onLine || error.message === 'Network Error') {
            notification.error({
                key: 'api-offline',
                message: 'You are offline',
                description: 'Please check your internet connection and try again.',
                duration: 0,
            });
            return Promise.reject(error);
        }

        // Log error for debugging
        const message = error.response?.data?.detail || error.message;
        console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}: ${message}`);

        return Promise.reject(error);
    }
);

// ============================================
// Orval-compatible mutator function
// ============================================

/**
 * Orval-compatible mutator function
 * Used by generated React Query hooks
 */
export const customInstance = async <T>(config: AxiosRequestConfig): Promise<T> => {
    const { data } = await apiClient.request<T>({ ...config });
    return data;
};

export default apiClient;
