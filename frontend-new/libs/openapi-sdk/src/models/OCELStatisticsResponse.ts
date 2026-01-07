/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * OCEL statistics response.
 */
export type OCELStatisticsResponse = {
    dataset_id: string;
    total_events: number;
    total_objects: number;
    total_object_types: number;
    total_activities: number;
    object_types: Array<string>;
    activities: Array<string>;
    objects_per_type: Record<string, number>;
};

