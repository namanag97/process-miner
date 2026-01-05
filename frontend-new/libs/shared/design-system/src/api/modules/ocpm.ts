/**
 * OCPM Module - SDK methods for Object-Centric Process Mining
 */

import type { ApiClient } from '../client';
import type {
  OCELLogResponse,
  OCELLogListResponse,
  OCELObjectTypeResponse,
  OCELStatisticsResponse,
  OCPetriNetResponse,
  OCDFGResponse,
} from '../types';
import {
  transformOCELLog,
  transformOCELStatistics,
  type OCELLog,
  type OCELStatistics,
} from '../transformers';

export interface OCPMModule {
  listLogs: () => Promise<{ logs: OCELLog[]; total: number }>;
  getLog: (id: string) => Promise<OCELLog>;
  uploadLog: (file: File, name?: string) => Promise<OCELLog>;
  deleteLog: (id: string) => Promise<void>;
  getObjectTypes: (datasetId: string) => Promise<OCELObjectTypeResponse[]>;
  getStatistics: (datasetId: string) => Promise<OCELStatistics>;
  discoverOCPN: (datasetId: string, modelName?: string) => Promise<OCPetriNetResponse>;
  getOCDFG: (datasetId: string) => Promise<OCDFGResponse>;
}

export function createOCPMModule(client: ApiClient): OCPMModule {
  return {
    async listLogs() {
      const response = await client.get<OCELLogListResponse>('/ocpm/logs');
      return {
        logs: response.logs.map(transformOCELLog),
        total: response.total,
      };
    },

    async getLog(id: string) {
      const response = await client.get<OCELLogResponse>(`/ocpm/logs/${id}`);
      return transformOCELLog(response);
    },

    async uploadLog(file: File, name?: string) {
      const formData = new FormData();
      formData.append('file', file);
      if (name) {
        formData.append('name', name);
      }
      const response = await client.postForm<OCELLogResponse>('/ocpm/upload', formData);
      return transformOCELLog(response);
    },

    async deleteLog(id: string) {
      await client.delete(`/ocpm/logs/${id}`);
    },

    async getObjectTypes(datasetId: string) {
      return client.get<OCELObjectTypeResponse[]>(`/ocpm/logs/${datasetId}/object-types`);
    },

    async getStatistics(datasetId: string) {
      const response = await client.get<OCELStatisticsResponse>(`/ocpm/logs/${datasetId}/statistics`);
      return transformOCELStatistics(response);
    },

    async discoverOCPN(datasetId: string, modelName?: string) {
      return client.post<OCPetriNetResponse>('/ocpm/discover', {
        dataset_id: datasetId,
        model_name: modelName,
      });
    },

    async getOCDFG(datasetId: string) {
      return client.get<OCDFGResponse>(`/ocpm/logs/${datasetId}/oc-dfg`);
    },
  };
}
