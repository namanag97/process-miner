/**
 * Backend Health Store Tests
 */

import { act, renderHook } from '@testing-library/react';
import {
  useBackendHealthStore,
  selectIsBackendDown,
  selectErrorMessage,
} from '../backendHealthStore';

// Reset store between tests - need to fully reset state including consecutiveFailures
beforeEach(() => {
  act(() => {
    // clearError doesn't reset consecutiveFailures, so we use setBackendUp which does
    useBackendHealthStore.getState().setBackendUp();
  });
});

describe('backendHealthStore', () => {
  describe('initial state', () => {
    it('should have backend up by default', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      expect(result.current.isBackendDown).toBe(false);
      expect(result.current.errorMessage).toBeNull();
      expect(result.current.isChecking).toBe(false);
      expect(result.current.consecutiveFailures).toBe(0);
    });
  });

  describe('setBackendDown', () => {
    it('should set backend down with error message', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      act(() => {
        result.current.setBackendDown('Connection refused');
      });

      expect(result.current.isBackendDown).toBe(true);
      expect(result.current.errorMessage).toBe('Connection refused');
      expect(result.current.lastCheckTime).toBeTruthy();
    });
  });

  describe('setBackendUp', () => {
    it('should clear error state and reset failures', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      act(() => {
        result.current.setBackendDown('Error');
        result.current.setBackendUp();
      });

      expect(result.current.isBackendDown).toBe(false);
      expect(result.current.errorMessage).toBeNull();
      expect(result.current.consecutiveFailures).toBe(0);
    });
  });

  describe('clearError', () => {
    it('should clear error without affecting other state', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      act(() => {
        result.current.setBackendDown('Error');
        result.current.clearError();
      });

      expect(result.current.isBackendDown).toBe(false);
      expect(result.current.errorMessage).toBeNull();
    });
  });

  describe('setChecking', () => {
    it('should update checking state', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      act(() => {
        result.current.setChecking(true);
      });

      expect(result.current.isChecking).toBe(true);

      act(() => {
        result.current.setChecking(false);
      });

      expect(result.current.isChecking).toBe(false);
    });
  });

  describe('recordCheckResult', () => {
    it('should record successful check', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      // First fail
      act(() => {
        result.current.recordCheckResult(false, 'Error');
      });

      expect(result.current.isBackendDown).toBe(true);
      expect(result.current.consecutiveFailures).toBe(1);

      // Then succeed
      act(() => {
        result.current.recordCheckResult(true);
      });

      expect(result.current.isBackendDown).toBe(false);
      expect(result.current.consecutiveFailures).toBe(0);
      expect(result.current.isChecking).toBe(false);
    });

    it('should increment failures on failed check', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      act(() => {
        result.current.recordCheckResult(false, 'Error 1');
        result.current.recordCheckResult(false, 'Error 2');
        result.current.recordCheckResult(false, 'Error 3');
      });

      expect(result.current.consecutiveFailures).toBe(3);
    });

    it('should use default error message if not provided', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      act(() => {
        result.current.recordCheckResult(false);
      });

      expect(result.current.errorMessage).toBe('Backend is unavailable');
    });
  });

  describe('shouldRetry', () => {
    it('should return false when backend is up', () => {
      const { result } = renderHook(() => useBackendHealthStore());
      expect(result.current.shouldRetry()).toBe(false);
    });

    it('should return false when currently checking', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      act(() => {
        result.current.setBackendDown('Error');
        result.current.setChecking(true);
      });

      expect(result.current.shouldRetry()).toBe(false);
    });

    it('should return false after max consecutive failures', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      act(() => {
        result.current.recordCheckResult(false, 'Error');
        result.current.recordCheckResult(false, 'Error');
        result.current.recordCheckResult(false, 'Error');
      });

      expect(result.current.consecutiveFailures).toBe(3);
      expect(result.current.shouldRetry()).toBe(false);
    });

    it('should return false if checked recently (within 30 seconds)', () => {
      const { result } = renderHook(() => useBackendHealthStore());

      act(() => {
        result.current.setBackendDown('Error');
      });

      // Just set backend down, so lastCheckTime is very recent
      expect(result.current.shouldRetry()).toBe(false);
    });
  });

  describe('selectors', () => {
    it('selectIsBackendDown returns backend status', () => {
      act(() => {
        useBackendHealthStore.getState().setBackendDown('Error');
      });

      expect(selectIsBackendDown(useBackendHealthStore.getState())).toBe(true);
    });

    it('selectErrorMessage returns error message', () => {
      act(() => {
        useBackendHealthStore.getState().setBackendDown('Connection refused');
      });

      expect(selectErrorMessage(useBackendHealthStore.getState())).toBe('Connection refused');
    });
  });
});
