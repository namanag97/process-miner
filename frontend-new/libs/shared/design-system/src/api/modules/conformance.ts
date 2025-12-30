/**
 * Conformance Module - SDK methods for conformance checking
 */

import type { ApiClient } from '../client';
import type { ConformanceResponse, DiagnosticsResponse } from '../types';

export interface ConformanceCheckOptions {
  logId: string;
  modelId: string;
  method?: 'token_replay' | 'alignment';
}

export interface ConformanceResult {
  id: string;
  logId: string;
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
  getDiagnostics: (logId: string, modelId: string) => Promise<DiagnosticsResponse>;
}

function transformConformanceResponse(be: ConformanceResponse): ConformanceResult {
  return {
    id: be.id,
    logId: be.log_id,
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
        log_id: options.logId,
        model_id: options.modelId,
        method: options.method ?? 'token_replay',
      });
      return transformConformanceResponse(response);
    },

    async getDiagnostics(logId: string, modelId: string) {
      return client.get<DiagnosticsResponse>(
        `/conformance/diagnostics/${encodeURIComponent(logId)}/${encodeURIComponent(modelId)}`
      );
    },
  };
}
