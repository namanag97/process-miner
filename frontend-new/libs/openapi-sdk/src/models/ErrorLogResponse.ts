/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Error log entry response.
 */
export type ErrorLogResponse = {
    id: string;
    error_type: string;
    message: string;
    stack_trace?: (string | null);
    user_id?: (string | null);
    path?: (string | null);
    resolved?: boolean;
    resolved_at?: (string | null);
    resolved_by?: (string | null);
    created_at: string;
};

