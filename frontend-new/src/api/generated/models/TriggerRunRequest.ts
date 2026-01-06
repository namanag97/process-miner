/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request to trigger a DAG run.
 */
export type TriggerRunRequest = {
    /**
     * DAG definition ID
     */
    definition_id?: (string | null);
    /**
     * DAG definition name (alternative to ID)
     */
    definition_name?: (string | null);
    /**
     * Shared context for all steps
     */
    context?: Record<string, any>;
    /**
     * Per-step parameter overrides
     */
    step_params?: Record<string, Record<string, any>>;
};

