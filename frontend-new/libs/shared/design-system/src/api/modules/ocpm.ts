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
  getObjectTypes: (logId: string) => Promise<OCELObjectTypeResponse[]>;
  getStatistics: (logId: string) => Promise<OCELStatistics>;
  discoverOCPN: (logId: string, modelName?: string) => Promise<OCPetriNetResponse>;
  getOCDFG: (logId: string) => Promise<OCDFGResponse>;
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

    async getObjectTypes(logId: string) {
      return client.get<OCELObjectTypeResponse[]>(`/ocpm/logs/${logId}/object-types`);
    },

    async getStatistics(logId: string) {
      const response = await client.get<OCELStatisticsResponse>(`/ocpm/logs/${logId}/statistics`);
      return transformOCELStatistics(response);
    },

    async discoverOCPN(logId: string, modelName?: string) {
      return client.post<OCPetriNetResponse>('/ocpm/discover', {
        log_id: logId,
        model_name: modelName,
      });
    },

    async getOCDFG(logId: string) {
      return client.get<OCDFGResponse>(`/ocpm/logs/${logId}/oc-dfg`);
    },
  };
}
