/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RunStepResponse } from './RunStepResponse';
/**
 * DAG run response.
 *
 * Extends BaseTaskResponse which provides:
 * - id, created_at, updated_at (from BaseEntityResponse)
 * - status, started_at, completed_at, error_message (from BaseTaskResponse)
 */
export type RunResponse = {
    /**
     * Creation timestamp
     */
    created_at: string;
    /**
     * Last update timestamp
     */
    updated_at?: (string | null);
    /**
     * Unique identifier
     */
    id: string;
    /**
     * Current status (pending/running/completed/failed)
     */
    status: string;
    /**
     * Execution start time
     */
    started_at?: (string | null);
    /**
     * Execution end time
     */
    completed_at?: (string | null);
    /**
     * Error details if failed
     */
    error_message?: (string | null);
    /**
     * ID of the DAG definition
     */
    definition_id: string;
    /**
     * How the run was triggered
     */
    trigger_type?: (string | null);
    /**
     * Step statuses
     */
    steps?: Array<RunStepResponse>;
};

