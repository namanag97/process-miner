// Application constants - eliminates magic strings

// =============================================================================
// FILE HANDLING
// =============================================================================

export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export const ACCEPTED_FILE_TYPES = {
    'text/csv': ['.csv'],
    'text/plain': ['.csv'],
    'application/csv': ['.csv'],
    'application/vnd.ms-excel': ['.csv'],
    'application/xml': ['.xes'],
    'text/xml': ['.xes'],
} as const;

export const FILE_EXTENSIONS = {
    CSV: '.csv',
    XES: '.xes',
} as const;

// =============================================================================
// ROUTES
// =============================================================================

export const ROUTES = {
    HOME: '/',
    UPLOAD: '/upload',
    CONFIGURE: '/configure',
    PROCESS_MAP: '/process-map',
    INSIGHTS: '/insights',
} as const;

// =============================================================================
// WORKFLOW STEPS
// =============================================================================

export const STEPS = [
    { number: 1, label: 'Upload', route: ROUTES.UPLOAD },
    { number: 2, label: 'Configure', route: ROUTES.CONFIGURE },
    { number: 3, label: 'Analyze', route: ROUTES.PROCESS_MAP },
    { number: 4, label: 'Visualize', route: ROUTES.INSIGHTS },
] as const;

export type StepNumber = 1 | 2 | 3 | 4;

// =============================================================================
// NAVIGATION
// =============================================================================

export const NAV_ITEMS = [
    { name: 'Home', href: ROUTES.HOME, iconName: 'House' as const },
    { name: 'Upload Data', href: ROUTES.UPLOAD, iconName: 'Upload' as const },
    { name: 'Configure', href: ROUTES.CONFIGURE, iconName: 'Settings2' as const },
    { name: 'Process Map', href: ROUTES.PROCESS_MAP, iconName: 'GitBranch' as const },
    { name: 'Insights', href: ROUTES.INSIGHTS, iconName: 'BarChart3' as const },
] as const;

// =============================================================================
// AUTO-DETECTION PATTERNS
// =============================================================================

export const COLUMN_PATTERNS = {
    CASE_ID: ['case', 'trace', 'instance', 'case_id', 'caseid', 'case-id'],
    ACTIVITY: ['activity', 'event', 'action', 'task', 'concept:name', 'activity_name', 'eventname'],
    TIMESTAMP: ['time', 'date', 'timestamp', 'time:timestamp', 'start', 'end', 'datetime'],
    RESOURCE: ['resource', 'user', 'employee', 'org', 'org:resource', 'performer', 'agent'],
    COST: ['cost', 'price', 'amount', 'value', 'cost:total'],
} as const;

// =============================================================================
// LOGGING
// =============================================================================

export const MAX_LOGS = 500;

export const LOG_LEVELS = ['info', 'success', 'warning', 'error'] as const;
export type LogLevel = typeof LOG_LEVELS[number];

// =============================================================================
// UI
// =============================================================================

export const SIDEBAR_WIDTH = 250;
export const LOG_PANEL_EXPANDED_HEIGHT = 200;
export const LOG_PANEL_COLLAPSED_HEIGHT = 40;
