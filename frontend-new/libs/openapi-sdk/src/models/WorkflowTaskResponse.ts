/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Individual task within a workflow execution.
 */
export type WorkflowTaskResponse = {
    id: string;
    /**
     * Task name, e.g. 'validate_file', 'ingest_events'
     */
    task_name: string;
    /**
     * Execution order within workflow
     */
    task_order: number;
    /**
     * pending, running, completed, failed, skipped
     */
    status: string;
    progress_percent?: number;
    started_at?: (string | null);
    completed_at?: (string | null);
    /**
     * Task duration in milliseconds
     */
    duration_ms?: (number | null);
    error_message?: (string | null);
};

