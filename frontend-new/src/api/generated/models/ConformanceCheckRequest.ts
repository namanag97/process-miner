/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ConformanceMethod } from './ConformanceMethod';
/**
 * Request for conformance checking.
 */
export type ConformanceCheckRequest = {
    /**
     * Dataset UUID for conformance check
     */
    dataset_id: string;
    /**
     * Process model UUID for conformance check
     */
    model_id: string;
    method?: ConformanceMethod;
};

