/**
 * Process Mining SDK
 *
 * A TypeScript SDK for the Process Mining Platform API.
 * Uses business verbs following CodeOpinion guidance.
 *
 * @example
 * ```typescript
 * import { ProcessMiningSdk } from 'process-mining-sdk';
 *
 * const sdk = new ProcessMiningSdk({ baseUrl: 'http://localhost:8001' });
 *
 * // Sign in
 * await sdk.auth.signIn({ email: 'user@example.com', password: 'test' });
 *
 * // Ingest event log
 * const log = await sdk.processes.ingest(file, { name: 'My Process' });
 *
 * // Discover process model
 * const model = await sdk.discovery.discover({ logId: log.id, minerType: 'inductive' });
 *
 * // Check conformance
 * const result = await sdk.conformance.check({ logId: log.id, modelId: model.modelId });
 *
 * // Find bottlenecks
 * const bottlenecks = await sdk.performance.findBottlenecks(log.id);
 * ```
 */

import { HttpClient } from "./client.js";
import { SdkConfig } from "./types/common.js";

// Import all clients
import { AuthClient } from "./clients/auth.client.js";
import { ProcessesClient } from "./clients/processes.client.js";
import { DiscoveryClient } from "./clients/discovery.client.js";
import { ConformanceClient } from "./clients/conformance.client.js";
import { PerformanceClient } from "./clients/performance.client.js";
import { AnalyticsClient } from "./clients/analytics.client.js";
import { OCPMClient } from "./clients/ocpm.client.js";
import { OrgClient } from "./clients/org.client.js";
import { ModelsClient } from "./clients/models.client.js";
import { WorkflowsClient } from "./clients/workflows.client.js";
import { NotificationsClient } from "./clients/notifications.client.js";
import { IntegrationsClient } from "./clients/integrations.client.js";
import { ProcessMiningClient } from "./clients/process-mining.client.js";
import { FilteringClient } from "./clients/filtering.client.js";
import { PredictionsClient } from "./clients/predictions.client.js";
import { SimulationClient } from "./clients/simulation.client.js";
import { VisualizationClient } from "./clients/visualization.client.js";

/**
 * Process Mining SDK
 *
 * Main entry point for all API operations.
 * Provides domain-specific clients with business-focused method names.
 */
export class ProcessMiningSdk {
  private readonly http: HttpClient;

  /** Authentication operations (signIn, signOut, whoAmI) */
  public readonly auth: AuthClient;

  /** Event log operations (ingest, analyze, assessQuality) */
  public readonly processes: ProcessesClient;

  /** Process discovery operations (discover, buildDFG, extractPetriNet) */
  public readonly discovery: DiscoveryClient;

  /** Conformance checking operations (check, measureFitness, computeAlignments) */
  public readonly conformance: ConformanceClient;

  /** Performance analysis operations (analyze, findBottlenecks, summarize) */
  public readonly performance: PerformanceClient;

  /** Analytics operations (getDashboard, discoverInsights, detectAnomalies) */
  public readonly analytics: AnalyticsClient;

  /** Object-Centric Process Mining operations (ingest, discoverOCPN) */
  public readonly ocpm: OCPMClient;

  /** Organizational mining operations (profileResources, buildHandoverNetwork, discoverRoles) */
  public readonly org: OrgClient;

  /** Process model management operations (list, get, visualize) */
  public readonly models: ModelsClient;

  /** Workflow automation operations (start, listPipelines, cancel) */
  public readonly workflows: WorkflowsClient;

  /** Notification operations (send, subscribe, configure) */
  public readonly notifications: NotificationsClient;

  /** External integration operations (createConnector, sync, fetchData) */
  public readonly integrations: IntegrationsClient;

  /** PM4Py advanced features (analyzeFootprints, extractLogSkeleton, analyzeSNA) */
  public readonly processMining: ProcessMiningClient;

  /** Event log filtering operations (applyFilter, previewFilter, getFilterOptions) */
  public readonly filtering: FilteringClient;

  /** ML-based predictions operations (trainPredictor, predict, predictBatch) */
  public readonly predictions: PredictionsClient;

  /** Process simulation operations (playOut, simulate, capacityPlan) */
  public readonly simulation: SimulationClient;

  /** Process visualization operations (getDFG, getPetriNet, getModelSVG) */
  public readonly visualization: VisualizationClient;

  constructor(config: SdkConfig) {
    this.http = new HttpClient(config);

    // Initialize all clients
    this.auth = new AuthClient(this.http);
    this.processes = new ProcessesClient(this.http);
    this.discovery = new DiscoveryClient(this.http);
    this.conformance = new ConformanceClient(this.http);
    this.performance = new PerformanceClient(this.http);
    this.analytics = new AnalyticsClient(this.http);
    this.ocpm = new OCPMClient(this.http);
    this.org = new OrgClient(this.http);
    this.models = new ModelsClient(this.http);
    this.workflows = new WorkflowsClient(this.http);
    this.notifications = new NotificationsClient(this.http);
    this.integrations = new IntegrationsClient(this.http);
    this.processMining = new ProcessMiningClient(this.http);
    this.filtering = new FilteringClient(this.http);
    this.predictions = new PredictionsClient(this.http);
    this.simulation = new SimulationClient(this.http);
    this.visualization = new VisualizationClient(this.http);
  }

  /**
   * Check if user is authenticated.
   */
  isAuthenticated(): boolean {
    return this.http.isAuthenticated();
  }
}

// Export the SDK class and config type
export type { SdkConfig };

// Re-export all types
export * from "./types/index.js";

// Re-export individual clients for advanced usage
export { AuthClient } from "./clients/auth.client.js";
export { ProcessesClient } from "./clients/processes.client.js";
export { DiscoveryClient } from "./clients/discovery.client.js";
export { ConformanceClient } from "./clients/conformance.client.js";
export { PerformanceClient } from "./clients/performance.client.js";
export { AnalyticsClient } from "./clients/analytics.client.js";
export { OCPMClient } from "./clients/ocpm.client.js";
export { OrgClient } from "./clients/org.client.js";
export { ModelsClient } from "./clients/models.client.js";
export { WorkflowsClient } from "./clients/workflows.client.js";
export { NotificationsClient } from "./clients/notifications.client.js";
export { IntegrationsClient } from "./clients/integrations.client.js";
export { ProcessMiningClient } from "./clients/process-mining.client.js";
export { FilteringClient } from "./clients/filtering.client.js";
export { PredictionsClient } from "./clients/predictions.client.js";
export { SimulationClient } from "./clients/simulation.client.js";
export { VisualizationClient } from "./clients/visualization.client.js";
