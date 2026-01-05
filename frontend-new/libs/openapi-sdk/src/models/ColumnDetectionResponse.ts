/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Column detection result.
 */
export type ColumnDetectionResponse = {
    columns: Array<string>;
    suggestions: Record<string, (string | null)>;
    sample_rows: Array<Record<string, any>>;
    row_count: number;
};

