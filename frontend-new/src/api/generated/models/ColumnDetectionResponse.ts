/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ColumnTypeInfo } from './ColumnTypeInfo';
/**
 * Column detection result for the mapping UI.
 */
export type ColumnDetectionResponse = {
    dataset_id: string;
    /**
     * Dataset status
     */
    status: string;
    columns: Array<ColumnTypeInfo>;
    /**
     * Suggested mappings: {role: {column, confidence}}
     */
    suggestions?: Record<string, Record<string, any>>;
    /**
     * True if auto-mapping confidence is below threshold
     */
    requires_user_input?: boolean;
};

