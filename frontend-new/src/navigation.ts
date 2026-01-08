/**
 * Application Navigation
 *
 * Explicit navigation configuration for the entire application.
 * Used by the sidebar and any navigation components.
 */

// ============================================
// Types
// ============================================

export interface NavItem {
  key: string;
  label: string;
  path: string;
  icon: string; // Ant Design icon name
  order: number;
  children?: NavItem[];
}

// ============================================
// Main Navigation Items
// ============================================

/**
 * Primary sidebar navigation items
 * Displayed in the main navigation area
 *
 * Structure:
 * - PROJECTS: Where users organize their work
 * - ANALYZE: Tools for exploring and analyzing data
 * - AI TOOLS: AI-powered features
 */
export const mainNavItems: NavItem[] = [
  { key: 'projects', label: 'Projects', path: '/workspace', icon: 'FolderOutlined', order: 1 },
  { key: 'explorer', label: 'Process Explorer', path: '/explore', icon: 'SearchOutlined', order: 2 },
  { key: 'analytics', label: 'Analytics', path: '/analytics', icon: 'BarChartOutlined', order: 3 },
];

/**
 * AI Tools navigation items
 * Grouped separately for clarity
 */
export const aiNavItems: NavItem[] = [
  { key: 'ai-assistant', label: 'AI Assistant', path: '/ai/assistant', icon: 'RobotOutlined', order: 4 },
  { key: 'predictions', label: 'Predictions', path: '/ai/predictions', icon: 'ExperimentOutlined', order: 5 },
];

/**
 * Bottom navigation items (settings, help, etc.)
 * Displayed at the bottom of the sidebar
 */
export const bottomNavItems: NavItem[] = [
  { key: 'settings', label: 'Settings', path: '/settings/profile', icon: 'SettingOutlined', order: 100 },
  { key: 'help', label: 'Help', path: '/help', icon: 'QuestionCircleOutlined', order: 101 },
];

// ============================================
// Dataset-scoped Navigation
// ============================================

/**
 * Navigation items shown when viewing a specific dataset
 * These are relative paths appended to the dataset base path
 */
export const datasetNavItems: NavItem[] = [
  { key: 'explorer', label: 'Explorer', path: 'explorer', icon: 'SearchOutlined', order: 1 },
  { key: 'discovery', label: 'Discovery', path: 'discovery', icon: 'ThunderboltOutlined', order: 2 },
  { key: 'kpi', label: 'KPI Dashboard', path: 'kpi', icon: 'DashboardOutlined', order: 3 },
  { key: 'questions', label: 'Questions', path: 'questions', icon: 'QuestionOutlined', order: 4 },
];

// ============================================
// Route Mappings
// ============================================

/**
 * Map nav IDs to paths for programmatic navigation
 * Used by AppShell's onNavigate handler
 */
export const navRoutes: Record<string, string> = {
  login: '/login',
  projects: '/workspace',
  workspace: '/workspace', // Alias for backwards compatibility
  home: '/workspace',
  explorer: '/explore',
  analytics: '/analytics',
  'ai-assistant': '/ai/assistant',
  predictions: '/ai/predictions',
  settings: '/settings/profile',
  help: '/help',
  notifications: '/notifications',
  'test-bench': '/test-bench',
};

/**
 * Get the active nav item ID from the current path
 */
export function getActiveNavId(path: string): string {
  if (path.startsWith('/login')) return 'login';
  if (path.startsWith('/workspace')) return 'projects';
  if (path.startsWith('/home')) return 'projects';
  if (path.startsWith('/projects')) return 'projects';
  if (path.startsWith('/explorer') || path.startsWith('/explore')) return 'explorer';
  if (path.startsWith('/analytics')) return 'analytics';
  if (path.startsWith('/ai/assistant')) return 'ai-assistant';
  if (path.startsWith('/ai/predictions') || path.startsWith('/predictions')) return 'predictions';
  if (path.startsWith('/ai')) return 'ai-assistant'; // Default AI route
  if (path.startsWith('/settings')) return 'settings';
  if (path.startsWith('/help')) return 'help';
  if (path.startsWith('/notifications')) return 'notifications';
  if (path.startsWith('/test-bench')) return 'test-bench';
  return 'projects';
}
