/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response for a workflow run.
 */
export type WorkflowRunResponse = {
    /**
     * Run ID
     */
    id: string;
    /**
     * Workflow ID
     */
    workflow_id: string;
    /**
     * Run status
     */
    status: string;
    /**
     * Start time
     */
    started_at?: (string | null);
    /**
     * Completion time
     */
    completed_at?: (string | null);
    /**
     * Run result
     */
    result?: (Record<string, any> | null);
    /**
     * Error message if failed
     */
    error?: (string | null);
};

