/**
 * Upload Wizard Types
 *
 * Local type definitions for the upload wizard.
 * These maintain frontend naming conventions (camelCase).
 */

// ============================================
// SDK Types for Reference (use transform functions)
// ============================================

export type {
    ColumnTypeInfo as SDKColumnTypeInfo,
    PreviewResponse as SDKDataPreview,
} from '@frontend-new/openapi-sdk';

// ============================================
// Wizard Types (frontend-specific)
// ============================================

export type WizardStep = 'upload' | 'sheets' | 'configure' | 'mapping' | 'finalize';

export interface ColumnTypeInfo {
    name: string;
    detected_type: 'STRING' | 'INTEGER' | 'DECIMAL' | 'DATETIME' | 'BOOLEAN';
    sample_values: unknown[];
    null_count: number;
    date_format?: string;
}

export interface DataPreview {
    dataset_id: string;
    filename: string;
    columns: ColumnTypeInfo[];
    rows: Record<string, unknown>[];
    total_rows: number;
    has_header: boolean;
    field_separator: string;
    encoding: string;
}

export interface SheetInfo {
    name: string;
    index: number;
    row_count: number;
    column_count: number;
}

export interface SheetsResponse {
    dataset_id: string;
    filename: string;
    sheets: SheetInfo[];
}

export interface ColumnMapping {
    case_id_column: string;
    activity_column: string;
    timestamp_column: string;
    resource_column?: string;
}

export interface WizardState {
    currentStep: WizardStep;
    datasetId: string | null;
    filename: string | null;
    fileSize: number | null;
    selectedSheet: string | null;
    preview: DataPreview | null;
    mapping: ColumnMapping | null;
    jobId: string | null;
    error: string | null;
    isLoading: boolean;
}

export interface ParseConfig {
    has_header: boolean;
    field_separator: string;
    decimal_separator: string;
    thousand_separator: string;
    sheet_name?: string;
    encoding: string;
}
