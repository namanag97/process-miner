/**
 * Projects Feature Types
 *
 * Type definitions for projects and related entities.
 */

// ============================================
// Core Entity Types
// ============================================

/**
 * Project entity (list view)
 */
export interface Project {
  id: string;
  name: string;
  description?: string;
  totalFiles: number;
  createdAt: string;
  updatedAt: string;
}

/**
 * Project entity with event logs (detail view)
 */
export interface ProjectDetail extends Project {
  eventLogs: EventLogSummary[];
}

/**
 * Event log summary within a project
 */
export interface EventLogSummary {
  id: string;
  name: string;
  totalCases: number;
  totalEvents: number;
  createdAt: string;
}

/**
 * Data source representation for UI
 */
export interface DataSourceInfo {
  id: string;
  name: string;
  type: 'csv' | 'xes';
  caseCount: number;
  eventCount: number;
  uploadedAt: string;
  status: 'processing' | 'ready' | 'error';
}

// ============================================
// Input Types (mutations)
// ============================================

/**
 * Input for creating a new project
 */
export interface CreateProjectInput {
  name: string;
  description?: string;
}

/**
 * Input for updating a project
 */
export interface UpdateProjectInput {
  name?: string;
  description?: string;
}

// ============================================
// Query Options
// ============================================

/**
 * Options for listing projects
 */
export interface ProjectListOptions {
  page?: number;
  pageSize?: number;
  search?: string;
  sortBy?: keyof Project;
  sortOrder?: 'asc' | 'desc';
}

/**
 * Paginated response for project list
 */
export interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  pageSize: number;
}

// ============================================
// Utility Functions
// ============================================

/**
 * Transform event logs to data source info format
 */
export function toDataSources(logs: EventLogSummary[]): DataSourceInfo[] {
  return logs.map((log) => ({
    id: log.id,
    name: log.name,
    type: log.name.endsWith('.xes') ? 'xes' as const : 'csv' as const,
    caseCount: log.totalCases,
    eventCount: log.totalEvents,
    uploadedAt: log.createdAt,
    status: 'ready' as const,
  }));
}
