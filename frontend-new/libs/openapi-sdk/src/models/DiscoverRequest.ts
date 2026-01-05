/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MinerType } from './MinerType';
/**
 * Request to discover a process model.
 */
export type DiscoverRequest = {
    /**
     * Dataset ID to mine
     */
    dataset_id: string;
    miner_type?: MinerType;
    model_name?: (string | null);
};

