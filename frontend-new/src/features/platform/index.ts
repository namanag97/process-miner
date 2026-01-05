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

import { FeatureRegistry } from '../../core/plugins/FeatureRegistry';
import { platformRouteConfig } from './routes';

// Import sub-features (projects, upload-wizard)
import './projects';
import './upload-wizard';

// ============================================
// Feature Configuration
// ============================================

export const FEATURE_ID = 'platform';

export const FEATURE_CONFIG = {
    id: 'platform',
    name: 'Platform',
    version: '1.0.0',
    icon: 'SettingOutlined',
    // No navPath - platform items are in bottom nav, handled separately
    navOrder: 100, // Low priority - bottom nav
};

// Register feature (auto-registration on import)
FeatureRegistry.register({
    ...FEATURE_CONFIG,
    routes: platformRouteConfig,
});

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
// Route Exports
// ============================================

export { platformRouteConfig } from './routes';
