/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EdgeConfig } from './EdgeConfig';
import type { StepConfig } from './StepConfig';
/**
 * Request to create a DAG definition.
 */
export type CreateDefinitionRequest = {
    /**
     * Human-readable DAG name
     */
    name: string;
    /**
     * Optional description
     */
    description?: (string | null);
    /**
     * List of steps
     */
    steps: Array<StepConfig>;
    /**
     * Dependencies between steps
     */
    edges?: Array<EdgeConfig>;
};

