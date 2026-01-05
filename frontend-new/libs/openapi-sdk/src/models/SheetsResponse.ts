/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SheetInfo } from './SheetInfo';
/**
 * Available sheets in an Excel file.
 */
export type SheetsResponse = {
    dataset_id: string;
    filename: string;
    sheets: Array<SheetInfo>;
};

