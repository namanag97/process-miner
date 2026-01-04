/**
 * Projects Feature Types
 *
 * Type definitions for projects and related entities.
 *
 * NOTE: SDK types are available at @frontend-new/openapi-sdk for API validation.
 * Frontend uses camelCase conventions while SDK uses snake_case from backend.
 */

// ============================================
// SDK Types for Reference/Validation
// ============================================

export type {
  ProjectResponse as SDKProjectResponse,
  ProjectDetailResponse as SDKProjectDetailResponse,
  ProjectListResponse as SDKProjectListResponse,
  ProjectCreateRequest as SDKProjectCreateRequest,
  ProjectUpdateRequest as SDKProjectUpdateRequest,
  DatasetResponse as SDKDatasetResponse,
  DatasetListResponse as SDKDatasetListResponse,
} from '@frontend-new/openapi-sdk';

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
