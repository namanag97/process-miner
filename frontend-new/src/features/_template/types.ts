/**
 * {{FEATURE_NAME_PASCAL}} Feature Types
 *
 * Define all TypeScript types for this feature.
 * Keep types co-located with the feature for better maintainability.
 */

// ============================================
// Core Entity Types
// ============================================

/**
 * Base {{FEATURE_NAME_PASCAL}} entity (list view)
 */
export interface {{FEATURE_NAME_PASCAL}} {
  id: string;
  name: string;
  description?: string;
  status: {{FEATURE_NAME_PASCAL}}Status;
  createdAt: string;
  updatedAt: string;
}

/**
 * Detailed {{FEATURE_NAME_PASCAL}} entity (detail view)
 */
export interface {{FEATURE_NAME_PASCAL}}Detail extends {{FEATURE_NAME_PASCAL}} {
  // Add additional detail fields here
  metadata?: Record<string, unknown>;
}

/**
 * Status enum for {{FEATURE_NAME_PASCAL}}
 */
export type {{FEATURE_NAME_PASCAL}}Status = 'draft' | 'active' | 'archived';

// ============================================
// Input Types (for mutations)
// ============================================

/**
 * Input for creating a new {{FEATURE_NAME_PASCAL}}
 */
export interface {{FEATURE_NAME_PASCAL}}CreateInput {
  name: string;
  description?: string;
}

/**
 * Input for updating an existing {{FEATURE_NAME_PASCAL}}
 */
export interface {{FEATURE_NAME_PASCAL}}UpdateInput {
  name?: string;
  description?: string;
  status?: {{FEATURE_NAME_PASCAL}}Status;
}

// ============================================
// Query Options
// ============================================

/**
 * Options for listing {{FEATURE_NAME_PASCAL}}s
 */
export interface {{FEATURE_NAME_PASCAL}}ListOptions {
  page?: number;
  pageSize?: number;
  status?: {{FEATURE_NAME_PASCAL}}Status;
  search?: string;
  sortBy?: keyof {{FEATURE_NAME_PASCAL}};
  sortOrder?: 'asc' | 'desc';
}

/**
 * Paginated response for {{FEATURE_NAME_PASCAL}} list
 */
export interface {{FEATURE_NAME_PASCAL}}ListResponse {
  items: {{FEATURE_NAME_PASCAL}}[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}
