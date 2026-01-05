/**
 * Discovery Module - SDK methods for process discovery and visualization
 */

import type { ApiClient } from '../client';
import type {
  DFGResponse,
  VariantResponse,
  ActivityDetailResponse,
  ProcessExplorerDataResponse,
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

export interface ExplorerDataOptions {
  includePerformance?: boolean;
  includeComplexity?: boolean;
  topVariants?: number;
}

export interface ExplorerData {
  datasetId: string;
  dfg: DFGData;
  variants: Variant[];
  activities: ActivityDetail[];
  statistics: {
    totalEvents: number;
    totalCases: number;
    totalActivities: number;
    totalVariants: number;
    activities: string[];
    startActivities: Record<string, number>;
    endActivities: Record<string, number>;
    avgCaseDurationSeconds?: number;
    minCaseDurationSeconds?: number;
    maxCaseDurationSeconds?: number;
    dateRange?: { start: string; end: string };
  };
}

export interface DiscoveryModule {
  buildDFG: (datasetId: string, options?: DFGOptions) => Promise<DFGData>;
  getVariants: (datasetId: string, options?: VariantOptions) => Promise<Variant[]>;
  getActivities: (datasetId: string, sortBy?: string) => Promise<ActivityDetail[]>;
  getExplorerData: (datasetId: string, options?: ExplorerDataOptions) => Promise<ExplorerData>;
  discover: (options: { datasetId: string; minerType?: string; modelName?: string }) => Promise<{ modelId: string }>;
}

export function createDiscoveryModule(client: ApiClient): DiscoveryModule {
  return {
    async buildDFG(datasetId: string, options?: DFGOptions) {
      const response = await client.get<DFGResponse>(`/visualization/${datasetId}/dfg`, {
        include_performance: options?.includePerformance ?? false,
      });
      return transformDFG(response);
    },

    async getVariants(datasetId: string, options?: VariantOptions) {
      const response = await client.get<VariantResponse[]>(`/datasets/${datasetId}/variants`, {
        top_n: options?.topN ?? 20,
        top_k_percent: options?.topKPercent,
        include_complexity: options?.includeComplexity ?? false,
        sort_by: options?.sortBy,
      });
      return transformVariants(response);
    },

    async getActivities(datasetId: string, sortBy?: string) {
      const response = await client.get<ActivityDetailResponse[]>(`/datasets/${datasetId}/activities`, {
        sort_by: sortBy,
      });
      return transformActivityDetails(response);
    },

    async getExplorerData(datasetId: string, options?: ExplorerDataOptions): Promise<ExplorerData> {
      const response = await client.get<ProcessExplorerDataResponse>(`/visualization/${datasetId}/explorer-data`, {
        include_performance: options?.includePerformance ?? true,
        include_complexity: options?.includeComplexity ?? true,
        top_variants: options?.topVariants ?? 50,
      });

      // Transform to frontend-friendly format
      return {
        datasetId: response.dataset_id,
        dfg: transformDFG(response.dfg),
        variants: transformVariants(response.variants),
        activities: transformActivityDetails(response.activities),
        statistics: {
          totalEvents: response.statistics.total_events,
          totalCases: response.statistics.total_cases,
          totalActivities: response.statistics.total_activities,
          totalVariants: response.statistics.total_variants,
          activities: response.statistics.activities,
          startActivities: response.statistics.start_activities,
          endActivities: response.statistics.end_activities,
          avgCaseDurationSeconds: response.statistics.avg_case_duration_seconds,
          minCaseDurationSeconds: response.statistics.min_case_duration_seconds,
          maxCaseDurationSeconds: response.statistics.max_case_duration_seconds,
          dateRange: response.statistics.date_range,
        },
      };
    },

    async discover(options: { datasetId: string; minerType?: string; modelName?: string }) {
      const response = await client.post<{ id: string }>('/discovery/discover', {
        dataset_id: options.datasetId,
        miner_type: options.minerType ?? 'inductive',
        model_name: options.modelName,
      });
      return { modelId: response.id };
    },
  };
}
