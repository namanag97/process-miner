/**
 * Analyses Module - SDK methods for saved analyses
 */

import type { ApiClient } from '../client';

export interface AnalysisConfig {
  miner_type?: 'alpha' | 'inductive' | 'heuristics';
  [key: string]: unknown;
}

export interface AnalysisCreateRequest {
  name: string;
  analysis_type: 'discovery' | 'conformance' | 'variants' | 'bottleneck';
  config?: AnalysisConfig;
}

export interface Analysis {
  id: string;
  logId: string;
  name: string;
  analysisType: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  config?: AnalysisConfig;
  resultSummary?: Record<string, unknown>;
  modelId?: string;
  createdAt: Date;
  completedAt?: Date;
  errorMessage?: string;
}

export interface AnalysisDetail extends Analysis {
  dfg?: {
    nodes: Array<{ id: string; name: string; frequency: number; is_start: boolean; is_end: boolean }>;
    edges: Array<{ source: string; target: string; frequency: number; probability: number }>;
    start_activities: Record<string, number>;
    end_activities: Record<string, number>;
    total_frequency: number;
  };
  variants?: Array<{
    variant_key: string;
    activity_trace: string;
    activities: string[];
    case_count: number;
    frequency_percent: number;
  }>;
  statistics?: Record<string, unknown>;
}

interface AnalysisResponse {
  id: string;
  log_id: string;
  name: string;
  analysis_type: string;
  status: string;
  config?: AnalysisConfig;
  result_summary?: Record<string, unknown>;
  model_id?: string;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

function transformAnalysis(response: AnalysisResponse): Analysis {
  return {
    id: response.id,
    logId: response.log_id,
    name: response.name,
    analysisType: response.analysis_type,
    status: response.status as Analysis['status'],
    config: response.config,
    resultSummary: response.result_summary,
    modelId: response.model_id,
    createdAt: new Date(response.created_at),
    completedAt: response.completed_at ? new Date(response.completed_at) : undefined,
    errorMessage: response.error_message,
  };
}

export interface AnalysesModule {
  create: (logId: string, request: AnalysisCreateRequest) => Promise<Analysis>;
  get: (id: string, includeResults?: boolean) => Promise<AnalysisDetail>;
  list: (logId?: string) => Promise<Analysis[]>;
  delete: (id: string) => Promise<void>;
}

export function createAnalysesModule(client: ApiClient): AnalysesModule {
  return {
    async create(logId: string, request: AnalysisCreateRequest) {
      const response = await client.post<AnalysisResponse>(
        `/analyses?log_id=${encodeURIComponent(logId)}`,
        request
      );
      return transformAnalysis(response);
    },

    async get(id: string, includeResults = true) {
      const response = await client.get<AnalysisResponse & { dfg?: unknown; variants?: unknown; statistics?: unknown }>(
        `/analyses/${id}`,
        { include_results: includeResults }
      );
      return {
        ...transformAnalysis(response),
        dfg: response.dfg,
        variants: response.variants,
        statistics: response.statistics,
      } as AnalysisDetail;
    },

    async list(logId?: string) {
      const params: Record<string, string> = {};
      if (logId) params.log_id = logId;
      
      const response = await client.get<{ items: AnalysisResponse[] }>('/analyses', params);
      return response.items.map(transformAnalysis);
    },

    async delete(id: string) {
      await client.delete(`/analyses/${id}`);
    },
  };
}
