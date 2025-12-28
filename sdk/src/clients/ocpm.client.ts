/**
 * OCPM Client - Object-Centric Process Mining Operations
 * 
 * Business verbs:
 * - ingest() - Import OCEL file
 * - listLogs() - List all OCEL logs
 * - getLog() - Get OCEL log details
 * - removeLog() - Delete OCEL log
 * - listObjectTypes() - Get object types in log
 * - analyze() - Get OCEL statistics
 * - discoverOCPN() - Discover Object-Centric Petri Net
 * - listModels() - List discovered OC-PNs
 * - getModel() - Get OC-PN details
 */

import { HttpClient } from '../client.js';
import {
  OCELLog,
  ObjectType,
  OCELStatistics,
  OCPetriNet,
  IngestOCELOptions,
} from '../types/ocpm.js';

export class OCPMClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Ingest an OCEL file into the system.
   * Supports JSON, SQLite, and XML OCEL formats.
   */
  async ingest(file: File | Blob, options?: IngestOCELOptions): Promise<OCELLog> {
    const formData = new FormData();
    formData.append('file', file);
    if (options?.name) formData.append('name', options.name);
    return this.http.postForm<OCELLog>('/ocpm/upload', formData);
  }

  /**
   * List all OCEL logs.
   */
  async listLogs(): Promise<OCELLog[]> {
    const response = await this.http.get<{ logs: OCELLog[]; total: number }>('/ocpm/logs');
    return response.logs;
  }

  /**
   * Get OCEL log details.
   */
  async getLog(logId: string): Promise<OCELLog> {
    return this.http.get<OCELLog>(`/ocpm/logs/${logId}`);
  }

  /**
   * Remove an OCEL log from the system.
   */
  async removeLog(logId: string): Promise<void> {
    await this.http.delete(`/ocpm/logs/${logId}`);
  }

  /**
   * List object types in an OCEL log.
   */
  async listObjectTypes(logId: string): Promise<ObjectType[]> {
    const response = await this.http.get<{ objectTypes: ObjectType[] }>(
      `/ocpm/logs/${logId}/object-types`
    );
    return response.objectTypes;
  }

  /**
   * Analyze OCEL log and get detailed statistics.
   */
  async analyze(logId: string): Promise<OCELStatistics> {
    return this.http.get<OCELStatistics>(`/ocpm/logs/${logId}/statistics`);
  }

  /**
   * Discover an Object-Centric Petri Net from an OCEL log.
   */
  async discoverOCPN(logId: string, modelName?: string): Promise<OCPetriNet> {
    return this.http.post<OCPetriNet>('/ocpm/discover', {
      log_id: logId,
      model_name: modelName,
    });
  }

  /**
   * List all discovered Object-Centric Petri Nets.
   */
  async listModels(): Promise<OCPetriNet[]> {
    const response = await this.http.get<{ models: OCPetriNet[] }>('/ocpm/models');
    return response.models;
  }

  /**
   * Get Object-Centric Petri Net details.
   */
  async getModel(modelId: string): Promise<OCPetriNet> {
    return this.http.get<OCPetriNet>(`/ocpm/models/${modelId}`);
  }
}
