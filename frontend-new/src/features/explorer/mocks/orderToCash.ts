/**
 * Order-to-Cash Mock Data
 *
 * Comprehensive mock data for the Order-to-Cash process used as fallback
 * when backend is unavailable. Demonstrates all features of the Process Explorer.
 */

import type {
  DFGResponse,
  DFGNode,
  DFGEdge,
  Variant,
  ActivityDetail,
} from '../types';

// ============================================
// DFG Mock Data
// ============================================

const mockDFGNodes: DFGNode[] = [
  {
    id: 'receive-order',
    label: 'Receive Order',
    frequency: 1000,
    isStart: true,
    isEnd: false,
  },
  {
    id: 'check-inventory',
    label: 'Check Inventory',
    frequency: 850,
    isStart: false,
    isEnd: false,
  },
  {
    id: 'request-restock',
    label: 'Request Restock',
    frequency: 150,
    isStart: false,
    isEnd: false,
  },
  {
    id: 'pick-items',
    label: 'Pick Items',
    frequency: 980,
    isStart: false,
    isEnd: false,
  },
  {
    id: 'pack-order',
    label: 'Pack Order',
    frequency: 970,
    isStart: false,
    isEnd: false,
  },
  {
    id: 'generate-invoice',
    label: 'Generate Invoice',
    frequency: 960,
    isStart: false,
    isEnd: false,
  },
  {
    id: 'ship-order',
    label: 'Ship Order',
    frequency: 950,
    isStart: false,
    isEnd: false,
  },
  {
    id: 'deliver-order',
    label: 'Deliver Order',
    frequency: 920,
    isStart: false,
    isEnd: false,
  },
  {
    id: 'close-order',
    label: 'Close Order',
    frequency: 900,
    isStart: false,
    isEnd: true,
  },
  {
    id: 'process-return',
    label: 'Process Return',
    frequency: 50,
    isStart: false,
    isEnd: false,
  },
  {
    id: 'issue-refund',
    label: 'Issue Refund',
    frequency: 45,
    isStart: false,
    isEnd: true,
  },
];

const mockDFGEdges: DFGEdge[] = [
  // Happy path
  {
    source: 'receive-order',
    target: 'check-inventory',
    frequency: 850,
    avgDuration: 1800, // 30 minutes
  },
  {
    source: 'check-inventory',
    target: 'pick-items',
    frequency: 800,
    avgDuration: 3600, // 1 hour
  },
  {
    source: 'pick-items',
    target: 'pack-order',
    frequency: 970,
    avgDuration: 1200, // 20 minutes
  },
  {
    source: 'pack-order',
    target: 'generate-invoice',
    frequency: 960,
    avgDuration: 600, // 10 minutes
  },
  {
    source: 'generate-invoice',
    target: 'ship-order',
    frequency: 950,
    avgDuration: 7200, // 2 hours
  },
  {
    source: 'ship-order',
    target: 'deliver-order',
    frequency: 920,
    avgDuration: 86400, // 24 hours
  },
  {
    source: 'deliver-order',
    target: 'close-order',
    frequency: 870,
    avgDuration: 1800, // 30 minutes
  },

  // Rush orders (skip inventory check)
  {
    source: 'receive-order',
    target: 'pick-items',
    frequency: 150,
    avgDuration: 900, // 15 minutes
  },

  // Backorder flow
  {
    source: 'check-inventory',
    target: 'request-restock',
    frequency: 50,
    avgDuration: 3600, // 1 hour
  },
  {
    source: 'request-restock',
    target: 'check-inventory',
    frequency: 150,
    avgDuration: 172800, // 48 hours (rework loop)
  },

  // Rework: Packing issues
  {
    source: 'pack-order',
    target: 'pick-items',
    frequency: 10,
    avgDuration: 1800, // 30 minutes (repick)
  },

  // Return flow
  {
    source: 'deliver-order',
    target: 'process-return',
    frequency: 50,
    avgDuration: 7200, // 2 hours
  },
  {
    source: 'process-return',
    target: 'issue-refund',
    frequency: 45,
    avgDuration: 3600, // 1 hour
  },
];

export const mockOrderToCashDFG: DFGResponse = {
  nodes: mockDFGNodes,
  edges: mockDFGEdges,
  stats: {
    totalCases: 1000,
    totalActivities: mockDFGNodes.length,
    totalTransitions: mockDFGEdges.length,
  },
};

// ============================================
// Variants Mock Data
// ============================================

export const mockOrderToCashVariants: Variant[] = [
  // Happy path (60%)
  {
    key: 'variant-1-happy-path',
    activities: [
      'Receive Order',
      'Check Inventory',
      'Pick Items',
      'Pack Order',
      'Generate Invoice',
      'Ship Order',
      'Deliver Order',
      'Close Order',
    ],
    caseCount: 600,
    frequencyPercent: 60.0,
    avgDuration: 97800, // ~27 hours
    complexityScore: 8,
  },

  // Rush order - skip inventory check (15%)
  {
    key: 'variant-2-rush-order',
    activities: [
      'Receive Order',
      'Pick Items',
      'Pack Order',
      'Generate Invoice',
      'Ship Order',
      'Deliver Order',
      'Close Order',
    ],
    caseCount: 150,
    frequencyPercent: 15.0,
    avgDuration: 89400, // ~25 hours (faster)
    complexityScore: 7,
  },

  // Backorder with restock (10%)
  {
    key: 'variant-3-backorder',
    activities: [
      'Receive Order',
      'Check Inventory',
      'Request Restock',
      'Check Inventory',
      'Pick Items',
      'Pack Order',
      'Generate Invoice',
      'Ship Order',
      'Deliver Order',
      'Close Order',
    ],
    caseCount: 100,
    frequencyPercent: 10.0,
    avgDuration: 270600, // ~75 hours (much slower due to restock)
    complexityScore: 10,
  },

  // Multiple restocks (5%)
  {
    key: 'variant-4-multiple-restocks',
    activities: [
      'Receive Order',
      'Check Inventory',
      'Request Restock',
      'Check Inventory',
      'Request Restock',
      'Check Inventory',
      'Pick Items',
      'Pack Order',
      'Generate Invoice',
      'Ship Order',
      'Deliver Order',
      'Close Order',
    ],
    caseCount: 50,
    frequencyPercent: 5.0,
    avgDuration: 432000, // ~120 hours (very slow)
    complexityScore: 12,
  },

  // Packing rework (5%)
  {
    key: 'variant-5-packing-rework',
    activities: [
      'Receive Order',
      'Check Inventory',
      'Pick Items',
      'Pack Order',
      'Pick Items',
      'Pack Order',
      'Generate Invoice',
      'Ship Order',
      'Deliver Order',
      'Close Order',
    ],
    caseCount: 50,
    frequencyPercent: 5.0,
    avgDuration: 102000, // ~28 hours
    complexityScore: 10,
  },

  // Return and refund (4%)
  {
    key: 'variant-6-return-refund',
    activities: [
      'Receive Order',
      'Check Inventory',
      'Pick Items',
      'Pack Order',
      'Generate Invoice',
      'Ship Order',
      'Deliver Order',
      'Process Return',
      'Issue Refund',
    ],
    caseCount: 40,
    frequencyPercent: 4.0,
    avgDuration: 108600, // ~30 hours
    complexityScore: 9,
  },

  // Cancelled before delivery (1%)
  {
    key: 'variant-7-partial',
    activities: [
      'Receive Order',
      'Check Inventory',
      'Pick Items',
      'Pack Order',
      'Generate Invoice',
      'Ship Order',
      'Close Order',
    ],
    caseCount: 10,
    frequencyPercent: 1.0,
    avgDuration: 10800, // ~3 hours (cancelled early)
    complexityScore: 7,
  },
];

// ============================================
// Activities Mock Data
// ============================================

export const mockOrderToCashActivities: ActivityDetail[] = [
  {
    id: 'receive-order',
    name: 'Receive Order',
    frequency: 1000,
    frequencyPercent: 100.0,
    avgDuration: 600,
    minDuration: 120,
    maxDuration: 1800,
    isStart: true,
    isEnd: false,
    resources: ['Order System', 'Customer Portal', 'Sales Team'],
  },
  {
    id: 'check-inventory',
    name: 'Check Inventory',
    frequency: 850,
    frequencyPercent: 85.0,
    avgDuration: 1800,
    minDuration: 600,
    maxDuration: 3600,
    isStart: false,
    isEnd: false,
    resources: ['Warehouse System', 'Inventory Manager'],
  },
  {
    id: 'request-restock',
    name: 'Request Restock',
    frequency: 150,
    frequencyPercent: 15.0,
    avgDuration: 172800,
    minDuration: 86400,
    maxDuration: 259200,
    isStart: false,
    isEnd: false,
    resources: ['Procurement Team', 'Supplier System'],
  },
  {
    id: 'pick-items',
    name: 'Pick Items',
    frequency: 980,
    frequencyPercent: 98.0,
    avgDuration: 2400,
    minDuration: 900,
    maxDuration: 5400,
    isStart: false,
    isEnd: false,
    resources: ['Warehouse Staff', 'Picking System', 'Forklift Operators'],
  },
  {
    id: 'pack-order',
    name: 'Pack Order',
    frequency: 970,
    frequencyPercent: 97.0,
    avgDuration: 1200,
    minDuration: 600,
    maxDuration: 2400,
    isStart: false,
    isEnd: false,
    resources: ['Packing Station', 'Warehouse Staff'],
  },
  {
    id: 'generate-invoice',
    name: 'Generate Invoice',
    frequency: 960,
    frequencyPercent: 96.0,
    avgDuration: 600,
    minDuration: 300,
    maxDuration: 1200,
    isStart: false,
    isEnd: false,
    resources: ['Billing System', 'Finance Team'],
  },
  {
    id: 'ship-order',
    name: 'Ship Order',
    frequency: 950,
    frequencyPercent: 95.0,
    avgDuration: 7200,
    minDuration: 3600,
    maxDuration: 14400,
    isStart: false,
    isEnd: false,
    resources: ['Shipping Carrier', 'Logistics Coordinator', 'Delivery System'],
  },
  {
    id: 'deliver-order',
    name: 'Deliver Order',
    frequency: 920,
    frequencyPercent: 92.0,
    avgDuration: 86400,
    minDuration: 43200,
    maxDuration: 172800,
    isStart: false,
    isEnd: false,
    resources: ['Delivery Driver', 'Delivery System'],
  },
  {
    id: 'close-order',
    name: 'Close Order',
    frequency: 900,
    frequencyPercent: 90.0,
    avgDuration: 1800,
    minDuration: 600,
    maxDuration: 3600,
    isStart: false,
    isEnd: true,
    resources: ['Order System', 'Customer Service'],
  },
  {
    id: 'process-return',
    name: 'Process Return',
    frequency: 50,
    frequencyPercent: 5.0,
    avgDuration: 7200,
    minDuration: 3600,
    maxDuration: 14400,
    isStart: false,
    isEnd: false,
    resources: ['Returns Department', 'Customer Service', 'Warehouse Staff'],
  },
  {
    id: 'issue-refund',
    name: 'Issue Refund',
    frequency: 45,
    frequencyPercent: 4.5,
    avgDuration: 3600,
    minDuration: 1800,
    maxDuration: 7200,
    isStart: false,
    isEnd: true,
    resources: ['Finance Team', 'Payment System'],
  },
];

// ============================================
// Log Metadata Mock
// ============================================

export const mockOrderToCashLogInfo = {
  id: 'mock-order-to-cash-log',
  name: 'Order-to-Cash Process (Mock Data)',
  description: 'Demonstration data showing a typical Order-to-Cash process with variants',
  status: 'ready' as const,
  totalCases: 1000,
  totalEvents: 9500,
  startDate: '2024-01-01T00:00:00Z',
  endDate: '2024-12-31T23:59:59Z',
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-12-31T23:59:59Z',
};
