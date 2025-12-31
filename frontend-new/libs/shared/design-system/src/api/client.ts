/**
 * API Client - Base HTTP client for backend communication
 * Handles auth headers, error parsing, request/response logging, and retry logic
 */

import { logRequest, logResponse, logError } from '../utils/devLogger';

export interface ApiClientConfig {
  baseUrl: string;
  getAuthToken?: () => string | null;
  maxRetries?: number;
  retryDelay?: number;
}

const DEFAULT_MAX_RETRIES = 3;
const DEFAULT_RETRY_DELAY = 1000; // ms

/**
 * RFC 7807 Problem Details error format
 */
export class APIError extends Error {
  constructor(
    public status: number,
    public title: string,
    public detail: string,
    public instance?: string
  ) {
    super(detail);
    this.name = 'APIError';
  }

  static fromResponse(data: unknown, status: number): APIError {
    if (typeof data === 'object' && data !== null) {
      const err = data as Record<string, unknown>;
      return new APIError(
        status,
        String(err.title || 'Error'),
        String(err.detail || 'An error occurred'),
        err.instance ? String(err.instance) : undefined
      );
    }
    return new APIError(status, 'Error', 'An error occurred');
  }
}

export class ApiClient {
  private baseUrl: string;
  private getAuthToken?: () => string | null;
  private maxRetries: number;
  private retryDelay: number;
  private isBackendHealthy = true;

  constructor(config: ApiClientConfig) {
    // Remove trailing slash and ensure /api/v1 suffix
    this.baseUrl = config.baseUrl.replace(/\/$/, '');
    if (!this.baseUrl.endsWith('/api/v1')) {
      this.baseUrl = `${this.baseUrl}/api/v1`;
    }
    this.getAuthToken = config.getAuthToken;
    this.maxRetries = config.maxRetries ?? DEFAULT_MAX_RETRIES;
    this.retryDelay = config.retryDelay ?? DEFAULT_RETRY_DELAY;
  }

  /**
   * Check if backend is reachable
   */
  async checkHealth(): Promise<boolean> {
    try {
      const healthUrl = this.baseUrl.replace('/api/v1', '/health');
      const response = await fetch(healthUrl, { method: 'GET' });
      this.isBackendHealthy = response.ok;
      return response.ok;
    } catch {
      this.isBackendHealthy = false;
      return false;
    }
  }

  /**
   * Get backend health status
   */
  getHealthStatus(): boolean {
    return this.isBackendHealthy;
  }

  /**
   * Sleep for retry delay with exponential backoff
   */
  private async sleep(attempt: number): Promise<void> {
    const delay = this.retryDelay * Math.pow(2, attempt);
    return new Promise((resolve) => setTimeout(resolve, delay));
  }

  /**
   * Determine if error is retryable (network errors, 5xx)
   */
  private isRetryable(error: unknown): boolean {
    if (error instanceof APIError) {
      return error.status >= 500 && error.status < 600;
    }
    // Network errors are retryable
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return true;
    }
    return false;
  }

  private getHeaders(contentType?: string): HeadersInit {
    const headers: Record<string, string> = {};
    
    if (contentType) {
      headers['Content-Type'] = contentType;
    }

    const token = this.getAuthToken?.();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw APIError.fromResponse(errorData, response.status);
    }
    return response.json();
  }

  async get<T>(path: string, params?: Record<string, unknown>): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.set(key, String(value));
        }
      });
    }

    // Log request (skip dev log endpoint to avoid recursion)
    if (!path.startsWith('/dev/')) {
      logRequest('GET', path, params);
    }
    const start = performance.now();
    const maxRetryTime = 30000; // 30 seconds max
    const retryStart = performance.now();

    let lastError: Error | APIError | undefined;
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const response = await fetch(url.toString(), {
          method: 'GET',
          headers: this.getHeaders('application/json'),
        });

        const result = await this.handleResponse<T>(response);
        this.isBackendHealthy = true;

        if (!path.startsWith('/dev/')) {
          logResponse('GET', path, response.status, performance.now() - start);
          if (attempt > 0) {
            console.info(`[API] Request succeeded after ${attempt} retries`);
          }
        }
        return result;
      } catch (error) {
        lastError = error as Error | APIError;
        this.isBackendHealthy = false;

        // Check timeout
        if (performance.now() - retryStart > maxRetryTime) {
          console.error(`[API] Max retry time exceeded for ${path}`);
          break;
        }

        // Only retry if retryable and not last attempt
        if (attempt < this.maxRetries && this.isRetryable(error)) {
          const delay = this.retryDelay * Math.pow(2, attempt);
          console.warn(`[API] Retrying ${path} (attempt ${attempt + 1}/${this.maxRetries}) after ${delay}ms`);
          await this.sleep(attempt);
          continue;
        }

        if (!path.startsWith('/dev/')) {
          logError(`GET ${path}`, error);
        }

        // Improve error message for network failures
        if (error instanceof TypeError && error.message === 'Failed to fetch') {
          throw new APIError(
            0,
            'Connection Failed',
            'Unable to reach the backend server. Please ensure it is running on http://localhost:8001'
          );
        }
        throw error;
      }
    }

    if (!lastError) {
      lastError = new APIError(0, 'Unknown Error', 'Request failed without error details');
    }
    throw lastError;
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    if (!path.startsWith('/dev/')) {
      logRequest('POST', path, body);
    }
    const start = performance.now();
    const maxRetryTime = 30000; // 30 seconds max
    const retryStart = performance.now();

    let lastError: Error | APIError | undefined;
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const response = await fetch(`${this.baseUrl}${path}`, {
          method: 'POST',
          headers: this.getHeaders('application/json'),
          body: body ? JSON.stringify(body) : undefined,
        });

        const result = await this.handleResponse<T>(response);
        this.isBackendHealthy = true;

        if (!path.startsWith('/dev/')) {
          logResponse('POST', path, response.status, performance.now() - start);
          if (attempt > 0) {
            console.info(`[API] Request succeeded after ${attempt} retries`);
          }
        }
        return result;
      } catch (error) {
        lastError = error as Error | APIError;
        this.isBackendHealthy = false;

        // Check timeout
        if (performance.now() - retryStart > maxRetryTime) {
          console.error(`[API] Max retry time exceeded for ${path}`);
          break;
        }

        if (attempt < this.maxRetries && this.isRetryable(error)) {
          const delay = this.retryDelay * Math.pow(2, attempt);
          console.warn(`[API] Retrying ${path} (attempt ${attempt + 1}/${this.maxRetries}) after ${delay}ms`);
          await this.sleep(attempt);
          continue;
        }

        if (!path.startsWith('/dev/')) {
          logError(`POST ${path}`, error);
        }

        if (error instanceof TypeError && error.message === 'Failed to fetch') {
          throw new APIError(
            0,
            'Connection Failed',
            'Unable to reach the backend server. Please ensure it is running on http://localhost:8001'
          );
        }
        throw error;
      }
    }

    if (!lastError) {
      lastError = new APIError(0, 'Unknown Error', 'Request failed without error details');
    }
    throw lastError;
  }

  async postForm<T>(path: string, formData: FormData): Promise<T> {
    if (!path.startsWith('/dev/')) {
      logRequest('POST-FORM', path, 'FormData');
    }
    const start = performance.now();

    // Don't set Content-Type for FormData - browser sets it with boundary
    const headers: Record<string, string> = {};
    const token = this.getAuthToken?.();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    let lastError: unknown;
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const response = await fetch(`${this.baseUrl}${path}`, {
          method: 'POST',
          headers,
          body: formData,
        });

        const result = await this.handleResponse<T>(response);
        this.isBackendHealthy = true;

        if (!path.startsWith('/dev/')) {
          logResponse('POST-FORM', path, response.status, performance.now() - start);
        }
        return result;
      } catch (error) {
        lastError = error;
        this.isBackendHealthy = false;

        if (attempt < this.maxRetries && this.isRetryable(error)) {
          await this.sleep(attempt);
          continue;
        }

        if (!path.startsWith('/dev/')) {
          logError(`POST-FORM ${path}`, error);
        }

        if (error instanceof TypeError && error.message === 'Failed to fetch') {
          throw new APIError(
            0,
            'Connection Failed',
            'Unable to reach the backend server. Please ensure it is running on http://localhost:8001'
          );
        }
        throw error;
      }
    }
    throw lastError;
  }

  /**
   * POST with FormData and progress tracking using XMLHttpRequest
   */
  async postFormWithProgress<T>(
    path: string,
    formData: FormData,
    onProgress?: (percent: number) => void
  ): Promise<T> {
    if (!path.startsWith('/dev/')) {
      logRequest('POST-FORM-PROGRESS', path, 'FormData');
    }
    const start = performance.now();

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const url = `${this.baseUrl}${path}`;

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const percent = Math.round((event.loaded / event.total) * 100);
          onProgress(percent);
        }
      });

      xhr.addEventListener('load', () => {
        if (!path.startsWith('/dev/')) {
          logResponse('POST-FORM-PROGRESS', path, xhr.status, performance.now() - start);
        }

        if (xhr.status >= 200 && xhr.status < 300) {
          this.isBackendHealthy = true;
          try {
            const result = JSON.parse(xhr.responseText);
            resolve(result as T);
          } catch {
            reject(new APIError(xhr.status, 'Parse Error', 'Failed to parse response'));
          }
        } else {
          this.isBackendHealthy = false;
          try {
            const errorData = JSON.parse(xhr.responseText);
            reject(APIError.fromResponse(errorData, xhr.status));
          } catch {
            reject(new APIError(xhr.status, 'Error', xhr.statusText || 'Upload failed'));
          }
        }
      });

      xhr.addEventListener('error', () => {
        this.isBackendHealthy = false;
        if (!path.startsWith('/dev/')) {
          logError(`POST-FORM-PROGRESS ${path}`, 'Network error');
        }
        reject(new APIError(0, 'Connection Failed', 'Unable to reach the backend server. Please ensure it is running on http://localhost:8001'));
      });

      xhr.addEventListener('abort', () => {
        reject(new APIError(0, 'Aborted', 'Upload was cancelled'));
      });

      xhr.open('POST', url);
      
      const token = this.getAuthToken?.();
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }

      xhr.send(formData);
    });
  }

  async delete<T = void>(path: string): Promise<T> {
    if (!path.startsWith('/dev/')) {
      logRequest('DELETE', path);
    }
    const start = performance.now();

    let lastError: unknown;
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const response = await fetch(`${this.baseUrl}${path}`, {
          method: 'DELETE',
          headers: this.getHeaders('application/json'),
        });

        const result = await this.handleResponse<T>(response);
        this.isBackendHealthy = true;

        if (!path.startsWith('/dev/')) {
          logResponse('DELETE', path, response.status, performance.now() - start);
        }
        return result;
      } catch (error) {
        lastError = error;
        this.isBackendHealthy = false;

        if (attempt < this.maxRetries && this.isRetryable(error)) {
          await this.sleep(attempt);
          continue;
        }

        if (!path.startsWith('/dev/')) {
          logError(`DELETE ${path}`, error);
        }

        if (error instanceof TypeError && error.message === 'Failed to fetch') {
          throw new APIError(
            0,
            'Connection Failed',
            'Unable to reach the backend server. Please ensure it is running on http://localhost:8001'
          );
        }
        throw error;
      }
    }
    throw lastError;
  }
}

