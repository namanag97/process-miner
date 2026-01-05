/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Current mapping response.
 */
export type MappingResponse = {
    dataset_id: string;
    case_id_column: string;
    activity_column: string;
    timestamp_column: string;
    resource_column?: (string | null);
    timestamp_format?: (string | null);
    additional_columns?: Array<string>;
    auto_mapped?: boolean;
    created_at?: (string | null);
    updated_at?: (string | null);
};

