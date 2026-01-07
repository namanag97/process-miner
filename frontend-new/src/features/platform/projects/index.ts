/**
 * Projects Feature Module
 *
 * Self-contained feature module for project management.
 * Provides pages, hooks, and components for managing projects.
 */

// ============================================
// Page Exports
// ============================================

export { ProjectsListPage } from './pages/ProjectsListPage';
export { ProjectDetailPage } from './pages/ProjectDetailPage';

// ============================================
// Hook Exports
// ============================================

export {
  useProjectList,
  useProjectDetail,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
  useRemoveFileFromProject,
} from './hooks';

// ============================================
// Component Exports
// ============================================

export { CreateProjectModal } from './components/CreateProjectModal';
export { DataSourcesList } from './components/DataSourcesList';
export { ProjectCard } from './components/ProjectCard';

// ============================================
// Type Exports
// ============================================

export type {
  Project,
  ProjectDetail,
  ProjectListOptions,
  ProjectListResponse,
  CreateProjectInput,
  UpdateProjectInput,
  DataSourceInfo,
  DatasetSummary,
} from './types';

export { toDataSources } from './types';
