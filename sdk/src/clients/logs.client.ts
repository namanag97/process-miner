/**
 * Logs Client - Event Log Operations
 *
 * Business verbs (following CodeOpinion guidance):
 * - ingest() - Import event log file into system
 * - preview() - Preview file before ingestion
 * - detectColumns() - Auto-detect CSV column mappings
 * - analyze() - Get log statistics
 * - assessQuality() - Run quality assessment
 * - listVariants() - Get process variants
 * - listActivities() - Get all activities
 * - remove() - Delete event log
 */

import { HttpClient } from "../client.js";
import { PaginationOptions } from "../types/common.js";
import {
  EventLog,
  EventLogDetails,
  IngestLogOptions,
  IngestionResult,
  ColumnDetection,
  FilePreview,
  LogStatistics,
  QualityReport,
  ProcessVariant,
  PaginatedLogs,
  UpdateLogMetadata,
} from "../types/logs.js";

export interface ListLogsOptions extends PaginationOptions {
  search?: string;
  sortBy?: "created_at" | "name" | "total_cases" | "total_events";
  sortOrder?: "asc" | "desc";
}

export class LogsClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Ingest an event log file into the system.
   * Supports CSV and XES formats.
   */
  async ingest(file: File | Blob, options?: IngestLogOptions): Promise<IngestionResult> {
    const formData = new FormData();
    formData.append("file", file);

    if (options?.name) formData.append("name", options.name);
    if (options?.caseIdColumn) formData.append("case_id_column", options.caseIdColumn);
    if (options?.activityColumn) formData.append("activity_column", options.activityColumn);
    if (options?.timestampColumn) formData.append("timestamp_column", options.timestampColumn);
    if (options?.resourceColumn) formData.append("resource_column", options.resourceColumn);

    const response = await this.http.postForm<{
      id: string;
      name: string;
      total_cases: number;
      total_events: number;
      validation: { is_valid: boolean; errors: string[]; warnings: string[] };
    }>("/api/v1/processes/upload", formData);

    return {
      id: response.id,
      name: response.name,
      totalCases: response.total_cases,
      totalEvents: response.total_events,
      validation: {
        isValid: response.validation.is_valid,
        errors: response.validation.errors,
        warnings: response.validation.warnings,
      },
    };
  }

  /**
   * Preview a file before ingestion.
   * Returns column information and sample rows.
   */
  async preview(file: File | Blob): Promise<FilePreview> {
    const formData = new FormData();
    formData.append("file", file);
    return this.http.postForm<FilePreview>("/api/v1/processes/preview", formData);
  }

  /**
   * Detect column types from a CSV file.
   * Suggests mappings for case ID, activity, timestamp, and resource.
   */
  async detectColumns(file: File | Blob): Promise<ColumnDetection> {
    const formData = new FormData();
    formData.append("file", file);
    return this.http.postForm<ColumnDetection>("/api/v1/processes/detect-columns", formData);
  }

  /**
   * List all event logs with optional filtering and pagination.
   */
  async list(options?: ListLogsOptions): Promise<PaginatedLogs> {
    return this.http.get<PaginatedLogs>("/api/v1/processes", {
      page: options?.page,
      page_size: options?.pageSize,
      search: options?.search,
      sort_by: options?.sortBy,
      sort_order: options?.sortOrder,
    });
  }

  /**
   * Get detailed information about a specific event log.
   */
  async get(logId: string): Promise<EventLogDetails> {
    return this.http.get<EventLogDetails>(`/api/v1/processes/${logId}`);
  }

  /**
   * Update event log metadata.
   */
  async updateMetadata(logId: string, updates: UpdateLogMetadata): Promise<EventLog> {
    return this.http.patch<EventLog>(`/api/v1/processes/${logId}`, updates);
  }

  /**
   * Analyze event log and get detailed statistics.
   */
  async analyze(logId: string): Promise<LogStatistics> {
    return this.http.get<LogStatistics>(`/api/v1/processes/${logId}/statistics`);
  }

  /**
   * Assess quality of an event log.
   * Returns completeness, validity scores, and issues found.
   */
  async assessQuality(logId: string): Promise<QualityReport> {
    return this.http.get<QualityReport>(`/api/v1/processes/${logId}/quality`);
  }

  /**
   * List process variants in an event log.
   */
  async listVariants(logId: string, limit = 50): Promise<ProcessVariant[]> {
    return this.http.get<ProcessVariant[]>(`/api/v1/processes/${logId}/variants`, { limit });
  }

  /**
   * List all unique activities in an event log.
   */
  async listActivities(logId: string): Promise<string[]> {
    const response = await this.http.get<{ activities: string[] }>(`/api/v1/processes/${logId}/activities`);
    return response.activities;
  }

  /**
   * Remove an event log from the system.
   */
  async remove(logId: string): Promise<void> {
    await this.http.delete(`/api/v1/processes/${logId}`);
  }
}
