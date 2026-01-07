/**
 * Analytics Module - SDK methods for performance and rework analytics
 */

import type { ApiClient } from '../client';
import type {
  PerformanceDashboardResponse,
  ReworkListResponse,
  CycleTimeResponse,
  ThroughputResponse,
  BottleneckResponse,
} from '../types';
import {
  transformPerformance,
  transformRework,
  PerformanceData,
  ReworkData,
} from '../transformers';

// Process Summary type for LLM context
export interface ProcessSummaryData {
  datasetId: string;
  cycleTime: {
    minSeconds: number;
    maxSeconds: number;
    avgSeconds: number;
    medianSeconds: number;
  };
  throughput: {
    totalCases: number;
    completedCases: number;
    casesPerDay: number;
    casesPerWeek: number;
  };
  bottlenecks: Array<{
    activity: string;
    avgWaitingTimeSeconds: number;
    severity: string;
    isBottleneck: boolean;
  }>;
  rework: {
    totalReworkCases: number;
    reworkPercentage: number;
    activities: Array<{
      activity: string;
      reworkCount: number;
      reworkPercentage: number;
    }>;
  };
  patterns: Array<{
    pattern: string[];
    support: number;
    frequency: number;
  }>;
}

export interface PatternResponse {
  pattern: string[];
  support: number;
  confidence: number;
  frequency: number;
}

export interface AnalyticsModule {
  getPerformance: (datasetId: string) => Promise<PerformanceData>;
  getRework: (datasetId: string) => Promise<ReworkData>;
  getBottlenecks: (datasetId: string) => Promise<{ dataset_id: string; bottlenecks: BottleneckResponse[]; total_bottlenecks: number }>;
  getCycleTime: (datasetId: string) => Promise<CycleTimeResponse>;
  getThroughput: (datasetId: string) => Promise<ThroughputResponse>;
  getPatterns: (datasetId: string, minSupport?: number) => Promise<PatternResponse[]>;
  getProcessSummary: (datasetId: string) => Promise<ProcessSummaryData>;
}

export function createAnalyticsModule(client: ApiClient): AnalyticsModule {
  return {
    async getPerformance(datasetId: string) {
      const response = await client.get<PerformanceDashboardResponse>(
        `/analytics/datasets/${datasetId}/performance`
      );
      return transformPerformance(response);
    },

    async getRework(datasetId: string) {
      const response = await client.get<ReworkListResponse>(
        `/analytics/datasets/${datasetId}/rework`
      );
      return transformRework(response);
    },

    async getBottlenecks(datasetId: string) {
      return client.get(`/analytics/datasets/${datasetId}/bottlenecks`);
    },

    async getCycleTime(datasetId: string) {
      return client.get(`/analytics/datasets/${datasetId}/cycle-time`);
    },

    async getThroughput(datasetId: string) {
      return client.get(`/analytics/datasets/${datasetId}/throughput`);
    },

    async getPatterns(datasetId: string, minSupport = 0.1) {
      return client.get(`/analytics/datasets/${datasetId}/patterns`, { min_support: minSupport });
    },

    async getProcessSummary(datasetId: string): Promise<ProcessSummaryData> {
      // Aggregate multiple analytics endpoints into a unified summary
      const [cycleTimeRes, throughputRes, bottlenecksRes, reworkRes, patternsRes] = await Promise.allSettled([
        client.get<CycleTimeResponse>(`/analytics/datasets/${datasetId}/cycle-time`),
        client.get<ThroughputResponse>(`/analytics/datasets/${datasetId}/throughput`),
        client.get<{ bottlenecks: BottleneckResponse[] }>(`/analytics/datasets/${datasetId}/bottlenecks`),
        client.get<ReworkListResponse>(`/analytics/datasets/${datasetId}/rework`),
        client.get<PatternResponse[]>(`/analytics/datasets/${datasetId}/patterns`, { min_support: 0.1 }),
      ]);

      // Extract data with fallbacks for failed requests
      const cycleTime = cycleTimeRes.status === 'fulfilled' ? cycleTimeRes.value : null;
      const throughput = throughputRes.status === 'fulfilled' ? throughputRes.value : null;
      const bottlenecks = bottlenecksRes.status === 'fulfilled' ? bottlenecksRes.value : null;
      const rework = reworkRes.status === 'fulfilled' ? reworkRes.value : null;
      const patterns = patternsRes.status === 'fulfilled' ? patternsRes.value : [];

      return {
        datasetId,
        cycleTime: {
          minSeconds: cycleTime?.min_seconds ?? 0,
          maxSeconds: cycleTime?.max_seconds ?? 0,
          avgSeconds: cycleTime?.avg_seconds ?? 0,
          medianSeconds: cycleTime?.median_seconds ?? 0,
        },
        throughput: {
          totalCases: throughput?.total_cases ?? 0,
          completedCases: throughput?.completed_cases ?? 0,
          casesPerDay: throughput?.cases_per_day ?? 0,
          casesPerWeek: throughput?.cases_per_week ?? 0,
        },
        bottlenecks: (bottlenecks?.bottlenecks ?? []).map((b) => ({
          activity: b.activity,
          avgWaitingTimeSeconds: b.avg_waiting_time_seconds,
          severity: b.severity,
          isBottleneck: b.is_bottleneck,
        })),
        rework: {
          totalReworkCases: rework?.total_rework_cases ?? 0,
          reworkPercentage: rework?.rework_percentage ?? 0,
          activities: (rework?.rework_activities ?? []).map((r) => ({
            activity: r.activity,
            reworkCount: r.rework_count,
            reworkPercentage: r.rework_percentage,
          })),
        },
        patterns: patterns.map((p) => ({
          pattern: p.pattern,
          support: p.support,
          frequency: p.frequency,
        })),
      };
    },
  };
}

