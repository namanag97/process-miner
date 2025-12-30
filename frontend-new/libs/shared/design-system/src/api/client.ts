/**
 * API Client - Base HTTP client for backend communication
 * Handles auth headers, error parsing, and request/response logging
 */

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

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: this.getHeaders('application/json'),
    });

    return this.handleResponse<T>(response);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: this.getHeaders('application/json'),
      body: body ? JSON.stringify(body) : undefined,
    });

    return this.handleResponse<T>(response);
  }

  async postForm<T>(path: string, formData: FormData): Promise<T> {
    // Don't set Content-Type for FormData - browser sets it with boundary
    const headers: Record<string, string> = {};
    const token = this.getAuthToken?.();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    return this.handleResponse<T>(response);
  }

  async delete<T = void>(path: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'DELETE',
      headers: this.getHeaders('application/json'),
    });

    return this.handleResponse<T>(response);
  }
}
