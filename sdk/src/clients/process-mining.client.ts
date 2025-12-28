/**
 * Process Mining Client - PM4Py Advanced Features
 * 
 * Business verbs:
 * - analyzeFootprints() - Get behavioral relations matrix
 * - extractLogSkeleton() - Extract declarative constraints
 * - analyzeSNA() - Perform social network analysis
 * - detectBatches() - Detect batch processing patterns
 * - buildTransitionSystem() - Build transition system
 * - measureDuration() - Get duration statistics
 * - measureArrivalRate() - Get case arrival rate
 * - runComprehensiveAnalysis() - Run full PM4Py analysis
 * - listVariants() - Get process variants
 * - listStartActivities() - Get start activities
 * - listEndActivities() - Get end activities
 */

import { HttpClient } from '../client.js';
import {
  FootprintMatrix,
  LogSkeleton,
  SNAResult,
  BatchPattern,
  TransitionSystem,
  DurationStats,
  ArrivalRate,
  ComprehensiveAnalysis,
} from '../types/process-mining.js';

export class ProcessMiningClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Analyze footprints (behavioral relations) of an event log.
   * Returns directly-follows, causal, parallel, and choice relations.
   */
  async analyzeFootprints(logId: string): Promise<FootprintMatrix> {
    return this.http.get<FootprintMatrix>(`/process-mining/footprints/${logId}`);
  }

  /**
   * Extract log skeleton (declarative constraints).
   * Returns always-after, always-before, never-together relations.
   */
  async extractLogSkeleton(logId: string): Promise<LogSkeleton> {
    return this.http.get<LogSkeleton>(`/process-mining/log-skeleton/${logId}`);
  }

  /**
   * Perform social network analysis.
   */
  async analyzeSNA(logId: string, metric = 'handover'): Promise<SNAResult> {
    return this.http.get<SNAResult>(`/process-mining/sna/${logId}`, { metric });
  }

  /**
   * Discover organizational roles.
   */
  async discoverRoles(logId: string): Promise<{ roles: Array<{ roleName: string; resources: string[]; activities: string[] }> }> {
    return this.http.get(`/process-mining/roles/${logId}`);
  }

  /**
   * Detect batch processing patterns.
   */
  async detectBatches(logId: string): Promise<BatchPattern[]> {
    const response = await this.http.get<{ batches: BatchPattern[] }>(
      `/process-mining/batches/${logId}`
    );
    return response.batches;
  }

  /**
   * Build transition system from event log.
   */
  async buildTransitionSystem(logId: string): Promise<TransitionSystem> {
    return this.http.get<TransitionSystem>(`/process-mining/transition-system/${logId}`);
  }

  /**
   * Discover process tree using inductive miner.
   */
  async discoverProcessTree(logId: string): Promise<{ tree: string; root: unknown }> {
    return this.http.get(`/process-mining/process-tree/${logId}`);
  }

  /**
   * Measure case duration statistics.
   */
  async measureDuration(logId: string): Promise<DurationStats> {
    return this.http.get<DurationStats>(`/process-mining/duration-stats/${logId}`);
  }

  /**
   * Measure average case arrival rate.
   */
  async measureArrivalRate(logId: string): Promise<ArrivalRate> {
    return this.http.get<ArrivalRate>(`/process-mining/arrival-rate/${logId}`);
  }

  /**
   * Run comprehensive PM4Py analysis.
   * Returns summary, variants, activities in a single call.
   */
  async runComprehensiveAnalysis(logId: string): Promise<ComprehensiveAnalysis> {
    return this.http.get<ComprehensiveAnalysis>(`/process-mining/comprehensive/${logId}`);
  }

  /**
   * Get process variants with counts.
   */
  async listVariants(logId: string): Promise<Array<{ activities: string[]; count: number }>> {
    const response = await this.http.get<{ variants: Array<{ activities: string[]; count: number }> }>(
      `/process-mining/variants/${logId}`
    );
    return response.variants;
  }

  /**
   * Get start activities with frequencies.
   */
  async listStartActivities(logId: string): Promise<Record<string, number>> {
    const response = await this.http.get<{ startActivities: Record<string, number> }>(
      `/process-mining/start-activities/${logId}`
    );
    return response.startActivities;
  }

  /**
   * Get end activities with frequencies.
   */
  async listEndActivities(logId: string): Promise<Record<string, number>> {
    const response = await this.http.get<{ endActivities: Record<string, number> }>(
      `/process-mining/end-activities/${logId}`
    );
    return response.endActivities;
  }
}
