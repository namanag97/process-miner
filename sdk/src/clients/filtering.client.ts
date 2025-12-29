/**
 * Filtering Client - Event Log Filtering Operations
 *
 * Business verbs:
 * - applyFilter() - Apply filter chain to event log
 * - previewFilter() - Preview filter impact without saving
 * - getFilterOptions() - Get available filter options for a log
 * - listFilteredLogs() - List all filtered versions of a log
 * - deleteFiltered() - Remove a filtered log
 * - getTemplates() - Get pre-built filter templates
 */

import { HttpClient } from "../client.js";
import {
  FilterRequest,
  FilteredLogResponse,
  FilterPreviewRequest,
  FilterPreviewResponse,
  FilterOptionsResponse,
  FilteredLogListResponse,
  FilterTemplateListResponse,
} from "../types/filtering.js";

export class FilteringClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Apply filter chain to an event log.
   * Creates a new filtered log (if save_result=true) or returns preview.
   */
  async applyFilter(logId: string, request: FilterRequest): Promise<FilteredLogResponse> {
    return this.http.post<FilteredLogResponse>(`/api/v1/filtering/logs/${logId}/apply`, request);
  }

  /**
   * Preview filter impact without saving.
   * Returns statistics about what would be filtered out.
   */
  async previewFilter(logId: string, request: FilterPreviewRequest): Promise<FilterPreviewResponse> {
    return this.http.post<FilterPreviewResponse>(`/api/v1/filtering/logs/${logId}/preview`, request);
  }

  /**
   * Get available filter options based on event log.
   * Returns unique activities, resources, time ranges, etc.
   */
  async getFilterOptions(logId: string): Promise<FilterOptionsResponse> {
    return this.http.get<FilterOptionsResponse>(`/api/v1/filtering/logs/${logId}/options`);
  }

  /**
   * List all filtered versions of an event log.
   */
  async listFilteredLogs(logId: string): Promise<FilteredLogListResponse> {
    return this.http.get<FilteredLogListResponse>(`/api/v1/filtering/logs/${logId}/results`);
  }

  /**
   * Delete a filtered log.
   */
  async deleteFiltered(logId: string, filteredId: string): Promise<void> {
    await this.http.delete(`/api/v1/filtering/logs/${logId}/results/${filteredId}`);
  }

  /**
   * Get pre-built filter templates.
   * Returns common filtering patterns (e.g., "only completed cases", "top 80% variants").
   */
  async getTemplates(): Promise<FilterTemplateListResponse> {
    return this.http.get<FilterTemplateListResponse>("/api/v1/filtering/templates");
  }
}
