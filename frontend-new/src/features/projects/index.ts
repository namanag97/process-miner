/**
 * Projects Feature Module
 *
 * Self-contained feature module for project management.
 * Provides pages, hooks, and components for managing projects.
 */

import { FeatureRegistry } from '../../core/plugins/FeatureRegistry';
import { projectsRouteConfig } from './routes';

// ============================================
// Feature Configuration
// ============================================

export const FEATURE_ID = 'projects';

export const FEATURE_CONFIG = {
  id: 'projects',
  name: 'Projects',
  version: '1.0.0',
  icon: 'FolderOutlined',
  navPath: '/workspace',
  navOrder: 1,
};

// Register feature (auto-registration on import)
FeatureRegistry.register({
  ...FEATURE_CONFIG,
  routes: projectsRouteConfig,
});

// ============================================
// Page Exports
// ============================================

export { ProjectsListPage } from './pages/ProjectsListPage';
export { ProjectDetailPage } from './pages/ProjectDetailPage';

// ============================================
// Route Exports
// ============================================

export { ProjectsRoutes, projectsRouteConfig } from './routes';

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
  EventLogSummary,
} from './types';

export { toDataSources } from './types';
