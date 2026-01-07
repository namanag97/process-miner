/**
 * MSW Request Handlers
 *
 * Mock API handlers for testing. These intercept requests and return
 * controlled responses without hitting the real backend.
 *
 * @see https://mswjs.io/docs/basics/mocking-responses
 */

import { http, HttpResponse } from 'msw';

const API_BASE = '/api/v1';

// ============================================
// Mock Data
// ============================================

export const mockProjects = [
  {
    id: 'project-1',
    name: 'Test Project',
    description: 'A test project for testing',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
    workspaceId: 'workspace-1',
  },
  {
    id: 'project-2',
    name: 'Another Project',
    description: 'Another test project',
    createdAt: '2024-01-02T00:00:00Z',
    updatedAt: '2024-01-02T00:00:00Z',
    workspaceId: 'workspace-1',
  },
];

export const mockProcesses = [
  {
    id: 'process-1',
    name: 'Order to Cash',
    totalCases: 1000,
    totalEvents: 5000,
    status: 'ready',
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: 'process-2',
    name: 'Purchase to Pay',
    totalCases: 500,
    totalEvents: 2500,
    status: 'ready',
    createdAt: '2024-01-02T00:00:00Z',
  },
];

export const mockDFG = {
  nodes: [
    { id: 'start', label: 'Start', frequency: 1000, isStart: true, isEnd: false },
    { id: 'activity-1', label: 'Create Order', frequency: 950, isStart: false, isEnd: false },
    { id: 'activity-2', label: 'Approve Order', frequency: 900, isStart: false, isEnd: false },
    { id: 'activity-3', label: 'Ship Order', frequency: 850, isStart: false, isEnd: false },
    { id: 'end', label: 'End', frequency: 800, isStart: false, isEnd: true },
  ],
  edges: [
    { source: 'start', target: 'activity-1', frequency: 950 },
    { source: 'activity-1', target: 'activity-2', frequency: 900 },
    { source: 'activity-2', target: 'activity-3', frequency: 850 },
    { source: 'activity-3', target: 'end', frequency: 800 },
  ],
};

export const mockVariants = [
  {
    key: 'variant-1',
    activities: ['Create Order', 'Approve Order', 'Ship Order'],
    caseCount: 600,
    frequencyPercent: 60,
    avgDuration: 86400,
  },
  {
    key: 'variant-2',
    activities: ['Create Order', 'Ship Order'],
    caseCount: 200,
    frequencyPercent: 20,
    avgDuration: 43200,
  },
];

export const mockPerformanceData = {
  cycleTime: {
    avgSeconds: 86400,
    minSeconds: 3600,
    maxSeconds: 604800,
    p50Seconds: 72000,
    p90Seconds: 172800,
  },
  throughput: {
    casesPerDay: 10.5,
    casesPerWeek: 73.5,
  },
  topBottlenecks: [
    { activity: 'Approve Order', avgWaitTime: 28800, frequency: 900 },
    { activity: 'Ship Order', avgWaitTime: 14400, frequency: 850 },
  ],
};

export const mockReworkData = {
  reworkPercentage: 15.5,
  reworkActivities: [
    { activity: 'Review Order', reworkCount: 150, reworkPercent: 15 },
    { activity: 'Update Details', reworkCount: 50, reworkPercent: 5 },
  ],
};

// ============================================
// Request Handlers
// ============================================

export const handlers = [
  // Projects
  http.get(`${API_BASE}/projects`, () => {
    return HttpResponse.json({ items: mockProjects, total: mockProjects.length });
  }),

  http.get(`${API_BASE}/projects/:id`, ({ params }) => {
    const project = mockProjects.find((p) => p.id === params.id);
    if (!project) {
      return HttpResponse.json({ error: 'Not found' }, { status: 404 });
    }
    return HttpResponse.json(project);
  }),

  http.post(`${API_BASE}/projects`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>;
    const newProject = {
      id: `project-${Date.now()}`,
      name: body.name || 'New Project',
      description: body.description || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      workspaceId: body.workspaceId || 'workspace-1',
    };
    return HttpResponse.json(newProject, { status: 201 });
  }),

  // Processes / Event Logs
  http.get(`${API_BASE}/processes`, () => {
    return HttpResponse.json({ items: mockProcesses, total: mockProcesses.length });
  }),

  http.get(`${API_BASE}/processes/:id`, ({ params }) => {
    const process = mockProcesses.find((p) => p.id === params.id);
    if (!process) {
      return HttpResponse.json({ error: 'Not found' }, { status: 404 });
    }
    return HttpResponse.json(process);
  }),

  // Discovery
  http.get(`${API_BASE}/discovery/:datasetId/dfg`, () => {
    return HttpResponse.json(mockDFG);
  }),

  http.get(`${API_BASE}/discovery/:datasetId/variants`, () => {
    return HttpResponse.json({ items: mockVariants, total: mockVariants.length });
  }),

  http.get(`${API_BASE}/discovery/:datasetId/explorer`, () => {
    return HttpResponse.json({
      dfg: mockDFG,
      variants: mockVariants,
      activities: mockDFG.nodes.filter((n) => !n.isStart && !n.isEnd).map((n) => ({
        id: n.id,
        name: n.label,
        frequency: n.frequency,
        frequencyPercent: (n.frequency / 1000) * 100,
        avgDuration: 3600,
        minDuration: 1800,
        maxDuration: 7200,
        isStart: n.isStart,
        isEnd: n.isEnd,
        resources: ['User A', 'User B'],
      })),
    });
  }),

  // Analytics
  http.get(`${API_BASE}/analytics/:datasetId/performance`, () => {
    return HttpResponse.json(mockPerformanceData);
  }),

  http.get(`${API_BASE}/analytics/:datasetId/rework`, () => {
    return HttpResponse.json(mockReworkData);
  }),

  http.get(`${API_BASE}/analytics/:datasetId/bottlenecks`, () => {
    return HttpResponse.json({ items: mockPerformanceData.topBottlenecks });
  }),

  // Health check
  http.get('/health/live', () => {
    return HttpResponse.json({ status: 'ok' });
  }),

  http.get('/health/ready', () => {
    return HttpResponse.json({ status: 'ok' });
  }),
];

// ============================================
// Error Handlers (for testing error states)
// ============================================

export const errorHandlers = {
  networkError: http.get(`${API_BASE}/projects`, () => {
    return HttpResponse.error();
  }),

  serverError: http.get(`${API_BASE}/projects`, () => {
    return HttpResponse.json({ error: 'Internal server error' }, { status: 500 });
  }),

  notFound: http.get(`${API_BASE}/projects/:id`, () => {
    return HttpResponse.json({ error: 'Not found' }, { status: 404 });
  }),

  unauthorized: http.get(`${API_BASE}/projects`, () => {
    return HttpResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }),
};
