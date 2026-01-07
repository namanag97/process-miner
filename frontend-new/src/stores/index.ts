/**
 * Zustand Stores Index
 *
 * Central export for all application state stores.
 * Uses Zustand for client-side state management.
 *
 * Architecture:
 * - filterStore: Process mining filters with URL sync
 * - selectionStore: Graph node/edge/variant selection
 * - uiStore: Panel/modal/layout state with persistence
 * - wizardStore: Multi-step upload wizard state
 * - userStore: User profile, workspace, preferences
 * - notificationStore: App notifications
 * - backendHealthStore: Backend health status
 */

// Filter state
export { useFilterStore, selectFilters, selectFilterCount, selectHasFilters } from './filterStore';
export type { FilterState } from './filterStore';

// Selection state
export {
  useSelectionStore,
  selectSelectedNode,
  selectSelectedEdge,
  selectSelectedVariant,
} from './selectionStore';
export type { SelectionState } from './selectionStore';

// UI state
export { useUIStore } from './uiStore';
export type { UIState, RightPanelTab } from './uiStore';

// Wizard state
export { useWizardStore } from './wizardStore';
export type { WizardState, WizardStep, ColumnMapping, DataPreview } from './wizardStore';

// User state
export { useUserStore, selectUser, selectWorkspace, selectOrganization } from './userStore';
export type { UserState, User, Workspace, Organization, UserPreferences } from './userStore';

// Notification state
export { useNotificationStore, selectNotifications, selectUnreadCount } from './notificationStore';
export type { NotificationState, AppNotification } from './notificationStore';

// Backend health state
export { useBackendHealthStore } from './backendHealthStore';
export type { BackendHealthState } from './backendHealthStore';

// Entity store (normalized cache)
export {
    useEntityStore,
    // Single entity selectors
    useDataset,
    useProject,
    useModel,
    useJob,
    // Multiple entity selectors
    useDatasetsById,
    useProjectsById,
    useModelsById,
    useJobsById,
    // All entities selectors
    useAllDatasets,
    useAllProjects,
    useAllModels,
    useAllJobs,
    // Relationship selectors
    useProjectDatasets,
    useDatasetModels,
    useEntityJobs,
    // Static selectors
    selectDataset,
    selectProject,
    selectModel,
    selectJob,
    selectAllDatasets,
    selectAllProjects,
    selectAllModels,
    selectAllJobs,
} from './entityStore';

export type {
    EntityState,
    NormalizedDataset,
    NormalizedProject,
    NormalizedModel,
    NormalizedJob,
    DatasetStatus,
    JobStatus,
} from './entityStore.types';

// Transformation utilities
export {
    transformDataset,
    transformProject,
    transformModel,
    transformJob,
} from './entityStore.types';
