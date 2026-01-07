/**
 * Wizard Store Tests
 */

import { act, renderHook } from '@testing-library/react';
import { useWizardStore } from '../wizardStore';

// Reset store between tests
beforeEach(() => {
  act(() => {
    useWizardStore.getState().resetWizard();
  });
});

describe('wizardStore', () => {
  describe('initial state', () => {
    it('should have correct initial values', () => {
      const { result } = renderHook(() => useWizardStore());

      expect(result.current.currentStep).toBe('upload');
      expect(result.current.completedSteps).toEqual([]);
      expect(result.current.projectId).toBeNull();
      expect(result.current.datasetId).toBeNull();
      expect(result.current.filename).toBeNull();
      expect(result.current.hasHeader).toBe(true);
      expect(result.current.delimiter).toBe(',');
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });
  });

  describe('initWizard', () => {
    it('should initialize with project id', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.initWizard('project-123');
      });

      expect(result.current.projectId).toBe('project-123');
      expect(result.current.currentStep).toBe('upload');
    });

    it('should start at sheets step when resuming', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.initWizard('project-123', 'dataset-456');
      });

      expect(result.current.projectId).toBe('project-123');
      expect(result.current.datasetId).toBe('dataset-456');
      expect(result.current.currentStep).toBe('sheets');
    });
  });

  describe('navigation', () => {
    it('setStep should change current step', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setStep('mapping');
      });

      expect(result.current.currentStep).toBe('mapping');
    });

    it('nextStep should advance to next step', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.nextStep();
      });

      expect(result.current.currentStep).toBe('sheets');
      expect(result.current.completedSteps).toContain('upload');
    });

    it('nextStep should mark current step as completed', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.nextStep();
        result.current.nextStep();
      });

      expect(result.current.completedSteps).toContain('upload');
      expect(result.current.completedSteps).toContain('sheets');
    });

    it('prevStep should go back one step', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setStep('mapping');
        result.current.prevStep();
      });

      expect(result.current.currentStep).toBe('configure');
    });

    it('prevStep should not go before first step', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.prevStep();
      });

      expect(result.current.currentStep).toBe('upload');
    });

    it('nextStep should not go beyond last step', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setStep('finalize');
        result.current.nextStep();
      });

      expect(result.current.currentStep).toBe('finalize');
    });
  });

  describe('canProceed', () => {
    it('should return false on upload step without datasetId', () => {
      const { result } = renderHook(() => useWizardStore());
      expect(result.current.canProceed()).toBe(false);
    });

    it('should return true on upload step with datasetId', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setUploadResult('dataset-123', 'file.csv', 1000);
      });

      expect(result.current.canProceed()).toBe(true);
    });

    it('should return false on sheets step without selection', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setStep('sheets');
      });

      expect(result.current.canProceed()).toBe(false);
    });

    it('should return true on sheets step with selection', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setStep('sheets');
        result.current.selectSheet('Sheet1');
      });

      expect(result.current.canProceed()).toBe(true);
    });

    it('should return false on mapping step without required fields', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setStep('mapping');
      });

      expect(result.current.canProceed()).toBe(false);
    });

    it('should return true on mapping step with required fields', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setStep('mapping');
        result.current.setMapping({
          caseId: 'case_id',
          activity: 'activity',
          timestamp: 'timestamp',
        });
      });

      expect(result.current.canProceed()).toBe(true);
    });
  });

  describe('upload actions', () => {
    it('setUploadResult should set upload data', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setUploadResult('dataset-123', 'orders.csv', 50000);
      });

      expect(result.current.datasetId).toBe('dataset-123');
      expect(result.current.filename).toBe('orders.csv');
      expect(result.current.fileSize).toBe(50000);
    });
  });

  describe('sheet actions', () => {
    it('setAvailableSheets should set sheets list', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setAvailableSheets(['Sheet1', 'Sheet2', 'Data']);
      });

      expect(result.current.availableSheets).toEqual(['Sheet1', 'Sheet2', 'Data']);
    });

    it('selectSheet should set selected sheet', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.selectSheet('Sheet1');
      });

      expect(result.current.selectedSheet).toBe('Sheet1');
    });
  });

  describe('configure actions', () => {
    it('setPreview should set preview data', () => {
      const { result } = renderHook(() => useWizardStore());

      const preview = {
        columns: ['case_id', 'activity', 'timestamp'],
        rows: [{ case_id: '1', activity: 'Start', timestamp: '2024-01-01' }],
        totalRows: 100,
      };

      act(() => {
        result.current.setPreview(preview);
      });

      expect(result.current.preview).toEqual(preview);
    });

    it('setHasHeader should update header setting', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setHasHeader(false);
      });

      expect(result.current.hasHeader).toBe(false);
    });

    it('setDelimiter should update delimiter', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setDelimiter(';');
      });

      expect(result.current.delimiter).toBe(';');
    });
  });

  describe('mapping actions', () => {
    it('setMapping should set full mapping', () => {
      const { result } = renderHook(() => useWizardStore());

      const mapping = {
        caseId: 'case_id',
        activity: 'activity_name',
        timestamp: 'event_time',
        resource: 'user',
      };

      act(() => {
        result.current.setMapping(mapping);
      });

      expect(result.current.mapping).toEqual(mapping);
    });

    it('updateMapping should merge updates', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setMapping({
          caseId: 'case_id',
          activity: 'activity',
          timestamp: 'timestamp',
        });
        result.current.updateMapping({ resource: 'user_id' });
      });

      expect(result.current.mapping?.resource).toBe('user_id');
      expect(result.current.mapping?.caseId).toBe('case_id');
    });
  });

  describe('job actions', () => {
    it('setJobId should set job id', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setJobId('job-123');
      });

      expect(result.current.jobId).toBe('job-123');
    });

    it('setJobStatus should update job status', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setJobStatus({
          status: 'running',
          progress: 50,
          message: 'Processing...',
        });
      });

      expect(result.current.jobStatus?.status).toBe('running');
      expect(result.current.jobStatus?.progress).toBe(50);
    });
  });

  describe('ui actions', () => {
    it('setLoading should update loading state', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setLoading(true);
      });

      expect(result.current.isLoading).toBe(true);
    });

    it('setError should set error and clear loading', () => {
      const { result } = renderHook(() => useWizardStore());

      act(() => {
        result.current.setLoading(true);
        result.current.setError('Something went wrong');
      });

      expect(result.current.error).toBe('Something went wrong');
      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('resetWizard', () => {
    it('should reset all state to initial values', () => {
      const { result } = renderHook(() => useWizardStore());

      // Set various state
      act(() => {
        result.current.initWizard('project-123');
        result.current.setUploadResult('dataset-456', 'file.csv', 1000);
        result.current.selectSheet('Sheet1');
        result.current.setStep('mapping');
        result.current.setMapping({
          caseId: 'case_id',
          activity: 'activity',
          timestamp: 'timestamp',
        });
      });

      // Reset
      act(() => {
        result.current.resetWizard();
      });

      // Verify reset
      expect(result.current.currentStep).toBe('upload');
      expect(result.current.projectId).toBeNull();
      expect(result.current.datasetId).toBeNull();
      expect(result.current.filename).toBeNull();
      expect(result.current.selectedSheet).toBeNull();
      expect(result.current.mapping).toBeNull();
    });
  });
});
