/**
 * Consolidated API Client
 * 
 * Single axios instance for all API calls.
 * Compatible with Orval-generated React Query hooks.
 */
import axios, { AxiosRequestConfig, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json' },
    timeout: 30000,
});

// Request interceptor for auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError<{ detail?: string }>) => {
        const message = error.response?.data?.detail || error.message;
        console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}: ${message}`);
        return Promise.reject(error);
    }
);

/**
 * Orval-compatible mutator function
 * Used by generated React Query hooks
 */
export const customInstance = async <T>(config: AxiosRequestConfig): Promise<T> => {
    const { data } = await apiClient.request<T>({ ...config });
    return data;
};

export default apiClient;
