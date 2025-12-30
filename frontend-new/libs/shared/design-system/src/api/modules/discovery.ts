/**
 * Discovery Module - SDK methods for process discovery and visualization
 */

import type { ApiClient } from '../client';
import type {
  DFGResponse,
  VariantResponse,
  ActivityDetailResponse,
} from '../types';
import {
  transformDFG,
  transformVariants,
  transformActivityDetails,
  DFGData,
  Variant,
  ActivityDetail,
} from '../transformers';

export interface DFGOptions {
  includePerformance?: boolean;
}

export interface VariantOptions {
  topN?: number;
  topKPercent?: number;
  includeComplexity?: boolean;
  sortBy?: 'frequency' | 'complexity' | 'duration';
}

export interface DiscoveryModule {
  buildDFG: (logId: string, options?: DFGOptions) => Promise<DFGData>;
  getVariants: (logId: string, options?: VariantOptions) => Promise<Variant[]>;
  getActivities: (logId: string, sortBy?: string) => Promise<ActivityDetail[]>;
  discover: (options: { logId: string; minerType?: string; modelName?: string }) => Promise<{ modelId: string }>;
}

export function createDiscoveryModule(client: ApiClient): DiscoveryModule {
  return {
    async buildDFG(logId: string, options?: DFGOptions) {
      const response = await client.get<DFGResponse>(`/visualization/${logId}/dfg`, {
        include_performance: options?.includePerformance ?? false,
      });
      return transformDFG(response);
    },

    async getVariants(logId: string, options?: VariantOptions) {
      const response = await client.get<VariantResponse[]>(`/processes/${logId}/variants`, {
        top_n: options?.topN ?? 20,
        top_k_percent: options?.topKPercent,
        include_complexity: options?.includeComplexity ?? false,
        sort_by: options?.sortBy,
      });
      return transformVariants(response);
    },

    async getActivities(logId: string, sortBy?: string) {
      const response = await client.get<ActivityDetailResponse[]>(`/processes/${logId}/activities`, {
        sort_by: sortBy,
      });
      return transformActivityDetails(response);
    },

    async discover(options: { logId: string; minerType?: string; modelName?: string }) {
      const response = await client.post<{ id: string }>('/discovery/discover', {
        log_id: options.logId,
        miner_type: options.minerType ?? 'inductive',
        model_name: options.modelName,
      });
      return { modelId: response.id };
    },
  };
}
