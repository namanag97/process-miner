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
  description: string | null;
  totalFiles: number;
  createdAt: string;
  updatedAt: string | null;
  tags?: string[];
  totalAnalyses?: number;
}

/**
 * Project entity with datasets (detail view)
 */
export interface ProjectDetail extends Project {
  datasets: DatasetSummary[];
}

/**
 * Dataset status for lifecycle tracking
 */
export type DatasetStatus = 'unstructured' | 'analyzing' | 'ready' | 'error';

/**
 * Dataset summary within a project
 */
export interface DatasetSummary {
  id: string;
  name: string;
  sourceFormat: string;
  totalEvents: number;
  totalCases: number;
  totalActivities: number;
  activities: string[];
  createdAt: string;
  sourceFile: string | null;
  status?: DatasetStatus;
  errorMessage?: string;
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
  status: DatasetStatus;
  errorMessage?: string;
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
  pages: number;
}

// ============================================
// Utility Functions
// ============================================

/**
 * Transform datasets to data source info format
 */
export function toDataSources(datasets: DatasetSummary[]): DataSourceInfo[] {
  return datasets.map((dataset) => ({
    id: dataset.id,
    name: dataset.name,
    type: dataset.name.endsWith('.xes') ? 'xes' as const : 'csv' as const,
    caseCount: dataset.totalCases,
    eventCount: dataset.totalEvents,
    uploadedAt: dataset.createdAt,
    status: dataset.status || 'ready',
    errorMessage: dataset.errorMessage,
  }));
}
