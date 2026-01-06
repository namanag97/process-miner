/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkflowStep } from './WorkflowStep';
/**
 * Workflow response.
 */
export type WorkflowResponse = {
    /**
     * Workflow ID
     */
    id: string;
    /**
     * Workflow name
     */
    name: string;
    /**
     * Description
     */
    description?: (string | null);
    /**
     * Workflow status
     */
    status?: string;
    /**
     * Workflow steps
     */
    steps?: Array<WorkflowStep>;
    /**
     * Associated dataset
     */
    dataset_id?: (string | null);
    /**
     * Creation time
     */
    created_at?: (string | null);
    /**
     * Last update time
     */
    updated_at?: (string | null);
};

