/**
 * Pre-computed Analysis Results for Process Mining Showcase
 * 
 * Contains sample results for all 24 analysis types organized by category.
 */

import type { ProcessGraphData } from '../../explorer/components/CytoscapeCanvas';

// ============================================================================
// Type Definitions
// ============================================================================

export interface AnalysisResult<T = unknown> {
    type: string;
    name: string;
    category: AnalysisCategory;
    description: string;
    resultType: 'graph' | 'table' | 'json' | 'metrics' | 'constraints';
    data: T;
}

export type AnalysisCategory =
    | 'Discovery'
    | 'Variants'
    | 'Statistics'
    | 'Performance'
    | 'Organizational'
    | 'Conformance'
    | 'Declarative';

export interface VariantData {
    rank: number;
    variant: string[];
    count: number;
    percentage: number;
}

export interface StatisticsData {
    totalCases: number;
    totalEvents: number;
    uniqueActivities: number;
    uniqueResources: number;
    uniqueVariants: number;
    avgCaseLength: number;
    avgDurationDays: number;
    medianDurationDays: number;
}

export interface BottleneckData {
    activity: string;
    avgWaitTime: number;
    frequency: number;
    impactScore: number;
}

export interface ConformanceData {
    fitness: number;
    precision: number;
    generalization: number;
    simplicity: number;
    alignedTraces: number;
    totalTraces: number;
    deviations: Array<{ trace: string; issue: string; count: number }>;
}

export interface ConstraintData {
    type: string;
    antecedent: string;
    consequent?: string;
    support: number;
    confidence: number;
}

export interface ResourceUtilization {
    resource: string;
    caseCount: number;
    eventCount: number;
    avgEventsPerCase: number;
    activities: string[];
}

// ============================================================================
// Sample DFG (Directly-Follows Graph) Data
// ============================================================================

export const SAMPLE_DFG: ProcessGraphData = {
    nodes: [
        { id: 'start', label: '●', isStart: true, frequency: 250 },
        { id: 'order_received', label: 'Order Received', frequency: 250 },
        { id: 'validate', label: 'Validate Order', frequency: 220 },
        { id: 'credit_check', label: 'Credit Check', frequency: 175 },
        { id: 'approved', label: 'Order Approved', frequency: 200 },
        { id: 'rejected', label: 'Order Rejected', frequency: 38 },
        { id: 'prepare', label: 'Prepare Shipment', frequency: 200 },
        { id: 'ship', label: 'Ship Order', frequency: 200 },
        { id: 'deliver', label: 'Deliver Order', frequency: 200 },
        { id: 'payment', label: 'Receive Payment', frequency: 212 },
        { id: 'close', label: 'Close Case', isEnd: true, frequency: 250 },
    ],
    edges: [
        { id: 'e1', source: 'start', target: 'order_received', frequency: 250 },
        { id: 'e2', source: 'order_received', target: 'validate', frequency: 200 },
        { id: 'e3', source: 'order_received', target: 'approved', frequency: 50 },
        { id: 'e4', source: 'validate', target: 'credit_check', frequency: 175 },
        { id: 'e5', source: 'validate', target: 'order_received', frequency: 25 },
        { id: 'e6', source: 'credit_check', target: 'approved', frequency: 150 },
        { id: 'e7', source: 'credit_check', target: 'rejected', frequency: 38 },
        { id: 'e8', source: 'approved', target: 'prepare', frequency: 200 },
        { id: 'e9', source: 'rejected', target: 'close', frequency: 38 },
        { id: 'e10', source: 'prepare', target: 'ship', frequency: 200 },
        { id: 'e11', source: 'ship', target: 'deliver', frequency: 200 },
        { id: 'e12', source: 'deliver', target: 'payment', frequency: 200 },
        { id: 'e13', source: 'payment', target: 'close', frequency: 200 },
        { id: 'e14', source: 'payment', target: 'payment', frequency: 25 },
    ],
    metadata: { nodeCount: 11, edgeCount: 14, type: 'DFG' },
};

// ============================================================================
// Sample Social Network (Handover of Work)
// ============================================================================

export const SAMPLE_HANDOVER_NETWORK: ProcessGraphData = {
    nodes: [
        { id: 'sarah', label: 'Sarah Chen', frequency: 312 },
        { id: 'mike', label: 'Mike Johnson', frequency: 287 },
        { id: 'emma', label: 'Emma Williams', frequency: 298 },
        { id: 'david', label: 'David Brown', frequency: 276 },
        { id: 'lisa', label: 'Lisa Garcia', frequency: 245 },
        { id: 'james', label: 'James Wilson', frequency: 231 },
        { id: 'maria', label: 'Maria Martinez', frequency: 268 },
        { id: 'robert', label: 'Robert Taylor', frequency: 221 },
    ],
    edges: [
        { id: 'h1', source: 'sarah', target: 'mike', frequency: 45 },
        { id: 'h2', source: 'sarah', target: 'emma', frequency: 38 },
        { id: 'h3', source: 'mike', target: 'david', frequency: 52 },
        { id: 'h4', source: 'mike', target: 'lisa', frequency: 31 },
        { id: 'h5', source: 'emma', target: 'james', frequency: 44 },
        { id: 'h6', source: 'emma', target: 'maria', frequency: 36 },
        { id: 'h7', source: 'david', target: 'robert', frequency: 48 },
        { id: 'h8', source: 'lisa', target: 'sarah', frequency: 29 },
        { id: 'h9', source: 'james', target: 'mike', frequency: 33 },
        { id: 'h10', source: 'maria', target: 'emma', frequency: 41 },
        { id: 'h11', source: 'robert', target: 'lisa', frequency: 27 },
    ],
    metadata: { nodeCount: 8, edgeCount: 11, type: 'Social Network' },
};

// ============================================================================
// Sample Variant Analysis
// ============================================================================

export const SAMPLE_VARIANTS: VariantData[] = [
    { rank: 1, variant: ['Order Received', 'Validate Order', 'Credit Check', 'Order Approved', 'Prepare Shipment', 'Ship Order', 'Deliver Order', 'Receive Payment', 'Close Case'], count: 112, percentage: 44.8 },
    { rank: 2, variant: ['Order Received', 'Order Approved', 'Prepare Shipment', 'Ship Order', 'Deliver Order', 'Receive Payment', 'Close Case'], count: 50, percentage: 20.0 },
    { rank: 3, variant: ['Order Received', 'Validate Order', 'Credit Check', 'Order Rejected', 'Close Case'], count: 38, percentage: 15.2 },
    { rank: 4, variant: ['Order Received', 'Validate Order', 'Credit Check', 'Order Approved', 'Prepare Shipment', 'Ship Order', 'Deliver Order', 'Receive Payment', 'Receive Payment', 'Close Case'], count: 25, percentage: 10.0 },
    { rank: 5, variant: ['Order Received', 'Validate Order', 'Order Received', 'Validate Order', 'Credit Check', 'Order Approved', 'Prepare Shipment', 'Ship Order', 'Deliver Order', 'Receive Payment', 'Close Case'], count: 25, percentage: 10.0 },
];

// ============================================================================
// Sample Statistics
// ============================================================================

export const SAMPLE_STATISTICS: StatisticsData = {
    totalCases: 250,
    totalEvents: 2138,
    uniqueActivities: 10,
    uniqueResources: 8,
    uniqueVariants: 5,
    avgCaseLength: 8.55,
    avgDurationDays: 4.2,
    medianDurationDays: 3.8,
};

// ============================================================================
// Sample Bottleneck Analysis
// ============================================================================

export const SAMPLE_BOTTLENECKS: BottleneckData[] = [
    { activity: 'Credit Check', avgWaitTime: 14400, frequency: 175, impactScore: 0.85 },
    { activity: 'Prepare Shipment', avgWaitTime: 10800, frequency: 200, impactScore: 0.72 },
    { activity: 'Validate Order', avgWaitTime: 7200, frequency: 220, impactScore: 0.58 },
    { activity: 'Ship Order', avgWaitTime: 5400, frequency: 200, impactScore: 0.45 },
    { activity: 'Deliver Order', avgWaitTime: 3600, frequency: 200, impactScore: 0.30 },
];

// ============================================================================
// Sample Conformance Results
// ============================================================================

export const SAMPLE_CONFORMANCE: ConformanceData = {
    fitness: 0.92,
    precision: 0.88,
    generalization: 0.85,
    simplicity: 0.78,
    alignedTraces: 230,
    totalTraces: 250,
    deviations: [
        { trace: 'CASE-0034', issue: 'Skipped Credit Check activity', count: 12 },
        { trace: 'CASE-0089', issue: 'Double payment recorded', count: 8 },
    ],
};

// ============================================================================
// Sample DECLARE Constraints
// ============================================================================

export const SAMPLE_DECLARE_CONSTRAINTS: ConstraintData[] = [
    { type: 'Response', antecedent: 'Order Received', consequent: 'Validate Order', support: 0.88, confidence: 0.95 },
    { type: 'Precedence', antecedent: 'Credit Check', consequent: 'Order Approved', support: 0.80, confidence: 0.92 },
    { type: 'Existence', antecedent: 'Close Case', support: 1.0, confidence: 1.0 },
    { type: 'NotCoExistence', antecedent: 'Order Approved', consequent: 'Order Rejected', support: 0.85, confidence: 0.98 },
    { type: 'ChainResponse', antecedent: 'Ship Order', consequent: 'Deliver Order', support: 0.80, confidence: 0.97 },
    { type: 'AlternateResponse', antecedent: 'Prepare Shipment', consequent: 'Ship Order', support: 0.80, confidence: 0.96 },
];

// ============================================================================
// Sample Resource Utilization
// ============================================================================

export const SAMPLE_RESOURCE_UTILIZATION: ResourceUtilization[] = [
    { resource: 'Sarah Chen', caseCount: 78, eventCount: 312, avgEventsPerCase: 4.0, activities: ['Order Received', 'Validate Order', 'Close Case'] },
    { resource: 'Mike Johnson', caseCount: 72, eventCount: 287, avgEventsPerCase: 3.99, activities: ['Credit Check', 'Order Approved', 'Order Rejected'] },
    { resource: 'Emma Williams', caseCount: 75, eventCount: 298, avgEventsPerCase: 3.97, activities: ['Prepare Shipment', 'Ship Order'] },
    { resource: 'David Brown', caseCount: 69, eventCount: 276, avgEventsPerCase: 4.0, activities: ['Deliver Order', 'Receive Payment'] },
    { resource: 'Lisa Garcia', caseCount: 62, eventCount: 245, avgEventsPerCase: 3.95, activities: ['Validate Order', 'Credit Check'] },
    { resource: 'James Wilson', caseCount: 58, eventCount: 231, avgEventsPerCase: 3.98, activities: ['Order Approved', 'Prepare Shipment'] },
    { resource: 'Maria Martinez', caseCount: 67, eventCount: 268, avgEventsPerCase: 4.0, activities: ['Ship Order', 'Deliver Order'] },
    { resource: 'Robert Taylor', caseCount: 56, eventCount: 221, avgEventsPerCase: 3.95, activities: ['Receive Payment', 'Close Case'] },
];

// ============================================================================
// Complete Analysis Registry (all analyses grouped by category)
// ============================================================================

export const ANALYSIS_BY_CATEGORY: Record<AnalysisCategory, AnalysisResult[]> = {
    Discovery: [
        { type: 'dfg', name: 'Directly-Follows Graph (DFG)', category: 'Discovery', description: 'Shows activity transitions and their frequencies', resultType: 'graph', data: SAMPLE_DFG },
        { type: 'alpha', name: 'Alpha Miner', category: 'Discovery', description: 'Classic algorithm for discovering Petri nets', resultType: 'graph', data: SAMPLE_DFG },
        { type: 'inductive', name: 'Inductive Miner', category: 'Discovery', description: 'Guarantees sound process models', resultType: 'graph', data: SAMPLE_DFG },
        { type: 'heuristic', name: 'Heuristics Miner', category: 'Discovery', description: 'Handles noise and incomplete logs well', resultType: 'graph', data: SAMPLE_DFG },
        { type: 'ilp', name: 'ILP Miner', category: 'Discovery', description: 'Integer Linear Programming for optimal Petri nets', resultType: 'graph', data: SAMPLE_DFG },
        { type: 'powl', name: 'POWL Discovery', category: 'Discovery', description: 'Partially Ordered Workflow Language', resultType: 'graph', data: SAMPLE_DFG },
        { type: 'bpmn', name: 'BPMN Discovery', category: 'Discovery', description: 'Direct BPMN 2.0 model output', resultType: 'graph', data: SAMPLE_DFG },
        { type: 'prefix_tree', name: 'Prefix Tree', category: 'Discovery', description: 'Trie of all trace prefixes for prediction', resultType: 'graph', data: SAMPLE_DFG },
        { type: 'transition_system', name: 'Transition System', category: 'Discovery', description: 'State-based model from activity sequences', resultType: 'graph', data: SAMPLE_DFG },
        { type: 'performance_dfg', name: 'Performance DFG', category: 'Discovery', description: 'DFG with timing information between activities', resultType: 'graph', data: SAMPLE_DFG },
    ],
    Variants: [
        { type: 'variants', name: 'Process Variants', category: 'Variants', description: 'Unique execution paths and their frequencies', resultType: 'table', data: SAMPLE_VARIANTS },
    ],
    Statistics: [
        { type: 'statistics', name: 'Basic Statistics', category: 'Statistics', description: 'Key process metrics and distributions', resultType: 'metrics', data: SAMPLE_STATISTICS },
    ],
    Performance: [
        { type: 'bottlenecks', name: 'Bottleneck Analysis', category: 'Performance', description: 'Identify activities causing delays', resultType: 'table', data: SAMPLE_BOTTLENECKS },
    ],
    Organizational: [
        { type: 'handover', name: 'Handover of Work Network', category: 'Organizational', description: 'Work handover patterns between resources', resultType: 'graph', data: SAMPLE_HANDOVER_NETWORK },
        { type: 'working_together', name: 'Working Together Network', category: 'Organizational', description: 'Collaboration patterns between resources', resultType: 'graph', data: SAMPLE_HANDOVER_NETWORK },
        { type: 'resource_utilization', name: 'Resource Utilization', category: 'Organizational', description: 'Workload distribution across resources', resultType: 'table', data: SAMPLE_RESOURCE_UTILIZATION },
    ],
    Conformance: [
        { type: 'token_replay', name: 'Token-Based Replay', category: 'Conformance', description: 'Check conformance using token replay', resultType: 'metrics', data: SAMPLE_CONFORMANCE },
        { type: 'alignments', name: 'Alignments', category: 'Conformance', description: 'Optimal alignments between log and model', resultType: 'metrics', data: SAMPLE_CONFORMANCE },
    ],
    Declarative: [
        { type: 'declare', name: 'DECLARE Constraints', category: 'Declarative', description: 'Declarative constraints (LTL-based)', resultType: 'constraints', data: SAMPLE_DECLARE_CONSTRAINTS },
        { type: 'log_skeleton', name: 'Log Skeleton', category: 'Declarative', description: 'Activity occurrence and ordering constraints', resultType: 'constraints', data: SAMPLE_DECLARE_CONSTRAINTS },
        { type: 'temporal_profile', name: 'Temporal Profile', category: 'Declarative', description: 'Time-based constraints between activities', resultType: 'constraints', data: SAMPLE_DECLARE_CONSTRAINTS },
    ],
};

export const CATEGORY_ORDER: AnalysisCategory[] = [
    'Discovery',
    'Variants',
    'Statistics',
    'Performance',
    'Organizational',
    'Conformance',
    'Declarative',
];

export const CATEGORY_ICONS: Record<AnalysisCategory, string> = {
    Discovery: '🔍',
    Variants: '🔀',
    Statistics: '📊',
    Performance: '⚡',
    Organizational: '👥',
    Conformance: '✅',
    Declarative: '📋',
};
