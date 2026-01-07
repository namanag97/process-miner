/**
 * Projects Feature Types
 *
 * Type definitions for projects and related entities.
 * All types defined locally for frontend use.
 */

// ============================================
// Frontend Types (camelCase convention)
// ============================================

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

export type DatasetStatus = 'unstructured' | 'analyzing' | 'ready' | 'error';

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

export interface ProjectDetail extends Project {
  datasets: DatasetSummary[];
}

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

export interface CreateProjectInput {
  name: string;
  description?: string;
  workspaceId?: string;
}

export interface UpdateProjectInput {
  name?: string;
  description?: string;
}

// ============================================
// Query Options
// ============================================

export interface ProjectListOptions {
  page?: number;
  pageSize?: number;
  search?: string;
  sortBy?: keyof Project;
  sortOrder?: 'asc' | 'desc';
}

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

// ============================================
// SDK Compatibility Aliases
// ============================================

export type SDKProjectResponse = Project;
export type SDKProjectDetailResponse = ProjectDetail;
export type SDKProjectListResponse = ProjectListResponse;
export type SDKProjectCreateRequest = CreateProjectInput;
export type SDKProjectUpdateRequest = UpdateProjectInput;
export type SDKDatasetResponse = DatasetSummary;
export type SDKDatasetListResponse = { items: DatasetSummary[] };
