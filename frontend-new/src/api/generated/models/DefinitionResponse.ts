/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EdgeResponse } from './EdgeResponse';
import type { StepResponse } from './StepResponse';
/**
 * DAG definition response.
 *
 * Uses BaseSchema for ORM compatibility. Note: Does not extend
 * BaseEntityResponse since we only need created_at, not updated_at.
 */
export type DefinitionResponse = {
    id: string;
    name: string;
    description?: (string | null);
    version: number;
    is_active: boolean;
    steps: Array<StepResponse>;
    edges: Array<EdgeResponse>;
    created_at: string;
};

