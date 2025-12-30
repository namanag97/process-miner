/**
 * Logs Module - SDK methods for event log operations
 */

import type { ApiClient } from '../client';
import type {
  PaginatedResponse,
  ProcessResponse,
  ProcessDetailResponse,
  ColumnDetectionResponse,
} from '../types';
import { transformProcess, transformProcessDetail, EventLog } from '../transformers';

export interface ListLogsOptions {
  page?: number;
  pageSize?: number;
  sourceFormat?: string;
}

export interface LogMetadata {
  name?: string;
  caseIdColumn?: string;
  activityColumn?: string;
  timestampColumn?: string;
  resourceColumn?: string;
}

export interface LogsModule {
  list: (options?: ListLogsOptions) => Promise<{ items: EventLog[]; total: number; page: number; pageSize: number; pages: number }>;
  get: (id: string) => Promise<EventLog>;
  ingest: (file: File, metadata?: LogMetadata) => Promise<{ id: string }>;
  delete: (id: string) => Promise<void>;
  detectColumns: (file: File) => Promise<ColumnDetectionResponse>;
  analyze: (logId: string) => Promise<Record<string, unknown>>;
}

export function createLogsModule(client: ApiClient): LogsModule {
  return {
    async list(options?: ListLogsOptions) {
      const response = await client.get<PaginatedResponse<ProcessResponse>>('/processes', {
        page: options?.page ?? 1,
        page_size: options?.pageSize ?? 20,
        source_format: options?.sourceFormat,
      });

      return {
        items: response.items.map(transformProcess),
        total: response.total,
        page: response.page,
        pageSize: response.page_size,
        pages: response.pages,
      };
    },

    async get(id: string) {
      const response = await client.get<ProcessDetailResponse>(`/processes/${id}`);
      return transformProcessDetail(response);
    },

    async ingest(file: File, metadata?: LogMetadata) {
      const formData = new FormData();
      formData.append('file', file);
      
      if (metadata?.name) {
        formData.append('name', metadata.name);
      }
      if (metadata?.caseIdColumn) {
        formData.append('case_id_column', metadata.caseIdColumn);
      }
      if (metadata?.activityColumn) {
        formData.append('activity_column', metadata.activityColumn);
      }
      if (metadata?.timestampColumn) {
        formData.append('timestamp_column', metadata.timestampColumn);
      }
      if (metadata?.resourceColumn) {
        formData.append('resource_column', metadata.resourceColumn);
      }

      const response = await client.postForm<ProcessResponse>('/processes/upload', formData);
      return { id: response.id };
    },

    async delete(id: string) {
      await client.delete(`/processes/${id}`);
    },

    async detectColumns(file: File) {
      const formData = new FormData();
      formData.append('file', file);
      
      return client.postForm<ColumnDetectionResponse>('/processes/detect-columns', formData);
    },

    async analyze(logId: string) {
      // Get statistics for a log
      return client.get<Record<string, unknown>>(`/processes/${logId}/statistics`);
    },
  };
}
