/**
 * Analytics Module - SDK methods for performance and rework analytics
 */

import type { ApiClient } from '../client';
import type {
  PerformanceDashboardResponse,
  ReworkListResponse,
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
  getBottlenecks: (logId: string) => Promise<unknown>;
  getCycleTime: (logId: string) => Promise<unknown>;
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
