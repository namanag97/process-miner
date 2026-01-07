/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FilteredLogResponse } from './FilteredLogResponse';
/**
 * List of filtered logs derived from a source log.
 */
export type FilteredLogListResponse = {
    source_dataset_id: string;
    source_dataset_name: string;
    filtered_logs: Array<FilteredLogResponse>;
    total: number;
};

