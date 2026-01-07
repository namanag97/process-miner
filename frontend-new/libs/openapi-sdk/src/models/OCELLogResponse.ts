/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * OCEL log response.
 */
export type OCELLogResponse = {
    id: string;
    name: string;
    source_file: (string | null);
    source_format: string;
    total_events: number;
    total_objects: number;
    total_object_types: number;
    object_types?: Array<string>;
    activities?: Array<string>;
    created_at: string;
};

