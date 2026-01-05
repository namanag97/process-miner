/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Analysis response.
 */
export type AnalysisResponse = {
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
};

