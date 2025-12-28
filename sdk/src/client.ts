/**
 * Base HTTP Client for Process Mining SDK
 * Handles authentication, error normalization, and request/response processing
 */

import { ApiError, ProblemDetails, SdkConfig, AuthState } from './types/common.js';

export class HttpClient {
  private baseUrl: string;
  private apiPrefix: string;
  private timeout: number;
  private authState: AuthState = {
    accessToken: null,
    tokenType: 'bearer',
    isAuthenticated: false,
  };
  private onAuthError?: () => void;

  constructor(config: SdkConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, '');
    this.apiPrefix = config.apiPrefix ?? '/api/v1';
    this.timeout = config.timeout ?? 30000;
    this.onAuthError = config.onAuthError;
  }

  /**
   * Set authentication token after successful login
   */
  setAuth(token: string, tokenType = 'bearer'): void {
    this.authState = {
      accessToken: token,
      tokenType,
      isAuthenticated: true,
    };
  }

  /**
   * Clear authentication state
   */
  clearAuth(): void {
    this.authState = {
      accessToken: null,
      tokenType: 'bearer',
      isAuthenticated: false,
    };
  }

  /**
   * Check if client is authenticated
   */
  isAuthenticated(): boolean {
    return this.authState.isAuthenticated;
  }

  /**
   * Build full URL for API endpoint
   */
  private buildUrl(path: string): string {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${this.baseUrl}${this.apiPrefix}${normalizedPath}`;
  }

  /**
   * Build request headers
   */
  private buildHeaders(contentType?: string): HeadersInit {
    const headers: Record<string, string> = {};

    if (this.authState.accessToken) {
      headers['Authorization'] = `${this.authState.tokenType} ${this.authState.accessToken}`;
    }

    if (contentType) {
      headers['Content-Type'] = contentType;
    }

    return headers;
  }

  /**
   * Process response and handle errors
   */
  private async processResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      // Handle 401 Unauthorized
      if (response.status === 401) {
        this.clearAuth();
        this.onAuthError?.();
      }

      // Try to parse RFC 7807 Problem Details
      let problem: ProblemDetails;
      try {
        problem = await response.json();
      } catch {
        problem = {
          type: 'about:blank',
          title: response.statusText || 'Request Failed',
          status: response.status,
        };
      }

      throw new ApiError(response.status, problem);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    // Check content type
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      return response.json();
    }

    // Return text for other content types (e.g., SVG)
    return response.text() as Promise<T>;
  }

  /**
   * Make GET request
   */
  async get<T>(path: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
    const url = new URL(this.buildUrl(path));
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: this.buildHeaders(),
      signal: AbortSignal.timeout(this.timeout),
    });

    return this.processResponse<T>(response);
  }

  /**
   * Make POST request with JSON body
   */
  async post<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(this.buildUrl(path), {
      method: 'POST',
      headers: this.buildHeaders('application/json'),
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(this.timeout),
    });

    return this.processResponse<T>(response);
  }

  /**
   * Make POST request with FormData (for file uploads)
   */
  async postForm<T>(path: string, formData: FormData): Promise<T> {
    const response = await fetch(this.buildUrl(path), {
      method: 'POST',
      headers: this.buildHeaders(), // No Content-Type - browser sets it with boundary
      body: formData,
      signal: AbortSignal.timeout(this.timeout),
    });

    return this.processResponse<T>(response);
  }

  /**
   * Make PATCH request
   */
  async patch<T>(path: string, body: unknown): Promise<T> {
    const response = await fetch(this.buildUrl(path), {
      method: 'PATCH',
      headers: this.buildHeaders('application/json'),
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(this.timeout),
    });

    return this.processResponse<T>(response);
  }

  /**
   * Make DELETE request
   */
  async delete<T>(path: string): Promise<T> {
    const response = await fetch(this.buildUrl(path), {
      method: 'DELETE',
      headers: this.buildHeaders(),
      signal: AbortSignal.timeout(this.timeout),
    });

    return this.processResponse<T>(response);
  }
}
