/**
 * Common types for Process Mining SDK
 * Following CodeOpinion guidance: business-focused types with available actions
 */

// =============================================================================
// API ERROR TYPES (RFC 7807 Problem Details)
// =============================================================================

export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
  [key: string]: unknown;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly problem: ProblemDetails,
    message?: string
  ) {
    super(message ?? problem.title);
    this.name = "ApiError";
  }
}

// =============================================================================
// HYPERMEDIA TYPES (Following CodeOpinion: Include available actions)
// =============================================================================

/**
 * Represents an available action on a resource.
 * Allows clients to discover what operations are currently permitted.
 */
export interface ResourceAction {
  name: string;
  href: string;
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  title?: string;
}

/**
 * Hypermedia links following HATEOAS principles.
 */
export interface HypermediaLinks {
  self?: { href: string };
  [key: string]: { href: string; title?: string } | undefined;
}

/**
 * Base response with hypermedia support.
 * All API responses can include links and available actions.
 */
export interface HypermediaResponse {
  _links?: HypermediaLinks;
  _actions?: ResourceAction[];
}

// =============================================================================
// PAGINATION TYPES
// =============================================================================

export interface PaginatedResponse<T> extends HypermediaResponse {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface PaginationOptions {
  page?: number;
  pageSize?: number;
}

// =============================================================================
// COMMON DOMAIN TYPES
// =============================================================================

export interface DateRange {
  start: string;
  end: string;
}

export interface Duration {
  seconds: number;
  formatted?: string;
}

// =============================================================================
// SDK CONFIGURATION
// =============================================================================

export interface SdkConfig {
  baseUrl: string;
  apiPrefix?: string;
  timeout?: number;
  onAuthError?: () => void;
}

export interface AuthState {
  accessToken: string | null;
  tokenType: string;
  isAuthenticated: boolean;
}
