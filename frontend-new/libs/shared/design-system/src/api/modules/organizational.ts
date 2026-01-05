/**
 * Organizational Module - SDK methods for organizational mining
 *
 * Business verbs:
 * - getHandoverNetwork() - Discover handover of work network
 * - getCollaborationNetwork() - Discover working together network
 * - getResourceSimilarity() - Find similar resources
 * - getRoles() - Discover organizational roles
 * - getResourceProfile() - Get detailed resource profile
 * - getWorkload() - Get workload distribution
 */

import type { ApiClient } from '../client';

// Types
export interface NetworkNode {
  id: string;
  label: string;
  frequency: number;
  centrality?: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
  frequency: number;
}

export interface SocialNetwork {
  datasetId: string;
  networkType: 'handover' | 'collaboration' | 'similarity';
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  metrics: {
    density: number;
    avgCentrality: number;
    clusters?: number;
  };
}

export interface ResourceRole {
  roleId: string;
  roleName: string;
  resources: string[];
  activities: string[];
  frequency: number;
}

export interface ResourceProfile {
  resource: string;
  totalEvents: number;
  uniqueActivities: string[];
  avgEventsPerDay: number;
  peakHours: number[];
  collaborators: string[];
  performanceMetrics: {
    avgDuration: number;
    throughput: number;
  };
}

export interface WorkloadDistribution {
  datasetId: string;
  resources: Array<{
    resource: string;
    eventCount: number;
    caseCount: number;
    workloadPercent: number;
    avgDuration: number;
  }>;
  giniCoefficient: number;
  isBalanced: boolean;
}

export interface OrganizationalModule {
  getHandoverNetwork: (datasetId: string) => Promise<SocialNetwork>;
  getCollaborationNetwork: (datasetId: string) => Promise<SocialNetwork>;
  getResourceSimilarity: (datasetId: string) => Promise<SocialNetwork>;
  getRoles: (datasetId: string) => Promise<ResourceRole[]>;
  getResourceProfile: (datasetId: string, resource: string) => Promise<ResourceProfile>;
  getWorkload: (datasetId: string) => Promise<WorkloadDistribution>;
}

// Backend response types (snake_case)
interface NetworkNodeResponse {
  id: string;
  label: string;
  frequency: number;
  centrality?: number;
}

interface NetworkEdgeResponse {
  source: string;
  target: string;
  weight: number;
  frequency: number;
}

interface SocialNetworkResponse {
  dataset_id: string;
  network_type: string;
  nodes: NetworkNodeResponse[];
  edges: NetworkEdgeResponse[];
  metrics: {
    density: number;
    avg_centrality: number;
    clusters?: number;
  };
}

interface ResourceRoleResponse {
  role_id: string;
  role_name: string;
  resources: string[];
  activities: string[];
  frequency: number;
}

interface ResourceProfileResponse {
  resource: string;
  total_events: number;
  unique_activities: string[];
  avg_events_per_day: number;
  peak_hours: number[];
  collaborators: string[];
  performance_metrics: {
    avg_duration: number;
    throughput: number;
  };
}

interface WorkloadResponse {
  dataset_id: string;
  resources: Array<{
    resource: string;
    event_count: number;
    case_count: number;
    workload_percent: number;
    avg_duration: number;
  }>;
  gini_coefficient: number;
  is_balanced: boolean;
}

function transformNetwork(be: SocialNetworkResponse): SocialNetwork {
  // Validate and normalize network_type (BUG-005 fix)
  const validNetworkTypes: Array<SocialNetwork['networkType']> = ['handover', 'collaboration', 'similarity'];
  const networkType = validNetworkTypes.includes(be.network_type as any)
    ? (be.network_type as SocialNetwork['networkType'])
    : 'handover'; // Default fallback

  return {
    datasetId: be.dataset_id,
    networkType,
    nodes: be.nodes.map((n) => ({
      id: n.id,
      label: n.label,
      frequency: n.frequency,
      centrality: n.centrality,
    })),
    edges: be.edges.map((e) => ({
      source: e.source,
      target: e.target,
      weight: e.weight,
      frequency: e.frequency,
    })),
    metrics: {
      density: be.metrics.density,
      avgCentrality: be.metrics.avg_centrality,
      clusters: be.metrics.clusters,
    },
  };
}

function transformRole(be: ResourceRoleResponse): ResourceRole {
  return {
    roleId: be.role_id,
    roleName: be.role_name,
    resources: be.resources,
    activities: be.activities,
    frequency: be.frequency,
  };
}

function transformProfile(be: ResourceProfileResponse): ResourceProfile {
  return {
    resource: be.resource,
    totalEvents: be.total_events,
    uniqueActivities: be.unique_activities,
    avgEventsPerDay: be.avg_events_per_day,
    peakHours: be.peak_hours,
    collaborators: be.collaborators,
    performanceMetrics: {
      avgDuration: be.performance_metrics.avg_duration,
      throughput: be.performance_metrics.throughput,
    },
  };
}

function transformWorkload(be: WorkloadResponse): WorkloadDistribution {
  return {
    datasetId: be.dataset_id,
    resources: be.resources.map((r) => ({
      resource: r.resource,
      eventCount: r.event_count,
      caseCount: r.case_count,
      workloadPercent: r.workload_percent,
      avgDuration: r.avg_duration,
    })),
    giniCoefficient: be.gini_coefficient,
    isBalanced: be.is_balanced,
  };
}

export function createOrganizationalModule(client: ApiClient): OrganizationalModule {
  return {
    async getHandoverNetwork(datasetId: string) {
      const response = await client.get<SocialNetworkResponse>(
        `/organizational/logs/${datasetId}/handover-network`
      );
      return transformNetwork(response);
    },

    async getCollaborationNetwork(datasetId: string) {
      const response = await client.get<SocialNetworkResponse>(
        `/organizational/logs/${datasetId}/collaboration-network`
      );
      return transformNetwork(response);
    },

    async getResourceSimilarity(datasetId: string) {
      const response = await client.get<SocialNetworkResponse>(
        `/organizational/logs/${datasetId}/resource-similarity`
      );
      return transformNetwork(response);
    },

    async getRoles(datasetId: string) {
      const response = await client.get<ResourceRoleResponse[]>(
        `/organizational/logs/${datasetId}/roles`
      );
      return response.map(transformRole);
    },

    async getResourceProfile(datasetId: string, resource: string) {
      const response = await client.get<ResourceProfileResponse>(
        `/organizational/logs/${datasetId}/resources/${encodeURIComponent(resource)}/profile`
      );
      return transformProfile(response);
    },

    async getWorkload(datasetId: string) {
      const response = await client.get<WorkloadResponse>(
        `/organizational/logs/${datasetId}/workload`
      );
      return transformWorkload(response);
    },
  };
}
