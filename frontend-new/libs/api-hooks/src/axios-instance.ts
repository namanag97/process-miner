/**
 * Custom Axios instance for Orval-generated React Query hooks.
 * 
 * This allows central configuration of:
 * - Base URL from environment
 * - Authentication headers
 * - Error handling
 * - Request/response interceptors
 */

import Axios, { AxiosError, AxiosRequestConfig } from 'axios';

// Get base URL from environment or use default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const axiosInstance = Axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for auth
axiosInstance.interceptors.request.use(
    (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
axiosInstance.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        // Handle 401 - redirect to login
        if (error.response?.status === 401) {
            localStorage.removeItem('auth_token');
            // Could dispatch to auth context or redirect here
        }
        return Promise.reject(error);
    }
);

/**
 * Custom instance function for Orval.
 * 
 * Orval uses this as a mutator to wrap all generated API calls.
 */
export const customInstance = <T>(config: AxiosRequestConfig): Promise<T> => {
    const source = Axios.CancelToken.source();

    const promise = axiosInstance({
        ...config,
        cancelToken: source.token,
    }).then(({ data }) => data);

    // @ts-expect-error - Adding cancel function for React Query
    promise.cancel = () => {
        source.cancel('Query was cancelled');
    };

    return promise;
};

export default customInstance;
