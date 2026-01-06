/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Edge configuration for DAG definition.
 */
export type EdgeConfig = {
    /**
     * Source step name
     */
    from_step: string;
    /**
     * Target step name
     */
    to_step: string;
    /**
     * Optional condition for edge execution
     */
    condition?: (Record<string, any> | null);
};

