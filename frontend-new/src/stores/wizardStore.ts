/**
 * Wizard Store
 *
 * Manages multi-step upload wizard state.
 * Tracks progress through upload, sheet selection, configuration, mapping, and finalization.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type WizardStep = 'upload' | 'sheets' | 'configure' | 'mapping' | 'finalize';

export interface ColumnMapping {
  caseId: string | null;
  activity: string | null;
  timestamp: string | null;
  resource?: string | null;
  startTimestamp?: string | null;
  cost?: string | null;
  additionalAttributes?: string[];
}

export interface DataPreview {
  columns: string[];
  rows: Record<string, unknown>[];
  totalRows: number;
}

export interface JobStatus {
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  error?: string;
}

export interface WizardState {
  // Progress state
  currentStep: WizardStep;
  completedSteps: WizardStep[];

  // Data state
  projectId: string | null;
  datasetId: string | null;
  filename: string | null;
  fileSize: number | null;
  availableSheets: string[];
  selectedSheet: string | null;
  preview: DataPreview | null;
  mapping: ColumnMapping | null;
  hasHeader: boolean;
  delimiter: string;

  // Job state
  jobId: string | null;
  jobStatus: JobStatus | null;

  // UI state
  isLoading: boolean;
  error: string | null;

  // Actions - Navigation
  initWizard: (projectId: string, resumeDatasetId?: string) => void;
  setStep: (step: WizardStep) => void;
  nextStep: () => void;
  prevStep: () => void;
  canProceed: () => boolean;

  // Actions - Upload
  setUploadResult: (datasetId: string, filename: string, fileSize: number) => void;

  // Actions - Sheets
  setAvailableSheets: (sheets: string[]) => void;
  selectSheet: (sheetName: string) => void;

  // Actions - Configure
  setPreview: (preview: DataPreview) => void;
  setHasHeader: (hasHeader: boolean) => void;
  setDelimiter: (delimiter: string) => void;

  // Actions - Mapping
  setMapping: (mapping: ColumnMapping) => void;
  updateMapping: (updates: Partial<ColumnMapping>) => void;

  // Actions - Job
  setJobId: (jobId: string) => void;
  setJobStatus: (status: JobStatus | null) => void;

  // Actions - UI
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Reset
  resetWizard: () => void;
}

const STEP_ORDER: WizardStep[] = ['upload', 'sheets', 'configure', 'mapping', 'finalize'];

const initialState = {
  currentStep: 'upload' as WizardStep,
  completedSteps: [] as WizardStep[],
  projectId: null,
  datasetId: null,
  filename: null,
  fileSize: null,
  availableSheets: [],
  selectedSheet: null,
  preview: null,
  mapping: null,
  hasHeader: true,
  delimiter: ',',
  jobId: null,
  jobStatus: null,
  isLoading: false,
  error: null,
};

export const useWizardStore = create<WizardState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // Navigation actions
      initWizard: (projectId, resumeDatasetId) =>
        set(
          {
            ...initialState,
            projectId,
            datasetId: resumeDatasetId || null,
            currentStep: resumeDatasetId ? 'sheets' : 'upload',
          },
          false,
          'wizard/init'
        ),

      setStep: (step) =>
        set({ currentStep: step, error: null }, false, 'wizard/setStep'),

      nextStep: () => {
        const { currentStep, completedSteps } = get();
        const currentIndex = STEP_ORDER.indexOf(currentStep);
        if (currentIndex < STEP_ORDER.length - 1) {
          const newCompletedSteps = completedSteps.includes(currentStep)
            ? completedSteps
            : [...completedSteps, currentStep];
          set(
            {
              currentStep: STEP_ORDER[currentIndex + 1],
              completedSteps: newCompletedSteps,
              error: null,
            },
            false,
            'wizard/nextStep'
          );
        }
      },

      prevStep: () => {
        const { currentStep } = get();
        const currentIndex = STEP_ORDER.indexOf(currentStep);
        if (currentIndex > 0) {
          set(
            { currentStep: STEP_ORDER[currentIndex - 1], error: null },
            false,
            'wizard/prevStep'
          );
        }
      },

      canProceed: () => {
        const state = get();
        switch (state.currentStep) {
          case 'upload':
            return !!state.datasetId;
          case 'sheets':
            return !!state.selectedSheet;
          case 'configure':
            return !!state.preview;
          case 'mapping':
            return !!(
              state.mapping?.caseId &&
              state.mapping?.activity &&
              state.mapping?.timestamp
            );
          case 'finalize':
            return state.jobStatus?.status === 'completed';
          default:
            return false;
        }
      },

      // Upload actions
      setUploadResult: (datasetId, filename, fileSize) =>
        set(
          {
            datasetId,
            filename,
            fileSize,
            error: null,
          },
          false,
          'wizard/setUploadResult'
        ),

      // Sheet actions
      setAvailableSheets: (sheets) =>
        set({ availableSheets: sheets }, false, 'wizard/setAvailableSheets'),

      selectSheet: (sheetName) =>
        set({ selectedSheet: sheetName }, false, 'wizard/selectSheet'),

      // Configure actions
      setPreview: (preview) =>
        set({ preview }, false, 'wizard/setPreview'),

      setHasHeader: (hasHeader) =>
        set({ hasHeader }, false, 'wizard/setHasHeader'),

      setDelimiter: (delimiter) =>
        set({ delimiter }, false, 'wizard/setDelimiter'),

      // Mapping actions
      setMapping: (mapping) =>
        set({ mapping }, false, 'wizard/setMapping'),

      updateMapping: (updates) =>
        set(
          (state) => ({
            mapping: state.mapping
              ? { ...state.mapping, ...updates }
              : { caseId: null, activity: null, timestamp: null, ...updates },
          }),
          false,
          'wizard/updateMapping'
        ),

      // Job actions
      setJobId: (jobId) =>
        set({ jobId }, false, 'wizard/setJobId'),

      setJobStatus: (status) =>
        set({ jobStatus: status }, false, 'wizard/setJobStatus'),

      // UI actions
      setLoading: (loading) =>
        set({ isLoading: loading }, false, 'wizard/setLoading'),

      setError: (error) =>
        set({ error, isLoading: false }, false, 'wizard/setError'),

      // Reset
      resetWizard: () => set(initialState, false, 'wizard/reset'),
    }),
    { name: 'WizardStore' }
  )
);

// Selectors
export const selectCurrentStep = (state: WizardState) => state.currentStep;
export const selectCanProceed = (state: WizardState) => state.canProceed();
export const selectIsLoading = (state: WizardState) => state.isLoading;
export const selectError = (state: WizardState) => state.error;
export const selectJobProgress = (state: WizardState) => state.jobStatus?.progress ?? 0;
