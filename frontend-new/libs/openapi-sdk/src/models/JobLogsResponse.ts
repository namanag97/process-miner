/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { JobLogEntry } from './JobLogEntry';
/**
 * Job logs response.
 */
export type JobLogsResponse = {
    job_id: string;
    logs: Array<JobLogEntry>;
    total: number;
};

