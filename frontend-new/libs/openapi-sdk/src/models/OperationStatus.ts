/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Operation status response from Temporal.
 */
export type OperationStatus = {
    /**
     * Temporal workflow ID
     */
    workflow_id: string;
    /**
     * PENDING, RUNNING, COMPLETED, FAILED, CANCELLED, TIMED_OUT
     */
    status: string;
    /**
     * Progress percentage 0-100
     */
    progress?: number;
    /**
     * Current activity/step name
     */
    current_step?: (string | null);
    /**
     * ISO timestamp when started
     */
    started_at?: (string | null);
    /**
     * ISO timestamp when completed
     */
    completed_at?: (string | null);
    /**
     * Error message if failed
     */
    error_message?: (string | null);
    /**
     * Entity type (dataset, model, etc)
     */
    entity_type?: (string | null);
    /**
     * Entity ID
     */
    entity_id?: (string | null);
    /**
     * Operation type (ingest, discover, etc)
     */
    operation_type?: (string | null);
};

