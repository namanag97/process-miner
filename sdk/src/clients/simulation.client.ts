/**
 * Simulation Client - Process Simulation Operations
 *
 * Business verbs:
 * - playOut() - Generate synthetic event log from process model
 * - simulate() - Run what-if simulation scenario
 * - capacityPlan() - Estimate resource requirements for target throughput
 */

import { HttpClient } from "../client.js";
import {
  PlayOutRequest,
  PlayOutResponse,
  SimulationRequest,
  SimulationResponse,
  CapacityPlanResponse,
} from "../types/simulation.js";

export class SimulationClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Generate synthetic event log by playing out tokens from a Petri net model.
   * Creates artificial cases that follow the process model.
   */
  async playOut(modelId: string, request: PlayOutRequest): Promise<PlayOutResponse> {
    return this.http.post<PlayOutResponse>(`/api/v1/simulation/models/${modelId}/play-out`, request);
  }

  /**
   * Run what-if simulation with process modifications.
   * Test changes to resource allocation, activity durations, etc.
   */
  async simulate(logId: string, request: SimulationRequest): Promise<SimulationResponse> {
    return this.http.post<SimulationResponse>(`/api/v1/simulation/logs/${logId}/simulate`, request);
  }

  /**
   * Estimate capacity requirements to achieve target throughput.
   * Helps determine resource needs for performance goals.
   */
  async capacityPlan(logId: string, targetThroughput: number): Promise<CapacityPlanResponse> {
    return this.http.post<CapacityPlanResponse>(
      `/api/v1/simulation/logs/${logId}/capacity-plan?target_throughput=${targetThroughput}`,
      {}
    );
  }
}
