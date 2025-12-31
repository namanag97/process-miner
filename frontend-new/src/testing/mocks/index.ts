/**
 * Mock data factories for testing
 * Export all mock factories from a single entry point
 */

export {
  createMockProject,
  createMockProcess,
  createMockProjectWithProcesses,
  resetMockCounters,
  type MockProject,
  type MockProcess,
} from './projects';

export {
  createMockDFG,
  createMockVariants,
  createComplexMockDFG,
  type MockDFGNode,
  type MockDFGEdge,
  type MockDFG,
  type MockVariant,
} from './dfg';
