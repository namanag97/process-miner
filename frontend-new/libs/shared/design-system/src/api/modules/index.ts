/**
 * API Modules Index - Re-exports all SDK modules
 */

export { createProcessesModule, type ProcessesModule, type ListProcessesOptions, type ProcessMetadata } from './processes';
export { createDiscoveryModule, type DiscoveryModule, type DFGOptions, type VariantOptions } from './discovery';
export { createAnalyticsModule, type AnalyticsModule } from './analytics';
export { createConformanceModule, type ConformanceModule, type ConformanceCheckOptions, type ConformanceResult } from './conformance';
export { createAIModule, type AIModule, type Predictor } from './ai';
export { createPredictionsModule, type PredictionsModule, type TrainOptions, type PredictionResult } from './predictions';
export { createSimulationModule, type SimulationModule, type PlayOutOptions, type SimulationModification, type SimulationResult } from './simulation';
export { createOrganizationalModule, type OrganizationalModule, type SocialNetwork, type ResourceRole, type ResourceProfile, type WorkloadDistribution } from './organizational';
