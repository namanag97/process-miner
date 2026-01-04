/**
 * Analytics Feature Types
 *
 * NOTE: Core API types are now auto-generated from OpenAPI spec.
 * Import them from @frontend-new/openapi-sdk for type safety.
 */

// ============================================
// Re-export SDK types
// ============================================

export type {
  PerformanceDashboardResponse,
  CycleTimeResponse,
  ThroughputResponse,
  BottleneckResponse,
  BottleneckListResponse,
  ReworkResponse,
  ReworkListResponse,
  ConformanceResponse,
  DiagnosticsResponse,
  ResourceProfileResponse,
  ResourceWorkloadResponse,
} from '@frontend-new/openapi-sdk';

// ============================================
// Performance Types (frontend extensions)
// ============================================

export interface AnalyticsPerformanceData {
  cycleTime?: {
    avgSeconds: number;
    medianSeconds: number;
    minSeconds: number;
    maxSeconds: number;
  };
  throughput?: {
    casesPerDay: number;
    totalCases: number;
  };
  topBottlenecks?: BottleneckData[];
}

export interface BottleneckData {
  activity: string;
  avgWaitingTime: number;
  avgProcessingTime?: number;
  frequency: number;
  impactScore: number;
}

// ============================================
// Conformance Types
// ============================================

export interface ConformanceData {
  fitnessScore: number;
  precisionScore: number;
  generalizationScore: number;
  overallScore: number;
  violations?: ConformanceViolation[];
}

export interface ConformanceViolation {
  type: 'missing' | 'unexpected' | 'wrong_order';
  activity: string;
  caseCount: number;
  percentage: number;
}

// ============================================
// Rework Types
// ============================================

export interface ReworkData {
  reworkPercentage: number;
  totalReworkCases: number;
  totalCases: number;
  topReworkActivities?: ReworkActivity[];
  reworkPatterns?: ReworkPattern[];
}

export interface ReworkActivity {
  activity: string;
  reworkCount: number;
  avgRepetitions: number;
  impactOnCycleTime: number;
}

export interface ReworkPattern {
  pattern: string[];
  frequency: number;
  avgAdditionalTime: number;
}

// ============================================
// Resource Types
// ============================================

export interface ResourceData {
  resources: ResourceDetail[];
  handoffs?: HandoffData[];
  workloadDistribution?: WorkloadEntry[];
}

export interface ResourceDetail {
  id: string;
  name: string;
  totalActivities: number;
  uniqueActivities: string[];
  avgCasesPerDay: number;
  avgActivityDuration: number;
}

export interface HandoffData {
  from: string;
  to: string;
  frequency: number;
  avgTransitionTime: number;
}

export interface WorkloadEntry {
  resource: string;
  workload: number;
  period: string;
}

// ============================================
// Tab Props Types
// ============================================

export interface AnalyticsTabProps {
  logId: string | null;
  data?: unknown;
  loading?: boolean;
}
