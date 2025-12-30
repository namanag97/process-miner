/**
 * API Client - Base HTTP client for backend communication
 * Handles auth headers, error parsing, and request/response logging
 */

import { logRequest, logResponse, logError } from '../utils/devLogger';

export interface ApiClientConfig {
  baseUrl: string;
  getAuthToken?: () => string | null;
}

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

  constructor(config: ApiClientConfig) {
    // Remove trailing slash and ensure /api/v1 suffix
    this.baseUrl = config.baseUrl.replace(/\/$/, '');
    if (!this.baseUrl.endsWith('/api/v1')) {
      this.baseUrl = `${this.baseUrl}/api/v1`;
    }
    this.getAuthToken = config.getAuthToken;
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

    try {
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: this.getHeaders('application/json'),
      });

      const result = await this.handleResponse<T>(response);
      
      if (!path.startsWith('/dev/')) {
        logResponse('GET', path, response.status, performance.now() - start);
      }
      return result;
    } catch (error) {
      if (!path.startsWith('/dev/')) {
        logError(`GET ${path}`, error);
      }
      throw error;
    }
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    if (!path.startsWith('/dev/')) {
      logRequest('POST', path, body);
    }
    const start = performance.now();

    try {
      const response = await fetch(`${this.baseUrl}${path}`, {
        method: 'POST',
        headers: this.getHeaders('application/json'),
        body: body ? JSON.stringify(body) : undefined,
      });

      const result = await this.handleResponse<T>(response);
      
      if (!path.startsWith('/dev/')) {
        logResponse('POST', path, response.status, performance.now() - start);
      }
      return result;
    } catch (error) {
      if (!path.startsWith('/dev/')) {
        logError(`POST ${path}`, error);
      }
      throw error;
    }
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

    try {
      const response = await fetch(`${this.baseUrl}${path}`, {
        method: 'POST',
        headers,
        body: formData,
      });

      const result = await this.handleResponse<T>(response);
      
      if (!path.startsWith('/dev/')) {
        logResponse('POST-FORM', path, response.status, performance.now() - start);
      }
      return result;
    } catch (error) {
      if (!path.startsWith('/dev/')) {
        logError(`POST-FORM ${path}`, error);
      }
      throw error;
    }
  }

  async delete<T = void>(path: string): Promise<T> {
    if (!path.startsWith('/dev/')) {
      logRequest('DELETE', path);
    }
    const start = performance.now();

    try {
      const response = await fetch(`${this.baseUrl}${path}`, {
        method: 'DELETE',
        headers: this.getHeaders('application/json'),
      });

      const result = await this.handleResponse<T>(response);
      
      if (!path.startsWith('/dev/')) {
        logResponse('DELETE', path, response.status, performance.now() - start);
      }
      return result;
    } catch (error) {
      if (!path.startsWith('/dev/')) {
        logError(`DELETE ${path}`, error);
      }
      throw error;
    }
  }
}

