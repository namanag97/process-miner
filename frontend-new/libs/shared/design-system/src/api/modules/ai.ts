/**
 * AI Module - SDK methods for predictions and AI insights
 */

import type { ApiClient } from '../client';
import type { PredictorResponse } from '../types';

export interface Predictor {
  id: string;
  logId: string;
  targetType: string;
  algorithm: string;
  metrics?: Record<string, number>;
  trainedAt?: string;
}

export interface AIModule {
  listPredictors: (logId: string) => Promise<Predictor[]>;
  getInsights: (logId: string) => Promise<{ predictions: unknown[]; insights: unknown[] }>;
  getPredictorDetail: (id: string) => Promise<Predictor>;
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

export function createAIModule(client: ApiClient): AIModule {
  return {
    async listPredictors(logId: string) {
      const response = await client.get<PredictorResponse[]>(`/predictions/logs/${logId}/predictors`);
      return response.map(transformPredictor);
    },

    async getInsights(logId: string) {
      // Uses predictions endpoint for insights
      return client.get(`/predictions/logs/${logId}/predictions`);
    },

    async getPredictorDetail(id: string) {
      const response = await client.get<PredictorResponse>(`/predictions/predictors/${id}`);
      return transformPredictor(response);
    },
  };
}
