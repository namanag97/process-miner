import { useEffect } from 'react';

/**
 * Hook to warn users before they leave the page with unsaved changes.
 * Shows browser's native "Leave site?" dialog on refresh/close.
 * 
 * @param enabled - Whether to show the warning
 * @param message - Custom message (note: most browsers ignore custom messages now)
 */
export function useBeforeUnload(enabled: boolean, message?: string) {
  useEffect(() => {
    if (!enabled) return;

    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      // Modern browsers require returnValue to be set
      e.returnValue = message || 'You have unsaved changes. Are you sure you want to leave?';
      return e.returnValue;
    };

    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [enabled, message]);
}

export default useBeforeUnload;
