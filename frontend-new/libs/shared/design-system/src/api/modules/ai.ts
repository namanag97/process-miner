/**
 * AI Module - SDK methods for predictions and AI insights
 */

import type { ApiClient } from '../client';
import type { PredictorResponse } from '../types';

export interface Predictor {
  id: string;
  datasetId: string;
  targetType: string;
  algorithm: string;
  metrics?: Record<string, number>;
  trainedAt?: string;
}

export interface AIModule {
  listPredictors: (datasetId: string) => Promise<Predictor[]>;
  getInsights: (datasetId: string) => Promise<{ predictions: unknown[]; insights: unknown[] }>;
  getPredictorDetail: (id: string) => Promise<Predictor>;
}

function transformPredictor(be: PredictorResponse): Predictor {
  return {
    id: be.id,
    datasetId: be.dataset_id,
    targetType: be.target_type,
    algorithm: be.algorithm,
    metrics: be.metrics,
    trainedAt: be.trained_at,
  };
}

export function createAIModule(client: ApiClient): AIModule {
  return {
    async listPredictors(datasetId: string) {
      const response = await client.get<PredictorResponse[]>(`/predictions/datasets/${datasetId}/predictors`);
      return response.map(transformPredictor);
    },

    async getInsights(datasetId: string) {
      // Uses predictions endpoint for insights
      return client.get(`/predictions/datasets/${datasetId}/predictions`);
    },

    async getPredictorDetail(id: string) {
      const response = await client.get<PredictorResponse>(`/predictions/predictors/${id}`);
      return transformPredictor(response);
    },
  };
}
