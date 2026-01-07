/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkflowStep } from './WorkflowStep';
/**
 * Workflow response.
 */
export type WorkflowResponse = {
    id: string;
    name: string;
    steps?: Array<WorkflowStep>;
    schedule: (string | null);
    is_active: boolean;
    created_at: string;
};

