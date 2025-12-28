/**
 * Conformance Checking Types for Process Mining SDK
 * Business-focused types for conformance analysis operations
 */

import { HypermediaResponse } from './common.js';

// =============================================================================
// BUSINESS OPERATION INPUTS
// =============================================================================

export type ConformanceMethod = 'token_replay' | 'alignments';

export interface CheckConformanceOptions {
  logId: string;
  modelId: string;
  method?: ConformanceMethod;
}

// =============================================================================
// CONFORMANCE RESULTS
// =============================================================================

export interface ConformanceResult extends HypermediaResponse {
  resultId: string;
  logId: string;
  modelId: string;
  fitness: number;
  precision?: number;
  isConformant: boolean;
  method: string;
}

export interface ConformanceDiagnostics extends HypermediaResponse {
  totalTraces: number;
  fittingTraces: number;
  nonFittingTraces: number;
  traceFitnessRatio: number;
  deviations: Deviation[];
}

// =============================================================================
// DEVIATIONS
// =============================================================================

export interface Deviation {
  caseId: string;
  deviationType: 'missing_activity' | 'unexpected_activity' | 'wrong_order';
  details: string;
  activity?: string;
}

export interface DeviationPattern extends HypermediaResponse {
  patternId: string;
  patternType: string;
  description: string;
  activity?: string;
  occurrenceCount: number;
  occurrenceRate: number;
  affectedCases: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface DeviationAnalysis extends HypermediaResponse {
  logId: string;
  modelId: string;
  totalDeviations: number;
  deviationRate: number;
  totalCasesWithDeviations: number;
  patterns: DeviationPattern[];
}

// =============================================================================
// ALIGNMENTS
// =============================================================================

export type AlignmentStepType = 'sync' | 'model_move' | 'log_move';

export interface AlignmentStep {
  stepIndex: number;
  stepType: AlignmentStepType;
  logActivity?: string;
  modelActivity?: string;
  cost: number;
}

export interface CaseAlignment extends HypermediaResponse {
  caseId: string;
  fitness: number;
  isFitting: boolean;
  alignmentCost: number;
  syncMoves: number;
  modelMoves: number;
  logMoves: number;
  alignment: AlignmentStep[];
}

export interface AlignmentAnalysis extends HypermediaResponse {
  logId: string;
  modelId: string;
  totalTraces: number;
  fittingTraces: number;
  averageFitness: number;
  averageCost: number;
  alignedTraces: CaseAlignment[];
}

// =============================================================================
// COMPREHENSIVE QUALITY
// =============================================================================

export interface ComprehensiveQuality extends HypermediaResponse {
  logId: string;
  modelId: string;
  fitness: number;
  traceFitness: number;
  logFitness: number;
  precision?: number;
  generalization?: number;
  simplicity?: number;
  fittingTracesCount: number;
  nonFittingTracesCount: number;
  fittingTracesPercentage: number;
  overallQuality: number;
}
