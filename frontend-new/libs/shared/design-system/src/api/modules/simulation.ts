/**
 * Simulation Module - SDK methods for process simulation
 *
 * Business verbs:
 * - playOut() - Generate synthetic log from model
 * - simulate() - Run what-if simulation
 * - estimateCapacity() - Plan resource capacity
 */

import type { ApiClient } from '../client';

// Types
export interface PlayOutOptions {
  numTraces: number;
}

export interface PlayOutResult {
  modelId: string;
  generatedLogId: string;
  tracesGenerated: number;
  eventsGenerated: number;
}

export interface SimulationModification {
  type: 'remove_activity' | 'add_resource' | 'change_duration';
  activity?: string;
  resource?: string;
  durationMultiplier?: number;
}

export interface SimulationMetrics {
  avgCycleTime: number;
  throughput: number;
  bottleneckActivity?: string;
}

export interface SimulationResult {
  logId: string;
  scenario: string;
  originalMetrics: SimulationMetrics;
  simulatedMetrics: SimulationMetrics;
  impact: {
    cycleTimeChange: number;
    throughputChange: number;
  };
}

export interface CapacityEstimate {
  logId: string;
  targetThroughput: number;
  currentThroughput: number;
  resourcesRequired: Record<string, number>;
  bottlenecks: string[];
  recommendations: string[];
}

export interface SimulationModule {
  playOut: (modelId: string, options: PlayOutOptions) => Promise<PlayOutResult>;
  simulate: (logId: string, modifications: SimulationModification[]) => Promise<SimulationResult>;
  estimateCapacity: (logId: string, targetThroughput: number) => Promise<CapacityEstimate>;
}

// Backend response types (snake_case)
interface PlayOutResponse {
  model_id: string;
  generated_log_id: string;
  traces_generated: number;
  events_generated: number;
}

interface SimulationResponse {
  log_id: string;
  scenario: string;
  original_metrics: {
    avg_cycle_time: number;
    throughput: number;
    bottleneck_activity?: string;
  };
  simulated_metrics: {
    avg_cycle_time: number;
    throughput: number;
    bottleneck_activity?: string;
  };
  impact: {
    cycle_time_change: number;
    throughput_change: number;
  };
}

function transformPlayOut(be: PlayOutResponse): PlayOutResult {
  return {
    modelId: be.model_id,
    generatedLogId: be.generated_log_id,
    tracesGenerated: be.traces_generated,
    eventsGenerated: be.events_generated,
  };
}

function transformSimulationResult(be: SimulationResponse): SimulationResult {
  return {
    logId: be.log_id,
    scenario: be.scenario,
    originalMetrics: {
      avgCycleTime: be.original_metrics.avg_cycle_time,
      throughput: be.original_metrics.throughput,
      bottleneckActivity: be.original_metrics.bottleneck_activity,
    },
    simulatedMetrics: {
      avgCycleTime: be.simulated_metrics.avg_cycle_time,
      throughput: be.simulated_metrics.throughput,
      bottleneckActivity: be.simulated_metrics.bottleneck_activity,
    },
    impact: {
      cycleTimeChange: be.impact.cycle_time_change,
      throughputChange: be.impact.throughput_change,
    },
  };
}

export function createSimulationModule(client: ApiClient): SimulationModule {
  return {
    async playOut(modelId: string, options: PlayOutOptions) {
      const response = await client.post<PlayOutResponse>(
        `/simulation/models/${modelId}/play-out`,
        { num_traces: options.numTraces }
      );
      return transformPlayOut(response);
    },

    async simulate(logId: string, modifications: SimulationModification[]) {
      const response = await client.post<SimulationResponse>(
        `/simulation/logs/${logId}/simulate`,
        {
          modifications: modifications.map((m) => ({
            type: m.type,
            activity: m.activity,
            resource: m.resource,
            duration_multiplier: m.durationMultiplier,
          })),
        }
      );
      return transformSimulationResult(response);
    },

    async estimateCapacity(logId: string, targetThroughput: number) {
      const result = await client.post<{
        log_id: string;
        target_throughput: number;
        current_throughput: number;
        resources_required: Record<string, number>;
        bottlenecks: string[];
        recommendations: string[];
      }>(`/simulation/logs/${logId}/capacity-plan`, {
        target_throughput: targetThroughput,
      });

      return {
        logId: result.log_id,
        targetThroughput: result.target_throughput,
        currentThroughput: result.current_throughput,
        resourcesRequired: result.resources_required,
        bottlenecks: result.bottlenecks,
        recommendations: result.recommendations,
      };
    },
  };
}
