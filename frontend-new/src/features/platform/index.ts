/**
 * Platform Feature Module
 *
 * Central feature for platform-level functionality:
 * - Settings (profile, preferences, notifications)
 * - Activity log
 * - Audit logs
 * - Help center
 * - Developer tools (test bench)
 * - Projects (workspace organization)
 * - Upload wizard (dataset ingestion)
 */

// ============================================
// Page Exports
// ============================================

export { default as SettingsPage } from './pages/settings/SettingsPage';
export { default as NotificationsPage } from './pages/NotificationsPage';
export { default as ActivityLogPage } from './pages/ActivityLogPage';
export { default as AuditLogsPage } from './pages/AuditLogsPage';
export { default as HelpCenterPage } from './pages/HelpCenterPage';
export { default as TestBenchPage } from './pages/TestBenchPage';
export { default as ProcessQuestionsPage } from './pages/ProcessQuestionsPage';

// ============================================
// Sub-feature Re-exports
// ============================================

export * from './projects';
export * from './upload-wizard';
