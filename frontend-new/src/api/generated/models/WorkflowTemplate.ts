/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkflowStep } from './WorkflowStep';
/**
 * Predefined workflow template.
 */
export type WorkflowTemplate = {
    /**
     * Template ID
     */
    id: string;
    /**
     * Template name
     */
    name: string;
    /**
     * Template description
     */
    description?: (string | null);
    /**
     * Workflow steps
     */
    steps?: Array<WorkflowStep>;
};

