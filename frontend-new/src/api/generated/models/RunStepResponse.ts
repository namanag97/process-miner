/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Step status within a run.
 *
 * Similar to BaseTaskResponse but without created_at/updated_at since
 * step timing is tracked via started_at/completed_at relative to the run.
 */
export type RunStepResponse = {
    id: string;
    name: string;
    task_name: string;
    /**
     * Step status (pending/running/completed/failed)
     */
    status: string;
    /**
     * Step start time
     */
    started_at?: (string | null);
    /**
     * Step completion time
     */
    completed_at?: (string | null);
    /**
     * Error details if failed
     */
    error_message?: (string | null);
};

