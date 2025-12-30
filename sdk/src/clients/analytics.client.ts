/**
 * Analytics Client - Performance Analytics Operations
 *
 * Business verbs:
 * - getBottlenecks() - Detect process bottlenecks
 * - getRework() - Analyze rework patterns
 * - getServiceTimes() - Get service time statistics per activity
 * - getCycleTime() - Get cycle time (case duration) statistics
 * - getThroughput() - Get throughput metrics
 * - getPatterns() - Get frequent activity patterns
 * - getPerformance() - Get comprehensive performance data (FE-friendly)
 */

import { HttpClient } from "../client.js";
import {
  BottleneckListResponse,
  Bottleneck,
  ReworkListResponse,
  ReworkActivity,
  ServiceTimeResponse,
  CycleTimeResponse,
  ThroughputResponse,
  PatternResponse,
  PerformanceData,
} from "../types/analytics.js";

// =============================================================================
// Backend Response Types (snake_case)
// =============================================================================

interface BEBottleneckResponse {
  activity: string;
  avg_waiting_time_seconds: number;
  avg_service_time_seconds: number;
  frequency: number;
  is_bottleneck: boolean;
  severity: "low" | "medium" | "high";
  bottleneck_impact_score: number;
}

interface BEBottleneckListResponse {
  log_id: string;
  bottlenecks: BEBottleneckResponse[];
  total_bottlenecks: number;
}

interface BEReworkResponse {
  activity: string;
  rework_count: number;
  cases_with_rework: number;
  rework_percentage: number;
}

interface BEReworkListResponse {
  log_id: string;
  rework_activities: BEReworkResponse[];
  total_rework_cases: number;
  rework_percentage: number;
}

interface BECycleTimeResponse {
  log_id: string;
  min_seconds: number;
  max_seconds: number;
  avg_seconds: number;
  median_seconds: number;
  percentile_25_seconds: number;
  percentile_75_seconds: number;
  percentile_95_seconds: number;
}

interface BEThroughputResponse {
  log_id: string;
  total_cases: number;
  completed_cases: number;
  cases_per_day: number;
  cases_per_week: number;
  cases_per_month: number;
  time_range_days: number;
}

interface BEServiceTimeResponse {
  activity: string;
  min_seconds: number;
  max_seconds: number;
  avg_seconds: number;
  median_seconds: number;
  std_dev_seconds: number;
}

interface BEPatternResponse {
  pattern: string;
  frequency: number;
  support: number;
}

interface BEPerformanceDashboardResponse {
  log_id: string;
  cycle_time: BECycleTimeResponse;
  throughput: BEThroughputResponse;
  top_bottlenecks: BEBottleneckResponse[];
  rework_summary: Record<string, unknown>;
}

// =============================================================================
// Transformation Helpers
// =============================================================================

function transformBottleneck(be: BEBottleneckResponse): Bottleneck {
  return {
    activity: be.activity,
    avgWaitingTime: be.avg_waiting_time_seconds,
    avgServiceTime: be.avg_service_time_seconds,
    frequency: be.frequency,
    isBottleneck: be.is_bottleneck,
    severity: be.severity,
    impactScore: be.bottleneck_impact_score,
  };
}

function transformReworkActivity(be: BEReworkResponse): ReworkActivity {
  return {
    activity: be.activity,
    reworkCount: be.rework_count,
    casesWithRework: be.cases_with_rework,
    reworkPercentage: be.rework_percentage,
  };
}

function transformCycleTime(be: BECycleTimeResponse): CycleTimeResponse {
  return {
    logId: be.log_id,
    minSeconds: be.min_seconds,
    maxSeconds: be.max_seconds,
    avgSeconds: be.avg_seconds,
    medianSeconds: be.median_seconds,
    percentile25: be.percentile_25_seconds,
    percentile75: be.percentile_75_seconds,
    percentile95: be.percentile_95_seconds,
  };
}

function transformThroughput(be: BEThroughputResponse): ThroughputResponse {
  return {
    logId: be.log_id,
    totalCases: be.total_cases,
    completedCases: be.completed_cases,
    casesPerDay: be.cases_per_day,
    casesPerWeek: be.cases_per_week,
    casesPerMonth: be.cases_per_month,
    timeRangeDays: be.time_range_days,
  };
}

function transformServiceTime(be: BEServiceTimeResponse): ServiceTimeResponse {
  return {
    activity: be.activity,
    minSeconds: be.min_seconds,
    maxSeconds: be.max_seconds,
    avgSeconds: be.avg_seconds,
    medianSeconds: be.median_seconds,
    stdDevSeconds: be.std_dev_seconds,
  };
}

function transformPattern(be: BEPatternResponse): PatternResponse {
  return {
    pattern: be.pattern,
    frequency: be.frequency,
    support: be.support,
  };
}

export class AnalyticsClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Detect process bottlenecks based on waiting times.
   * Returns activities with highest waiting times.
   */
  async getBottlenecks(logId: string): Promise<BottleneckListResponse> {
    const response = await this.http.get<BEBottleneckListResponse>(
      `/api/v1/analytics/logs/${logId}/bottlenecks`
    );
    return {
      logId: response.log_id,
      bottlenecks: response.bottlenecks.map(transformBottleneck),
      totalBottlenecks: response.total_bottlenecks,
    };
  }

  /**
   * Analyze rework (repeated activities) in cases.
   * Identifies activities that are repeated within cases.
   */
  async getRework(logId: string): Promise<ReworkListResponse> {
    const response = await this.http.get<BEReworkListResponse>(
      `/api/v1/analytics/logs/${logId}/rework`
    );
    return {
      logId: response.log_id,
      reworkActivities: response.rework_activities.map(transformReworkActivity),
      totalReworkCases: response.total_rework_cases,
      reworkPercentage: response.rework_percentage,
    };
  }

  /**
   * Get service time statistics per activity.
   * Returns mean, median, min, max service times for each activity.
   */
  async getServiceTimes(logId: string): Promise<ServiceTimeResponse[]> {
    const response = await this.http.get<BEServiceTimeResponse[]>(
      `/api/v1/analytics/logs/${logId}/service-times`
    );
    return response.map(transformServiceTime);
  }

  /**
   * Get cycle time (case duration) statistics.
   * Returns mean, median, min, max duration across all cases.
   */
  async getCycleTime(logId: string): Promise<CycleTimeResponse> {
    const response = await this.http.get<BECycleTimeResponse>(
      `/api/v1/analytics/logs/${logId}/cycle-time`
    );
    return transformCycleTime(response);
  }

  /**
   * Get throughput metrics (cases per day/week/month).
   * Returns cases completed per time unit.
   */
  async getThroughput(logId: string): Promise<ThroughputResponse> {
    const response = await this.http.get<BEThroughputResponse>(
      `/api/v1/analytics/logs/${logId}/throughput`
    );
    return transformThroughput(response);
  }

  /**
   * Get frequent activity patterns/subsequences.
   * @param logId - Event log ID
   * @param minSupport - Minimum support threshold (default: 0.1 = 10%)
   */
  async getPatterns(logId: string, minSupport: number = 0.1): Promise<PatternResponse[]> {
    const response = await this.http.get<BEPatternResponse[]>(
      `/api/v1/analytics/logs/${logId}/patterns`,
      { min_support: minSupport }
    );
    return response.map(transformPattern);
  }

  /**
   * Get comprehensive performance data for FE PerformanceTab.
   * Combines cycle time, throughput, and bottlenecks.
   */
  async getPerformance(logId: string): Promise<PerformanceData> {
    const response = await this.http.get<BEPerformanceDashboardResponse>(
      `/api/v1/analytics/logs/${logId}/performance`
    );

    return {
      logId: response.log_id,
      cycleTime: transformCycleTime(response.cycle_time),
      throughput: transformThroughput(response.throughput),
      topBottlenecks: response.top_bottlenecks.map((b) => ({
        activity: b.activity,
        avgWaitingTime: b.avg_waiting_time_seconds,
        impactScore: b.bottleneck_impact_score,
      })),
      reworkSummary: {
        totalReworkCases:
          (response.rework_summary as { total_rework_cases?: number })?.total_rework_cases ?? 0,
        reworkPercentage:
          (response.rework_summary as { rework_percentage?: number })?.rework_percentage ?? 0,
      },
    };
  }
}
