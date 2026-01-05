/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ColumnTypeInfo } from './ColumnTypeInfo';
/**
 * Data preview for upload wizard Configure step.
 */
export type DataPreviewResponse = {
    dataset_id: string;
    filename: string;
    columns: Array<ColumnTypeInfo>;
    rows: Array<Record<string, any>>;
    total_rows: number;
    has_header?: boolean;
    field_separator?: string;
    encoding?: string;
};

