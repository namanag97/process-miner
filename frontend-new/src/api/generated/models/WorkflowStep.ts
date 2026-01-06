/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * A step in a workflow.
 */
export type WorkflowStep = {
    /**
     * Step name
     */
    name: string;
    /**
     * Type of task to execute
     */
    task_type: string;
    /**
     * Step configuration
     */
    config?: (Record<string, any> | null);
    /**
     * Dependencies
     */
    depends_on?: Array<string>;
};

