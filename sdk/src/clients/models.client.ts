/**
 * Models Client - Process Model Management
 *
 * Business verbs:
 * - list() - List all process models
 * - get() - Get model details
 * - updateMetadata() - Update model metadata
 * - visualize() - Get model visualization
 * - remove() - Delete a model
 */

import { HttpClient } from "../client.js";
import { ProcessModelSummary, UpdateModelMetadata } from "../types/models.js";

export class ModelsClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * List all discovered process models.
   */
  async list(): Promise<ProcessModelSummary[]> {
    const response = await this.http.get<{ models: ProcessModelSummary[] }>("/models/");
    return response.models;
  }

  /**
   * Get process model details.
   */
  async get(modelId: string): Promise<ProcessModelSummary> {
    return this.http.get<ProcessModelSummary>(`/models/${modelId}`);
  }

  /**
   * Update process model metadata.
   */
  async updateMetadata(
    modelId: string,
    updates: UpdateModelMetadata
  ): Promise<ProcessModelSummary> {
    return this.http.patch<ProcessModelSummary>(`/models/${modelId}`, updates);
  }

  /**
   * Get visual representation of a process model.
   */
  async visualize(modelId: string, format: "svg" | "png" = "svg"): Promise<string> {
    return this.http.get<string>(`/models/${modelId}/visualize`, { format });
  }

  /**
   * Remove a process model from the system.
   */
  async remove(modelId: string): Promise<void> {
    await this.http.delete(`/models/${modelId}`);
  }
}
