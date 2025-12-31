/**
 * Projects Module - SDK methods for project operations
 */

import type { ApiClient } from '../client';

export interface Project {
  id: string;
  name: string;
  description: string | null;
  tags: string[];
  totalFiles: number;
  totalAnalyses: number;
  createdAt: string;
  updatedAt: string | null;
}

export interface ProjectDetail extends Project {
  eventLogs: Array<{
    id: string;
    name: string;
    sourceFormat: string;
    totalEvents: number;
    totalCases: number;
    totalActivities: number;
    activities: string[];
    createdAt: string;
    sourceFile: string | null;
  }>;
}

export interface CreateProjectData {
  name: string;
  description?: string;
  tags?: string[];
}

export interface UpdateProjectData {
  name?: string;
  description?: string;
  tags?: string[];
}

interface ProjectApiResponse {
  id: string;
  name: string;
  description: string | null;
  tags: string[];
  total_files: number;
  total_analyses: number;
  created_at: string;
  updated_at: string | null;
}

interface ProjectDetailApiResponse extends ProjectApiResponse {
  event_logs: Array<{
    id: string;
    name: string;
    source_format: string;
    total_events: number;
    total_cases: number;
    total_activities: number;
    activities: string[];
    created_at: string;
    source_file: string | null;
  }>;
}

interface ProjectListApiResponse {
  items: ProjectApiResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

function transformProject(response: ProjectApiResponse): Project {
  return {
    id: response.id,
    name: response.name,
    description: response.description,
    tags: response.tags,
    totalFiles: response.total_files,
    totalAnalyses: response.total_analyses,
    createdAt: response.created_at,
    updatedAt: response.updated_at,
  };
}

function transformProjectDetail(response: ProjectDetailApiResponse): ProjectDetail {
  return {
    ...transformProject(response),
    eventLogs: response.event_logs.map((log) => ({
      id: log.id,
      name: log.name,
      sourceFormat: log.source_format,
      totalEvents: log.total_events,
      totalCases: log.total_cases,
      totalActivities: log.total_activities,
      activities: log.activities,
      createdAt: log.created_at,
      sourceFile: log.source_file,
    })),
  };
}

export interface ProjectsModule {
  list: (options?: { page?: number; pageSize?: number; search?: string }) => Promise<{
    items: Project[];
    total: number;
    page: number;
    pageSize: number;
    pages: number;
  }>;
  get: (id: string) => Promise<ProjectDetail>;
  create: (data: CreateProjectData) => Promise<Project>;
  update: (id: string, data: UpdateProjectData) => Promise<Project>;
  delete: (id: string) => Promise<void>;
  addFile: (projectId: string, logId: string) => Promise<ProjectDetail>;
  removeFile: (projectId: string, logId: string) => Promise<void>;
}

export function createProjectsModule(client: ApiClient): ProjectsModule {
  return {
    async list(options) {
      const response = await client.get<ProjectListApiResponse>('/projects', {
        page: options?.page ?? 1,
        page_size: options?.pageSize ?? 20,
        search: options?.search,
      });

      return {
        items: response.items.map(transformProject),
        total: response.total,
        page: response.page,
        pageSize: response.page_size,
        pages: response.pages,
      };
    },

    async get(id: string) {
      const response = await client.get<ProjectDetailApiResponse>(`/projects/${id}`);
      return transformProjectDetail(response);
    },

    async create(data: CreateProjectData) {
      const response = await client.post<ProjectApiResponse>('/projects', data);
      return transformProject(response);
    },

    async update(id: string, data: UpdateProjectData) {
      const response = await client.post<ProjectApiResponse>(`/projects/${id}`, data);
      return transformProject(response);
    },

    async delete(id: string) {
      await client.delete(`/projects/${id}`);
    },

    async addFile(projectId: string, logId: string) {
      const response = await client.post<ProjectDetailApiResponse>(
        `/projects/${projectId}/files/${logId}`
      );
      return transformProjectDetail(response);
    },

    async removeFile(projectId: string, logId: string) {
      await client.delete(`/projects/${projectId}/files/${logId}`);
    },
  };
}
