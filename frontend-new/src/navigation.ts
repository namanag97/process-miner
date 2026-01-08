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
 */
export const mainNavItems: NavItem[] = [
  { key: 'workspace', label: 'Workspace', path: '/workspace', icon: 'FolderOutlined', order: 1 },
  { key: 'explorer', label: 'Explorer', path: '/explore', icon: 'SearchOutlined', order: 3 },
  { key: 'analytics', label: 'Analytics', path: '/analytics', icon: 'BarChartOutlined', order: 5 },
  { key: 'ai', label: 'AI & Predictions', path: '/ai', icon: 'RobotOutlined', order: 6 },
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
  workspace: '/workspace',
  home: '/workspace',
  logs: '/processes',
  explorer: '/explore',
  analytics: '/analytics',
  'ai-insights': '/ai/assistant',
  predictions: '/ai/predictions',
  settings: '/settings/profile',
  help: '/help',
  notifications: '/notifications',
  activity: '/activity',
  'test-bench': '/test-bench',
};

/**
 * Get the active nav item ID from the current path
 */
export function getActiveNavId(path: string): string {
  if (path.startsWith('/login')) return 'login';
  if (path.startsWith('/workspace')) return 'workspace';
  if (path.startsWith('/home')) return 'workspace';
  if (path.startsWith('/projects')) return 'workspace';
  if (path.startsWith('/processes')) return 'logs';
  if (path.startsWith('/explorer') || path.startsWith('/explore')) return 'explorer';
  if (path.startsWith('/analytics')) return 'analytics';
  if (path.startsWith('/ai')) return 'ai-insights';
  if (path.startsWith('/predictions')) return 'predictions';
  if (path.startsWith('/settings')) return 'settings';
  if (path.startsWith('/help')) return 'help';
  if (path.startsWith('/notifications')) return 'notifications';
  if (path.startsWith('/activity')) return 'activity';
  if (path.startsWith('/test-bench')) return 'test-bench';
  if (path.startsWith('/audit')) return 'audit-logs';
  return 'workspace';
}
