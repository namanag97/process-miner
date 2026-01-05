/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventResponse } from './EventResponse';
/**
 * Paginated event list.
 */
export type EventListResponse = {
    items: Array<EventResponse>;
    total: number;
    page: number;
    page_size: number;
};

