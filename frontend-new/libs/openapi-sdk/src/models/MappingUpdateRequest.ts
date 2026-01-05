/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Update mapping request.
 */
export type MappingUpdateRequest = {
    /**
     * Column for case ID
     */
    case_id_column: string;
    /**
     * Column for activity
     */
    activity_column: string;
    /**
     * Column for timestamp
     */
    timestamp_column: string;
    /**
     * Column for resource
     */
    resource_column?: (string | null);
    /**
     * Timestamp format
     */
    timestamp_format?: (string | null);
    additional_columns?: Array<string>;
};

