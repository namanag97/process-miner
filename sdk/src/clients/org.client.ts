/**
 * Organizational Mining Client - Resource & Social Network Analysis
 * 
 * Business verbs:
 * - profileResources() - Get resource profiles with activity involvement
 * - buildHandoverNetwork() - Build handover of work network
 * - buildCollaborationNetwork() - Build working together network
 * - discoverRoles() - Discover organizational roles
 * - analyzeWorkload() - Analyze resource workload distribution
 */

import { HttpClient } from '../client.js';
import {
  ResourceProfile,
  SocialNetwork,
  RoleAnalysis,
  WorkloadAnalysis,
} from '../types/org.js';

export class OrgClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Profile resources in the event log.
   * Returns activity involvement, event counts, and workload metrics.
   */
  async profileResources(logId: string): Promise<ResourceProfile[]> {
    const response = await this.http.get<{ resources: ResourceProfile[] }>(
      `/org/resources/${logId}`
    );
    return response.resources;
  }

  /**
   * Build handover of work network.
   * Shows how work is transferred between resources.
   */
  async buildHandoverNetwork(logId: string): Promise<SocialNetwork> {
    return this.http.get<SocialNetwork>(`/org/handover-network/${logId}`);
  }

  /**
   * Build collaboration (working together) network.
   * Shows which resources work together on the same cases.
   */
  async buildCollaborationNetwork(logId: string): Promise<SocialNetwork> {
    return this.http.get<SocialNetwork>(`/org/working-together/${logId}`);
  }

  /**
   * Discover organizational roles.
   * Groups resources by similar activity patterns.
   */
  async discoverRoles(logId: string): Promise<RoleAnalysis> {
    return this.http.get<RoleAnalysis>(`/org/roles/${logId}`);
  }

  /**
   * Analyze resource workload distribution.
   * Returns workload metrics for each resource.
   */
  async analyzeWorkload(logId: string): Promise<WorkloadAnalysis> {
    return this.http.get<WorkloadAnalysis>(`/org/workload/${logId}`);
  }
}
