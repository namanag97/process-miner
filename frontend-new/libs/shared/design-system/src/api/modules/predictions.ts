/**
 * Predictions Module - SDK methods for ML predictions
 *
 * Business verbs:
 * - trainPredictor() - Train a prediction model
 * - listPredictors() - List predictors for a log
 * - getPredictor() - Get predictor details
 * - predict() - Make a single prediction
 * - predictBatch() - Make batch predictions
 * - deletePredictor() - Remove a predictor
 */

import type { ApiClient } from '../client';

// Response types
export interface PredictorMetrics {
  accuracy?: number;
  f1_score?: number;
  mae?: number;
  activities?: string[];
}

export interface Predictor {
  id: string;
  logId: string;
  targetType: 'next_activity' | 'remaining_time';
  algorithm: string;
  metrics: PredictorMetrics;
  trainedAt: string;
}

export interface PredictionResult {
  predictorId: string;
  casePrefix: string[];
  prediction: string | number;
  confidence: number;
  alternatives?: Array<{ activity: string; probability: number }>;
}

export interface TrainOptions {
  targetType: 'next_activity' | 'remaining_time';
  algorithm?: 'random_forest' | 'xgboost' | 'lstm';
}

export interface PredictionsModule {
  trainPredictor: (logId: string, options: TrainOptions) => Promise<{ id: string } | { jobId: string; status: string }>;
  listPredictors: (logId: string) => Promise<Predictor[]>;
  getPredictor: (predictorId: string) => Promise<Predictor>;
  predict: (predictorId: string, casePrefix: string[]) => Promise<PredictionResult>;
  predictBatch: (predictorId: string, cases: Array<{ case_prefix: string[] }>) => Promise<PredictionResult[]>;
  deletePredictor: (predictorId: string) => Promise<void>;
  getJobStatus: (jobId: string) => Promise<{ status: string; progress?: number; result?: unknown }>;
}

// Backend response types (snake_case)
interface PredictorResponse {
  id: string;
  log_id: string;
  target_type: 'next_activity' | 'remaining_time';
  algorithm: string;
  metrics: PredictorMetrics;
  trained_at: string;
}

interface PredictorListResponse {
  log_id: string;
  predictors: PredictorResponse[];
  total: number;
}

interface PredictionResponse {
  predictor_id: string;
  case_prefix: string[];
  prediction: string | number;
  confidence: number;
  alternatives?: Array<{ activity: string; probability: number }>;
}

function transformPredictor(be: PredictorResponse): Predictor {
  return {
    id: be.id,
    logId: be.log_id,
    targetType: be.target_type,
    algorithm: be.algorithm,
    metrics: be.metrics,
    trainedAt: be.trained_at,
  };
}

function transformPrediction(be: PredictionResponse): PredictionResult {
  return {
    predictorId: be.predictor_id,
    casePrefix: be.case_prefix,
    prediction: be.prediction,
    confidence: be.confidence,
    alternatives: be.alternatives,
  };
}

export function createPredictionsModule(client: ApiClient): PredictionsModule {
  return {
    async trainPredictor(logId: string, options: TrainOptions) {
      const response = await client.post<{ id?: string; job_id?: string; status?: string }>(
        `/predictions/logs/${logId}/train`,
        {
          target_type: options.targetType,
          algorithm: options.algorithm ?? 'random_forest',
        }
      );

      if (response.job_id) {
        return { jobId: response.job_id, status: response.status ?? 'pending' };
      }
      return { id: response.id! };
    },

    async listPredictors(logId: string) {
      const response = await client.get<PredictorListResponse>(
        `/predictions/logs/${logId}/predictors`
      );
      return response.predictors.map(transformPredictor);
    },

    async getPredictor(predictorId: string) {
      const response = await client.get<PredictorResponse>(
        `/predictions/predictors/${predictorId}`
      );
      return transformPredictor(response);
    },

    async predict(predictorId: string, casePrefix: string[]) {
      const response = await client.post<PredictionResponse>(
        `/predictions/predictors/${predictorId}/predict`,
        { case_prefix: casePrefix }
      );
      return transformPrediction(response);
    },

    async predictBatch(predictorId: string, cases: Array<{ case_prefix: string[] }>) {
      const response = await client.post<{ predictions: PredictionResponse[] }>(
        `/predictions/predictors/${predictorId}/predict-batch`,
        { cases }
      );
      return response.predictions.map(transformPrediction);
    },

    async deletePredictor(predictorId: string) {
      await client.delete(`/predictions/predictors/${predictorId}`);
    },

    async getJobStatus(jobId: string) {
      return client.get<{ status: string; progress?: number; result?: unknown }>(
        `/predictions/jobs/${jobId}`
      );
    },
  };
}
