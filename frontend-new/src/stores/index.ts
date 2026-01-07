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
