/**
 * Analytics Client - Process Analytics Operations
 * 
 * Business verbs:
 * - getDashboard() - Get comprehensive dashboard data
 * - discoverInsights() - Find process insights
 * - detectAnomalies() - Identify anomalous cases
 * - analyzeVariants() - Analyze variant distribution
 * - analyzeResources() - Analyze resource utilization
 * - analyzeTime() - Analyze temporal patterns
 */

import { HttpClient } from '../client.js';
import {
  DashboardData,
  ProcessInsight,
  AnomalyAnalysis,
  VariantStatistics,
  ResourceStatistics,
  TimeAnalysis,
} from '../types/analytics.js';

export class AnalyticsClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Get comprehensive dashboard data for an event log.
   * Includes overview metrics, top variants, and distributions.
   */
  async getDashboard(logId: string): Promise<DashboardData> {
    return this.http.get<DashboardData>(`/analytics/dashboard/${logId}`);
  }

  /**
   * Discover process insights from the event log.
   * Returns actionable findings with recommendations.
   */
  async discoverInsights(logId: string): Promise<ProcessInsight[]> {
    const response = await this.http.get<{ insights: ProcessInsight[] }>(
      `/analytics/insights/${logId}`
    );
    return response.insights;
  }

  /**
   * Detect anomalous cases in the event log.
   * Identifies cases that deviate from normal behavior.
   */
  async detectAnomalies(logId: string): Promise<AnomalyAnalysis> {
    return this.http.get<AnomalyAnalysis>(`/analytics/anomalies/${logId}`);
  }

  /**
   * Analyze variant distribution and statistics.
   */
  async analyzeVariants(logId: string): Promise<VariantStatistics> {
    return this.http.get<VariantStatistics>(`/analytics/variants/${logId}`);
  }

  /**
   * Analyze resource utilization and workload.
   */
  async analyzeResources(logId: string): Promise<ResourceStatistics> {
    return this.http.get<ResourceStatistics>(`/analytics/resources/${logId}`);
  }

  /**
   * Analyze temporal patterns in the process.
   * Returns cases over time, peak hours, and duration trends.
   */
  async analyzeTime(logId: string): Promise<TimeAnalysis> {
    return this.http.get<TimeAnalysis>(`/analytics/time/${logId}`);
  }
}
