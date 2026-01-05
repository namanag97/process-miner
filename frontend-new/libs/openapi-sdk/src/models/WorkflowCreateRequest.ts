/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkflowStep } from './WorkflowStep';
/**
 * Request to create a workflow.
 */
export type WorkflowCreateRequest = {
    name: string;
    steps: Array<WorkflowStep>;
    schedule?: (string | null);
};

