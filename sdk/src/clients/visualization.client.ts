/**
 * Visualization Client - Process Visualization Operations
 *
 * Business verbs:
 * - getDFG() - Get Directly-Follows Graph JSON data
 * - getPetriNet() - Get Petri net structure
 * - getModelSVG() - Get process model as SVG
 * - getDFGSVG() - Get DFG as SVG
 * - getFootprints() - Get behavioral footprint matrix
 */

import { HttpClient } from "../client.js";
import { DFGResponse, PetriNetResponse, FootprintsResponse } from "../types/visualization.js";

export class VisualizationClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Get Directly-Follows Graph JSON data.
   * Returns nodes (activities) and edges (transitions) with frequencies.
   */
  async getDFG(logId: string): Promise<DFGResponse> {
    return this.http.get<DFGResponse>(`/api/v1/visualization/${logId}/dfg`);
  }

  /**
   * Get Petri net structure for visualization.
   * Returns places, transitions, arcs, and initial/final markings.
   */
  async getPetriNet(modelId: string): Promise<PetriNetResponse> {
    return this.http.get<PetriNetResponse>(`/api/v1/visualization/models/${modelId}/petri`);
  }

  /**
   * Get process model as SVG image.
   * Returns SVG string for display in browsers.
   */
  async getModelSVG(modelId: string): Promise<string> {
    return this.http.get<string>(`/api/v1/visualization/models/${modelId}/svg`);
  }

  /**
   * Get Directly-Follows Graph as SVG image.
   * Returns SVG string for display in browsers.
   */
  async getDFGSVG(logId: string): Promise<string> {
    return this.http.get<string>(`/api/v1/visualization/${logId}/dfg/svg`);
  }

  /**
   * Get behavioral footprint matrix.
   * Shows sequence, parallel, and choice relations between activities.
   */
  async getFootprints(logId: string): Promise<FootprintsResponse> {
    return this.http.get<FootprintsResponse>(`/api/v1/visualization/${logId}/footprints`);
  }
}
