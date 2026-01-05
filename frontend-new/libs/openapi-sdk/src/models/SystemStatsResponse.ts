/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * System-wide statistics.
 */
export type SystemStatsResponse = {
    total_users: number;
    total_organizations: number;
    total_workspaces: number;
    total_datasets: number;
    total_jobs_today: number;
    active_users_24h: number;
    storage_used_bytes?: number;
    uptime_seconds: number;
};

