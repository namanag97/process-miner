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
 * - getPerformanceDashboard() - Get comprehensive performance dashboard
 */

import { HttpClient } from "../client.js";
import {
  BottleneckListResponse,
  ReworkListResponse,
  ServiceTimeResponse,
  CycleTimeResponse,
  ThroughputResponse,
  PatternResponse,
  PerformanceDashboardResponse,
} from "../types/analytics.js";

export class AnalyticsClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Detect process bottlenecks based on waiting times.
   * Returns activities with highest waiting times.
   */
  async getBottlenecks(logId: string): Promise<BottleneckListResponse> {
    return this.http.get<BottleneckListResponse>(`/api/v1/analytics/logs/${logId}/bottlenecks`);
  }

  /**
   * Analyze rework (repeated activities) in cases.
   * Identifies activities that are repeated within cases.
   */
  async getRework(logId: string): Promise<ReworkListResponse> {
    return this.http.get<ReworkListResponse>(`/api/v1/analytics/logs/${logId}/rework`);
  }

  /**
   * Get service time statistics per activity.
   * Returns mean, median, min, max service times for each activity.
   */
  async getServiceTimes(logId: string): Promise<ServiceTimeResponse[]> {
    return this.http.get<ServiceTimeResponse[]>(`/api/v1/analytics/logs/${logId}/service-times`);
  }

  /**
   * Get cycle time (case duration) statistics.
   * Returns mean, median, min, max duration across all cases.
   */
  async getCycleTime(logId: string): Promise<CycleTimeResponse> {
    return this.http.get<CycleTimeResponse>(`/api/v1/analytics/logs/${logId}/cycle-time`);
  }

  /**
   * Get throughput metrics (cases per day/week/month).
   * Returns cases completed per time unit.
   */
  async getThroughput(logId: string): Promise<ThroughputResponse> {
    return this.http.get<ThroughputResponse>(`/api/v1/analytics/logs/${logId}/throughput`);
  }

  /**
   * Get frequent activity patterns/subsequences.
   * @param logId - Event log ID
   * @param minSupport - Minimum support threshold (default: 0.1 = 10%)
   */
  async getPatterns(logId: string, minSupport: number = 0.1): Promise<PatternResponse[]> {
    return this.http.get<PatternResponse[]>(`/api/v1/analytics/logs/${logId}/patterns`, {
      min_support: minSupport,
    });
  }

  /**
   * Get comprehensive performance dashboard.
   * Combines cycle time, throughput, bottlenecks, and rework summary.
   */
  async getPerformanceDashboard(logId: string): Promise<PerformanceDashboardResponse> {
    return this.http.get<PerformanceDashboardResponse>(`/api/v1/analytics/logs/${logId}/performance`);
  }
}
