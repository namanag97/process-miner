/**
 * Performance Client - Performance Analysis Operations
 *
 * Business verbs:
 * - analyze() - Run performance analysis on event log
 * - summarize() - Get performance summary
 * - findBottlenecks() - Identify process bottlenecks
 * - measureActivityPerformance() - Get activity-level metrics
 * - measureTransitionPerformance() - Get transition-level metrics
 * - buildDurationHistogram() - Build case duration distribution
 */

import { HttpClient } from "../client.js";
import {
  PerformanceSummary,
  BottleneckAnalysis,
  ActivityPerformance,
  TransitionPerformance,
  DurationHistogram,
} from "../types/performance.js";

export class PerformanceClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Run performance analysis on an event log.
   * Triggers computation of all performance metrics.
   */
  async analyze(logId: string): Promise<{ runId: string; status: string }> {
    return this.http.post<{ runId: string; status: string }>(`/performance/analyze/${logId}`);
  }

  /**
   * Get aggregated performance summary for an event log.
   * Returns average, median, min, max case durations.
   */
  async summarize(logId: string): Promise<PerformanceSummary> {
    return this.http.get<PerformanceSummary>(`/performance/summary/${logId}`);
  }

  /**
   * Find bottlenecks in the process.
   * Returns activities and transitions causing delays with severity levels.
   */
  async findBottlenecks(logId: string): Promise<BottleneckAnalysis> {
    return this.http.get<BottleneckAnalysis>(`/performance/bottlenecks/${logId}`);
  }

  /**
   * Measure performance at the activity level.
   * Returns duration metrics for each activity.
   */
  async measureActivityPerformance(logId: string): Promise<ActivityPerformance[]> {
    const response = await this.http.get<{ activities: ActivityPerformance[] }>(
      `/performance/activities/${logId}`
    );
    return response.activities;
  }

  /**
   * Measure performance at the transition level.
   * Returns duration metrics for each edge in the DFG.
   */
  async measureTransitionPerformance(logId: string): Promise<TransitionPerformance[]> {
    const response = await this.http.get<{ transitions: TransitionPerformance[] }>(
      `/performance/transitions/${logId}`
    );
    return response.transitions;
  }

  /**
   * Build case duration histogram.
   * Returns distribution of case durations across buckets.
   */
  async buildDurationHistogram(logId: string, bucketCount = 10): Promise<DurationHistogram> {
    return this.http.get<DurationHistogram>(`/performance/duration-histogram/${logId}`, {
      buckets: bucketCount,
    });
  }
}
