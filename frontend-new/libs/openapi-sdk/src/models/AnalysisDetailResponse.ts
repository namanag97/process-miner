/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DFGResponse } from './DFGResponse';
import type { StatisticsResponse } from './StatisticsResponse';
import type { VariantResponse } from './VariantResponse';
/**
 * Detailed analysis with full results.
 */
export type AnalysisDetailResponse = {
    id: string;
    dataset_id: string;
    name: string;
    analysis_type: string;
    status: string;
    config?: (Record<string, any> | null);
    result_summary?: (Record<string, any> | null);
    model_id?: (string | null);
    created_at: string;
    completed_at?: (string | null);
    error_message?: (string | null);
    dfg?: (DFGResponse | null);
    variants?: (Array<VariantResponse> | null);
    statistics?: (StatisticsResponse | null);
};

