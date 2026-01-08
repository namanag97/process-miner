/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AlgorithmParameters } from './AlgorithmParameters';
import type { MinerType } from './MinerType';
/**
 * Request to discover a process model.
 */
export type DiscoverRequest = {
    /**
     * Dataset UUID to mine
     */
    dataset_id: string;
    miner_type?: MinerType;
    /**
     * Optional name for the discovered model
     */
    model_name?: (string | null);
    /**
     * Algorithm-specific parameters. If not provided, defaults are used.
     */
    parameters?: (AlgorithmParameters | null);
};

