/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Browser log entry.
 */
export type BrowserLog = {
    level: string;
    message: string;
    timestamp: string;
    data?: (Record<string, any> | null);
    trace_id?: (string | null);
    span_id?: (string | null);
};

