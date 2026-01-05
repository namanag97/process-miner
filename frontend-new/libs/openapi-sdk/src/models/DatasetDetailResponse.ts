/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Detailed dataset response with statistics.
 */
export type DatasetDetailResponse = {
    id: string;
    name: string;
    source_format: string;
    total_events: number;
    total_cases: number;
    total_activities: number;
    activities?: Array<string>;
    created_at: string;
    source_file: (string | null);
    status?: string;
    validation_job_id?: (string | null);
    ingestion_job_id?: (string | null);
    file_size_bytes?: (number | null);
    statistics: (Record<string, any> | null);
    updated_at: (string | null);
};

