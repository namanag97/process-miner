/**
 * {{FEATURE_NAME_PASCAL}} Feature Module
 *
 * Self-contained feature module following the standard feature architecture.
 * Copy this template to create new features.
 *
 * Structure:
 * - index.ts        - Public exports and feature registration
 * - types.ts        - Feature-specific TypeScript types
 * - routes.tsx      - Feature route configuration
 * - hooks/          - Data fetching hooks (queries, mutations)
 * - components/     - Feature UI components
 * - pages/          - Page components for routes
 * - utils/          - Feature-specific utilities (optional)
 */

// ============================================
// Feature Configuration
// ============================================

export const FEATURE_ID = '{{FEATURE_NAME}}';

export const FEATURE_CONFIG = {
  id: '{{FEATURE_NAME}}',
  name: '{{FEATURE_NAME_PASCAL}}',
  version: '1.0.0',
  icon: 'AppstoreOutlined', // Ant Design icon name
  navPath: '/{{FEATURE_NAME}}',
  navOrder: 10,
};

// ============================================
// Page Exports (for lazy loading)
// ============================================

export { {{FEATURE_NAME_PASCAL}}ListPage } from './pages/{{FEATURE_NAME_PASCAL}}ListPage';
export { {{FEATURE_NAME_PASCAL}}DetailPage } from './pages/{{FEATURE_NAME_PASCAL}}DetailPage';

// ============================================
// Route Exports
// ============================================

export { {{FEATURE_NAME}}Routes } from './routes';

// ============================================
// Hook Exports (for cross-feature use)
// ============================================

export {
  use{{FEATURE_NAME_PASCAL}}List,
  use{{FEATURE_NAME_PASCAL}}Detail,
  useCreate{{FEATURE_NAME_PASCAL}},
  useUpdate{{FEATURE_NAME_PASCAL}},
  useDelete{{FEATURE_NAME_PASCAL}},
} from './hooks';

// ============================================
// Type Exports
// ============================================

export type {
  {{FEATURE_NAME_PASCAL}},
  {{FEATURE_NAME_PASCAL}}Detail,
  {{FEATURE_NAME_PASCAL}}CreateInput,
  {{FEATURE_NAME_PASCAL}}UpdateInput,
  {{FEATURE_NAME_PASCAL}}ListOptions,
} from './types';
