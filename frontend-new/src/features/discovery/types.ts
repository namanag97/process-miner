/**
 * Discovery Feature Types
 *
 * Types for process discovery algorithms, jobs, and model visualization.
 *
 * NOTE: SDK types are available at @frontend-new/openapi-sdk for API validation.
 * Frontend uses camelCase conventions while SDK uses snake_case from backend.
 */

// ============================================
// SDK Types for Reference/Validation
// ============================================

export type {
    DFGNode as SDKDFGNode,
    DFGEdge as SDKDFGEdge,
    DFGResponse as SDKDFGResponse,
    MinerType as SDKMinerType,
    DiscoverRequest as SDKDiscoverRequest,
    ModelResponse as SDKModelResponse,
    JobStatusResponse as SDKJobStatusResponse,
} from '@frontend-new/openapi-sdk';

// ============================================
// Job Types
// ============================================

export type JobStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface Job {
    id: string;
    jobType: string;
    status: JobStatus;
    progress: number;
    stage?: string;
    entityType?: string;
    entityId?: string;
    error?: string;
    createdAt: string;
    startedAt?: string;
    completedAt?: string;
}

// ============================================
// Discovery Types
// ============================================

export type MinerType =
    | 'alpha'
    | 'alpha_plus'
    | 'inductive'
    | 'inductive_infrequent'
    | 'heuristics'
    | 'dfg'
    | 'performance_dfg'
    | 'ilp'
    | 'powl'
    | 'bpmn_inductive'
    | 'declare'
    | 'log_skeleton'
    | 'temporal_profile'
    | 'prefix_tree'
    | 'transition_system';

export type ModelFormat =
    | 'petri_net'
    | 'process_tree'
    | 'dfg'
    | 'performance_dfg'
    | 'bpmn'
    | 'powl'
    | 'declare'
    | 'log_skeleton'
    | 'temporal_profile'
    | 'prefix_tree'
    | 'transition_system'
    | 'batches';

export interface DiscoveryRequest {
    datasetId: string;
    minerType: MinerType;
    modelName?: string;
    parameters?: Record<string, unknown>;
}

export interface DiscoveryResponse {
    id?: string;
    jobId?: string;
    modelId?: string;
    status: string;
}

export interface DiscoveredModel {
    id: string;
    name: string;
    datasetId: string;
    minerType: MinerType;
    modelFormat: ModelFormat;
    fitness?: number;
    precision?: number;
    createdAt: string;
}

// ============================================
// Analysis Metadata Types
// ============================================

export interface ConfigSchemaField {
    type: 'string' | 'integer' | 'float' | 'boolean';
    default?: unknown;
    min?: number;
    max?: number;
    enum?: string[];
    description?: string;
}

export interface AnalysisTypeInfo {
    name: string;
    category: string;
    description: string;
    result_type: string;
    config_schema: Record<string, ConfigSchemaField>;
}

export interface AnalysisMetadata {
    categories: string[];
    analysis_types: Record<string, AnalysisTypeInfo>;
}

// ============================================
// Visualization Types
// ============================================

export interface DFGNode {
    id: string;
    label: string;
    frequency: number;
    isStart?: boolean;
    isEnd?: boolean;
}

export interface DFGEdge {
    source: string;
    target: string;
    frequency: number;
    avgDuration?: number;
}

export interface DFGData {
    nodes: DFGNode[];
    edges: DFGEdge[];
    startActivities: Record<string, number>;
    endActivities: Record<string, number>;
}

export interface DeclareConstraint {
    template: string;
    activities: string[];
    support: number;
    confidence?: number;
}

export interface TemporalProfileEntry {
    sourceActivity: string;
    targetActivity: string;
    meanDuration: number;
    stdDeviation: number;
}
