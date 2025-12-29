/**
 * Process Discovery Types for Process Mining SDK
 * Business-focused types for model discovery operations
 */

import { HypermediaResponse } from "./common.js";

// =============================================================================
// MINING ALGORITHMS
// =============================================================================

export type MinerType = "alpha" | "alpha_plus" | "heuristics" | "inductive" | "dfg";

export interface MinerInfo extends HypermediaResponse {
  id: string;
  name: string;
  description: string;
  outputFormat: string;
  parameters?: MinerParameter[];
}

export interface MinerParameter {
  name: string;
  type: "number" | "string" | "boolean";
  default?: unknown;
  description?: string;
}

// =============================================================================
// BUSINESS OPERATION INPUTS
// =============================================================================

/**
 * Options for discovering a process model
 */
export interface DiscoverModelOptions {
  logId: string;
  minerType?: MinerType;
  modelName?: string;
  parameters?: Record<string, unknown>;
}

// =============================================================================
// CORE ENTITIES
// =============================================================================

/**
 * Discovered process model
 */
export interface ProcessModel extends HypermediaResponse {
  modelId: string;
  modelName: string;
  minerType: string;
  modelFormat: string;
  sourceLogId: string;
  createdAt?: string;
}

// =============================================================================
// DIRECTLY-FOLLOWS GRAPH (DFG)
// =============================================================================

export interface DFGNode {
  name: string;
  frequency: number;
  isStart: boolean;
  isEnd: boolean;
}

export interface DFGEdge {
  source: string;
  target: string;
  frequency: number;
  probability: number;
  avgDurationSeconds?: number;
}

export interface DirectlyFollowsGraph extends HypermediaResponse {
  logId: string;
  nodes: DFGNode[];
  edges: DFGEdge[];
  startActivities: Record<string, number>;
  endActivities: Record<string, number>;
  totalCases: number;
  totalEvents: number;
}

// =============================================================================
// PETRI NET
// =============================================================================

export interface PetriNetPlace {
  id: string;
  name: string;
  isInitial: boolean;
  isFinal: boolean;
}

export interface PetriNetTransition {
  id: string;
  label?: string;
  isSilent: boolean;
}

export interface PetriNetArc {
  source: string;
  target: string;
  sourceType: "place" | "transition";
  targetType: "place" | "transition";
}

export interface PetriNet extends HypermediaResponse {
  modelId: string;
  modelName: string;
  places: PetriNetPlace[];
  transitions: PetriNetTransition[];
  arcs: PetriNetArc[];
  initialMarking: Record<string, number>;
  finalMarking: Record<string, number>;
}

// =============================================================================
// PROCESS TREE
// =============================================================================

export interface ProcessTreeNode {
  operator?: "sequence" | "choice" | "parallel" | "loop";
  label?: string;
  children: ProcessTreeNode[];
}

export interface ProcessTree extends HypermediaResponse {
  modelId: string;
  modelName: string;
  root: ProcessTreeNode;
  treeString: string;
}

// =============================================================================
// MODEL QUALITY
// =============================================================================

export interface ModelQualityMetrics extends HypermediaResponse {
  modelId: string;
  logId: string;
  fitness: number;
  precision?: number;
  generalization?: number;
  simplicity?: number;
  overallQuality: number;
}
