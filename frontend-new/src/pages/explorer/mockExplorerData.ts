/**
 * Mock data for Process Explorer
 * Local types matching the expected structure for DFG nodes and edges
 */

// =============================================================================
// LOCAL TYPE DEFINITIONS
// =============================================================================

export interface DFGNode {
  id: string;
  label: string;
  frequency: number;
}

export interface DFGEdge {
  source: string;
  target: string;
  frequency: number;
  performance?: number;
}

export interface DFGResponse {
  log_id: string;
  nodes: DFGNode[];
  edges: DFGEdge[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  total_cases: number;
}

// =============================================================================
// MOCK DFG DATA
// =============================================================================

export const mockDFGNodes: DFGNode[] = [
  { id: 'start', label: 'Start', frequency: 1250 },
  { id: 'receive_order', label: 'Receive Order', frequency: 1250 },
  { id: 'check_stock', label: 'Check Stock', frequency: 1250 },
  { id: 'confirm_order', label: 'Confirm Order', frequency: 1100 },
  { id: 'reject_order', label: 'Reject Order', frequency: 150 },
  { id: 'pick_items', label: 'Pick Items', frequency: 1100 },
  { id: 'pack_order', label: 'Pack Order', frequency: 1100 },
  { id: 'ship_order', label: 'Ship Order', frequency: 1050 },
  { id: 'handle_return', label: 'Handle Return', frequency: 80 },
  { id: 'close_order', label: 'Close Order', frequency: 1180 },
  { id: 'end', label: 'End', frequency: 1250 },
];

export const mockDFGEdges: DFGEdge[] = [
  { source: 'start', target: 'receive_order', frequency: 1250, performance: 0 },
  { source: 'receive_order', target: 'check_stock', frequency: 1250, performance: 3600 },
  { source: 'check_stock', target: 'confirm_order', frequency: 1100, performance: 7200 },
  { source: 'check_stock', target: 'reject_order', frequency: 150, performance: 1800 },
  { source: 'confirm_order', target: 'pick_items', frequency: 1100, performance: 14400 },
  { source: 'pick_items', target: 'pack_order', frequency: 1100, performance: 10800 },
  { source: 'pack_order', target: 'ship_order', frequency: 1050, performance: 7200 },
  { source: 'pack_order', target: 'handle_return', frequency: 50, performance: 86400 },
  { source: 'ship_order', target: 'close_order', frequency: 1050, performance: 172800 },
  { source: 'ship_order', target: 'handle_return', frequency: 30, performance: 259200 },
  { source: 'handle_return', target: 'close_order', frequency: 80, performance: 43200 },
  { source: 'reject_order', target: 'close_order', frequency: 150, performance: 3600 },
  { source: 'close_order', target: 'end', frequency: 1180, performance: 0 },
];

export const mockDFGResponse: DFGResponse = {
  log_id: '1',
  nodes: mockDFGNodes,
  edges: mockDFGEdges,
  start_activities: { 'Receive Order': 1250 },
  end_activities: { 'Close Order': 1180, 'End': 70 },
  total_cases: 1250,
};

// =============================================================================
// MOCK VARIANTS DATA
// =============================================================================

export interface MockVariant {
  key: string;
  activities: string[];
  caseCount: number;
  frequencyPercent: number;
  avgDurationSeconds: number;
  isHappyPath?: boolean;
}

export const mockVariants: MockVariant[] = [
  {
    key: 'v1',
    activities: ['Receive Order', 'Check Stock', 'Confirm Order', 'Pick Items', 'Pack Order', 'Ship Order', 'Close Order'],
    caseCount: 850,
    frequencyPercent: 68,
    avgDurationSeconds: 216000, // 2.5 days
    isHappyPath: true,
  },
  {
    key: 'v2',
    activities: ['Receive Order', 'Check Stock', 'Reject Order', 'Close Order'],
    caseCount: 150,
    frequencyPercent: 12,
    avgDurationSeconds: 7200, // 2 hours
  },
  {
    key: 'v3',
    activities: ['Receive Order', 'Check Stock', 'Confirm Order', 'Pick Items', 'Pack Order', 'Handle Return', 'Close Order'],
    caseCount: 50,
    frequencyPercent: 4,
    avgDurationSeconds: 345600, // 4 days
  },
  {
    key: 'v4',
    activities: ['Receive Order', 'Check Stock', 'Confirm Order', 'Pick Items', 'Pack Order', 'Ship Order', 'Handle Return', 'Close Order'],
    caseCount: 30,
    frequencyPercent: 2.4,
    avgDurationSeconds: 432000, // 5 days
  },
  {
    key: 'v5',
    activities: ['Receive Order', 'Check Stock', 'Confirm Order', 'Pick Items', 'Pack Order', 'Ship Order', 'Close Order'],
    caseCount: 170,
    frequencyPercent: 13.6,
    avgDurationSeconds: 259200, // 3 days
  },
];

// =============================================================================
// MOCK FILTER OPTIONS
// =============================================================================

export interface MockFilterOptions {
  activities: string[];
  resources: string[];
  timeRange: { start: string; end: string };
  caseDuration: { min: number; max: number; mean: number };
}

export const mockFilterOptions: MockFilterOptions = {
  activities: [
    'Receive Order',
    'Check Stock',
    'Confirm Order',
    'Reject Order',
    'Pick Items',
    'Pack Order',
    'Ship Order',
    'Handle Return',
    'Close Order',
  ],
  resources: [
    'System',
    'John Doe',
    'Jane Smith',
    'Warehouse Team',
    'Shipping Dept',
    'Customer Service',
  ],
  timeRange: {
    start: '2024-01-01T00:00:00Z',
    end: '2024-12-31T23:59:59Z',
  },
  caseDuration: {
    min: 3600,      // 1 hour
    max: 604800,    // 7 days
    mean: 216000,   // 2.5 days
  },
};

// =============================================================================
// MOCK ACTIVITY DETAILS
// =============================================================================

export interface MockActivityDetail {
  id: string;
  name: string;
  totalOccurrences: number;
  casePercentage: number;
  avgDurationSeconds: number;
  minDurationSeconds: number;
  maxDurationSeconds: number;
  resources: string[];
}

export function getActivityDetail(activityId: string): MockActivityDetail | null {
  const node = mockDFGNodes.find(n => n.id === activityId);
  if (!node) return null;

  return {
    id: node.id,
    name: node.label,
    totalOccurrences: node.frequency,
    casePercentage: Math.round((node.frequency / 1250) * 100),
    avgDurationSeconds: 14400, // 4 hours
    minDurationSeconds: 1800,  // 30 min
    maxDurationSeconds: 86400, // 24 hours
    resources: ['John Doe', 'Jane Smith', 'System'],
  };
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

export function formatDuration(seconds: number): string {
  if (seconds < 3600) {
    return `${Math.round(seconds / 60)} min`;
  } else if (seconds < 86400) {
    return `${(seconds / 3600).toFixed(1)} hrs`;
  } else {
    return `${(seconds / 86400).toFixed(1)} days`;
  }
}
