/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkflowStep } from './WorkflowStep';
/**
 * Request to create a new workflow.
 */
export type WorkflowCreateRequest = {
    /**
     * Workflow name
     */
    name: string;
    /**
     * Description
     */
    description?: (string | null);
    /**
     * Template to use
     */
    template_id?: (string | null);
    /**
     * Custom steps
     */
    steps?: Array<WorkflowStep>;
    /**
     * Associated dataset
     */
    dataset_id?: (string | null);
};

