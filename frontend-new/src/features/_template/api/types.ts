/**
 * Feature API Types
 *
 * Define all request/response types for this feature.
 * These types should match the OpenAPI schema from the backend.
 *
 * Prefer importing from @lumina/design-system or auto-generated
 * types when available.
 */

/**
 * Base feature item
 */
export interface FeatureItem {
  id: string;
  name: string;
  description: string | null;
  status: 'active' | 'inactive' | 'pending';
  createdAt: string; // ISO 8601 datetime
  updatedAt: string; // ISO 8601 datetime
  metadata?: Record<string, unknown>;
}

/**
 * Request to create a new feature item
 */
export interface CreateFeatureItemRequest {
  name: string;
  description?: string;
  status?: 'active' | 'inactive';
  metadata?: Record<string, unknown>;
}

/**
 * Request to update an existing feature item
 */
export interface UpdateFeatureItemRequest {
  name?: string;
  description?: string | null;
  status?: 'active' | 'inactive' | 'pending';
  metadata?: Record<string, unknown>;
}

/**
 * List response with pagination
 */
export interface FeatureListResponse {
  items: FeatureItem[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

/**
 * Detail response
 */
export interface FeatureDetailResponse {
  item: FeatureItem;
  relatedCount?: number;
}

/**
 * Filter options for list queries
 */
export interface FeatureFilters {
  status?: 'active' | 'inactive' | 'pending';
  search?: string;
  sortBy?: 'name' | 'createdAt' | 'updatedAt';
  sortOrder?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

/**
 * API Error response
 *
 * Standardized error format from backend
 */
export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, unknown>;
  timestamp: string;
}
