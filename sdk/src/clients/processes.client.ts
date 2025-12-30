/**
 * Processes Client - Event Log Operations
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
} from "../types/processes.js";

// =============================================================================
// Backend Response Types (snake_case)
// =============================================================================

interface BEProcessResponse {
  id: string;
  name: string;
  source_format: string;
  total_events: number;
  total_cases: number;
  total_activities: number;
  activities: string[];
  created_at: string;
  source_file?: string;
}

interface BEProcessListResponse {
  items: BEProcessResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

interface BEStatisticsResponse {
  total_events: number;
  total_cases: number;
  total_activities: number;
  total_variants: number;
  activities: string[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  avg_case_duration_seconds: number | null;
  min_case_duration_seconds: number | null;
  max_case_duration_seconds: number | null;
  date_range: { start: string; end: string } | null;
}

interface BEVariantResponse {
  variant_key: string;
  activity_trace: string;
  case_count: number;
  frequency_percent: number;
  avg_duration_seconds: number | null;
}

// =============================================================================
// Transformation Helpers
// =============================================================================

function transformProcessToEventLog(be: BEProcessResponse): EventLog {
  return {
    id: be.id,
    name: be.name,
    sourceFile: be.source_file,
    totalCases: be.total_cases,
    totalEvents: be.total_events,
    createdAt: be.created_at,
  };
}

function transformStatistics(be: BEStatisticsResponse, logId: string): LogStatistics {
  return {
    logId,
    eventCount: be.total_events,
    caseCount: be.total_cases,
    activityCount: be.total_activities,
    variantCount: be.total_variants,
    activities: be.activities,
    startActivities: be.start_activities,
    endActivities: be.end_activities,
    avgCaseDurationSeconds: be.avg_case_duration_seconds ?? undefined,
    minCaseDurationSeconds: be.min_case_duration_seconds ?? undefined,
    maxCaseDurationSeconds: be.max_case_duration_seconds ?? undefined,
    dateRange: be.date_range ?? undefined,
  };
}

function transformVariant(be: BEVariantResponse): ProcessVariant {
  return {
    key: be.variant_key,
    activities: be.activity_trace.split(" -> "),
    caseCount: be.case_count,
    length: be.activity_trace.split(" -> ").length,
    frequencyPercent: be.frequency_percent,
    avgDurationSeconds: be.avg_duration_seconds ?? undefined,
  };
}

export interface ListLogsOptions extends PaginationOptions {
  search?: string;
  sortBy?: "created_at" | "name" | "total_cases" | "total_events";
  sortOrder?: "asc" | "desc";
}

export class ProcessesClient {
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
    const response = await this.http.get<BEProcessListResponse>("/api/v1/processes", {
      page: options?.page,
      page_size: options?.pageSize,
      search: options?.search,
      sort_by: options?.sortBy,
      sort_order: options?.sortOrder,
    });

    return {
      items: response.items.map(transformProcessToEventLog),
      total: response.total,
      page: response.page,
      pageSize: response.page_size,
      totalPages: response.pages,
    };
  }

  /**
   * Get detailed information about a specific event log.
   */
  async get(logId: string): Promise<EventLogDetails> {
    const response = await this.http.get<
      BEProcessResponse & {
        statistics?: BEStatisticsResponse;
      }
    >(`/api/v1/processes/${logId}`);

    return {
      ...transformProcessToEventLog(response),
      uniqueActivities: response.total_activities,
      uniqueResources: 0, // Not available in BE response
      variantCount: response.statistics?.total_variants ?? 0,
      dateRange: response.statistics?.date_range ?? undefined,
    };
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
    const response = await this.http.get<BEStatisticsResponse>(
      `/api/v1/processes/${logId}/statistics`
    );
    return transformStatistics(response, logId);
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
    const response = await this.http.get<BEVariantResponse[]>(
      `/api/v1/processes/${logId}/variants`,
      { limit }
    );
    return response.map(transformVariant);
  }

  /**
   * List all unique activities in an event log.
   */
  async listActivities(logId: string): Promise<string[]> {
    const response = await this.http.get<{ activities: string[] }>(
      `/api/v1/processes/${logId}/activities`
    );
    return response.activities;
  }

  /**
   * Remove an event log from the system.
   */
  async remove(logId: string): Promise<void> {
    await this.http.delete(`/api/v1/processes/${logId}`);
  }
}
