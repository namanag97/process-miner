/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Simulation result.
 */
export type SimulationResponse = {
    log_id: string;
    scenario: string;
    original_metrics: Record<string, number>;
    simulated_metrics: Record<string, number>;
    impact: Record<string, number>;
};

