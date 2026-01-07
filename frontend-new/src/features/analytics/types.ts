/**
 * Analytics Feature Types
 *
 * NOTE: Types are defined locally for frontend use.
 */

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
  datasetId: string | null;
  data?: unknown;
  loading?: boolean;
}

// ============================================
// SDK Response Types (local definitions)
// ============================================

export interface PerformanceDashboardResponse {
  cycleTime?: { avgSeconds: number; medianSeconds: number; minSeconds?: number; maxSeconds?: number };
  throughput?: { casesPerDay: number; totalCases: number };
  bottlenecks?: BottleneckData[];
}

export interface CycleTimeResponse {
  avgSeconds: number;
  medianSeconds: number;
  minSeconds?: number;
  maxSeconds?: number;
}

export interface ThroughputResponse {
  casesPerDay: number;
  totalCases: number;
}

export interface BottleneckResponse {
  activity: string;
  avgWaitingTime: number;
  frequency: number;
  impactScore?: number;
}

export interface BottleneckListResponse {
  bottlenecks: BottleneckResponse[];
}

export interface ReworkResponse {
  reworkPercentage: number;
  totalReworkCases: number;
  totalCases: number;
}

export interface ReworkListResponse {
  activities: ReworkActivity[];
}

export interface ConformanceResponse {
  fitnessScore: number;
  precisionScore: number;
  generalizationScore: number;
  overallScore: number;
}

export interface DiagnosticsResponse {
  status: string;
  issues?: { type: string; message: string }[];
}

export interface ResourceProfileResponse {
  resourceId: string;
  name: string;
  totalActivities: number;
}

export interface ResourceWorkloadResponse {
  entries: WorkloadEntry[];
}
