/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Column type information with suggestion data.
 */
export type ColumnTypeInfo = {
    name: string;
    /**
     * Detected type: STRING, INTEGER, DATETIME, FLOAT
     */
    dtype: string;
    position?: number;
    sample_values?: Array<any>;
    null_percentage?: number;
    unique_count?: number;
    /**
     * case_id, activity, timestamp, resource
     */
    suggested_role?: (string | null);
    /**
     * Confidence score
     */
    confidence?: (number | null);
};

