/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ConformanceMethod } from './ConformanceMethod';
/**
 * Request for conformance checking.
 */
export type ConformanceCheckRequest = {
    log_id: string;
    model_id: string;
    method?: ConformanceMethod;
};

