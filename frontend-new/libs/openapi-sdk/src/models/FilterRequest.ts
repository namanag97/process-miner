/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FilterConfig } from './FilterConfig';
/**
 * Request to apply filters to an event log.
 */
export type FilterRequest = {
    /**
     * Name for the filtered log
     */
    name?: (string | null);
    /**
     * List of filters to apply
     */
    filters: Array<FilterConfig>;
    /**
     * Whether to save the filtered log
     */
    save_result?: boolean;
};

