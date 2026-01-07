/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ReworkChain } from './ReworkChain';
/**
 * Response for rework chain analysis.
 */
export type ReworkChainListResponse = {
    dataset_id: string;
    chains: Array<ReworkChain>;
    total_chains: number;
    most_problematic_activity?: (string | null);
    cases_with_chains?: number;
    chains_percentage?: number;
};

