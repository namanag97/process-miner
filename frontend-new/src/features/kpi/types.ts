/**
 * KPI Feature Types
 */

// ============================================
// Performance Types
// ============================================

export interface PerformanceData {
  topBottlenecks: BottleneckActivity[];
  avgProcessingTime: number;
  waitingTimePercentage: number;
}

export interface BottleneckActivity {
  activity: string;
  avgWaitingTime: number;
  impactScore: number;
}

// ============================================
// Cycle Time Types
// ============================================

export interface CycleTimeData {
  avg_seconds: number;
  min_seconds: number;
  max_seconds: number;
  median_seconds: number;
  p90_seconds?: number;
}

// ============================================
// Throughput Types
// ============================================

export interface ThroughputData {
  total_cases: number;
  completed_cases: number;
  cases_per_day: number;
  cases_per_week?: number;
  cases_per_month?: number;
}

// ============================================
// Deadline Types
// ============================================

export interface DeadlineData {
  totalCases: number;
  onTimeCases: number;
  lateCases: number;
  onTimePercentage: number;
  avgDelayDays?: number;
  deadlineConfig?: DeadlineConfig;
}

export interface DeadlineConfig {
  targetDays: number;
  referenceActivity?: string;
}

// ============================================
// Unwanted Activities Types
// ============================================

export interface UnwantedActivityData {
  activity: string;
  occurrences: number;
  casePercentage: number;
  avgImpactOnCycleTime: number;
  recommendedAction?: string;
}

export interface UnwantedActivitiesResponse {
  activities: UnwantedActivityData[];
  totalImpact: number;
  potentialSavings?: number;
}

// ============================================
// Automation Types
// ============================================

export interface AutomationPotentialData {
  activity: string;
  automationScore: number;
  currentManualEffort: number;
  estimatedSavings: number;
  complexity: 'low' | 'medium' | 'high';
  prerequisites?: string[];
}

export interface AutomationResponse {
  activities: AutomationPotentialData[];
  totalPotentialSavings: number;
  recommendedPriority: string[];
}

// ============================================
// Tab Props Types
// ============================================

export interface KPITabProps {
  logId: string;
}
