/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DatasetResponse } from './DatasetResponse';
/**
 * Detailed project response with datasets.
 */
export type ProjectDetailResponse = {
    id: string;
    name: string;
    description: (string | null);
    tags?: Array<string>;
    total_files: number;
    total_analyses: number;
    created_at: string;
    updated_at: (string | null);
    datasets: Array<DatasetResponse>;
};

