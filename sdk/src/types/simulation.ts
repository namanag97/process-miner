/**
 * Simulation Types - Process Simulation
 *
 * TODO: These types should be auto-generated from OpenAPI spec
 * For now, they match the backend Pydantic schemas
 */

export interface PlayOutRequest {
  num_traces: number;
  max_trace_length?: number;
}

export interface PlayOutResponse {
  model_id: string;
  synthetic_log_id: string;
  num_traces: number;
  num_events: number;
  duration_seconds: number;
}

export interface SimulationRequest {
  modifications: {
    resource_changes?: Record<string, number>;
    activity_duration_changes?: Record<string, number>;
    arrival_rate_multiplier?: number;
  };
  simulation_parameters?: {
    num_instances?: number;
    time_unit?: "seconds" | "minutes" | "hours" | "days";
  };
}

export interface SimulationResponse {
  log_id: string;
  simulated_log_id: string;
  modifications_applied: Record<string, any>;
  baseline_metrics: {
    avg_cycle_time: number;
    throughput: number;
    resource_utilization: Record<string, number>;
  };
  simulated_metrics: {
    avg_cycle_time: number;
    throughput: number;
    resource_utilization: Record<string, number>;
  };
  improvement: {
    cycle_time_change_pct: number;
    throughput_change_pct: number;
  };
}

export interface CapacityPlanResponse {
  log_id: string;
  target_throughput: number;
  current_throughput: number;
  recommended_resources: Record<string, number>;
  estimated_cost_increase?: number;
  bottleneck_activities: string[];
}
