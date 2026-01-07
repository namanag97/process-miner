/**
 * Predictions & Conformance Zod Schemas
 */
import { z } from 'zod';

// ============================================
// Predictor
// ============================================

export const PredictorResponseSchema = z.object({
  id: z.string(),
  dataset_id: z.string(),
  target_type: z.string(),
  algorithm: z.string(),
  metrics: z.record(z.string(), z.number()).optional(),
  trained_at: z.string().optional(),
});

export type PredictorResponse = z.infer<typeof PredictorResponseSchema>;

export const PredictorListResponseSchema = z.object({
  predictors: z.array(PredictorResponseSchema),
  total: z.number(),
});

export type PredictorListResponse = z.infer<typeof PredictorListResponseSchema>;

// ============================================
// Prediction
// ============================================

export const PredictionAlternativeSchema = z.object({
  activity: z.string(),
  probability: z.number(),
});

export type PredictionAlternative = z.infer<typeof PredictionAlternativeSchema>;

export const PredictionResponseSchema = z.object({
  predictor_id: z.string(),
  case_prefix: z.array(z.string()),
  prediction: z.string(),
  confidence: z.number(),
  alternatives: z.array(PredictionAlternativeSchema).optional(),
});

export type PredictionResponse = z.infer<typeof PredictionResponseSchema>;

// ============================================
// Train Predictor
// ============================================

export const TrainPredictorRequestSchema = z.object({
  dataset_id: z.string(),
  target_type: z.enum(['next_activity', 'remaining_time', 'outcome']),
  algorithm: z.enum(['lstm', 'random_forest', 'xgboost']).optional(),
});

export type TrainPredictorRequest = z.infer<typeof TrainPredictorRequestSchema>;

// ============================================
// Conformance
// ============================================

export const ConformanceResponseSchema = z.object({
  id: z.string(),
  dataset_id: z.string(),
  model_id: z.string(),
  fitness: z.number(),
  precision: z.number().optional(),
  generalization: z.number().optional(),
  simplicity: z.number().optional(),
  method: z.string(),
  is_conformant: z.boolean(),
  fitting_traces: z.number(),
  total_traces: z.number(),
  created_at: z.string(),
});

export type ConformanceResponse = z.infer<typeof ConformanceResponseSchema>;

// ============================================
// Deviation / Diagnostics
// ============================================

export const DeviationDetailSchema = z.object({
  case_id: z.string(),
  activity: z.string(),
  violation_type: z.string(),
  expected_after: z.string().optional(),
  frequency: z.number(),
  impact: z.string(),
});

export type DeviationDetail = z.infer<typeof DeviationDetailSchema>;

export const DiagnosticsResponseSchema = z.object({
  fitness: z.number(),
  precision: z.number().optional(),
  generalization: z.number().optional(),
  simplicity: z.number().optional(),
  total_traces: z.number(),
  fitting_traces: z.number(),
  non_fitting_traces: z.number(),
  fitness_ratio: z.number(),
  deviations: z.array(DeviationDetailSchema).optional(),
});

export type DiagnosticsResponse = z.infer<typeof DiagnosticsResponseSchema>;

// ============================================
// AI Insights
// ============================================

export const InsightSchema = z.object({
  id: z.string(),
  type: z.enum(['bottleneck', 'anomaly', 'pattern', 'recommendation']),
  title: z.string(),
  description: z.string(),
  severity: z.enum(['low', 'medium', 'high']).optional(),
  affected_activities: z.array(z.string()).optional(),
  impact_score: z.number().optional(),
});

export type Insight = z.infer<typeof InsightSchema>;

export const InsightsResponseSchema = z.object({
  dataset_id: z.string(),
  predictions: z.array(PredictionResponseSchema).optional(),
  insights: z.array(InsightSchema),
  generated_at: z.string(),
});

export type InsightsResponse = z.infer<typeof InsightsResponseSchema>;
