/**
 * Discovery Client - Process Model Discovery Operations
 *
 * Business verbs:
 * - discover() - Discover process model from event log
 * - buildDFG() - Build Directly-Follows Graph
 * - getVariants() - Get process variants (alias for logs.listVariants)
 * - getActivities() - Get activities (alias for logs.listActivities)
 * - extractPetriNet() - Extract Petri Net from model
 * - extractProcessTree() - Extract Process Tree from model
 * - visualize() - Generate visual representation
 * - evaluateQuality() - Evaluate model quality metrics
 * - listMiners() - Get available mining algorithms
 */

import { HttpClient } from "../client.js";
import {
  DiscoverModelOptions,
  ProcessModel,
  DirectlyFollowsGraph,
  DFGNode,
  DFGEdge,
  PetriNet,
  ProcessTree,
  ModelQualityMetrics,
  MinerInfo,
} from "../types/discovery.js";

// =============================================================================
// Backend Response Types (snake_case)
// =============================================================================

interface BEDFGNode {
  id: string;
  name: string;
  frequency: number;
  is_start: boolean;
  is_end: boolean;
}

interface BEDFGEdge {
  source: string;
  target: string;
  frequency: number;
  probability: number;
  avg_duration_seconds?: number;
  min_duration_seconds?: number;
  max_duration_seconds?: number;
}

interface BEDFGResponse {
  nodes: BEDFGNode[];
  edges: BEDFGEdge[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  total_frequency: number;
}

interface BEVariantResponse {
  variant_key: string;
  activity_trace: string;
  case_count: number;
  frequency_percent: number;
  avg_duration_seconds: number | null;
  complexity_score?: number;
}

interface BEActivityResponse {
  activity: string;
  frequency: number;
  frequency_percent: number;
  avg_duration_seconds: number | null;
  min_duration_seconds: number | null;
  max_duration_seconds: number | null;
  is_start_activity: boolean;
  is_end_activity: boolean;
  position_avg: number | null;
  resources: string[];
}

// =============================================================================
// Transformation Helpers
// =============================================================================

function transformDFGNode(be: BEDFGNode): DFGNode {
  return {
    name: be.name,
    frequency: be.frequency,
    isStart: be.is_start,
    isEnd: be.is_end,
  };
}

function transformDFGEdge(be: BEDFGEdge): DFGEdge {
  return {
    source: be.source,
    target: be.target,
    frequency: be.frequency,
    probability: be.probability,
    avgDurationSeconds: be.avg_duration_seconds,
  };
}

function transformDFG(be: BEDFGResponse, logId: string): DirectlyFollowsGraph {
  return {
    logId,
    nodes: be.nodes.map(transformDFGNode),
    edges: be.edges.map(transformDFGEdge),
    startActivities: be.start_activities,
    endActivities: be.end_activities,
    totalCases: be.total_frequency,
    totalEvents: 0, // Not available in BE response
  };
}

// =============================================================================
// Options Types
// =============================================================================

export interface BuildDFGOptions {
  includePerformance?: boolean;
}

export interface GetVariantsOptions {
  topN?: number;
  includeComplexity?: boolean;
}

// =============================================================================
// FE-Expected Return Types (for methods that wrap BE calls)
// =============================================================================

export interface Variant {
  key: string;
  activities: string[];
  caseCount: number;
  frequencyPercent: number;
  avgDuration: number | null;
  complexityScore?: number;
}

export interface ActivityDetail {
  id: string;
  name: string;
  frequency: number;
  frequencyPercent: number;
  avgDuration: number | null;
  minDuration: number | null;
  maxDuration: number | null;
  isStart: boolean;
  isEnd: boolean;
  resources: string[];
}

export class DiscoveryClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * List all available mining algorithms.
   */
  async listMiners(): Promise<MinerInfo[]> {
    return this.http.get<MinerInfo[]>("/api/v1/discovery/miners");
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
    }>("/api/v1/discovery/discover", {
      log_id: options.logId,
      miner_type: options.minerType ?? "inductive",
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
   * @param logId - Event log ID
   * @param options - Optional settings for DFG generation
   */
  async buildDFG(logId: string, options?: BuildDFGOptions): Promise<DirectlyFollowsGraph> {
    const params: Record<string, string | boolean | undefined> = {};
    if (options?.includePerformance !== undefined) {
      params.include_performance = options.includePerformance;
    }

    const response = await this.http.get<BEDFGResponse>(
      `/api/v1/discovery/dfg/${logId}/detailed`,
      params
    );
    return transformDFG(response, logId);
  }

  /**
   * Build a simple DFG representation (JSON).
   */
  async buildSimpleDFG(logId: string): Promise<{
    nodes: string[];
    edges: Array<{ source: string; target: string; frequency: number }>;
  }> {
    return this.http.get(`/discovery/dfg/${logId}`);
  }

  /**
   * Get process variants for an event log.
   * @param logId - Event log ID
   * @param options - Optional settings (topN, includeComplexity)
   */
  async getVariants(logId: string, options?: GetVariantsOptions): Promise<Variant[]> {
    const params: Record<string, string | number | boolean | undefined> = {};
    if (options?.topN !== undefined) params.limit = options.topN;
    if (options?.includeComplexity !== undefined)
      params.include_complexity = options.includeComplexity;

    const response = await this.http.get<BEVariantResponse[]>(
      `/api/v1/processes/${logId}/variants`,
      params
    );

    return response.map((v) => ({
      key: v.variant_key,
      activities: v.activity_trace.split(" -> "),
      caseCount: v.case_count,
      frequencyPercent: v.frequency_percent,
      avgDuration: v.avg_duration_seconds,
      complexityScore: v.complexity_score,
    }));
  }

  /**
   * Get activity details for an event log.
   * @param logId - Event log ID
   */
  async getActivities(logId: string): Promise<ActivityDetail[]> {
    const response = await this.http.get<BEActivityResponse[]>(
      `/api/v1/processes/${logId}/activities/details`
    );

    return response.map((a) => ({
      id: a.activity,
      name: a.activity,
      frequency: a.frequency,
      frequencyPercent: a.frequency_percent,
      avgDuration: a.avg_duration_seconds,
      minDuration: a.min_duration_seconds,
      maxDuration: a.max_duration_seconds,
      isStart: a.is_start_activity,
      isEnd: a.is_end_activity,
      resources: a.resources,
    }));
  }

  /**
   * Extract Petri Net representation from a process model.
   * Returns places, transitions, arcs, and markings.
   */
  async extractPetriNet(modelId: string): Promise<PetriNet> {
    return this.http.get<PetriNet>(`/api/v1/discovery/petri-net/${modelId}`);
  }

  /**
   * Extract Process Tree representation from a process model.
   * Returns hierarchical tree structure.
   */
  async extractProcessTree(modelId: string): Promise<ProcessTree> {
    return this.http.get<ProcessTree>(`/api/v1/discovery/process-tree/${modelId}`);
  }

  /**
   * Generate visual representation of a process model.
   * Returns SVG image by default.
   */
  async visualize(modelId: string, format: "svg" | "png" = "svg"): Promise<string> {
    return this.http.get<string>(`/api/v1/discovery/visualize/${modelId}`, { format });
  }

  /**
   * Evaluate quality metrics of a process model.
   * Returns fitness, precision, generalization, and simplicity scores.
   */
  async evaluateQuality(modelId: string, logId?: string): Promise<ModelQualityMetrics> {
    const params: Record<string, string | undefined> = {};
    if (logId) params.log_id = logId;
    return this.http.get<ModelQualityMetrics>(`/api/v1/discovery/model/${modelId}/quality`, params);
  }
}
