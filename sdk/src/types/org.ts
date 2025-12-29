/**
 * Organizational Mining Types
 */

import { HypermediaResponse } from "./common.js";

// =============================================================================
// RESOURCES
// =============================================================================

export interface ResourceProfile extends HypermediaResponse {
  name: string;
  eventCount: number;
  caseCount: number;
  avgEventsPerCase: number;
  activities: string[];
  workload?: number;
}

// =============================================================================
// NETWORKS
// =============================================================================

export interface NetworkNode {
  id: string;
  name: string;
  weight?: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
}

export interface SocialNetwork extends HypermediaResponse {
  logId: string;
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  networkType: "handover" | "working_together" | "similar_activities";
}

// =============================================================================
// ROLES
// =============================================================================

export interface OrganizationalRole extends HypermediaResponse {
  roleId: string;
  roleName: string;
  resources: string[];
  activities: string[];
  eventCount: number;
}

export interface RoleAnalysis extends HypermediaResponse {
  logId: string;
  roles: OrganizationalRole[];
  totalResources: number;
  totalRoles: number;
}

// =============================================================================
// WORKLOAD
// =============================================================================

export interface ResourceWorkload extends HypermediaResponse {
  resource: string;
  eventCount: number;
  caseCount: number;
  avgDailyEvents: number;
  peakDay?: string;
  peakHour?: number;
  utilizationRate?: number;
}

export interface WorkloadAnalysis extends HypermediaResponse {
  logId: string;
  resources: ResourceWorkload[];
  avgWorkload: number;
  workloadStdDev: number;
}
