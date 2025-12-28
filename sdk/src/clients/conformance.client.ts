/**
 * Conformance Client - Conformance Checking Operations
 * 
 * Business verbs:
 * - check() - Check conformance between log and model
 * - measureFitness() - Calculate fitness score
 * - measurePrecision() - Calculate precision score
 * - diagnose() - Get detailed conformance diagnostics
 * - findDeviations() - Detect deviations from model
 * - computeAlignments() - Calculate optimal alignments
 * - analyzeDeviationPatterns() - Cluster and analyze deviation patterns
 * - evaluateComprehensiveQuality() - Get all quality metrics
 */

import { HttpClient } from '../client.js';
import {
  CheckConformanceOptions,
  ConformanceResult,
  ConformanceDiagnostics,
  Deviation,
  DeviationAnalysis,
  AlignmentAnalysis,
  ComprehensiveQuality,
} from '../types/conformance.js';

export class ConformanceClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Check conformance between an event log and a process model.
   * Returns overall fitness and conformance status.
   */
  async check(options: CheckConformanceOptions): Promise<ConformanceResult> {
    const response = await this.http.post<{
      result_id: string;
      log_id: string;
      model_id: string;
      fitness: number;
      precision?: number;
      is_conformant: boolean;
      method: string;
    }>('/conformance/check', {
      log_id: options.logId,
      model_id: options.modelId,
      method: options.method ?? 'token_replay',
    });

    return {
      resultId: response.result_id,
      logId: response.log_id,
      modelId: response.model_id,
      fitness: response.fitness,
      precision: response.precision,
      isConformant: response.is_conformant,
      method: response.method,
    };
  }

  /**
   * Measure fitness score between log and model.
   * Fitness measures how well the log fits the model.
   */
  async measureFitness(logId: string, modelId: string): Promise<number> {
    const response = await this.http.get<{ fitness: number }>('/conformance/fitness', {
      log_id: logId,
      model_id: modelId,
    });
    return response.fitness;
  }

  /**
   * Measure precision score between log and model.
   * Precision measures how much behavior the model allows beyond the log.
   */
  async measurePrecision(logId: string, modelId: string): Promise<number> {
    const response = await this.http.get<{ precision: number }>('/conformance/precision', {
      log_id: logId,
      model_id: modelId,
    });
    return response.precision;
  }

  /**
   * Get detailed conformance diagnostics.
   * Shows fitting vs non-fitting traces and deviations.
   */
  async diagnose(logId: string, modelId: string): Promise<ConformanceDiagnostics> {
    return this.http.get<ConformanceDiagnostics>('/conformance/diagnostics', {
      log_id: logId,
      model_id: modelId,
    });
  }

  /**
   * Find deviations from the process model.
   * Returns cases that don't conform and their deviation details.
   */
  async findDeviations(logId: string, modelId: string, threshold = 0.8): Promise<Deviation[]> {
    const response = await this.http.get<{ deviations: Deviation[] }>('/conformance/deviations', {
      log_id: logId,
      model_id: modelId,
      threshold,
    });
    return response.deviations;
  }

  /**
   * Compute optimal alignments between log traces and model.
   * Shows sync moves, model moves, and log moves for each trace.
   */
  async computeAlignments(logId: string, modelId: string, limit = 100): Promise<AlignmentAnalysis> {
    return this.http.get<AlignmentAnalysis>('/conformance/alignments', {
      log_id: logId,
      model_id: modelId,
      limit,
    });
  }

  /**
   * Analyze and cluster deviation patterns.
   * Groups similar deviations and provides occurrence statistics.
   */
  async analyzeDeviationPatterns(logId: string, modelId: string): Promise<DeviationAnalysis> {
    return this.http.get<DeviationAnalysis>('/conformance/deviation-patterns', {
      log_id: logId,
      model_id: modelId,
    });
  }

  /**
   * Evaluate comprehensive quality metrics.
   * Combines fitness, precision, generalization, and simplicity.
   */
  async evaluateComprehensiveQuality(logId: string, modelId: string): Promise<ComprehensiveQuality> {
    return this.http.get<ComprehensiveQuality>('/conformance/comprehensive-quality', {
      log_id: logId,
      model_id: modelId,
    });
  }
}
