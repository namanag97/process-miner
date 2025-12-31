/**
 * Mock data factories for DFG (Directly-Follows Graph)
 */

export interface MockDFGNode {
  id: string;
  label: string;
  frequency: number;
  isStart?: boolean;
  isEnd?: boolean;
  avgDuration?: number;
}

export interface MockDFGEdge {
  id: string;
  source: string;
  target: string;
  frequency: number;
  avgDuration?: number;
}

export interface MockDFG {
  nodes: MockDFGNode[];
  edges: MockDFGEdge[];
  totalCases: number;
  totalEvents: number;
}

export interface MockVariant {
  id: string;
  sequence: string[];
  caseCount: number;
  percentage: number;
  avgDuration: number;
}

/**
 * Create a simple mock DFG for testing
 */
export function createMockDFG(overrides: Partial<MockDFG> = {}): MockDFG {
  return {
    nodes: [
      { id: 'start', label: 'Start', frequency: 100, isStart: true },
      { id: 'activity-1', label: 'Create Order', frequency: 100 },
      { id: 'activity-2', label: 'Review Order', frequency: 95 },
      { id: 'activity-3', label: 'Approve Order', frequency: 90 },
      { id: 'activity-4', label: 'Ship Order', frequency: 85 },
      { id: 'end', label: 'End', frequency: 85, isEnd: true },
    ],
    edges: [
      { id: 'e1', source: 'start', target: 'activity-1', frequency: 100 },
      { id: 'e2', source: 'activity-1', target: 'activity-2', frequency: 95 },
      { id: 'e3', source: 'activity-2', target: 'activity-3', frequency: 90 },
      { id: 'e4', source: 'activity-3', target: 'activity-4', frequency: 85 },
      { id: 'e5', source: 'activity-4', target: 'end', frequency: 85 },
      { id: 'e6', source: 'activity-2', target: 'activity-1', frequency: 5 }, // Rework loop
    ],
    totalCases: 100,
    totalEvents: 455,
    ...overrides,
  };
}

/**
 * Create mock variants for testing
 */
export function createMockVariants(count = 5): MockVariant[] {
  const baseSequence = ['Create Order', 'Review Order', 'Approve Order', 'Ship Order'];

  return Array.from({ length: count }, (_, i) => ({
    id: `variant-${i + 1}`,
    sequence: i === 0 ? baseSequence : [...baseSequence.slice(0, 2), 'Escalate', ...baseSequence.slice(2)],
    caseCount: Math.floor(100 / (i + 1)),
    percentage: 100 / (i + 1),
    avgDuration: 3600 * (i + 1),
  }));
}

/**
 * Create a more complex DFG with branches and loops
 */
export function createComplexMockDFG(): MockDFG {
  return {
    nodes: [
      { id: 'start', label: 'Start', frequency: 200, isStart: true },
      { id: 'a1', label: 'Receive Request', frequency: 200 },
      { id: 'a2', label: 'Initial Review', frequency: 195 },
      { id: 'a3', label: 'Detailed Analysis', frequency: 150 },
      { id: 'a4', label: 'Quick Process', frequency: 45 },
      { id: 'a5', label: 'Approval', frequency: 180 },
      { id: 'a6', label: 'Rejection', frequency: 15 },
      { id: 'a7', label: 'Implementation', frequency: 165 },
      { id: 'a8', label: 'Quality Check', frequency: 160 },
      { id: 'a9', label: 'Completion', frequency: 155 },
      { id: 'end', label: 'End', frequency: 200, isEnd: true },
    ],
    edges: [
      { id: 'e1', source: 'start', target: 'a1', frequency: 200 },
      { id: 'e2', source: 'a1', target: 'a2', frequency: 195 },
      { id: 'e3', source: 'a2', target: 'a3', frequency: 150 },
      { id: 'e4', source: 'a2', target: 'a4', frequency: 45 },
      { id: 'e5', source: 'a3', target: 'a5', frequency: 135 },
      { id: 'e6', source: 'a3', target: 'a6', frequency: 15 },
      { id: 'e7', source: 'a4', target: 'a5', frequency: 45 },
      { id: 'e8', source: 'a5', target: 'a7', frequency: 165 },
      { id: 'e9', source: 'a6', target: 'end', frequency: 15 },
      { id: 'e10', source: 'a7', target: 'a8', frequency: 160 },
      { id: 'e11', source: 'a8', target: 'a9', frequency: 155 },
      { id: 'e12', source: 'a8', target: 'a7', frequency: 5 }, // Rework loop
      { id: 'e13', source: 'a9', target: 'end', frequency: 155 },
    ],
    totalCases: 200,
    totalEvents: 1850,
  };
}
