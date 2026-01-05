/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request to create a new analysis.
 */
export type AnalysisCreateRequest = {
    name: string;
    /**
     * Type: discovery, conformance, variants, bottleneck
     */
    analysis_type: string;
    /**
     * Analysis configuration
     */
    config?: Record<string, any>;
};

