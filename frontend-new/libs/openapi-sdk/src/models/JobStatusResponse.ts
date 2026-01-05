/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Async job status.
 */
export type JobStatusResponse = {
    id: string;
    job_type: string;
    status: string;
    progress: number;
    stage?: (string | null);
    result?: (Record<string, any> | null);
    error?: (string | null);
    created_at: string;
};

