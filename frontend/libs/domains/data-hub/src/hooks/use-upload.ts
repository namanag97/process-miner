/**
 * Upload Hooks - React Query hooks for file upload operations
 */
import { useState, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useSDK } from '@lumina/design-system';
import { logsKeys } from './use-logs';
import type { IngestLogOptions, FilePreview, ColumnDetection } from 'process-mining-sdk';

export type UploadStep = 'upload' | 'mapping' | 'validate' | 'confirm';

export interface UploadState {
  step: UploadStep;
  file: File | null;
  preview: FilePreview | null;
  columnMapping: ColumnMapping;
  validationResult: ValidationResult | null;
}

export interface ColumnMapping {
  caseIdColumn: string;
  activityColumn: string;
  timestampColumn: string;
  resourceColumn?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  estimatedCases: number;
  estimatedEvents: number;
}

const initialState: UploadState = {
  step: 'upload',
  file: null,
  preview: null,
  columnMapping: {
    caseIdColumn: '',
    activityColumn: '',
    timestampColumn: '',
    resourceColumn: undefined,
  },
  validationResult: null,
};

/**
 * Hook for managing the multi-step upload wizard
 */
export function useUploadWizard() {
  const [state, setState] = useState<UploadState>(initialState);
  const sdk = useSDK();
  const queryClient = useQueryClient();

  // Preview file mutation
  const previewMutation = useMutation({
    mutationFn: (file: File) => sdk.logs.preview(file),
    onSuccess: (preview, file) => {
      setState(prev => ({
        ...prev,
        file,
        preview,
        step: 'mapping',
        columnMapping: {
          caseIdColumn: preview.suggestions?.caseId || '',
          activityColumn: preview.suggestions?.activity || '',
          timestampColumn: preview.suggestions?.timestamp || '',
          resourceColumn: preview.suggestions?.resource,
        },
      }));
    },
  });

  // Detect columns mutation
  const detectColumnsMutation = useMutation({
    mutationFn: (file: File) => sdk.logs.detectColumns(file),
  });

  // Ingest file mutation
  const ingestMutation = useMutation({
    mutationFn: ({ file, options }: { file: File; options?: IngestLogOptions }) =>
      sdk.logs.ingest(file, options),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: logsKeys.all });
      reset();
    },
  });

  const setFile = useCallback((file: File) => {
    previewMutation.mutate(file);
  }, [previewMutation]);

  const setColumnMapping = useCallback((mapping: Partial<ColumnMapping>) => {
    setState(prev => ({
      ...prev,
      columnMapping: { ...prev.columnMapping, ...mapping },
    }));
  }, []);

  const validateMapping = useCallback(() => {
    if (!state.preview || !state.columnMapping.caseIdColumn ||
        !state.columnMapping.activityColumn || !state.columnMapping.timestampColumn) {
      return;
    }

    // Validation logic (client-side check)
    const errors: string[] = [];
    const warnings: string[] = [];

    const columns = state.preview.columns;

    if (!columns.includes(state.columnMapping.caseIdColumn)) {
      errors.push(`Case ID column "${state.columnMapping.caseIdColumn}" not found`);
    }
    if (!columns.includes(state.columnMapping.activityColumn)) {
      errors.push(`Activity column "${state.columnMapping.activityColumn}" not found`);
    }
    if (!columns.includes(state.columnMapping.timestampColumn)) {
      errors.push(`Timestamp column "${state.columnMapping.timestampColumn}" not found`);
    }
    if (state.columnMapping.resourceColumn && !columns.includes(state.columnMapping.resourceColumn)) {
      warnings.push(`Resource column "${state.columnMapping.resourceColumn}" not found (optional)`);
    }

    // Check for duplicate column selections
    const selectedColumns = [
      state.columnMapping.caseIdColumn,
      state.columnMapping.activityColumn,
      state.columnMapping.timestampColumn,
      state.columnMapping.resourceColumn,
    ].filter(Boolean);

    const uniqueColumns = new Set(selectedColumns);
    if (uniqueColumns.size !== selectedColumns.length) {
      errors.push('Each column can only be assigned to one field');
    }

    setState(prev => ({
      ...prev,
      step: 'validate',
      validationResult: {
        isValid: errors.length === 0,
        errors,
        warnings,
        estimatedCases: state.preview?.estimatedCaseCount || 0,
        estimatedEvents: state.preview?.estimatedEventCount || 0,
      },
    }));
  }, [state.preview, state.columnMapping]);

  const goToConfirm = useCallback(() => {
    if (state.validationResult?.isValid) {
      setState(prev => ({ ...prev, step: 'confirm' }));
    }
  }, [state.validationResult]);

  const submit = useCallback((name?: string) => {
    if (!state.file) return;

    ingestMutation.mutate({
      file: state.file,
      options: {
        name,
        caseIdColumn: state.columnMapping.caseIdColumn,
        activityColumn: state.columnMapping.activityColumn,
        timestampColumn: state.columnMapping.timestampColumn,
        resourceColumn: state.columnMapping.resourceColumn,
      },
    });
  }, [state.file, state.columnMapping, ingestMutation]);

  const goBack = useCallback(() => {
    setState(prev => {
      const steps: UploadStep[] = ['upload', 'mapping', 'validate', 'confirm'];
      const currentIndex = steps.indexOf(prev.step);
      if (currentIndex > 0) {
        return { ...prev, step: steps[currentIndex - 1] };
      }
      return prev;
    });
  }, []);

  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  return {
    state,
    setFile,
    setColumnMapping,
    validateMapping,
    goToConfirm,
    goBack,
    submit,
    reset,
    isLoading: previewMutation.isPending || ingestMutation.isPending,
    isPreviewLoading: previewMutation.isPending,
    isIngestLoading: ingestMutation.isPending,
    previewError: previewMutation.error,
    ingestError: ingestMutation.error,
    ingestResult: ingestMutation.data,
  };
}
