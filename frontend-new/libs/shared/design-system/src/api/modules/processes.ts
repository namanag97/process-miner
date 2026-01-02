/**
 * Processes Module - SDK methods for dataset operations
 */

import type { ApiClient } from '../client';
import type {
  PaginatedResponse,
  ProcessResponse,
  ProcessDetailResponse,
  ColumnDetectionResponse,
} from '../types';
import {
  transformProcess,
  transformProcessDetail,
  transformColumnDetection,
  EventLog,
  ColumnDetection,
} from '../transformers';

export interface ListProcessesOptions {
  page?: number;
  pageSize?: number;
  sourceFormat?: string;
}

export interface ProcessMetadata {
  name?: string;
  caseIdColumn?: string;
  activityColumn?: string;
  timestampColumn?: string;
  resourceColumn?: string;
}

export interface ProcessesModule {
  list: (options?: ListProcessesOptions) => Promise<{ items: EventLog[]; total: number; page: number; pageSize: number; pages: number }>;
  get: (id: string) => Promise<EventLog>;
  ingest: (file: File, metadata?: ProcessMetadata) => Promise<{ id: string }>;
  ingestWithProgress: (
    file: File,
    metadata?: ProcessMetadata,
    onProgress?: (percent: number) => void
  ) => Promise<{ id: string }>;
  delete: (id: string) => Promise<void>;
  detectColumns: (file: File) => Promise<ColumnDetection>;
  analyze: (logId: string) => Promise<Record<string, unknown>>;
}

export function createProcessesModule(client: ApiClient): ProcessesModule {
  return {
    async list(options?: ListProcessesOptions) {
      const response = await client.get<PaginatedResponse<ProcessResponse>>('/datasets', {
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
      const response = await client.get<ProcessDetailResponse>(`/datasets/${id}`);
      return transformProcessDetail(response);
    },

    async ingest(file: File, metadata?: ProcessMetadata) {
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

      const response = await client.postForm<ProcessResponse>('/datasets/upload', formData);
      return { id: response.id };
    },

    async ingestWithProgress(
      file: File,
      metadata?: ProcessMetadata,
      onProgress?: (percent: number) => void
    ) {
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

      const { promise } = client.postFormWithProgress<ProcessResponse>(
        '/datasets/upload',
        formData,
        onProgress
      );
      const response = await promise;
      return { id: response.id };
    },

    async delete(id: string) {
      await client.delete(`/datasets/${id}`);
    },

    async detectColumns(file: File) {
      const formData = new FormData();
      formData.append('file', file);

      const response = await client.postForm<ColumnDetectionResponse>('/datasets/detect-columns', formData);
      return transformColumnDetection(response);
    },

    async analyze(logId: string) {
      // Get statistics for a log
      return client.get<Record<string, unknown>>(`/datasets/${logId}/statistics`);
    },
  };
}
