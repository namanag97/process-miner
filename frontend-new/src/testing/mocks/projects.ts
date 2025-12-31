/**
 * Mock data factories for Projects
 */

export interface MockProject {
  id: string;
  name: string;
  description?: string;
  processCount: number;
  createdAt: string;
  updatedAt: string;
  processes?: MockProcess[];
}

export interface MockProcess {
  id: string;
  name: string;
  totalCases: number;
  totalEvents: number;
  totalActivities: number;
  sourceFormat: 'csv' | 'xes';
  createdAt: string;
}

let projectCounter = 0;
let processCounter = 0;

/**
 * Create a mock project with optional overrides
 */
export function createMockProject(overrides: Partial<MockProject> = {}): MockProject {
  projectCounter++;
  const now = new Date().toISOString();

  return {
    id: `project-${projectCounter}`,
    name: `Test Project ${projectCounter}`,
    description: 'A test project for unit testing',
    processCount: 0,
    createdAt: now,
    updatedAt: now,
    processes: [],
    ...overrides,
  };
}

/**
 * Create a mock process with optional overrides
 */
export function createMockProcess(overrides: Partial<MockProcess> = {}): MockProcess {
  processCounter++;
  const now = new Date().toISOString();

  return {
    id: `process-${processCounter}`,
    name: `test_data_${processCounter}.csv`,
    totalCases: 1000,
    totalEvents: 10000,
    totalActivities: 15,
    sourceFormat: 'csv',
    createdAt: now,
    ...overrides,
  };
}

/**
 * Create a project with processes
 */
export function createMockProjectWithProcesses(
  processCount: number,
  projectOverrides: Partial<MockProject> = {}
): MockProject {
  const processes = Array.from({ length: processCount }, () => createMockProcess());

  return createMockProject({
    processCount,
    processes,
    ...projectOverrides,
  });
}

/**
 * Reset counters between tests
 */
export function resetMockCounters(): void {
  projectCounter = 0;
  processCounter = 0;
}
