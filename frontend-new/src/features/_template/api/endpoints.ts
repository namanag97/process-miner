/**
 * Feature API Endpoints
 *
 * Centralize all API endpoint URLs for this feature.
 * Makes it easy to update base URLs or versioning.
 */

const API_BASE = '/api/v1';
const FEATURE_BASE = `${API_BASE}/features`;

/**
 * Feature API endpoints
 *
 * Use functions for parameterized endpoints to ensure type safety
 */
export const FEATURE_ENDPOINTS = {
  // List/search
  list: `${FEATURE_BASE}`,

  // CRUD operations
  create: `${FEATURE_BASE}`,
  detail: (id: string) => `${FEATURE_BASE}/${id}`,
  update: (id: string) => `${FEATURE_BASE}/${id}`,
  delete: (id: string) => `${FEATURE_BASE}/${id}`,

  // Related resources
  related: (id: string) => `${FEATURE_BASE}/${id}/related`,

  // Batch operations
  batchUpdate: `${FEATURE_BASE}/batch`,
  batchDelete: `${FEATURE_BASE}/batch`,

  // Actions
  activate: (id: string) => `${FEATURE_BASE}/${id}/activate`,
  deactivate: (id: string) => `${FEATURE_BASE}/${id}/deactivate`,

  // Statistics/aggregations
  stats: `${FEATURE_BASE}/stats`,
  summary: (id: string) => `${FEATURE_BASE}/${id}/summary`,
} as const;

/**
 * Example: External API endpoints
 *
 * If feature integrates with external services
 */
export const EXTERNAL_ENDPOINTS = {
  webhook: (id: string) => `${FEATURE_BASE}/${id}/webhook`,
  export: (id: string, format: 'csv' | 'json' | 'xlsx') =>
    `${FEATURE_BASE}/${id}/export?format=${format}`,
} as const;
