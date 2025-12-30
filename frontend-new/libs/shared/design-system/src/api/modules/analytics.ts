/**
 * Analytics Module - SDK methods for performance and rework analytics
 */

import type { ApiClient } from '../client';
import type {
  PerformanceDashboardResponse,
  ReworkListResponse,
  CycleTimeResponse,
} from '../types';
import {
  transformPerformance,
  transformRework,
  PerformanceData,
  ReworkData,
} from '../transformers';

export interface AnalyticsModule {
  getPerformance: (logId: string) => Promise<PerformanceData>;
  getRework: (logId: string) => Promise<ReworkData>;
  getBottlenecks: (logId: string) => Promise<{ log_id: string; bottlenecks: unknown[]; total_bottlenecks: number }>;
  getCycleTime: (logId: string) => Promise<CycleTimeResponse>;
}

export function createAnalyticsModule(client: ApiClient): AnalyticsModule {
  return {
    async getPerformance(logId: string) {
      const response = await client.get<PerformanceDashboardResponse>(
        `/analytics/logs/${logId}/performance`
      );
      return transformPerformance(response);
    },

    async getRework(logId: string) {
      const response = await client.get<ReworkListResponse>(
        `/analytics/logs/${logId}/rework`
      );
      return transformRework(response);
    },

    async getBottlenecks(logId: string) {
      return client.get(`/analytics/logs/${logId}/bottlenecks`);
    },

    async getCycleTime(logId: string) {
      return client.get(`/analytics/logs/${logId}/cycle-time`);
    },
  };
}
