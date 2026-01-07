/**
 * Conformance Module - SDK methods for conformance checking
 * 
 * FIXED: Standardized on datasetId (was datasetId)
 */

import type { ApiClient } from '../client';
import type { ConformanceResponse, DiagnosticsResponse } from '../types';

export interface ConformanceCheckOptions {
  datasetId: string;
  modelId: string;
  method?: 'token_replay' | 'alignment';
}

export interface ConformanceResult {
  id: string;
  datasetId: string;
  modelId: string;
  fitness: number;
  precision?: number;
  generalization?: number;
  simplicity?: number;
  method: string;
  isConformant: boolean;
  fittingTraces: number;
  totalTraces: number;
  createdAt: string;
}

export interface ConformanceModule {
  check: (options: ConformanceCheckOptions) => Promise<ConformanceResult>;
  getDiagnostics: (datasetId: string, modelId: string) => Promise<DiagnosticsResponse>;
}

function transformConformanceResponse(be: ConformanceResponse): ConformanceResult {
  return {
    id: be.id,
    datasetId: be.dataset_id,
    modelId: be.model_id,
    fitness: be.fitness,
    precision: be.precision,
    generalization: be.generalization,
    simplicity: be.simplicity,
    method: be.method,
    isConformant: be.is_conformant,
    fittingTraces: be.fitting_traces,
    totalTraces: be.total_traces,
    createdAt: be.created_at,
  };
}

export function createConformanceModule(client: ApiClient): ConformanceModule {
  return {
    async check(options: ConformanceCheckOptions) {
      const response = await client.post<ConformanceResponse>('/conformance/check', {
        dataset_id: options.datasetId,
        model_id: options.modelId,
        method: options.method ?? 'token_replay',
      });
      return transformConformanceResponse(response);
    },

    async getDiagnostics(datasetId: string, modelId: string) {
      return client.get<DiagnosticsResponse>(
        `/conformance/diagnostics/${encodeURIComponent(datasetId)}/${encodeURIComponent(modelId)}`
      );
    },
  };
}

