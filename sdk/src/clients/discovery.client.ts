/**
 * Discovery Client - Process Model Discovery Operations
 * 
 * Business verbs:
 * - discover() - Discover process model from event log
 * - buildDFG() - Build Directly-Follows Graph
 * - extractPetriNet() - Extract Petri Net from model
 * - extractProcessTree() - Extract Process Tree from model
 * - visualize() - Generate visual representation
 * - evaluateQuality() - Evaluate model quality metrics
 * - listMiners() - Get available mining algorithms
 */

import { HttpClient } from '../client.js';
import {
  DiscoverModelOptions,
  ProcessModel,
  DirectlyFollowsGraph,
  PetriNet,
  ProcessTree,
  ModelQualityMetrics,
  MinerInfo,
} from '../types/discovery.js';

export class DiscoveryClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * List all available mining algorithms.
   */
  async listMiners(): Promise<MinerInfo[]> {
    return this.http.get<MinerInfo[]>('/discovery/miners');
  }

  /**
   * Discover a process model from an event log.
   * Uses the specified mining algorithm (default: inductive miner).
   */
  async discover(options: DiscoverModelOptions): Promise<ProcessModel> {
    const response = await this.http.post<{
      model_id: string;
      model_name: string;
      miner_type: string;
      model_format: string;
      source_log_id: string;
    }>('/discovery/discover', {
      log_id: options.logId,
      miner_type: options.minerType ?? 'inductive',
      model_name: options.modelName,
    });

    return {
      modelId: response.model_id,
      modelName: response.model_name,
      minerType: response.miner_type,
      modelFormat: response.model_format,
      sourceLogId: response.source_log_id,
    };
  }

  /**
   * Build a Directly-Follows Graph from an event log.
   * Returns nodes (activities) and edges (transitions) with frequencies.
   */
  async buildDFG(logId: string): Promise<DirectlyFollowsGraph> {
    return this.http.get<DirectlyFollowsGraph>(`/discovery/dfg/${logId}/detailed`);
  }

  /**
   * Build a simple DFG representation (JSON).
   */
  async buildSimpleDFG(logId: string): Promise<{ nodes: string[]; edges: Array<{ source: string; target: string; frequency: number }> }> {
    return this.http.get(`/discovery/dfg/${logId}`);
  }

  /**
   * Extract Petri Net representation from a process model.
   * Returns places, transitions, arcs, and markings.
   */
  async extractPetriNet(modelId: string): Promise<PetriNet> {
    return this.http.get<PetriNet>(`/discovery/petri-net/${modelId}`);
  }

  /**
   * Extract Process Tree representation from a process model.
   * Returns hierarchical tree structure.
   */
  async extractProcessTree(modelId: string): Promise<ProcessTree> {
    return this.http.get<ProcessTree>(`/discovery/process-tree/${modelId}`);
  }

  /**
   * Generate visual representation of a process model.
   * Returns SVG image by default.
   */
  async visualize(modelId: string, format: 'svg' | 'png' = 'svg'): Promise<string> {
    return this.http.get<string>(`/discovery/visualize/${modelId}`, { format });
  }

  /**
   * Evaluate quality metrics of a process model.
   * Returns fitness, precision, generalization, and simplicity scores.
   */
  async evaluateQuality(modelId: string, logId?: string): Promise<ModelQualityMetrics> {
    const params: Record<string, string | undefined> = {};
    if (logId) params.log_id = logId;
    return this.http.get<ModelQualityMetrics>(`/discovery/model/${modelId}/quality`, params);
  }
}
