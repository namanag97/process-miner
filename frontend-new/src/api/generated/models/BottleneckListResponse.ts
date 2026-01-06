/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BottleneckResponse } from './BottleneckResponse';
/**
 * List of detected bottlenecks.
 */
export type BottleneckListResponse = {
    dataset_id: string;
    bottlenecks: Array<BottleneckResponse>;
    total_bottlenecks: number;
};

