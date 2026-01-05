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
     * Dataset/log ID to mine
     */
    log_id: string;
    miner_type?: MinerType;
    model_name?: (string | null);
};

