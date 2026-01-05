/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request to trigger background ingestion with column mapping.
 */
export type IngestRequest = {
    /**
     * Column name for case ID
     */
    case_id_column: string;
    /**
     * Column name for activity
     */
    activity_column: string;
    /**
     * Column name for timestamp
     */
    timestamp_column: string;
    /**
     * Column name for resource
     */
    resource_column?: (string | null);
};

