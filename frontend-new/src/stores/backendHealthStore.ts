/**
 * Backend Health Store
 *
 * Manages backend health status and error states.
 * Replaces BackendHealthContext with Zustand.
 *
 * Note: This store manages state only. The actual health check
 * logic should be handled in a React component or hook that
 * uses the SDK and updates this store.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface BackendHealthState {
  // State
  isBackendDown: boolean;
  errorMessage: string | null;
  lastCheckTime: number | null;
  isChecking: boolean;
  consecutiveFailures: number;

  // Actions
  setBackendDown: (message: string) => void;
  setBackendUp: () => void;
  clearError: () => void;
  setChecking: (checking: boolean) => void;
  recordCheckResult: (success: boolean, errorMessage?: string) => void;

  // Computed
  shouldRetry: () => boolean;
}

const initialState = {
  isBackendDown: false,
  errorMessage: null,
  lastCheckTime: null,
  isChecking: false,
  consecutiveFailures: 0,
};

const MAX_CONSECUTIVE_FAILURES = 3;
const RETRY_DELAY_MS = 30000; // 30 seconds

export const useBackendHealthStore = create<BackendHealthState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      setBackendDown: (message) =>
        set(
          {
            isBackendDown: true,
            errorMessage: message,
            lastCheckTime: Date.now(),
          },
          false,
          'health/setBackendDown'
        ),

      setBackendUp: () =>
        set(
          {
            isBackendDown: false,
            errorMessage: null,
            consecutiveFailures: 0,
            lastCheckTime: Date.now(),
          },
          false,
          'health/setBackendUp'
        ),

      clearError: () =>
        set(
          {
            isBackendDown: false,
            errorMessage: null,
          },
          false,
          'health/clearError'
        ),

      setChecking: (checking) =>
        set({ isChecking: checking }, false, 'health/setChecking'),

      recordCheckResult: (success, errorMessage) => {
        if (success) {
          set(
            {
              isBackendDown: false,
              errorMessage: null,
              consecutiveFailures: 0,
              lastCheckTime: Date.now(),
              isChecking: false,
            },
            false,
            'health/checkSuccess'
          );
        } else {
          set(
            (state) => ({
              isBackendDown: true,
              errorMessage: errorMessage || 'Backend is unavailable',
              consecutiveFailures: state.consecutiveFailures + 1,
              lastCheckTime: Date.now(),
              isChecking: false,
            }),
            false,
            'health/checkFailure'
          );
        }
      },

      shouldRetry: () => {
        const state = get();
        if (!state.isBackendDown) return false;
        if (state.isChecking) return false;
        if (state.consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) return false;

        const timeSinceLastCheck = state.lastCheckTime
          ? Date.now() - state.lastCheckTime
          : Infinity;

        return timeSinceLastCheck >= RETRY_DELAY_MS;
      },
    }),
    { name: 'BackendHealthStore' }
  )
);

// Selectors
export const selectIsBackendDown = (state: BackendHealthState) =>
  state.isBackendDown;
export const selectErrorMessage = (state: BackendHealthState) =>
  state.errorMessage;
export const selectIsChecking = (state: BackendHealthState) => state.isChecking;
